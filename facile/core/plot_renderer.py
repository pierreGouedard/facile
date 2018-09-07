# Global import
import pandas as pd
from bokeh import resources
from bokeh.embed import file_html

# Local import
from facile.graphs import bokeh_plots as bp


class PlotRerenderer(object):
    buttons = ('Retour', 'Suivant')

    def __init__(self, key, template, d_context={}):
        self.key = key
        self.template = template
        self.d_context = d_context

    def render_figure(self, data, **kwargs):
        self.validate_data(self.key, data)

        if self.key == 'pie':
            bokeh_plot = bp.plot_pie(data, **kwargs)
        else:
            raise NotImplementedError('{} not implemented yet')

        # Render bokeh plot
        html = file_html(bokeh_plot, resources=resources.CDN, template=self.template, template_variables=self.d_context)

        return html

    @staticmethod
    def validate_data(key, data):
        if key == 'pie':
            assert(isinstance(data, pd.DataFrame))
            assert('name' in data.columns and 'value' in data.columns)
