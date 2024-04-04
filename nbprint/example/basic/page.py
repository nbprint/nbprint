from IPython.display import HTML, Image
from pydantic import Field

from nbprint import ContentImage, PageRegion, PageRegionContent

from .cover import ExampleNBPrintLogo


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
        if self.logo.path:
            img = Image(filename=self.logo.path)
        else:
            img = Image(data=self.logo.content)
        return HTML(f"""<img class="footer-logo" src="data:image/png;base64,{img._repr_png_()}">""")
