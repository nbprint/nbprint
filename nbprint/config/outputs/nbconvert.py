import os
from pathlib import Path
from typing import Literal

from ccflow import PyObjectPath
from nbformat import NotebookNode
from pydantic import Field, PrivateAttr, field_validator

from nbprint.config import Configuration, Outputs, OutputsProcessing

__all__ = ("HTMLOutputs", "NBConvertOutputs", "NBConvertShortCircuitOutputs", "NotebookOutputs", "PDFOutputs", "WebHTMLOutputs", "short_circuit_hook")


class NBConvertOutputs(Outputs):
    target: Literal["ipynb", "notebook", "html", "webhtml", "pdf", "webpdf"] | None = "html"  # TODO: nbconvert types
    execute: bool | None = True
    timeout: int | None = 600
    template: str | None = "nbprint"

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

    def run(self, config: "Configuration", gen: NotebookNode) -> Path:
        from nbconvert.nbconvertapp import main as execute_nbconvert

        # Run parent to create notebook
        notebook = super().run(config=config, gen=gen)

        # If notebook is None, we stop
        if notebook in (None, OutputsProcessing.STOP):
            return OutputsProcessing.STOP

        # TODO: fix in nbconvert
        output = str(self.output).replace(".webpdf", ".pdf").replace(".pdf", "") if self.target == "webpdf" else str(self.output)

        cmd = [
            str(notebook),
            f"--to={self.target}",
            f"--output={output}",
            f"--template={self.template}",
        ]

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
            execute_nbconvert(nbex_cmd)

            # Extract cells by tags
            self._extract_cell_outputs()

            if self.execute_hook and self.execute_hook.object(config) in (OutputsProcessing.STOP, None):
                return OutputsProcessing.STOP

        if not (self.execute and self.target == "ipynb"):
            # If target is notebook, we already did it above
            execute_nbconvert(cmd)

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
