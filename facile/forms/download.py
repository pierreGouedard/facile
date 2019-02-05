# Global imports
from colander import Schema, SchemaNode, String
from deform.widget import HiddenWidget
from translationstring import TranslationStringFactory
_ = TranslationStringFactory('deform')

# Local import
from facile.forms.Deform import Form


class DownloadForm(Form):

    def __init__(self, request, template_deform_path):
        Form.__init__(self, request, template_deform_path, self.DownloadSchema(), buttons=('telecharger',))
        self.mapping_name = {'download': None, 'table': None}

    @staticmethod
    def DownloadSchema():
        class DownloadSchema(Schema):
            table = SchemaNode(
                String(),
                title="table",
                widget=HiddenWidget())

        return DownloadSchema()

