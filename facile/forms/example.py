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
        self.mapping_name = {'datefield': {'date': None},
                             'datetimefield': {'date': None, 'time': None, 'date_submit': None, 'time_submit': None},
                             'textfield': None,
                             'intfield': None,
                             'select_field': None,
                             'select_multiple_field': [],
                             'check': None,
                             'money': None,
                             'radio': None,
                             'submit': None}

        choices_radio = [('choice_1', 'display_choice_1'), ('choice_2', 'display_choice_2'),
                         ('choice_3', 'display_choice_3'), ('choice_4', 'display_choice_4')]
        choices_1 = [('value_1', 'display_value_1'), ('value_2', 'display_value_2'), ('value_3', 'display_value_3')]
        choices_2 = [('value_21', 'display_value_21'), ('value_22', 'display_value_22'),
                     ('value_23', 'display_value_23'), ('value_24', 'display_value_24')]

        Form.__init__(self, request, template_path, self.ExampleInputsSchema(choices_1, choices_2, choices_radio))

    # validate_ method should be re-defined in class that inherit from Form
    def validate_(self, pstruct):
        try:
           int(pstruct['intfield']) < 10000

        except AssertionError:
            raise deform.ValidationFailure

    # format_ function should be re-defined in class that inherit from Form
    def format_(self, pstruct):

        # Convert date and datetime into pandas Timestamp
        pstruct['datefield'] = pd.Timestamp(pstruct['datefield']['date'])
        pstruct['datetimefield'] = pd.Timestamp(' '.join([pstruct['datetimefield']['date'],
                                                          pstruct['datetimefield']['time']]))
        # cast int input
        pstruct['intfield'] = int(pstruct['intfield'])

        return pstruct

    @staticmethod
    def ExampleInputsSchema(choices_1, choices_2, choices_radio):

        class ExampleSchema(colander.Schema):

            datefield = colander.SchemaNode(colander.Date(),
                                            title='Date',
                                            widget=deform.widget.DateInputWidget(**{'key': 'datefield-date'})
                                            )

            datetimefield = colander.SchemaNode(colander.DateTime(),
                                                title='Date - Time',
                                                widget=deform.widget.DateTimeInputWidget(
                                                    **{'key_date': 'datetimefield-date',
                                                       'key_time': 'datetimefield-time'}
                                                    )
                                                )

            textfield = colander.SchemaNode(colander.String(), title='Text')

            intfield = colander.SchemaNode(colander.Integer(), title='Integer')

            select_field = colander.SchemaNode(colander.String(), widget=deform.widget.Select2Widget(values=choices_1))

            select_multiple_field = colander.SchemaNode(colander.Set(),
                                                        widget=deform.widget.Select2Widget(values=choices_2,
                                                                                           multiple=True),
                                                        )

            check = colander.SchemaNode(colander.Boolean(),
                                        widget=deform.widget.CheckboxWidget(),
                                        label='Really',
                                        title='is smthg')

            money = colander.SchemaNode(colander.Decimal(),
                                        widget=deform.widget.MoneyInputWidget(options={'allowZero': True}),
                                        title='Amount')

            radio = colander.SchemaNode(colander.Str(),
                                        validator=colander.OneOf([x[0] for x in choices_radio]),
                                        widget=deform.widget.RadioChoiceWidget(values=choices_radio, **{'key': 'radio'}),
                                        title='Choose your your choice')

        return ExampleSchema()
