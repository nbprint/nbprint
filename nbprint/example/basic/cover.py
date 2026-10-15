import os.path
from pathlib import Path

from IPython.display import HTML
from pydantic import FilePath

from nbprint import ContentCover, ContentImage

__all__ = (
    "ExampleCoverPageContent",
    "ExampleNBPrintLogo",
)


class ExampleNBPrintLogo(ContentImage):
    path: FilePath = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "docs", "img", "logo-light.png")))


class ExampleCoverPageContent(ContentCover):
    logo: ContentImage | None
    title: str | None = ""
    subtitle: str | None = ""

    def __call__(self, ctx=None, *args, **kwargs):
        assert ctx is not None
        assert self.logo is not None
        return HTML(f"""
            {self.logo()._repr_html_()}
            <h1>{self.title}</h1>
            <h2>{self.subtitle}</h2>
            <h3>{ctx.string}</h3>
            <p class="pagebreak"></p>
        """)
