import os.path
from IPython.display import HTML
from pydantic import FilePath
from typing import Optional

from nbprint import ContentCover, ContentImage

__all__ = (
    "ExampleNBPrintLogo",
    "ExampleCoverPageContent",
)


class ExampleNBPrintLogo(ContentImage):
    path: FilePath = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "docs", "img", "logo-light.png")
    )


class ExampleCoverPageContent(ContentCover):
    logo: Optional[ContentImage]
    title: Optional[str] = ""
    subtitle: Optional[str] = ""

    def __call__(self, *args, **kwargs):
        return HTML(f"""
            {self.logo()._repr_html_()}
            <h1>{self.title}</h1>
            <h2>{self.subtitle}</h2>
            <p class="pagebreak"></p>
        """)
