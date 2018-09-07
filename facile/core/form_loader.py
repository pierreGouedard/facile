class FormLoader(object):
    buttons = ('Retour', 'Suivant')

    def __init__(self, l_index, l_fields, l_subindex=[], use_subindex=False, use_groupindex=False):
        self.l_index = l_index
        self.l_fields = l_fields
        self.l_subindex = l_subindex
        self.use_subindex = use_subindex
        self.use_groupindex = use_groupindex
        self.d_form_data = None

    def load_init_form(self, action_node, index_node):
        self.d_form_data = {
            'nodes': [action_node.sn, index_node.sn],
            'buttons': ('Suivant',),
            'mapping': {'Suivant': None, 'action': None, 'index': None},
            'formatting': {}
        }

    def load(self, step,  data_db=None, data_form=None, l_buttons=[]):

        # Create mask fields
        d_mask_fields = {i: (s.round <= step, s.round == step) for i, s in enumerate(self.l_fields)}
        d_mask_index = {i: (s.round <= step, s.round == step) for i, s in enumerate(self.l_index)}

        l_fields, l_index = self.filter_fields(d_mask_fields), self.filter_index(d_mask_index)

        self.d_form_data = {
            'buttons': tuple(list(self.buttons) + l_buttons),
            'mapping': [('Retour', None), ('Suivant', None)]
        }

        if 'Ajouter' in data_form['action']:

            self.d_form_data['mapping'] += [('Ajouter', None)]
            self.d_form_data['data'] = {}

        else:
            # Make index and subindex hidden
            l_index = [f.hidden_mode() for f in l_index]

            if self.use_subindex:
                l_fields = map(lambda (i, x): x if not i in self.l_subindex else f.hidden_mode(), l_fields)

            self.d_form_data['mapping'] += [('Ajouter', None)]
            for f in l_index + l_fields:
                if f.name in data_db:
                    data_db[f.name] = f.processing_form['db'](data_db[f.name])

            self.d_form_data['data'] = data_db

        self.d_form_data['nodes'] = [f.sn for f in l_index + l_fields]
        self.d_form_data['mapping'] = dict(self.d_form_data['mapping'] +
                                           [(f.name, f.mapinit) for f in l_index + l_fields])

        if data_form is not None:
            l_names = [f.name for f in l_index + l_fields] + ['action', 'index']
            self.d_form_data['data'].update({k: v for k, v in data_form.items() if k in l_names})

        self.d_form_data['formatting'] = {f.name: f.processing_form['form'] for f in l_index + l_fields}

    def filter_index(self, d_mask_index):

        l_index_ = []
        for i, f in enumerate(self.l_index):
            if any(d_mask_index[i]):
                if not all(d_mask_index[i]):
                    l_index_ += [f.hidden_mode()]
                else:
                    l_index_ += [f.set_mode()]

        return l_index_

    def filter_fields(self, d_mask_fields):

        l_fields_ = []
        for i, f in enumerate(self.l_fields):
            if any(d_mask_fields[i]):
                if not all(d_mask_fields[i]):
                    l_fields_ += [f.hidden_mode()]
                else:
                    l_fields_ += [f.set_mode()]

        return l_fields_



