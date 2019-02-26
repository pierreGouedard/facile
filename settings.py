import os

facile_home = os.path.join(os.path.expanduser("~"), 'facile')
facile_data_path = os.path.join(facile_home, 'DATA/')
facile_db_path = os.path.join(facile_data_path, 'DB')
facile_commande_path = os.path.join(facile_db_path, 'LST_COM')
facile_admin_path = os.path.join(facile_data_path, 'ADMIN')
facile_test_path = os.path.join(facile_data_path, 'TEST')
deform_template_path = os.path.join(facile_home, 'facileapp/static/deform/templates/')
table_template_path = os.path.join(facile_home, 'facileapp/static/table/templates')
facile_business_closing_date = '{}-06-01'
facile_driver_tmpdir = '/tmp'
