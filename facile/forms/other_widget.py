# Global imports
import deform
import colander
import datetime
import pandas as pd
from translationstring import TranslationStringFactory
import pytz
_ = TranslationStringFactory('deform')

# Local import
from facile.forms.Deform import Form
utc = pytz.UTC

class OtherForm(Form):

    def __init__(self, request, template_deform_path):

        choices_radio = [('choice_1', 'Choice 1'), ('choice_2', 'Choice 2'), ('choice_3', 'Choice 3'),
                         ('choice_4', 'Choice 4')]

        # Define mapping
        self.mapping_name = {'check': None, 'money': None, 'radio': None, 'submit': None}

        Form.__init__(self, request, template_deform_path, self.OtherSchema(choices_radio))

    # validate_ method should be re-defined in class that inherit from Form
    def validate_(self, pstruct):
        print 'TODO'

    # format_ function should be re-defined in class that inherit from Form
    def format_(self, pstruct):

        return pstruct

    @staticmethod
    def OtherSchema(choices):

        class OtherSchema(colander.Schema):

            check = colander.SchemaNode(
                colander.Boolean(),
                widget=deform.widget.CheckboxWidget(),
                label='Really',
                title='is smthg')

            money = colander.SchemaNode(
                colander.Decimal(),
                widget=deform.widget.MoneyInputWidget(options={'allowZero': True}),
                title='Amount')

            radio = colander.SchemaNode(
                colander.Str(),
                validator=colander.OneOf([x[0] for x in choices]),
                widget=deform.widget.RadioChoiceWidget(values=choices, **{'key': 'radio'}),
                title='Choose your your choice')

        return OtherSchema()
