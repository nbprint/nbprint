"""
BSD 3-Clause License

Copyright (c) 2020, Tim Head <betatim@gmail.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import asyncio
import concurrent.futures
import os
import tempfile

import nbconvert
from nbconvert.exporters import Exporter
from pyppeteer import launch
from traitlets import default


async def html_to_pdf(html_file, pdf_file):
    """Convert a HTML file to a PDF"""
    browser = await launch(handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
    page = await browser.newPage()
    await page.setViewport(dict(width=994, height=768))
    await page.emulateMedia("screen")

    await page.goto(f"file:///{html_file}", {"waitUntil": ["networkidle2"]})

    page_margins = {
        "left": "0px",
        "right": "0px",
        "top": "0px",
        "bottom": "0px",
    }

    dimensions = await page.evaluate(
        """() => {
        return {
            width: document.body.scrollWidth,
            height: document.body.scrollHeight,
            offsetHeight: document.body.offsetHeight,
            deviceScaleFactor: window.devicePixelRatio,
        }
    }"""
    )
    width = dimensions["width"]
    height = dimensions["height"]

    await page.addStyleTag(
        {
            "content": """
                #notebook-container {
                    box-shadow: none;
                    padding: unset
                }
                div.cell {
                    page-break-inside: avoid;
                }
                div.output_wrapper {
                    page-break-inside: avoid;
                }
                div.output {
                    page-break-inside: avoid;
                }
         """
        }
    )

    await page.pdf(
        {
            "path": pdf_file,
            "width": width,
            # Adobe can not display pages longer than 200inches. So we limit
            # ourselves to that and start a new page if needed.
            "height": min(height, 200 * 72),
            "printBackground": True,
            "margin": page_margins,
        }
    )

    await browser.close()


async def notebook_to_pdf(notebook, pdf_path, config=None, resources=None, **kwargs):
    """Convert a notebook to PDF"""
    if config is None:
        config = {}
    exporter = nbconvert.HTMLExporter(config=config)
    exported_html, _ = exporter.from_notebook_node(notebook, resources=resources, **kwargs)

    with tempfile.NamedTemporaryFile(suffix=".html") as f:
        f.write(exported_html.encode())
        f.flush()
        await html_to_pdf(f.name, pdf_path)


class PDFExporter(Exporter):
    """Convert a notebook to a PDF

    Expose this package's functionality to nbconvert
    """

    # a thread pool to run our async event loop. We use our own
    # because `from_notebook_node` isn't async but sometimes is called
    # inside a tornado app that already has an event loop
    pool = concurrent.futures.ThreadPoolExecutor()

    export_from_notebook = "PDF via HTML"
    output_mimetype = "application/pdf"

    @default("file_extension")
    def _file_extension_default(self):
        return ".pdf"

    def __init__(self, config=None, **kw):
        with_default_config = self.default_config
        if config:
            with_default_config.merge(config)

        super().__init__(config=with_default_config, **kw)

    def from_notebook_node(self, notebook, resources=None, **kwargs):
        notebook, resources = super().from_notebook_node(notebook, resources=resources, **kwargs)

        # if it is unset or an empty value, set it
        if resources.get("ipywidgets_base_url", "") == "":
            resources["ipywidgets_base_url"] = "https://unpkg.com/"

        with tempfile.TemporaryDirectory(suffix="nb-as-pdf") as name:
            pdf_fname = os.path.join(name, "output.pdf")

            self.pool.submit(
                asyncio.run,
                notebook_to_pdf(
                    notebook,
                    pdf_fname,
                    config=self.config,
                    resources=resources,
                    **kwargs,
                ),
            ).result()
            resources["output_extension"] = ".pdf"

            with open(pdf_fname, "rb") as f:
                pdf_bytes = f.read()

        return (pdf_bytes, resources)
