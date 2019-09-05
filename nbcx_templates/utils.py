import sys
from IPython.display import Markdown, Latex, display

if 'nbconvert' in sys.argv:
    raise Exception('Test')


def p(text):
    display(Markdown(text))


def l(text):
    display(Latex(text))


def newpage():
    display(Latex('\\newpage'))


def table(df, title='', footnote=''):
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
