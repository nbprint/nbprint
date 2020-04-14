from IPython.display import Latex


def latex(text, color=''):
    '''print in latex'''
    if color:
        text = '\\textcolor{{color}}{{text}}'.format(color=color, text=text)
    return Latex(text)
