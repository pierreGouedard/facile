import os

facile_home = os.path.join(os.path.expanduser("~"), 'facile')
facile_data_path = os.path.join(facile_home, 'DATA/')
facile_project_path = os.path.join(facile_data_path, 'DB')
facile_admin_path = os.path.join(facile_data_path, 'ADMIN')
facile_test_path = os.path.join(facile_data_path, 'TEST')
deform_template_path = os.path.join(facile_home, 'facileapp/static/deform/templates/')
table_template_path = os.path.join(facile_home, 'facileapp/static/table/templates')