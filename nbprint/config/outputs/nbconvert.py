import base64
import binascii
import json
import os
import struct
import warnings
from collections import Counter
from pathlib import Path
from typing import Any, Literal

from ccflow import PyObjectPath
from nbformat import NotebookNode
from pydantic import Field, PrivateAttr, field_validator

from nbprint.config import Configuration, Outputs, OutputsProcessing

__all__ = (
    "HTMLOutputs",
    "NBConvertOutputs",
    "NBConvertShortCircuitOutputs",
    "NotebookOutputs",
    "PDFOutputs",
    "RenderCompletenessError",
    "RenderCompletenessWarning",
    "WebHTMLOutputs",
    "short_circuit_hook",
)


# nbconvert/traitlets paths that nbprint already drives through its own fields.
# Allowing these in ``nbconvert_config`` would silently shadow or fight nbprint's
# own wiring (e.g. ``ExecutePreprocessor.enabled`` only reaches the convert pass
# here, triggering a second execution). Maps each managed path — and its CLI
# alias form — to the nbprint field that should be used instead.
_NBPRINT_MANAGED_TRAITS: dict[str, str] = {
    "NbConvertApp.export_format": "the 'target' field",
    "to": "the 'target' field",
    "TemplateExporter.template_name": "the 'template' field",
    "template": "the 'template' field",
    "NbConvertApp.output_base": "the 'naming'/'root' fields",
    "output": "the 'naming'/'root' fields",
    "ExecutePreprocessor.timeout": "the 'timeout' field",
    "ExecutePreprocessor.enabled": "the 'execute' field",
    "execute": "the 'execute' field",
}

# nbconvert's stock webpdf exporter captures the PDF a fixed delay after the network goes idle, which
# races paged.js and silently truncates long documents. nbprint's exporter waits for the template's
# pagination-complete signal instead, so the webpdf target is routed to it rather than to upstream's.
# Registered under its own entry-point name so it never shadows nbconvert's builtin "webpdf".
_EXPORTER_FOR_TARGET = {"webpdf": "nbprintwebpdf"}

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# Byte offsets of the width/height pair inside a PNG's IHDR chunk: 8-byte
# signature + 4-byte length + 4-byte chunk type.
_PNG_IHDR_DIMENSIONS = slice(16, 24)


class RenderCompletenessWarning(UserWarning):
    """Emitted when a rendered PDF holds fewer figures than its source notebook."""


class RenderCompletenessError(RuntimeError):
    """Raised instead of :class:`RenderCompletenessWarning` under ``validate_figures='strict'``."""


def _png_dimensions(data: bytes) -> tuple[int, int] | None:
    """Read ``(width, height)`` in pixels straight out of a PNG header.

    Avoids taking an image-decoding dependency: the dimensions live in the
    fixed-position IHDR chunk that every PNG opens with. Returns ``None`` for
    anything that isn't a PNG or is truncated before the header ends, so
    callers can drop unattributable outputs rather than guess at them.
    """
    if not data.startswith(_PNG_SIGNATURE) or len(data) < _PNG_IHDR_DIMENSIONS.stop:
        return None
    width, height = struct.unpack(">II", data[_PNG_IHDR_DIMENSIONS])
    return width, height


def _run_nbconvert(argv: list[str]) -> None:
    """Run nbconvert in-process without reusing the global NbConvertApp singleton.

    nbconvert's ``main()`` goes through ``NbConvertApp.launch_instance``, which caches
    one app on the class. Reusing it across conversions in a single process leaks config
    (notably ``ExecutePreprocessor.enabled``), so a later plain convert pass re-executes
    the notebook. A fresh instance per call avoids that.
    """
    from nbconvert.nbconvertapp import NbConvertApp

    app = NbConvertApp()
    app.initialize(argv)
    app.start()  # ty: ignore[missing-argument]


