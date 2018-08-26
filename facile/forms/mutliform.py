# Global imports
import deform
import colander
from translationstring import TranslationStringFactory
import pytz
_ = TranslationStringFactory('deform')

# Local import
from facile.forms.Deform import Form
utc = pytz.UTC


class MultipleStepForm(Form):

    def __init__(self, request, static_path, step, nb_step=1, **kwargs):

        self.mapping_name = {'step': None, 'nb_step': None, 'action': None, 'index': None}

        appstruct, d_action, d_index = {'step': step, 'nb_step': nb_step}, {}, {}

        if 'data' in kwargs:
            appstruct.update(kwargs['data'])
            d_action = {0: 'action' in kwargs['data']}
            d_index = {0: 'index' in kwargs['data']}

        Form.__init__(self, request, static_path,
                      self.get_schema(kwargs['nodes'], d_action.get(0, False), d_index.get(0, False)),
                      appstruct, buttons=kwargs['buttons'])

        self.mapping_name.update(kwargs['mapping'])

    @staticmethod
    def get_schema(l_nodes, add_action, add_index):

        class Schema_(colander.Schema):
            step = colander.SchemaNode(colander.Integer(), title='Text', widget=deform.widget.HiddenWidget())
            nb_step = colander.SchemaNode(colander.Integer(), title='Text', widget=deform.widget.HiddenWidget())
            if add_action:
                action = colander.SchemaNode(colander.String(), title='Text', widget=deform.widget.HiddenWidget())
            if add_index:
                index = colander.SchemaNode(colander.String(), title='Text', widget=deform.widget.HiddenWidget())

        schema_ = Schema_()
        for node in l_nodes:
            schema_.add(node)

        return schema_
