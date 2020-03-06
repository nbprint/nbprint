import os
import sys
from functools import lru_cache
from IPython.display import Markdown, Latex, display


@lru_cache(None)
def in_nbconvert():
    return True if os.environ.get('NBCX_NBCONVERT', '') else False


@lru_cache(None)
def nbconvert_context():
    if in_nbconvert():
        if os.environ.get('NBCX_CONTEXT', ''):
            return 'html'
        return 'pdf'
    return 'html'


def print(text):
    if nbconvert_context() == 'pdf':
        l(text)
    else:
        p(text)


def p(text):
    display(Markdown(text))


def l(text):
    display(Latex(text))


def newpage():
    if nbconvert_context() == 'pdf':
        display(Latex('\\newpage'))
    else:
        display(Markdown('----'))


def table(df, title='', footnote=''):
    if nbconvert_context() == 'pdf':
        l('\\begin{center} '
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
        if title:
            p('### {}'.format(title))
        p(df.to_html())
        if footnote:
            p(footnote)
