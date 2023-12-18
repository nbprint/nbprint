from io import BytesIO

import dominate.tags as dt
import dominate.util as du
from IPython.display import HTML, display
from ipywidgets import Box, Output
from nbconvert.filters.pandoc import convert_pandoc

from .image import Image

_p = print


def _html(text, color=""):
    """print in html"""
    text = convert_pandoc(text, "markdown+tex_math_double_backslash", "html")

    if color:
        d = dt.div()
        d.attributes["style"] = "color: {};".format(color)
        d.appendChild(du.raw(text))
    else:
        d = du.raw(text)

    return HTML(str(d))


def print(text, **kwargs):
    """wrapper around printing"""
    if not isinstance(text, str):
        display(text)
        return
    display(_html(text, **kwargs))


def hr():
    """horizontal rule"""
    return HTML(str(dt.hr()))


def newpage():
    """make a new page. in html, this just does a horizontal rule"""
    p = dt.p()
    p.attributes["style"] = "page-break-before: always;"
    return _html(str(p))


def table(df, title="", footnote=""):
    """helper to display a table"""
    ret = ""
    if title:
        ret += "### {}\n".format(title)
    ret += df.to_html()
    if footnote:
        ret += "\n" + footnote + "\n"
    return _html(ret)


def pagenum():
    """display a page number (latex only)"""
    # TODO
    return "[pagenum]"


def _make(text, h_type, **kwargs):
    h = getattr(dt, h_type)(text)
    h.attributes.update(**kwargs)
    return h


def p(text, **kwargs):
    return HTML(str(_make(text, "p", **kwargs)))


def h1(text, **kwargs):
    return HTML(str(_make(text, "h1", **kwargs)))


def h2(text, **kwargs):
    return HTML(str(_make(text, "h2", **kwargs)))


def h3(text, **kwargs):
    return HTML(str(_make(text, "h3", **kwargs)))


def h4(text, **kwargs):
    return HTML(str(_make(text, "h4", **kwargs)))


def h5(text, **kwargs):
    return HTML(str(_make(text, "h5", **kwargs)))


def _grid(items_and_weights):
    d = dt.div()
    d.attributes["style"] = "display: flex; flex-direction: row;"

    for val, width in items_and_weights:
        if isinstance(val, Image):
            sd = dt.img()
            sd.set_attribute("src", "data:image/png;base64,{}".format(val._repr_png_()))
        else:
            raw_html = val._repr_html_()
            sd = dt.div(du.raw(raw_html))
        sd.attributes["style"] = "flex: {};".format(width)
        d.appendChild(sd)
    return HTML(str(d))


def grid(items_and_weights):
    children = []
    for val, width in items_and_weights:
        out = Output(layout={"flex": str(width)})
        children.append(out)
        with out:
            print(val)
    return Box(children, layout={"display": "flex", "flex-direction": "row"})


def plot(fig):
    imgdata = BytesIO()
    fig.savefig(imgdata)
    imgdata.seek(0)
    return Image(imgdata.read())
