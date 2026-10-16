"""Tests for the webhtml exporter's captured snapshot."""

import asyncio
import logging
from os.path import exists
from unittest.mock import MagicMock

import pytest

from nbprint.cli import run
from nbprint.nbconvert.webhtml import WebHTMLExporter
from nbprint.tests.test_webpdf_exporter import _FakePage


def test_waits_for_pagination_before_capturing():
    exporter = WebHTMLExporter()
    exporter.log = MagicMock(spec=logging.Logger)
    page = _FakePage(has_marker=True)

    asyncio.run(exporter._wait_until_paginated(page))

    assert page.slept == []
    assert page.waited_for == [('html[data-nbprint-paged="done"]', "attached", exporter.pagination_timeout)]


async def _open(snapshot, *, javascript):
    """Count the pages in ``snapshot`` and collect page errors, with or without JavaScript."""
    from playwright.async_api import async_playwright

    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(java_script_enabled=javascript)
        page = await context.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(snapshot.as_uri())
        await page.wait_for_load_state("networkidle")
        pages = await page.locator(".pagedjs_page").count()
        await browser.close()
    return pages, errors


@pytest.mark.skipif(not exists("examples"), reason="Examples not present")
def test_snapshot_keeps_its_pagination_when_opened(tmp_path):
    run("examples/chapters.yaml", [f"++outputs.root={tmp_path}", "++outputs.target=webhtml"])
    snapshot = tmp_path / "chapters.html"

    # paged.js numbers the TOC with rules it adds through the CSSOM; they must be saved as text
    has_toc_counters = "counter-increment: counterTocLevel1" in snapshot.read_text(encoding="utf-8")
    assert has_toc_counters

    saved_pages, _ = asyncio.run(_open(snapshot, javascript=False))
    opened_pages, errors = asyncio.run(_open(snapshot, javascript=True))

    assert errors == []
    assert saved_pages > 0
    assert opened_pages == saved_pages
