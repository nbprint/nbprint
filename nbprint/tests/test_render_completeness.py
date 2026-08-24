import struct
import sys
import warnings
import zlib
from base64 import b64encode
from pathlib import Path

import pytest
from nbformat import writes
from nbformat.v4 import new_code_cell, new_notebook, new_output

from nbprint.config.outputs.nbconvert import (
    NBConvertOutputs,
    RenderCompletenessError,
    RenderCompletenessWarning,
    _png_dimensions,
)

# PyMuPDF is a develop dependency, so this should not skip in CI. Both import
# names are tried for the same reason the code under test tries both: the
# package was renamed from ``fitz`` to ``pymupdf``, and pinning to one name
# would silently skip this entire file rather than fail, hiding every test in
# it behind a green run.
try:
    import pymupdf
except ImportError:
    pymupdf = pytest.importorskip("fitz", reason="PDF image counting needs PyMuPDF")


def make_png(width: int, height: int) -> bytes:
    """Encode a solid-colour PNG of exactly `width` x `height` pixels."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    scanlines = b"".join(b"\x00" + b"\x10\x20\x30" * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(scanlines))
        + chunk(b"IEND", b"")
    )


def write_notebook(path: Path, figure_sizes: list[tuple[int, int]]) -> Path:
    """Write an executed notebook carrying one image/png output per size."""
    cells = [
        new_code_cell(
            source="plot()",
            outputs=[new_output("display_data", data={"image/png": b64encode(make_png(width, height)).decode()})],
        )
        for width, height in figure_sizes
    ]
    path.write_text(writes(new_notebook(cells=cells)), encoding="utf-8")
    return path


def write_pdf(path: Path, pages: list[list[tuple[int, int]]]) -> Path:
    """Write a PDF whose pages embed images of the given pixel sizes."""
    doc = pymupdf.open()
    for page_sizes in pages:
        page = doc.new_page()
        top = 10.0
        for width, height in page_sizes:
            page.insert_image(pymupdf.Rect(10, top, 110, top + 100), stream=make_png(width, height))
            top += 110
    doc.save(path)
    doc.close()
    return path


def make_outputs(tmp_path: Path, notebook_sizes, pdf_pages, *, target="webpdf", validate_figures="warn") -> NBConvertOutputs:
    outputs = NBConvertOutputs(naming="{{name}}", root=tmp_path, target=target, validate_figures=validate_figures)
    outputs._nb_path = write_notebook(tmp_path / "report.ipynb", notebook_sizes)
    outputs._nb_executed_path = outputs._nb_path
    outputs._output_path = write_pdf(tmp_path / "report.pdf", pdf_pages)
    return outputs


class TestPngDimensions:
    def test_reads_ihdr(self):
        assert _png_dimensions(make_png(120, 80)) == (120, 80)

    def test_rejects_non_png(self):
        assert _png_dimensions(b"GIF89a" + b"\x00" * 32) is None

    def test_rejects_truncated_header(self):
        assert _png_dimensions(make_png(120, 80)[:20]) is None


class TestNotebookFigureSizes:
    def test_counts_png_outputs_by_size(self, tmp_path):
        from nbformat import reads

        path = write_notebook(tmp_path / "nb.ipynb", [(400, 300), (400, 300), (120, 40)])
        nb = reads(path.read_text(encoding="utf-8"), as_version=4)
        assert NBConvertOutputs._notebook_figure_sizes(nb) == {(400, 300): 2, (120, 40): 1}

    def test_ignores_non_image_outputs(self):
        nb = new_notebook(
            cells=[
                new_code_cell(source="1", outputs=[new_output("execute_result", data={"text/plain": "1"})]),
                new_code_cell(source="2", outputs=[new_output("stream", name="stdout", text="hi")]),
            ]
        )
        assert NBConvertOutputs._notebook_figure_sizes(nb) == {}

    def test_drops_undecodable_payloads(self):
        """An unattributable figure is dropped, not bucketed — it could never be matched."""
        nb = new_notebook(cells=[new_code_cell(source="1", outputs=[new_output("display_data", data={"image/png": "!!! not base64 !!!"})])])
        assert NBConvertOutputs._notebook_figure_sizes(nb) == {}


class TestPdfImageSizes:
    def test_counts_images_per_page(self, tmp_path):
        pdf = write_pdf(tmp_path / "doc.pdf", [[(120, 80), (64, 64)], [(120, 80)]])
        assert NBConvertOutputs._pdf_image_sizes(pdf) == {(120, 80): 2, (64, 64): 1}

    def test_empty_pdf_counts_nothing(self, tmp_path):
        pdf = write_pdf(tmp_path / "doc.pdf", [[]])
        assert NBConvertOutputs._pdf_image_sizes(pdf) == {}

    def test_unreadable_file_has_no_opinion(self, tmp_path):
        """`None` means "cannot tell", which the caller treats as "do not warn"."""
        broken = tmp_path / "broken.pdf"
        broken.write_bytes(b"not a pdf at all")
        assert NBConvertOutputs._pdf_image_sizes(broken) is None

    def test_missing_dependency_has_no_opinion(self, tmp_path, monkeypatch):
        pdf = write_pdf(tmp_path / "doc.pdf", [[(120, 80)]])
        monkeypatch.setitem(sys.modules, "pymupdf", None)
        monkeypatch.setitem(sys.modules, "fitz", None)
        assert NBConvertOutputs._pdf_image_sizes(pdf) is None


class TestFigureShortfall:
    def test_exact_match(self):
        assert NBConvertOutputs._figure_shortfall({(400, 300): 3}, {(400, 300): 3}) == {}

    def test_shortfall_per_bucket(self):
        assert NBConvertOutputs._figure_shortfall({(400, 300): 5}, {(400, 300): 3}) == {(400, 300): 2}

    def test_surplus_is_not_a_shortfall(self):
        assert NBConvertOutputs._figure_shortfall({(400, 300): 2}, {(400, 300): 4}) == {}

    def test_surplus_in_one_bucket_cannot_offset_a_deficit_in_another(self):
        """The cover-page trap: extra images only ever count as surplus in their own bucket."""
        notebook = {(400, 300): 5}
        pdf = {(400, 300): 3, (120, 40): 2}
        assert sum(notebook.values()) == sum(pdf.values())  # a naive total comparison sees no loss
        assert NBConvertOutputs._figure_shortfall(notebook, pdf) == {(400, 300): 2}


class TestValidateRenderCompleteness:
    def test_shortfall_warns(self, tmp_path):
        outputs = make_outputs(tmp_path, [(400, 300)] * 4, [[(400, 300)], [(400, 300)]])
        with pytest.warns(RenderCompletenessWarning, match="2 notebook figure"):
            outputs._validate_render_completeness()

    def test_exact_match_is_silent(self, tmp_path):
        outputs = make_outputs(tmp_path, [(400, 300), (200, 100)], [[(400, 300)], [(200, 100)]])
        with warnings.catch_warnings():
            warnings.simplefilter("error", RenderCompletenessWarning)
            outputs._validate_render_completeness()

    def test_surplus_is_silent(self, tmp_path):
        outputs = make_outputs(tmp_path, [(400, 300)], [[(400, 300), (400, 300), (120, 40)]])
        with warnings.catch_warnings():
            warnings.simplefilter("error", RenderCompletenessWarning)
            outputs._validate_render_completeness()

    def test_cover_page_images_do_not_mask_a_loss(self, tmp_path):
        """A cover logo inflates the PDF's total; the check must still see the two lost charts."""
        outputs = make_outputs(
            tmp_path,
            [(400, 300)] * 5,
            [[(120, 40), (120, 40)], [(400, 300)], [(400, 300)], [(400, 300)]],
        )
        pdf_total = sum(NBConvertOutputs._pdf_image_sizes(outputs.output).values())
        assert pdf_total == 5  # naive totals match the notebook's five figures
        with pytest.warns(RenderCompletenessWarning, match=r"2 notebook figure\(s\) missing.*400x300 \(x2\)"):
            outputs._validate_render_completeness()

    def test_off_by_default(self, tmp_path):
        outputs = make_outputs(tmp_path, [(400, 300)] * 4, [[(400, 300)]], validate_figures="off")
        assert NBConvertOutputs(naming="{{name}}", root=tmp_path).validate_figures == "off"
        with warnings.catch_warnings():
            warnings.simplefilter("error", RenderCompletenessWarning)
            outputs._validate_render_completeness()

    @pytest.mark.parametrize("target", ["html", "webhtml", "ipynb"])
    def test_non_pdf_target_is_a_no_op(self, tmp_path, target):
        outputs = make_outputs(tmp_path, [(400, 300)] * 4, [[(400, 300)]], target=target)
        with warnings.catch_warnings():
            warnings.simplefilter("error", RenderCompletenessWarning)
            outputs._validate_render_completeness()

    def test_strict_raises(self, tmp_path):
        outputs = make_outputs(tmp_path, [(400, 300)] * 4, [[(400, 300)]], validate_figures="strict")
        with pytest.raises(RenderCompletenessError, match="3 notebook figure"):
            outputs._validate_render_completeness()

    def test_strict_is_silent_when_complete(self, tmp_path):
        outputs = make_outputs(tmp_path, [(400, 300)], [[(400, 300)]], validate_figures="strict")
        outputs._validate_render_completeness()

    def test_missing_dependency_degrades_quietly(self, tmp_path, monkeypatch):
        """Even in strict mode: an absent optional dependency must not fail a render."""
        outputs = make_outputs(tmp_path, [(400, 300)] * 4, [[(400, 300)]], validate_figures="strict")
        monkeypatch.setitem(sys.modules, "pymupdf", None)
        monkeypatch.setitem(sys.modules, "fitz", None)
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            outputs._validate_render_completeness()

    def test_missing_pdf_is_a_no_op(self, tmp_path):
        outputs = make_outputs(tmp_path, [(400, 300)] * 4, [[(400, 300)]], validate_figures="strict")
        outputs.output.unlink()
        outputs._validate_render_completeness()

    def test_missing_notebook_is_a_no_op(self, tmp_path):
        outputs = make_outputs(tmp_path, [(400, 300)] * 4, [[(400, 300)]], validate_figures="strict")
        outputs.executed_notebook.unlink()
        outputs._validate_render_completeness()

    def test_unexecuted_run_reads_the_generated_notebook(self, tmp_path):
        outputs = make_outputs(tmp_path, [(400, 300)] * 4, [[(400, 300)]], validate_figures="warn")
        outputs.execute = False
        outputs._nb_executed_path = tmp_path / "does-not-exist.ipynb"
        with pytest.warns(RenderCompletenessWarning, match="3 notebook figure"):
            outputs._validate_render_completeness()
