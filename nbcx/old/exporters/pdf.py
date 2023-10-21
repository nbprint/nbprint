import os

from ipython_genutils.py3compat import getcwd
from nbconvert.exporters import PDFExporter
from nbconvert.exporters.pdf import LatexFailed
from nbconvert.filters.highlight import Highlight2Latex
from testpath.tempdir import TemporaryWorkingDirectory

from .template import TemplateOverrideMixin


class NBCXPDFExporter(TemplateOverrideMixin, PDFExporter):
    """Custom Exporter to reformat the notebook node to allow for document-level configuration
    from cell outputs based on tags"""

    export_from_notebook = "NBCX PDF Report via LaTeX"

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
        # call the overridden from_notebook_node
        latex, resources = super()._from_notebook_node_override(nb, resources=resources, **kw)
        # ********************************************** #

        # ********************************************** #
        # From PDFExporter
        # set texinputs directory, so that local files will be found
        if resources and resources.get("metadata", {}).get("path"):
            self.texinputs = resources["metadata"]["path"]
        else:
            self.texinputs = getcwd()

        self._captured_outputs = []
        with TemporaryWorkingDirectory():
            notebook_name = "notebook"
            resources["output_extension"] = ".tex"
            tex_file = self.writer.write(latex, resources, notebook_name=notebook_name)
            self.log.info("Building PDF")
            self.run_latex(tex_file)
            if self.run_bib(tex_file):
                self.run_latex(tex_file)

            pdf_file = notebook_name + ".pdf"
            if not os.path.isfile(pdf_file):
                raise LatexFailed("\n".join(self._captured_output))
            self.log.info("PDF successfully created")
            with open(pdf_file, "rb") as f:
                pdf_data = f.read()

        # convert output extension to pdf
        # the writer above required it to be tex
        resources["output_extension"] = ".pdf"
        # clear figure outputs, extracted by latex export,
        # so we don't claim to be a multi-file export.
        resources.pop("outputs", None)

        return pdf_data, resources
        # ********************************************** #
