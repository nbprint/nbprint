from IPython.display import Image, display
from nbconvert.filters.pandoc import convert_pandoc
from .common import nbconvert_context
from .html import html
from .latex import latex


def print(text, **kwargs):
    '''wrapper around printing'''
    if not isinstance(text, str):
        display(text)
        return
    if nbconvert_context() == 'pdf':
        display(latex(convert_pandoc(text, 'markdown+tex_math_double_backslash', 'latex'), **kwargs))
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
    # measure in pixels for html, but cm for latex
    width = kwargs.get('width', '')
    height = kwargs.get('height', '')
    align = kwargs.pop('align', 'left')
    metadata = kwargs.pop('metadata', {})

    if width:
        if isinstance(width, str) and not width.endswith('cm'):
            widthcm = width + 'cm'
        elif not isinstance(width, str):
            # assume in pixels, get cm

            # TODO assume 96 DPI
            widthcm = '{}cm'.format(int(width / 36))
        else:
            # assume already in cm, get pixels
            width, widthcm = float(width.replace('cm', '')), width

            # TODO assume 96 DPI
            width = int(width * 36)
            kwargs['width'] = width
    else:
        widthcm = ''

    if height:
        if isinstance(height, str) and not height.endswith('cm'):
            heightcm = height + 'cm'
        elif not isinstance(height, str):
            # assume in pixels, get cm

            # TODO assume 96 DPI
            heightcm = '{}cm'.format(int(height / 36))

        else:
            # assume already in cm, get pixels
            height, heightcm = float(height.replace('cm', '')), height

            # TODO assume 96 DPI
            height = int(height * 36)
            kwargs['height'] = height
    else:
        heightcm = ''

    metadata['widthcm'] = widthcm
    metadata['heightcm'] = heightcm
    metadata['align'] = align

    return Image(filename=path, metadata=metadata, **kwargs)


def pagenum():
    '''display a page number (latex only)'''
    if nbconvert_context() == 'pdf':
        return latex("\\thepage")
    else:
        return '[pagenum]'
