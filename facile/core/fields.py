import os
import pandas as pd
from colander import SchemaNode as sn, String, Date, DateTime, Integer, Money, Float
from deform.widget import DateInputWidget, DateTimeInputWidget, Select2Widget, CheckboxWidget, MoneyInputWidget, \
    RadioChoiceWidget, HiddenWidget, TextInputWidget
import copy


class StringFields(object):
    def __init__(self, title, name, round=1, missing='', widget=None, l_choices=None, multiple=False, desc=None):

        self.title = title
        self.name = name
        self.round = round
        self.type = str
        self.desc = desc

        if widget is not None:
            self.widget = widget
        else:
            if l_choices:
                self.widget = Select2Widget(values=l_choices, multiple=multiple)
            else:
                self.widget = TextInputWidget()

        self.mapinit = None
        self.processing_form = lambda x: str(x)
        self.processing_db = lambda x: str(x)

        self.sn = sn(String(), title=self.title, name=name, widget=self.widget, missing=missing, description=desc)

    def set_mode(self):
        return StringFields(self.title, self.name, self.round, widget=self.widget, desc=self.desc)

    def hidden_mode(self):
        return StringFields(self.title, self.name, self.round, widget=HiddenWidget())


class IntegerFields(object):
    def __init__(self, title, name, round=1, missing=-1, widget=None, l_choices=None, multiple=False, desc=None):
        self.title = title
        self.round = round
        self.name = name
        self.type = int
        self.desc = desc

        if widget is not None:
            self.widget = widget
        else:
            if l_choices:
                self.widget = Select2Widget(values=l_choices, multiple=multiple)
            else:
                self.widget = None

        self.mapinit = None
        self.processing_form = lambda x: int(x)
        self.processing_db = lambda x: int(x)

        self.sn = sn(Integer(), title=self.title, name=name, widget=self.widget, missing=missing, description=desc)

    def set_mode(self):
        return IntegerFields(self.title, self.name, self.round, widget=self.widget, desc=self.desc)

    def hidden_mode(self):
        return IntegerFields(self.title, self.name, self.round, widget=HiddenWidget())


class FloatFields(object):
    def __init__(self, title, name, round=1, missing=-1., widget=None, l_choices=None, multiple=None, desc=None):
        self.title = title
        self.round = round
        self.name = name
        self.type = float
        self.desc = desc

        if widget is not None:
            self.widget = widget
        else:
            if l_choices:
                self.widget = Select2Widget(values=l_choices, multiple=multiple, missing=missing)
            else:
                self.widget = None

        self.mapinit = None
        self.processing_form = lambda x: float(x)
        self.processing_db = lambda x: float(x)

        self.sn = sn(Float(), title=self.title, name=name, widget=widget, description=desc)

    def set_mode(self):
        return FloatFields(self.title, self.name, self.round, widget=self.widget, desc=self.desc)

    def hidden_mode(self):
        return FloatFields(self.title, self.name, self.round, widget=HiddenWidget())


class MoneyFields(object):
    def __init__(self, title, name, round=1, missing=-1., widget=None, l_choices=None, multiple=None, desc=None):
        self.title = title
        self.round = round
        self.name = name
        self.type = float
        self.desc = desc

        if widget is not None:
            self.widget = widget
        else:
            if l_choices:
                self.widget = Select2Widget(values=l_choices, multiple=multiple, missing=missing)
            else:
                self.widget = MoneyInputWidget()

        self.mapinit = None
        self.processing_form = lambda x: float(x)
        self.processing_db = lambda x: float(x)

        self.sn = sn(Money(), title=self.title, name=self.name, widget=self.widget, description=desc)

    @staticmethod
    def set_mode(title, name, round, widget=None):
        return MoneyFields(title, name, round, widget=widget, desc=self.desc)

    @staticmethod
    def hidden_mode(title, name, round):
        return MoneyFields(title, name, round, widget=HiddenWidget())


class DateFields(object):
    def __init__(self, title, name, round=1, missing='', widget=None, mapinit=None, processing_form=None, desc=None):
        self.title = title
        self.name = name
        self.type = str
        self.desc =desc

        self.widget = widget
        self.round = round
        self.mapinit = mapinit

        self.processing_form = processing_form
        self.processing_db = lambda x: pd.Timestamp(x)

        self.sn = sn(Date(), title=self.title, name=name, widget=self.widget, missign=missing, description=desc)

    def set_mode(self):

        return DateFields(self.title, self.name, self.round,
                          widget=DateInputWidget(**{'key': '{}-date'.format(self.name)}), mapinit={'date': None},
                          processing_form=lambda x: pd.Timestamp(x['date']), desc=self.desc)

    def hidden_mode(self):
        return DateFields(self.title, self.name, self.round, widget=HiddenWidget(), mapinit=None,
                          processing_form=lambda x: pd.Timestamp(x))


class DateTimeFields(object):
    def __init__(self, title, name, round=1, missing='', widget=None, mapinit=None, processing_form=None, desc=None):
        self.title = title
        self.name = name
        self.type = str
        self.desc = desc

        self.widget = widget
        self.round = round
        self.mapinit = mapinit

        self.processing_form = processing_form
        self.processing_db = lambda x: pd.Timestamp(x)

        self.sn = sn(DateTime(), title=self.title, name=name, widget=self.widget, missign=missing, description=desc)

    def set_mode(self):
        keyw = {'key_date': '{}-date'.format(self.name),
               'key_time': '{}-time'.format(self.name)}

        return DateTimeFields(
            self.title, self.name, self.round, widget=DateTimeInputWidget(**keyw), mapinit={'date': None, 'time': None},
            processing_form=lambda x: pd.Timestamp('{} {}'.format(x['date'], x['time']), desc=self.desc)
        )

    def hidden_mode(self):
        return DateTimeFields(
            self.title, self.name, self.round, widget=HiddenWidget(), mapinit=None,
            processing_form=lambda x: pd.Timestamp(x)
        )


