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


@pytest.mark.skipif(not exists("examples"), reason="Examples not present")
def test_snapshot_keeps_its_pagination_when_opened(tmp_path):
    from playwright.sync_api import sync_playwright

    run("examples/chapters.yaml", [f"++outputs.root={tmp_path}", "++outputs.target=webhtml"])
    snapshot = tmp_path / "chapters.html"

    # paged.js numbers the TOC with rules it adds through the CSSOM; they must be saved as text
    has_toc_counters = "counter-increment: counterTocLevel1" in snapshot.read_text(encoding="utf-8")
    assert has_toc_counters

    with sync_playwright() as p:
        browser = p.chromium.launch()
        pages = {}
        errors = []
        for javascript in (False, True):
            context = browser.new_context(java_script_enabled=javascript)
            page = context.new_page()
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(snapshot.as_uri())
            page.wait_for_load_state("networkidle")
            pages[javascript] = page.locator(".pagedjs_page").count()
            context.close()
        browser.close()

    assert errors == []
    assert pages[False] > 0
    assert pages[True] == pages[False]
