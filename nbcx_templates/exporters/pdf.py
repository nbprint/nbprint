import os
from ipython_genutils.py3compat import getcwd
from nbconvert.exporters import PDFExporter
from nbconvert.exporters.pdf import LatexFailed
from testpath.tempdir import TemporaryWorkingDirectory


class NBCXPDFExporter(PDFExporter):
    '''Custom Exporter to reformat the notebook node to allow for document-level configuration
    from cell outputs based on tags'''
    export_from_notebook = "NBCX PDF Report via LaTeX"

    def from_notebook_node(self, nb, resources=None, **kw):
        latex, resources = super(PDFExporter, self).from_notebook_node(
            nb, resources=resources, **kw
        )
        # set texinputs directory, so that local files will be found
        if resources and resources.get('metadata', {}).get('path'):
            self.texinputs = resources['metadata']['path']
        else:
            self.texinputs = getcwd()

        self._captured_outputs = []
        with TemporaryWorkingDirectory():
            notebook_name = 'notebook'
            resources['output_extension'] = '.tex'
            tex_file = self.writer.write(latex, resources, notebook_name=notebook_name)
            self.log.info("Building PDF")
            self.run_latex(tex_file)
            if self.run_bib(tex_file):
                self.run_latex(tex_file)

            pdf_file = notebook_name + '.pdf'
            if not os.path.isfile(pdf_file):
                raise LatexFailed('\n'.join(self._captured_output))
            self.log.info('PDF successfully created')
            with open(pdf_file, 'rb') as f:
                pdf_data = f.read()

        # convert output extension to pdf
        # the writer above required it to be tex
        resources['output_extension'] = '.pdf'
        # clear figure outputs, extracted by latex export,
        # so we don't claim to be a multi-file export.
        resources.pop('outputs', None)

        return pdf_data, resources
