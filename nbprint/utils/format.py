import dominate.tags as dt
import dominate.util as du
from io import BytesIO
from IPython.display import HTML, display
from ipywidgets import Box, Output
from matplotlib.figure import Figure
from nbconvert.filters.pandoc import convert_pandoc

from .image import Image

_p = print


def _html(text, color="") -> HTML:
    """Print in html."""
    text = convert_pandoc(text, "markdown+tex_math_double_backslash", "html")

    if color:
        d = dt.div()
        d.attributes["style"] = f"color: {color};"
        d.appendChild(du.raw(text))
    else:
        d = du.raw(text)

    return HTML(str(d))


def print(text, **kwargs) -> None:  # noqa: A001
    """Wrapper around printing."""
    if not isinstance(text, str):
        display(text)
        return
    display(_html(text, **kwargs))


def hr() -> HTML:
    """Horizontal rule."""
    return HTML(str(dt.hr()))


def newpage() -> HTML:
    """Make a new page. in html, this just does a horizontal rule."""
    p = dt.p()
    p.attributes["style"] = "page-break-before: always;"
    return _html(str(p))


def _make(text, h_type, **kwargs):
    h = getattr(dt, h_type)(text)
    h.attributes.update(**kwargs)
    return h


def p(text, **kwargs) -> HTML:
    """Convenience method to return a <p> as an IPython HTML Element."""
    return HTML(str(_make(text, "p", **kwargs)))


def h1(text, **kwargs) -> HTML:
    """Convenience method to return a <h1> as an IPython HTML Element."""
    return HTML(str(_make(text, "h1", **kwargs)))


def h2(text, **kwargs) -> HTML:
    """Convenience method to return a <h2> as an IPython HTML Element."""
    return HTML(str(_make(text, "h2", **kwargs)))


def h3(text, **kwargs) -> HTML:
    """Convenience method to return a <h3> as an IPython HTML Element."""
    return HTML(str(_make(text, "h3", **kwargs)))


def h4(text, **kwargs) -> HTML:
    """Convenience method to return a <h4> as an IPython HTML Element."""
    return HTML(str(_make(text, "h4", **kwargs)))


def h5(text, **kwargs) -> HTML:
    """Convenience method to return a <h5> as an IPython HTML Element."""
    return HTML(str(_make(text, "h5", **kwargs)))


def _grid(items_and_weights) -> HTML:
    d = dt.div()
    d.attributes["style"] = "display: flex; flex-direction: row;"

    for val, width in items_and_weights:
        if isinstance(val, Image):
            sd = dt.img()
            sd.set_attribute("src", f"data:image/png;base64,{val._repr_png_()}")
        else:
            raw_html = val._repr_html_()
            sd = dt.div(du.raw(raw_html))
        sd.attributes["style"] = f"flex: {width};"
        d.appendChild(sd)
    return HTML(str(d))


def grid(items_and_weights) -> Box:
    """Layout elements in a flex grid."""
    children = []
    for val, width in items_and_weights:
        out = Output(layout={"flex": str(width)})
        children.append(out)
        with out:
            print(val)
    return Box(children, layout={"display": "flex", "flex-direction": "row"})


def plot(fig: Figure) -> Image:
    """Plot a figure as an IPython Image."""
    imgdata = BytesIO()
    fig.savefig(imgdata)
    imgdata.seek(0)
    return Image(imgdata.read())
