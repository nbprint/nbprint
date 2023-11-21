from nbconvert.exporters import LatexExporter
from nbconvert.filters.highlight import Highlight2Latex

from .template import TemplateOverrideMixin


class NBCXLatexExporter(TemplateOverrideMixin, LatexExporter):
    export_from_notebook = "NBCX LaTeX"

    def from_notebook_node(self, nb, resources=None, **kw):
        # ********************************************** #
        # From LatexExporter
        # https://github.com/jupyter/nbconvert/blob/master/nbconvert/exporters/latex.py
        langinfo = nb.metadata.get("language_info", {})
        lexer = langinfo.get("pygments_lexer", langinfo.get("name", None))
        highlight_code = self.filters.get("highlight_code", Highlight2Latex(pygments_lexer=lexer, parent=self))
        self.register_filter("highlight_code", highlight_code)
        # ********************************************** #

        # ***************** CUSTOM CODE **************** #
        return super()._from_notebook_node_override(nb, resources, **kw)
        # ********************************************** #
