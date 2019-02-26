# Global import
import pandas as pd
from colander import SchemaNode as sn, Schema, String, Date, DateTime, Integer, Money, Float, Sequence, Set
from deform import FileData
from deform.widget import DateInputWidget, DateTimeInputWidget, Select2Widget, MoneyInputWidget, HiddenWidget, \
    TextInputWidget, FileUploadWidget
import copy


class StringFields(object):
    def __init__(self, title, name, round=1, missing='', widget=None, l_choices=None, multiple=False, desc=None,
                 table_reduce=False, rank=0, required=False, missing_msg='champ requis'):

        # Form display
        self.title = title
        self.name = name
        self.round = round
        self.type = str
        self.desc = desc
        self.required = required
        self.missing_msg = missing_msg
        self.multiple = multiple
        self.mapinit = None if not self.multiple else []

        # Table display
        self.table_reduce, self.rank = table_reduce, rank

        if widget is not None:
            self.widget = widget
        else:
            if l_choices:
                self.widget = Select2Widget(values=l_choices, multiple=multiple)
            else:
                self.widget = TextInputWidget()

        self.processing_form = {'form': lambda x: str(x) if x else missing, 'db': lambda x: str(x)}
        self.processing_db = {'upload': lambda x: x, 'download': lambda x: x}

        if not multiple:
            self.sn = sn(String(), title=self.title, name=name, widget=self.widget, missing=missing, description=desc,
                         required=self.required, missing_msg=self.missing_msg)
        else:
            self.processing_form.update(
                {'form': lambda x: ';'.join(map(str, x)) if x else missing, 'db': lambda x: x.split(';')}
            )
            self.sn = sn(Set(), title=self.title, name=name, widget=self.widget, description=desc)

        if not required:
            self.sn.missing = missing

    def set_mode(self):
        return StringFields(
            self.title, self.name, self.round, widget=self.widget, desc=self.desc, multiple=self.multiple,
            required=self.required, missing_msg=self.missing_msg
        )

    def hidden_mode(self):
        return StringFields(self.title, self.name, self.round, widget=HiddenWidget())


class IntegerFields(object):
    def __init__(self, title, name, round=1, missing=-1, widget=None, l_choices=None, desc=None,
                 table_reduce=False, rank=0, required=False, missing_msg='champ requis'):

        # Form display & param
        self.title = title
        self.round = round
        self.name = name
        self.type = int
        self.desc = desc
        self.required = required
        self.missing_msg = missing_msg
        self.mapinit = None

        # Table display & param
        self.table_reduce, self.rank, = table_reduce, rank

        if widget is not None:
            self.widget = widget
        else:
            if l_choices:
                self.widget = Select2Widget(values=l_choices)
            else:
                self.widget = None

        self.processing_form = {'form': lambda x: int(x) if x else missing, 'db': lambda x: int(x)}
        self.processing_db = {'upload': lambda x: x, 'download': lambda x: x}

        self.sn = sn(Integer(), title=self.title, name=name, widget=self.widget, description=desc,
                     required=self.required, missing_msg=self.missing_msg)

        if not required:
            self.sn.missing = missing

    def set_mode(self):
        return IntegerFields(self.title, self.name, self.round, widget=self.widget, desc=self.desc,
                             required=self.required, missing_msg=self.missing_msg)

    def hidden_mode(self):
        return IntegerFields(self.title, self.name, self.round, widget=HiddenWidget())


class FloatFields(object):
    def __init__(self, title, name, round=1, missing=-1., widget=None, l_choices=None, desc=None,
                 decimal=100, table_reduce=False, rank=0, required=False, missing_msg='champ requis'):

        # Form display & param
        self.title = title
        self.round = round
        self.name = name
        self.type = float
        self.missing = missing
        self.required = required
        self.missing_msg = missing_msg
        self.desc = desc
        self.mapinit = None

        # Table display & param
        self.table_reduce, self.rank, = table_reduce, rank

        if widget is not None:
            self.widget = widget
        else:
            if l_choices:
                self.widget = Select2Widget(values=l_choices)
            else:
                self.widget = None

        self.processing_form = {'form': lambda x: float(x) if x else missing, 'db': lambda x: float(x)}
        self.processing_db = {'upload': lambda x: float(int(x * decimal)) / decimal, 'download': lambda x: x}

        self.sn = sn(Float(), title=self.title, name=name, widget=widget, description=desc,
                     required=self.required, missing_msg=self.missing_msg)

        if not required:
            self.sn.missing = missing

    def set_mode(self):
        return FloatFields(self.title, self.name, self.round, widget=self.widget, desc=self.desc, missing=self.missing,
                           required=self.required, missing_msg=self.missing_msg)

    def hidden_mode(self):
        return FloatFields(self.title, self.name, self.round, widget=HiddenWidget())


