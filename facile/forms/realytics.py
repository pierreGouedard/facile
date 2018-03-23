# Global imports
import deform
import colander
import datetime
import pandas as pd
from translationstring import TranslationStringFactory
_ = TranslationStringFactory('deform')

# Local import
from facile.forms.Deform import Form


class SeriesForm(Form):

    def __init__(self, request, template_deform_path, choices):
        Form.__init__(self, request, template_deform_path, self.SeriesInputsSchema(choices))
        self.mapping_name = {'dateStart': {'date': None}, 'dateEnd': {'date': None}, 'tag': None, 'submit': None}

    # validate_ method method should be re-defined in class that inherit from Form
    def validate_(self, pstruct):
        try:
            assert(pd.Timestamp(pstruct['dateStart']['date']) <= pd.Timestamp(pstruct['dateEnd']['date']))

        except AssertionError:
            raise deform.ValidationFailure

    # format_ function should be re-defined in class that inherit from Form
    def format_(self, pstruct):
        pstruct['dateStart'] = pd.Timestamp(pstruct['dateStart']['date'])
        pstruct['dateEnd'] = pd.Timestamp(pstruct['dateEnd']['date'])
        if pstruct['dateStart'] == pstruct['dateEnd']:
            pstruct['dateEnd'] += pd.Timedelta(days=1)

        return pstruct

    @staticmethod
    def SeriesInputsSchema(choices):

        # Format list of choices
        choices = [('', '- Select -')] + zip(choices, choices)

        class SeriesSchema(colander.Schema):

            dateStart = colander.SchemaNode(
                colander.Date(),
                title="Date start",
                validator=colander.Range(
                    min=datetime.date(2015, 1, 1),
                    min_err=_('${val} is earlier than earliest datetime ${min}')
                ),
                widget=deform.widget.DateInputWidget(**{'key': 'dateStart-date'})
            )

            dateEnd = colander.SchemaNode(
                colander.Date(),
                title="Date end",
                validator=colander.Range(
                    max=datetime.datetime.now().date(),
                    max_err=_('${val} is greater than maximum value ${max}')
                ),
                widget=deform.widget.DateInputWidget(**{'key': 'dateEnd-date'})
            )

            tag = colander.SchemaNode(
                    colander.String(),
                    title='Trafic category',
                    widget=deform.widget.Select2Widget(values=choices)
                )

        return SeriesSchema()
