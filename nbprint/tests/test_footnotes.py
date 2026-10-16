"""Tests for footnotes placed by paged.js."""

import asyncio

import pytest

from nbprint import footnote
from nbprint.cli import run

_REPORT = """\
_target_: nbprint.Configuration
name: footnotes
pagedjs: {pagedjs}
outputs:
  _target_: nbprint.NBConvertOutputs
  root: {root}
  naming: "{{{{name}}}}"
  target: html
  execute: false
content:
  - _target_: nbprint.ContentMarkdown
    content: |
      Revenue grew 12%<span class="nbprint-footnote">Unaudited, as of Q3.</span> year over year.
"""


def test_footnote_helper():
    assert footnote("Unaudited & preliminary.") == '<span class="nbprint-footnote">Unaudited &amp; preliminary.</span>'


async def _inspect(html):
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(html.as_uri())
        await page.wait_for_selector('html[data-nbprint-paged="done"]', state="attached")
        result = await page.evaluate(
            """() => {
              // paged.js leaves a call marker carrying the same class in the text
              const note = document.querySelector(".nbprint-footnote:not([data-footnote-call])");
              return {
                inFootnoteArea: !!note.closest(".pagedjs_footnote_area"),
                calls: document.querySelectorAll("[data-footnote-call]").length,
                text: note.textContent.trim(),
                before: getComputedStyle(note, "::before").content,
              };
            }"""
        )
        await browser.close()
    return result


@pytest.mark.parametrize("pagedjs", [True, False])
def test_footnote_placement(tmp_path, pagedjs):
    config = tmp_path / "footnotes.yaml"
    config.write_text(_REPORT.format(pagedjs=str(pagedjs).lower(), root=tmp_path))
    run(str(config), [])

    note = asyncio.run(_inspect(tmp_path / "footnotes.html"))

    assert note["text"] == "Unaudited, as of Q3."
    if pagedjs:
        assert note["inFootnoteArea"]
        assert note["calls"] == 1
    else:
        assert not note["inFootnoteArea"]
        assert note["before"] == '" ("'
