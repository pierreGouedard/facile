# Global imports
import deform
import colander
from translationstring import TranslationStringFactory
import pytz
_ = TranslationStringFactory('deform')

# Local import
from facile.forms.Deform import Form
utc = pytz.UTC


class DocumentForm(Form):

    def __init__(self, request, static_path, **kwargs):

        self.mapping_name = {'index': None, 'document': None}

        Form.__init__(self, request, static_path, self.get_schema(kwargs['nodes']), buttons=('Editer le document',))

    @staticmethod
    def get_schema(l_nodes):
        schema_ = colander.Schema()
        for node in l_nodes:
            schema_.add(node)

        return schema_
