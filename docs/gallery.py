"""Render the examples to HTML and screenshot their first page for the docs gallery.

Run from the repository root before ``yardang build``:

    python docs/gallery.py [slug ...]

Writes ``<slug>.html`` and ``<slug>.png`` into ``docs/html/gallery``.
"""

import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from playwright.sync_api import sync_playwright

from nbprint.cli import run

OUTPUT = Path("docs/html/gallery")

EXAMPLES = {
    "basic": "examples/basic.yaml",
    "finance": "examples/finance.yaml",
    "research": "examples/research.yaml",
    "chapters": "examples/chapters.yaml",
    "sections": "examples/sections.yaml",
    "inline": "examples/inline.yaml",
    "landscape": "examples/landscape.yaml",
    "plotly": "examples/plotly.yaml",
    "greattables": "examples/greattables.yaml",
    "notebook-sections": "examples/notebook-sections.ipynb",
    "notebook-runtime": "examples/notebook-runtime.ipynb",
    "notebook-overlays": "examples/notebook-overlays.ipynb",
    "notebook-page-boxes": "examples/notebook-page-boxes.ipynb",
}


def render(slug: str, path: str, workdir: Path) -> Path:
    # notebooks nest the configuration under ``nbprint``, YAML files do not
    prefix = "nbprint." if path.endswith(".ipynb") else ""
    run(path, [f"++{prefix}outputs.root={workdir}", f"++{prefix}outputs.target=html", f"++{prefix}outputs.naming={slug}"])
    html = OUTPUT / f"{slug}.html"
    shutil.copy(workdir / f"{slug}.html", html)
    return html


def screenshot(page, html: Path) -> None:
    page.goto(html.resolve().as_uri())
    page.wait_for_function("document.documentElement.dataset.nbprintPaged === 'done'", timeout=60_000)
    page.locator(".pagedjs_page").first.screenshot(path=html.with_suffix(".png"))


def main(slugs: list[str]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory() as td, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 1200})
        for slug in slugs or EXAMPLES:
            screenshot(page, render(slug, EXAMPLES[slug], Path(td)))
        browser.close()


if __name__ == "__main__":
    main(sys.argv[1:])
