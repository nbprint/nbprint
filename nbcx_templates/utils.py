import os
from functools import lru_cache
from IPython.display import Markdown, Latex, Image, display


@lru_cache(None)
def in_nbconvert():
    '''helper function to check if running in nbcx context'''
    return True if os.environ.get('NBCX_NBCONVERT', '') else False


@lru_cache(None)
def nbconvert_context():
    '''get context in which nbcx is running, either 'pdf' or 'html' '''
    if in_nbconvert():
        if os.environ.get('NBCX_CONTEXT', ''):
            return 'html'
        return 'pdf'
    return 'html'


def print(text, **kwargs):
    '''wrapper around printing'''
    if not isinstance(text, str):
        display(text)
        return
    if nbconvert_context() == 'pdf':
        display(latex(text, **kwargs))
    else:
        display(html(text, **kwargs))


def html(text, color=''):
    '''print in html'''
    return Markdown(text)


def latex(text, color=''):
    '''print in latex'''
    if color:
        text = '\\textcolor{{color}}{{text}}'.format(color=color, text=text)
    return Latex(text)


def hr():
    '''horizontal rule'''
    if nbconvert_context() == 'pdf':
        return Latex("\\noindent\\makebox[\\linewidth]{\\rule{\\paperwidth - 1cm}{0.4pt}}")
    else:
        return Markdown('----')


def newpage():
    '''make a new page. in html, this just does a horizontal rule'''
    if nbconvert_context() == 'pdf':
        return Latex('\\newpage')
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
