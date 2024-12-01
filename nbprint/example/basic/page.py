import os.path

from IPython.display import HTML, Image
from pydantic import Field, FilePath

from nbprint import Configuration, ContentImage, Page, PageOrientation, PageRegion, PageRegionContent, Role

from .cover import ExampleNBPrintLogo

__all__ = (
    "ExampleBookIcon",
    "ExampleLogoInFooter",
    "ExampleReportPage",
)


class ExampleLogoInFooter(PageRegion):
    logo: ContentImage = Field(default_factory=ExampleNBPrintLogo)
    content: PageRegionContent = Field(default_factory=lambda: PageRegionContent(content="element(footerLogo)"))

    ignore: bool = False

    css: str = """
.footer-logo {
  position: running(footerLogo);
  width: 75px;
}
"""

    def __call__(self, *args, **kwargs):
        img = Image(filename=self.logo.path) if self.logo.path else Image(data=self.logo.content)
        return HTML(f"""<img class="footer-logo" src="data:image/png;base64,{img._repr_png_()}">""")


class ExampleBookIcon(ContentImage):
    path: FilePath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "examples", "assets", "book.png"))


class ExampleReportPage(Page):
    bottom_left: PageRegion = Field(default=ExampleLogoInFooter())
    bottom: PageRegion = Field(default=PageRegion(content=PageRegionContent(content="Example Report")))
    bottom_right: PageRegion = Field(default=PageRegion())
    role: Role = Role.PAGE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.css += f"""
.pagedjs_first_page {{
    background-image: url("data:image/png;base64,{ExampleBookIcon().as_base64()}");
    background-size: 50%;
    background-repeat: no-repeat;
}}

.pagedjs_first_page div.pagedjs_margin-bottom {{
    display: none;
}}

.pagedjs_margin-bottom-center > pagedjs_margin-content::after {{
    font-weight: bold;
}}
"""

    def render(self, config: Configuration) -> None:
        super().render(config=config)
        if config.page.orientation == PageOrientation.landscape:
            self.css += """
.pagedjs_first_page {
    background-position-y: 85%;
    background-position-x: 95%;
}
"""
        else:
            self.css += """
.pagedjs_first_page {
    background-position-y: 75%;
    background-position-x: 50%;
}
"""
