"""Tests for nbprint's webpdf exporter and its pagination-complete wait."""

import asyncio
import logging
from unittest.mock import MagicMock

import pytest
from playwright.async_api import Error as PlaywrightError

from nbprint.nbconvert.webpdf import NBPrintWebPDFExporter


class _FakePage:
    """Stands in for a playwright ``Page``, recording how it was waited on."""

    def __init__(self, *, has_marker: bool, reaches_done: bool = True) -> None:
        self._has_marker = has_marker
        self._reaches_done = reaches_done
        self.queried: list[str] = []
        self.slept: list[int] = []
        self.waited_for: list[tuple[str, str | None, int]] = []

    async def query_selector(self, selector: str):
        self.queried.append(selector)
        return object() if self._has_marker else None

    async def wait_for_timeout(self, timeout: int) -> None:
        self.slept.append(timeout)

    async def wait_for_selector(self, selector: str, state: str | None = None, timeout: int | None = None) -> None:
        self.waited_for.append((selector, state, timeout))
        if not self._reaches_done:
            msg = "Timeout exceeded"
            raise PlaywrightError(msg)


@pytest.fixture
def exporter():
    out = NBPrintWebPDFExporter()
    out.log = MagicMock(spec=logging.Logger)
    return out


class TestWaitUntilPaginated:
    def test_waits_for_the_signal_instead_of_sleeping(self, exporter):
        """The whole point: no fixed delay when the document reports for itself."""
        page = _FakePage(has_marker=True)
        asyncio.run(exporter._wait_until_paginated(page))

        assert page.slept == []
        assert page.waited_for == [('html[data-nbprint-paged="done"]', "attached", exporter.pagination_timeout)]

    def test_falls_back_to_the_timer_without_a_marker(self, exporter):
        """A non-nbprint template gets upstream's behaviour rather than a 60s stall."""
        page = _FakePage(has_marker=False)
        asyncio.run(exporter._wait_until_paginated(page))

        assert page.slept == [exporter.page_render_timeout]
        assert page.waited_for == []

    def test_a_stalled_document_warns_but_still_captures(self, exporter):
        """Better a warned-about PDF than a hard failure at the end of a long render."""
        page = _FakePage(has_marker=True, reaches_done=False)
        asyncio.run(exporter._wait_until_paginated(page))

        assert exporter.log.warning.called

    def test_pagination_timeout_is_configurable(self):
        out = NBPrintWebPDFExporter()
        out.log = MagicMock(spec=logging.Logger)
        out.pagination_timeout = 1234
        page = _FakePage(has_marker=True)
        asyncio.run(out._wait_until_paginated(page))

        assert page.waited_for == [('html[data-nbprint-paged="done"]', "attached", 1234)]


class TestExporterRegistration:
    def test_produces_pdf_files(self):
        assert NBPrintWebPDFExporter().file_extension == ".pdf"

    def test_upstream_webpdf_config_still_applies(self):
        """Existing `WebPDFExporter.*` config must keep working through the subclass."""
        from traitlets.config import Config

        config = Config()
        config.WebPDFExporter.page_render_timeout = 4242
        assert NBPrintWebPDFExporter(config=config).page_render_timeout == 4242

    def test_resolvable_by_entry_point_name(self):
        from nbconvert.exporters.base import get_exporter

        assert get_exporter("nbprintwebpdf") is NBPrintWebPDFExporter