class MoneyFields(object):
    def __init__(self, title, name, round=1, missing=0., widget=None, l_choices=None, desc=None, decimal=100,
                 table_reduce=False, rank=0, required=False, missing_msg='champ requis'):

        # Form display & param
        self.title = title
        self.round = round
        self.name = name
        self.type = float
        self.missing = missing
        self.required = required
        self.missing_msg = missing_msg
        self.desc = desc
        self.mapinit = None

        # Table display & param
        self.table_reduce, self.rank, = table_reduce, rank

        if widget is not None:
            self.widget = widget
        else:
            if l_choices:
                self.widget = Select2Widget(values=l_choices)
            else:
                self.widget = MoneyInputWidget(options={'allowZero': True})

        self.processing_form = {'form': lambda x: float(x.replace(',', '')) if x else missing, 'db': lambda x: float(x)}
        self.processing_db = {'upload': lambda x: float(int(x * decimal)) / decimal, 'download': lambda x: x}

        self.sn = sn(Money(), title=self.title, name=self.name, widget=self.widget, description=desc,
                     required=self.required, missing_msg=self.missing_msg)

        if not required:
            self.sn.missing = missing

    def set_mode(self):
        return MoneyFields(self.title, self.name, self.round, widget=self.widget, desc=self.desc, missing=self.missing,
                           required=self.required, missing_msg=self.missing_msg)

    def hidden_mode(self):
        return MoneyFields(self.title, self.name, self.round, widget=HiddenWidget())


class DateFields(object):
    def __init__(self, title, name, round=1, missing='', widget=None, mapinit=None, processing_form=None,
                 desc=None, table_reduce=False, rank=0, required=False, missing_msg='champ requis'):

        self.title = title
        self.name = name
        self.type = str
        self.required = required
        self.missing_msg = missing_msg
        self.missing = missing
        self.desc = desc
        self.table_reduce, self.rank, = table_reduce, rank

        self.widget = widget
        self.round = round
        self.mapinit = mapinit
        self.processing_form = {'form': processing_form, 'db': lambda x: pd.Timestamp(x).date()}
        self.processing_db = {'upload': lambda x: pd.Timestamp(x).date(), 'download': lambda x: x}

        self.sn = sn(Date(), title=self.title, name=name, widget=self.widget, description=desc,
                     required=self.required, missing_msg=self.missing_msg)

        if not required:
            self.sn.missing = missing

    def set_mode(self):

        return DateFields(self.title, self.name, self.round,
                          widget=DateInputWidget(**{'key': '{}-date'.format(self.name)}), mapinit={'date': None},
                          processing_form=lambda x: pd.Timestamp(x['date']), desc=self.desc, missing=self.missing,
                          required=self.required, missing_msg=self.missing_msg)

    def hidden_mode(self):
        return DateFields(self.title, self.name, self.round, widget=HiddenWidget(), mapinit=None,
                          processing_form=lambda x: pd.Timestamp(x), missing=self.missing)


class DateTimeFields(object):
    def __init__(self, title, name, round=1, missing='', widget=None, mapinit=None, processing_form=None, desc=None,
                 table_reduce=False, rank=0, required=False, missing_msg='champ requis'):

        self.title = title
        self.name = name
        self.required = required
        self.missing_msg = missing_msg
        self.type = str
        self.desc = desc

        self.table_reduce, self.rank, = table_reduce, rank

        self.widget = widget
        self.round = round
        self.mapinit = mapinit

        self.processing_form = {'form': processing_form, 'db': lambda x: pd.Timestamp(x)}
        self.processing_db = {'upload': lambda x: pd.Timestamp(x), 'download': lambda x: x}

        self.sn = sn(DateTime(), title=self.title, name=name, widget=self.widget, description=desc,
                     required=self.required, missing_msg=self.missing_msg)

        if not required:
            self.sn.missing = missing

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