class NBConvertOutputs(Outputs):
    target: Literal["ipynb", "notebook", "html", "webhtml", "pdf", "webpdf"] | None = "html"  # TODO: nbconvert types
    execute: bool | None = True
    timeout: int | None = 600
    template: str | None = "nbprint"

    # Generic passthrough for any nbconvert / traitlets configuration. Maps 1:1
    # onto nbconvert's ``--Class.trait=value`` CLI options, so anything
    # configurable on an exporter, preprocessor, or the app itself is reachable
    # without nbprint needing a dedicated field per option. Accepts either flat
    # dotted keys or nested namespaces (handled identically):
    #
    #   nbconvert_config:
    #     WebPDFExporter.page_render_timeout: 5000   # ms to wait for JS before PDF
    #     HTMLExporter:
    #       embed_images: true
    #     TemplateExporter.exclude_input: true
    #
    # The nested form maps cleanly onto a hydra/lerna CLI override:
    #   ++nbprint.outputs.nbconvert_config.WebPDFExporter.page_render_timeout=5000
    #
    # Applied to the conversion (exporter) pass. Scalars pass through directly;
    # bools render as ``True``/``False``; lists/tuples are JSON-encoded.
    nbconvert_config: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Generic nbconvert/traitlets configuration for the conversion pass. "
            "Keys are traitlet paths (flat 'Class.trait' or nested) mapping onto "
            "nbconvert's '--Class.trait=value' CLI options."
        ),
    )

    # TODO: maybe allow collecting by index
    # collect_cells: list[int] = Field(default=[], description="List of cell indices to collect outputs from.")
    collect_outputs: bool = Field(
        default=False, description=("Whether to collect cell outputs into the context. Cells with tag `nbprint:output:<key>` will be collected under `<key>`.")
    )
    execute_hook: PyObjectPath | None = Field(
        default=None,
        description=(
            "A callable hook that is called after nbconvert execution of the notebook. "
            "It is passed the config instance. "
            "If it returns something non-None, that value is returned by `run` instead of the output path."
            "NOTE: Parent/child class hooks may also be called."
        ),
    )
    nbconvert_hook: PyObjectPath | None = Field(
        default=None,
        description=(
            "A callable hook that is called after nbconvert of the previously executed notebook. "
            "It is passed the config instance. "
            "If it returns something non-None, that value is returned by `run` instead of the output path."
            "NOTE: Parent/child class hooks may also be called."
        ),
    )

    validate_figures: Literal["off", "warn", "strict"] = Field(
        default="off",
        description=(
            "Post-render check that every figure in the executed notebook survived into the PDF. "
            "'off' (default): no check. 'warn': emit a RenderCompletenessWarning listing what is "
            "missing. 'strict': raise RenderCompletenessError instead. Only runs for PDF targets, "
            "and silently does nothing when no PDF reader is installed."
        ),
    )

    _collected_cells: dict[int | str, list[dict[str, str]]] = PrivateAttr(default_factory=dict)

    @property
    def outputs(self) -> dict[int | str, list[dict[str, str]]]:
        # NOTE: parent class has `output`
        return self._collected_cells

    @field_validator("target", mode="before")
    @classmethod
    def validate_target(cls, v) -> str:
        if v is None:
            return "html"
        if v == "pdf":
            return "webpdf"
        if v == "notebook":
            return "ipynb"
        return v

    def _compute_outputs(self, config: "Configuration") -> None:
        super()._compute_outputs(config=config)
        # Update executed path if needed
        if self.execute:
            self._nb_executed_path = self.notebook.parent / f"{self.notebook.stem}.executed.ipynb"
        # Update output path
        if self.target == "webpdf":
            target = "pdf"
        elif self.target == "webhtml":
            target = "html"
        else:
            target = self.target
        if self.target == "ipynb" and self.execute:
            self._output_path = Path(str(self.output).replace(".ipynb", ".executed.ipynb"))
        else:
            self._output_path = Path(str(self.output).replace(".ipynb", f".{target}"))

    @staticmethod
    def _get_output_key(cell: NotebookNode) -> str | None:
        """Get the output key from cell metadata or tags."""
        if "nbprint" in cell.metadata and "output" in cell.metadata.nbprint:
            return cell.metadata.nbprint.output
        for tag in cell.metadata.get("tags", []):
            if tag.startswith("nbprint:output:"):
                return tag.split("nbprint:output:")[1]
        return None

    @staticmethod
    def _flatten_config(config: dict[str, Any]) -> dict[str, Any]:
        """Flatten nested traitlets namespaces into dotted-path keys.

        ``{"WebPDFExporter": {"page_render_timeout": 5000}}`` becomes
        ``{"WebPDFExporter.page_render_timeout": 5000}``. Flat keys are passed
        through unchanged, so flat and nested inputs normalize identically.
        """
        flat: dict[str, Any] = {}

        def _walk(mapping: dict[str, Any], prefix: str) -> None:
            for key, value in mapping.items():
                path = f"{prefix}{key}"
                if isinstance(value, dict):
                    _walk(value, prefix=f"{path}.")
                else:
                    flat[path] = value

        _walk(config, prefix="")
        return flat

    @field_validator("nbconvert_config", mode="after")
    @classmethod
    def _reject_managed_traits(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Reject traitlet paths that nbprint already manages via its own fields.

        These would silently shadow nbprint's wiring (and the
        ``ExecutePreprocessor.*`` ones only reach the convert pass here, so they
        either no-op or trigger an unwanted second execution). Point the user at
        the dedicated field instead.
        """
        for path in cls._flatten_config(v):
            hint = _NBPRINT_MANAGED_TRAITS.get(path)
            if hint is not None:
                msg = f"nbconvert_config key {path!r} is managed by nbprint; set {hint} instead."
                raise ValueError(msg)
        return v

    @staticmethod
    def _format_nbconvert_config_args(config: dict[str, Any]) -> list[str]:
        """Translate a traitlets config mapping into nbconvert CLI args.

        Keys map onto nbconvert's ``--Class.trait=value`` CLI options. Both
        shapes are accepted and treated identically, so the same option is
        reachable from flat YAML, nested YAML, or a hydra/lerna CLI override:

            {"WebPDFExporter.page_render_timeout": 5000}          # flat dotted key
            {"WebPDFExporter": {"page_render_timeout": 5000}}     # nested namespaces

        Nested dicts are flattened into dotted paths (mirroring traitlets' own
        hierarchical ``Config`` model). Booleans render as ``True``/``False``;
        ints/floats/strings pass through as-is; any other value (list, tuple)
        is JSON-encoded so container traits round-trip through the CLI.
        """
        args: list[str] = []
        for path, value in NBConvertOutputs._flatten_config(config).items():
            if isinstance(value, bool):
                rendered = "True" if value else "False"
            elif isinstance(value, (str, int, float)):
                rendered = str(value)
            else:
                rendered = json.dumps(value)
            args.append(f"--{path}={rendered}")
        return args

    def _extract_cell_outputs(self) -> None:
        """Extract outputs from selected cells into the context."""
        # We're going to:
        # - read the notebook
        # - go through each cell and look for nbprint metadata
        #   - either `nbprint:output:<key>` tag or
        #   - `nbprint` metadata with `output` key
        # - collect outputs from those cells into self._collected_cells, such that:
        #     - the mimetype is used to determine the type of output
        #     - if we know how to deal, store natively
        #     - else, store as-is

        from nbformat import reads

        notebook_content = self.executed_notebook.read_text()
        nb = reads(notebook_content, as_version=4)

        for cell in nb.cells:
            if "nbprint" not in cell.metadata and not any(tag.startswith("nbprint:output:") for tag in cell.metadata.get("tags", [])):
                continue

            output_key = self._get_output_key(cell)
            if output_key is None:
                continue

            outputs = []
            for output in cell.get("outputs", []):
                output_data = {}
                if "data" in output:
                    output_data = dict(output["data"].items())
                elif "text" in output:
                    output_data["text/plain"] = output["text"]
                outputs.append(output_data)
            if output_key not in self._collected_cells:
                self._collected_cells[output_key] = []
            self._collected_cells[output_key].extend(outputs)

    @staticmethod
    def _notebook_figure_sizes(nb: NotebookNode) -> Counter[tuple[int, int]]:
        """Tally the pixel dimensions of every ``image/png`` output in a notebook.

        Outputs whose payload will not decode, or that are not PNG after all,
        are dropped rather than bucketed together: an unattributable figure
        would otherwise be permanently unmatchable and warn on every render.
        """
        sizes: Counter[tuple[int, int]] = Counter()
        for cell in nb.cells:
            for output in cell.get("outputs", []):
                payload = output.get("data", {}).get("image/png")
                if payload is None:
                    continue
                if isinstance(payload, str):
                    try:
                        payload = base64.b64decode(payload)
                    except (binascii.Error, ValueError):
                        continue
                dimensions = _png_dimensions(payload)
                if dimensions is not None:
                    sizes[dimensions] += 1
        return sizes

    @staticmethod
    def _pdf_image_sizes(path: Path) -> Counter[tuple[int, int]] | None:
        """Tally the pixel dimensions of every image embedded in a PDF.

        Returns ``None`` — meaning "no opinion", not "no images" — when no PDF
        reader is installed or the file cannot be parsed, so a missing optional
        dependency or a half-written file can never fail a render.

        Images are counted once per page they appear on. A PDF writer is free
        to store one image object and reference it from several pages (a
        repeated header logo, say), and per-page counting keeps that in step
        with how many figures a reader actually sees.
        """
        try:
            import pymupdf
        except ImportError:
            try:
                import fitz as pymupdf
            except ImportError:
                return None
        sizes: Counter[tuple[int, int]] = Counter()
        try:
            with pymupdf.open(path) as doc:
                for page in doc:
                    for image in page.get_images(full=True):
                        # (xref, smask, width, height, bpc, colorspace, ...)
                        sizes[(image[2], image[3])] += 1
        except Exception:  # noqa: BLE001 - a render must not fail on an unreadable PDF
            return None
        return sizes

    @staticmethod
    def _figure_shortfall(notebook_sizes: Counter[tuple[int, int]], pdf_sizes: Counter[tuple[int, int]]) -> dict[tuple[int, int], int]:
        """Figures the PDF is short of, bucketed by pixel dimensions.

        Matching per size bucket rather than on bare totals is what makes the
        check trustworthy on real reports. A cover page contributes images that
        no notebook cell produced — a logo, a masthead — and against a total
        those extras read as credit, so a document that dropped two charts
        still totals up as complete. Because credit is only ever granted
        within a bucket, an unrelated image can never stand in for a lost
        figure; it lands in its own bucket and is ignored as surplus.
        """
        return {size: count - pdf_sizes.get(size, 0) for size, count in notebook_sizes.items() if count > pdf_sizes.get(size, 0)}

    def _figure_source_notebook(self) -> NotebookNode | None:
        """Parse whichever notebook on disk holds the outputs that were rendered."""
        from nbformat import reads

        path = self.executed_notebook if self.execute else self.notebook
        if path is None or not Path(path).exists():
            return None
        return reads(Path(path).read_text(encoding="utf-8"), as_version=4)

    def _validate_render_completeness(self) -> None:
        """Check that the figures in the executed notebook survived into the PDF.

        A PDF render can silently lose content — a chart that paged.js chunked
        off the end of the document, an output that never got a chance to
        decode — and the resulting file is perfectly valid, just short. This
        compares the figures the notebook produced against the images the PDF
        actually embeds and reports the difference.

        No-ops unless ``validate_figures`` is enabled and the target is a PDF.
        A shortfall warns by default and raises under ``'strict'``; a surplus
        is always silent, since a report legitimately carries artwork that no
        cell produced.

        The comparison keys on pixel dimensions, which assumes the PDF writer
        embeds figures at their source resolution. A writer that resamples
        would make this over-report; that possibility, not any doubt about the
        underlying loss, is why the check is off by default.
        """
        if self.validate_figures == "off" or self.target != "webpdf":
            return
        pdf = Path(self.output)
        if not pdf.exists():
            return
        pdf_sizes = self._pdf_image_sizes(pdf)
        if pdf_sizes is None:
            return
        nb = self._figure_source_notebook()
        if nb is None:
            return

        shortfall = self._figure_shortfall(self._notebook_figure_sizes(nb), pdf_sizes)
        if not shortfall:
            return
        detail = ", ".join(f"{width}x{height} (x{count})" for (width, height), count in sorted(shortfall.items()))
        msg = f"{pdf}: {sum(shortfall.values())} notebook figure(s) missing from the rendered PDF: {detail}"
        if self.validate_figures == "strict":
            raise RenderCompletenessError(msg)
        warnings.warn(msg, RenderCompletenessWarning, stacklevel=2)

    def run(self, config: "Configuration", gen: NotebookNode) -> Path:
        # Run parent to create notebook
        notebook = super().run(config=config, gen=gen)

        # If notebook is None, we stop
        if notebook in (None, OutputsProcessing.STOP):
            return OutputsProcessing.STOP

        # TODO: fix in nbconvert
        output = str(self.output).replace(".webpdf", ".pdf").replace(".pdf", "") if self.target == "webpdf" else str(self.output)

        cmd = [
            str(notebook),
            f"--to={_EXPORTER_FOR_TARGET.get(self.target, self.target)}",
            f"--output={output}",
            f"--template={self.template}",
        ]

        # Generic nbconvert/traitlets passthrough (e.g. WebPDFExporter.page_render_timeout)
        cmd.extend(self._format_nbconvert_config_args(self.nbconvert_config))

        # We have some cheats here because we have to
        os.environ["_NBPRINT_IN_NBCONVERT"] = "1"
        os.environ["PSP_JUPYTER_HTML_EXPORT"] = "1"

        if self.execute:
            nbex_cmd = [
                str(notebook),
                "--to=notebook",
                f"--output={self.executed_notebook!s}",
                "--execute",
                f"--ExecutePreprocessor.timeout={self.timeout}",
            ]

            # Update cmd to use executed notebook
            cmd[0] = str(self.executed_notebook)

            # Execute nbconvert
            _run_nbconvert(nbex_cmd)

            # Extract cells by tags
            self._extract_cell_outputs()

            if self.execute_hook and self.execute_hook.object(config) in (OutputsProcessing.STOP, None):
                return OutputsProcessing.STOP

        if not (self.execute and self.target == "ipynb"):
            # If target is notebook, we already did it above
            _run_nbconvert(cmd)

        self._validate_render_completeness()

        if self.nbconvert_hook and self.nbconvert_hook.object(config) in (OutputsProcessing.STOP, None):
            return OutputsProcessing.STOP
        return self.output


class NotebookOutputs(NBConvertOutputs):
    target: Literal["ipynb"] = "ipynb"


class HTMLOutputs(NBConvertOutputs):
    target: Literal["html"] = "html"


class WebHTMLOutputs(NBConvertOutputs):
    target: Literal["webhtml"] = "webhtml"


class PDFOutputs(NBConvertOutputs):
    target: Literal["webpdf"] = "webpdf"


def short_circuit_hook(config: "Configuration") -> OutputsProcessing | bool:
    """A hook that short-circuits processing if a certain cell returns True."""
    return (
        OutputsProcessing.STOP
        if config.outputs.outputs
        and "stop" in config.outputs.outputs
        and any(outcome.get("text/plain", "").strip().lower() == "true" for outcome in config.outputs.outputs["stop"])
        else True
    )


class NBConvertShortCircuitOutputs(NBConvertOutputs):
    """A specialized NBConvertOutputs that installs a default hook to stop processing if a certain cell
    with tag nbprint:output:stop returns True.
    """

    execute_hook: PyObjectPath = Field(
        default=PyObjectPath("nbprint.config.outputs.nbconvert.short_circuit_hook"),
        description="A hook that short-circuits processing if a certain cell with tag nbprint:output:stop returns True.",
    )
