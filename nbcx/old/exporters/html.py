from nbconvert.exporters import HTMLExporter
from nbconvert.filters.highlight import Highlight2HTML

from .template import TemplateOverrideMixin


class NBCXHTMLExporter(TemplateOverrideMixin, HTMLExporter):
    export_from_notebook = "NBCX HTML"

    def from_notebook_node(self, nb, resources=None, **kw):
        # ********************************************** #
        # From HTMLExporter
        # https://github.com/jupyter/nbconvert/blob/master/nbconvert/exporters/html.py
        langinfo = nb.metadata.get("language_info", {})
        lexer = langinfo.get("pygments_lexer", langinfo.get("name", None))
        highlight_code = self.filters.get("highlight_code", Highlight2HTML(pygments_lexer=lexer, parent=self))
        self.register_filter("highlight_code", highlight_code)
        # ********************************************** #

        # ***************** CUSTOM CODE **************** #
        return super()._from_notebook_node_override(nb, resources, **kw)
        # ********************************************** #
