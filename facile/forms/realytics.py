# Global imports
import deform
import colander
import datetime
from translationstring import TranslationStringFactory
_ = TranslationStringFactory('deform')

# Local import
from facile.forms.Deform import Form

class testdatewidget(deform.widget.DateInputWidget):
    type_name = 'pute'
    key = 'dates'


class SeriesForm(Form):

    def __init__(self, request, template_deform_path):
        Form.__init__(self, request, template_deform_path)

    def get_form(self):
        schema = SeriesSchema()
        deform.form.Form.set_zpt_renderer(self.search_path)
        form = deform.form.Form(schema, buttons=('submit',), use_ajax=True)
        form.set_zpt_renderer(self.search_path)
        import IPython
        IPython.embed()
        return self.render_form(form)

class TestForm(Form):

    def __init__(self, request, template_deform_path):
        Form.__init__(self, request, template_deform_path)

    def get_form(self, appstruct=colander.null):
        appstruct = {"people": [
            {
                'name': 'keith',
                'age': 20,
            },
            {
                'name': 'fred',
                'age': 23,
            },
        ]}
        schema = Schema()
        form = deform.form.Form(schema, buttons=('submit',))
        import IPython
        IPython.embed()
        return self.render_form(form, **{'mask': "salepute"})


class Person(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    age = colander.SchemaNode(colander.Integer(),
                              validator=colander.Range(0, 200))

class People(colander.SequenceSchema):
    person = Person()

class Schema(colander.MappingSchema):
    people = People()


class SeriesSchema(colander.Schema):

    dateStart = colander.SchemaNode(
        colander.Date(),
        title="Date start",
        validator=colander.Range(
            min=datetime.date(2015, 1, 1),
            min_err=_('${val} is earlier than earliest datetime ${min}')
        ),
        widget=deform.widget.DateInputWidget(**{'key': 'dateS'})
    )

    dateEnd = colander.SchemaNode(
        colander.Date(),
        title="Date end",
        validator=colander.Range(
            min=datetime.datetime.now(),
            max_err=_('${val} is greater than maximum value ${max}')
        ),
        widget=deform.widget.DateInputWidget(**{'key': 'dateE'})
    )

    tag = colander.SchemaNode(
        colander.String(),
        title="Trafic category")