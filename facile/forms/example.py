# Global imports
import deform
import colander
import pandas as pd
from translationstring import TranslationStringFactory
import pytz
_ = TranslationStringFactory('deform')

# Local import
from facile.forms.Deform import Form
utc = pytz.UTC


class ExampleForm(Form):

    def __init__(self, request, template_path):
        # Define mapping
        self.mapping_name = {'upload': {'filename': None}}
        btn_submit = deform.Button(name='submit', css_class='btn-danger')

        Form.__init__(self, request, template_path, self.ExampleInputsSchema(), buttons=(btn_submit,))

    @staticmethod
    def ExampleInputsSchema():

        class ExampleSchema(colander.Schema):

            tmpstore = FileUploadTempStore()
            upload = colander.SchemaNode(
                deform.FileData(),
                title='Upload',
                widget=deform.widget.FileUploadWidget(tmpstore)
                )

        return ExampleSchema()


class FileUploadTempStore(dict):
    """ A temporary storage for file uploads
    File uploads are stored in the session so that you don't need to upload
    your file again if validation of another schema node fails. """

    @staticmethod
    def preview_url(name=None):
        return None