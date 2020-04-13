from nbconvert.exporters import LatexExporter


class NBCXLatexExporter(LatexExporter):
    export_from_notebook = "NBCX LaTeX"

    def from_notebook_node(self, nb, resources=None, **kw):
        return super().from_notebook_node(nb, resources, **kw)
