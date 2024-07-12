from __future__ import annotations

from IPython.display import HTML
from pathlib import Path
from pydantic import FilePath

from nbprint import ContentCover, ContentImage

__all__ = (
    "ExampleNBPrintLogo",
    "ExampleCoverPageContent",
)


class ExampleNBPrintLogo(ContentImage):
    path: FilePath = Path(__file__).parent.resolve() / ".." / ".." / ".." / "docs" / "img" / "logo-light.png"


class ExampleCoverPageContent(ContentCover):
    logo: ContentImage | None
    title: str | None = ""
    subtitle: str | None = ""

    def __call__(self, ctx=None, *args, **kwargs):
        return HTML(f"""
            {self.logo()._repr_html_()}
            <h1>{self.title}</h1>
            <h2>{self.subtitle}</h2>
            <h3>{ctx.string}</h3>
            <p class="pagebreak"></p>
        """)
