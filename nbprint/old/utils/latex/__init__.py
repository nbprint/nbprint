from IPython.display import Latex, display
from nbconvert.filters.pandoc import convert_pandoc


def latex(text, color="", **kwargs):
    """print in latex"""
    if color:
        text = "\\textcolor{%s}{%s}" % (color, text)
    return Latex(text + "\n", **kwargs)


def print(text, **kwargs):
    """wrapper around printing"""
    if not isinstance(text, str):
        display(text)
        return
    display(
        latex(
            convert_pandoc(text + "\\newline", "markdown+tex_math_double_backslash", "latex"),
            **kwargs,
        )
    )


def hr():
    """horizontal rule"""
    return latex("\\noindent\\makebox[\\linewidth]{\\rule{\\paperwidth - 1cm}{0.4pt}}")


def newpage():
    """make a new page. in html, this just does a horizontal rule"""
    return latex("\\newpage")


def table(df, title="", footnote=""):
    """helper to display a table"""
    return latex(
        "\\begin{center} "
        "\\begin{threeparttable}"
        "\\caption{" + title + "}" + df.to_latex(escape=False) + "\\begin{tablenotes}"
        "\\small"
        "\\item " + footnote + "\\end{tablenotes}"
        "\\end{threeparttable}"
        "\\end{center}"
    )


def pagenum():
    """display a page number (latex only)"""
    return latex("\\thepage")


def _make(text, h_type):
    return convert_pandoc("#" * h_type + " " + text + "\n", "markdown+tex_math_double_backslash", "latex")


def p(text, **kwargs):
    return Latex(text, **kwargs)


def h1(text, **kwargs):
    return Latex(_make(text, 1), **kwargs)


def h2(text, **kwargs):
    return Latex(_make(text, 2), **kwargs)


def h3(text, **kwargs):
    return Latex(_make(text, 3), **kwargs)


def h4(text, **kwargs):
    return Latex(_make(text, 4), **kwargs)


def h5(text, **kwargs):
    return Latex(_make(text, 5), **kwargs)


def grid(items_and_weights):
    print(Latex("\n\\begin{Row}%\n"))
    for val, width in items_and_weights:
        print(Latex("\n\\begin{Cell}{" + str(width) + "}\n"))

        if not isinstance(val, str):
            print(Latex("\\vspace*{-.4cm}\n"))
        print(val)
        print(Latex("\n\n\\end{Cell}\n"))
    print(Latex("\n\\end{Row}\n"))
