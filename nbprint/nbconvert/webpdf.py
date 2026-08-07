# ruff: noqa: ANN201, ANN202, PTH108, ASYNC221
"""Export to PDF via a headless browser, capturing once paged.js has finished."""

import asyncio
import concurrent.futures
import os
import subprocess
import sys
import tempfile

from nbconvert.exporters.webpdf import WebPDFExporter
from traitlets import Int

__all__ = ("NBPrintWebPDFExporter",)

# Set to "pending" by the nbprint template before any async work starts, and
# flipped to "done" by embedded.js once pagination and postprocessing settle.
_PAGED_MARKER = "html[data-nbprint-paged]"
_PAGED_DONE = 'html[data-nbprint-paged="done"]'


class NBPrintWebPDFExporter(WebPDFExporter):
    """``WebPDFExporter`` that captures the PDF once paged.js reports it is done.

    Upstream navigates with ``wait_until="networkidle"`` and then sleeps
    ``page_render_timeout`` milliseconds before capturing. paged.js paginates
    long after the network goes quiet — chunking is pure DOM work — so on a
    document large enough to take a moment to lay out, the capture lands
    mid-pagination and the PDF is silently short, with nbconvert reporting
    success either way.

    nbprint ships paged.js in its own template, so it knows exactly when
    pagination has finished and waits for that instead of guessing. The wait is
    a ceiling rather than a fixed cost: a short document is captured as soon as
    it settles. Documents carrying no nbprint marker — a different template, or
    a static bundle predating the signal — fall back to upstream's timed sleep.
    """

    export_from_notebook = "PDF via nbprint"

    pagination_timeout = Int(
        60_000,
        help="""
        Milliseconds to wait for nbprint's pagination-complete signal before
        capturing the PDF anyway.

        This is a ceiling, not a delay: the capture happens as soon as the
        signal arrives. It elapses in full only when the document's JavaScript
        never finishes, which is logged as a warning.
        """,
    ).tag(config=True)

    async def _wait_until_paginated(self, page) -> None:
        """Block until the document reports that its DOM has stopped moving."""
        from playwright.async_api import Error as PlaywrightError

        if await page.query_selector(_PAGED_MARKER) is None:
            self.log.debug("No nbprint pagination marker found; falling back to page_render_timeout.")
            await page.wait_for_timeout(self.page_render_timeout)
            return

        try:
            await page.wait_for_selector(_PAGED_DONE, state="attached", timeout=self.pagination_timeout)
        except PlaywrightError:
            self.log.warning(
                "Timed out after %sms waiting for nbprint pagination to finish; the PDF may be truncated.",
                self.pagination_timeout,
            )

    def run_playwright(self, html):
        """Run playwright.

        Vendored from ``WebPDFExporter.run_playwright``; the only difference is
        that the post-navigation sleep becomes ``_wait_until_paginated``.
        nbconvert exposes no hook inside this method, so overriding it wholesale
        is the only way in. Diff against upstream when bumping nbconvert.
        """

        async def main(temp_file):
            """Run main playwright script."""
            try:
                from playwright.async_api import async_playwright
            except ModuleNotFoundError as e:
                msg = "Playwright is not installed to support Web PDF conversion. Please install `nbconvert[webpdf]` to enable."
                raise RuntimeError(msg) from e

            if self.allow_chromium_download:
                cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
                subprocess.check_call(cmd)  # noqa: S603

            playwright = await async_playwright().start()
            chromium = playwright.chromium

            args = self.browser_args
            if self.disable_sandbox:
                args.append("--no-sandbox")

            try:
                browser = await chromium.launch(handle_sigint=False, handle_sigterm=False, handle_sighup=False, args=args)
            except Exception as e:
                msg = (
                    "No suitable chromium executable found on the system. "
                    "Please use '--allow-chromium-download' to allow downloading one,"
                    "or install it using `playwright install chromium`."
                )
                await playwright.stop()
                raise RuntimeError(msg) from e

            page = await browser.new_page()
            await page.emulate_media(media="print")
            await page.wait_for_timeout(100)
            await page.goto(f"file://{temp_file.name}", wait_until="networkidle")
            await self._wait_until_paginated(page)

            pdf_params = {"print_background": True}
            if not self.paginate:
                # Floating point precision errors cause the printed
                # PDF from spilling over a new page by a pixel fraction.
                dimensions = await page.evaluate(
                    """() => {
                    const rect = document.body.getBoundingClientRect();
                    return {
                    width: Math.ceil(rect.width) + 1,
                    height: Math.ceil(rect.height) + 1,
                    }
                }"""
                )
                # 200 inches is the maximum size for Adobe Acrobat Reader.
                pdf_params.update(
                    {
                        "width": min(dimensions["width"], 200 * 72),
                        "height": min(dimensions["height"], 200 * 72),
                    }
                )
            pdf_data = await page.pdf(**pdf_params)

            await browser.close()
            await playwright.stop()
            return pdf_data

        pool = concurrent.futures.ThreadPoolExecutor()
        # Create a temporary file to pass the HTML code to Chromium:
        # Unfortunately, tempfile on Windows does not allow for an already open
        # file to be opened by a separate process. So we must close it first
        # before calling Chromium. We also specify delete=False to ensure the
        # file is not deleted after closing (the default behavior).
        temp_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False)  # noqa: SIM115
        with temp_file:
            temp_file.write(html.encode("utf-8"))
        try:
            pdf_data = pool.submit(asyncio.run, main(temp_file)).result()
        finally:
            # Ensure the file is deleted even if playwright raises an exception
            os.unlink(temp_file.name)
        return pdf_data
