from nbconvert.exporters import TemplateExporter


class TemplateOverrideMixin:
    def _from_notebook_node_override(self, nb, resources=None, **kw):
        # ********************************************** #
        # From Template Exporter
        # https://github.com/jupyter/nbconvert/blob/master/nbconvert/exporters/templateexporter.py
        # Call Exporter's from_notebook_node
        nb_copy, resources = super(TemplateExporter, self).from_notebook_node(nb, resources, **kw)
        resources.setdefault('raw_mimetypes', self.raw_mimetypes)
        resources['global_content_filter'] = {
            'include_code': not self.exclude_code_cell,
            'include_markdown': not self.exclude_markdown,
            'include_raw': not self.exclude_raw,
            'include_unknown': not self.exclude_unknown,
            'include_input': not self.exclude_input,
            'include_output': not self.exclude_output,
            'include_input_prompt': not self.exclude_input_prompt,
            'include_output_prompt': not self.exclude_output_prompt,
            'no_prompt': self.exclude_input_prompt and self.exclude_output_prompt,
        }
        # ********************************************** #

        # ***************** CUSTOM CODE **************** #
        # Inject our own vars
        resources['nbcx'] = {}
        resources['nbcx']['chead'] = 'BLARG'
        # ********************************************** #

        # ********************************************** #
        # Top level variables are passed to the template_exporter here.
        output = self.template.render(nb=nb_copy, resources=resources)
        output = output.lstrip('\r\n')
        return output, resources
        # ********************************************** #
