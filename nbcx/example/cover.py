from typing import Optional

from IPython.display import HTML, display

from nbcx import NBCXContentCover, NBCXContentImage


class ExampleCoverPageContent(NBCXContentCover):
    logo: Optional[NBCXContentImage]
    title: Optional[str] = ""
    subtitle: Optional[str] = ""

    def __call__(self, ctx=None, *args, **kwargs):
        self.logo(ctx=ctx, *args, **kwargs)
        display(HTML(f"<h1>{self.title}</h1>"))
        display(HTML(f"<h2>{self.subtitle}</h2>"))
        display(HTML('<p class="pagebreak"></p>'))
