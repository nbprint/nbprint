from io import BytesIO

import dominate.tags as dt
import dominate.util as du
from IPython.display import HTML
from nbconvert.filters.pandoc import convert_pandoc

from .image import Image


def _html(text, color="") -> HTML:
    """Print in html"""
    text = convert_pandoc(text, "markdown+tex_math_double_backslash", "html")

    if color:
        d = dt.div()
        d.attributes["style"] = f"color: {color};"
        d.appendChild(du.raw(text))
    else:
        d = du.raw(text)

    return HTML(str(d))


def hr() -> HTML:
    """Horizontal rule"""
    return HTML(str(dt.hr()))


def newpage() -> HTML:
    """Make a new page. in html, this just does a horizontal rule"""
    p = dt.p()
    p.attributes["style"] = "page-break-before: always;"
    return _html(str(p))


def _make(text, h_type, **kwargs) -> dt.html_tag:
    h = getattr(dt, h_type)(text)
    h.attributes.update(**kwargs)
    return h


def p(text, **kwargs) -> HTML:
    return HTML(str(_make(text, "p", **kwargs)))


def h1(text, **kwargs) -> HTML:
    return HTML(str(_make(text, "h1", **kwargs)))


def h2(text, **kwargs) -> HTML:
    return HTML(str(_make(text, "h2", **kwargs)))


def h3(text, **kwargs) -> HTML:
    return HTML(str(_make(text, "h3", **kwargs)))


def h4(text, **kwargs) -> HTML:
    return HTML(str(_make(text, "h4", **kwargs)))


def h5(text, **kwargs) -> HTML:
    return HTML(str(_make(text, "h5", **kwargs)))


def plot(fig) -> Image:
    imgdata = BytesIO()
    fig.savefig(imgdata)
    imgdata.seek(0)
    return Image(imgdata.read())
