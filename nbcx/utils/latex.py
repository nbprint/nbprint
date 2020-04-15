from IPython.display import Latex


def latex(text, color=''):
    '''print in latex'''
    if color:
        text = '\\textcolor{%s}{%s}' % (color, text)

    return Latex(text)
