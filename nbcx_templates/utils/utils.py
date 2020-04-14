from IPython.display import Image, display
from .common import nbconvert_context
from .html import html
from .latex import latex


def print(text, **kwargs):
    '''wrapper around printing'''
    if not isinstance(text, str):
        display(text)
        return
    if nbconvert_context() == 'pdf':
        display(latex(text, **kwargs))
    else:
        display(html(text, **kwargs))


def hr():
    '''horizontal rule'''
    if nbconvert_context() == 'pdf':
        return latex("\\noindent\\makebox[\\linewidth]{\\rule{\\paperwidth - 1cm}{0.4pt}}")
    else:
        return html('----')


def newpage():
    '''make a new page. in html, this just does a horizontal rule'''
    if nbconvert_context() == 'pdf':
        return latex('\\newpage')
    else:
        return hr()


def table(df, title='', footnote=''):
    '''helper to display a table'''
    if nbconvert_context() == 'pdf':
        return latex('\\begin{center} '
                     '\\begin{threeparttable}'
                     '\\caption{' + title + '}' +
                     df.to_latex(escape=False) +
                     '\\begin{tablenotes}'
                     '\\small'
                     '\\item ' + footnote +
                     '\\end{tablenotes}'
                     '\\end{threeparttable}'
                     '\\end{center}')
    else:
        ret = ''
        if title:
            ret += '### {}'.format(title)
        ret += df.to_html()
        if footnote:
            ret += footnote
        return html(ret)


def image(path, **kwargs):
    '''display a image'''
    return Image(filename=path, **kwargs)


def pagenum():
    '''display a page number (latex only)'''
    if nbconvert_context() == 'pdf':
        return latex("\\thepage")