class FileFields(object):
    def __init__(self, title, name, round=1, missing=None, widget=None, mapinit=None, desc=None, table_reduce=False,
                 rank=0, required=False, missing_msg='champ requis'):

        self.title = title
        self.name = name
        self.required = required
        self.missing_msg = missing_msg
        self.type = str
        self.desc = desc
        self.tmpstore = FileUploadTempStore(dict())

        self.table_reduce, self.rank, = table_reduce, rank

        self.widget = widget
        self.round = round
        self.mapinit = {'filename': None, 'fp': None, 'mimetype': None, 'preview_url': None, 'size': None, 'uid': None}

        if mapinit is not None:
            self.mapinit.update(mapinit)

        if missing is None:
            missing = {'filename': '', 'uid': ''}

        self.processing_form = {'form': lambda x: x, 'db': lambda x: {'filename': x}}
        self.processing_db = {'upload': lambda x: x.get('filename', ''), 'download': lambda x: x}

        self.sn = sn(FileData(), title=self.title, name=name, widget=self.widget, description=desc,
                     required=self.required, missing_msg=self.missing_msg)

        if not required:
            self.sn.missing = missing

    def set_mode(self):
        kwargs = {'key': self.name}
        return FileFields(
            self.title, self.name, self.round, widget=FileUploadWidget(self.tmpstore, **kwargs), mapinit=None,
            desc=self.desc
        )

    def hidden_mode(self):
        return FileFields(
            self.title, self.name, self.round, widget=HiddenWidget(), mapinit=None,
        )


class MappingFields(object):

    def __init__(self, title, name, prefix, l_fields, round=1, desc=None, widget=None):
        self.title = title
        self.desc = desc
        self.prefix = prefix
        self.name = name
        self.l_fields = []

        for f in l_fields:
            f_ = copy.deepcopy(f)
            f_.sn.name = '{}-{}'.format(prefix, f.name)
            self.l_fields += [f_]

        self.round = round
        self.mapinit = {f.name: f.mapinit for f in l_fields}

        self.processing_form = {'form': lambda x: {f.name: f.processing_form['form'](x[f.name]) for f in self.l_fields},
                                'db': lambda x: {f.sn.name: f.processing_form['db'](x[f.name]) for f in self.l_fields}}

        self.sn = Schema(title=self.title, name=name, description=desc, widget=widget)
        for f in self.l_fields:
            self.sn.add(f.sn)

    def set_mode(self):
        return MappingFields(self.title, self.name, self.prefix, self.l_fields, self.round, desc=self.desc)

    def hidden_mode(self):
        return MappingFields(self.title, self.name, self.prefix, self.l_fields, self.round, widget=HiddenWidget())


class SequenceFields(object):

    def __init__(self, title, name, field, round=1, desc=None, widget=None):
        self.title = title
        self.name = name
        self.field = field
        self.desc = desc
        self.round = round

        self.mapinit = [field.mapinit]
        self.processing_form = {'form': lambda l: [field.processing_form['form'](v) for v in l],
                                'db': lambda l: [field.processing_form['db'](v) for v in l]}

        self.sn = sn(Sequence(), field.sn, name=self.name, title=self.title, description=self.desc, widget=widget)

    def set_mode(self):
        return SequenceFields(self.title, self.name, self.field, self.round, desc=self.desc)

    def hidden_mode(self):
        return SequenceFields(self.title, self.name, self.field, self.round, widget=HiddenWidget())


class FileUploadTempStore(dict):
    """ A temporary storage for file uploads
    File uploads are stored in the session so that you don't need to upload
    your file again if validation of another schema node fails. """

    @staticmethod
    def preview_url(name=None):
        return None
