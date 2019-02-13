# Global import
from facileapp import app
from flask import render_template
from flask import Markup, session, redirect, url_for, request, send_file, jsonify
from jinja2 import Template

# Local import
from facile.forms import login, download
from facile.utils.forms import build_form, process_form, get_args_forms, get_title_from_step, build_document_form, \
    process_document_form
from facile.utils.tables import build_table
from facile.utils.controls import build_controls
from facile.layout import boostrap
from settings import deform_template_path
from facile.utils.drivers.comon import FileDriver


@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('log_in'))

    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def log_in():
    # Create page global layout
    custom_template = Template(render_template('login.html', custom_html=Markup(boostrap.get_login_layout())))

    # process request
    web, data = login.LoginForm(request, deform_template_path).process_form()

    if request.method == 'GET':
        html = render_template(custom_template, **{k: Markup(v) for k, v in web.items()})

    else:
        if data.pop('success'):
            form_data = data.pop('form_data')
            session['username'] = form_data['user'].username
            session['rights'] = form_data['user'].rights

            return redirect(url_for('home'))
        else:
            html = render_template(custom_template, **{k: Markup(v) for k, v in web.items()})

    return html


@app.route('/logout', methods=['GET', 'POST'])
def log_out():
   # Remove the username from the session if it is there
   session.pop('username', None)
   session.pop('rights', None)

   return redirect(url_for('home'))


@app.route('/forms', methods=['GET', 'POST'])
def form():
    if 'username' not in session:
        return redirect(url_for('log_in'))

    if request.method == 'GET':
        if request.args:
            # Get template
            custom_template = Template(
                render_template('form.html', form=Markup(boostrap.get_form_layout('Choisissez une action')))
            )

            # Get form
            web, data = build_form(request.args['table'], request, deform_template_path)

            # Get Table
            table = {'table': build_table(request.args['table'])}

            # Gather context and render template
            context = {k: Markup(v) for k, v in web.items() + table.items()}
            html = render_template(custom_template, **context)

        else:
            form = Markup('<h1>Page des Formulaires</h1>'
                          '<p class="lead"> Choisissez un onglet puis ajoutez, modifiez '
                          "ou suprimez un element d'une table</p>")
            html = render_template("form.html", **{'form': form})
    else:
        # Get data from form
        web, data = build_form(request.args['table'], request, deform_template_path, step=int(request.form['step']),
                               force_get=False, validate='Retour' not in request.form.keys(),
                               data={k: request.form.get(k, '') for k in ['step', 'action', 'index']})

        script = None
        if data['success']:

            # Get args that enable to know which form to display
            step, action, title = get_args_forms(data['form_data'])
            data['form_data'].update({'step': step})
            # Create template
            custom_template = Template(render_template('form.html', form=Markup(boostrap.get_form_layout(title))))

            # Process form if final step of action and layout option page
            if step > 0 and step % int(request.form['nb_step']) == 0 and 'Suivant' in request.form.keys():
                script = process_form(request.args['table'], data['form_data'], action)
                step, data['form_data'] = 0, {}

            # Generate new form
            web, data = build_form(request.args['table'], request, deform_template_path, step=step, force_get=True,
                                   data=data['form_data'], script=script)

        else:
            step = request.form['step']
            d_data = {k: request.form.get(k, '') for k in ['action', 'nb_step', 'index']}
            title = get_title_from_step(int(step), d_data)
            custom_template = Template(render_template('form.html', form=Markup(boostrap.get_form_layout(title))))

        # Generate table
        table = {'table': ''}
        if int(step) % int(request.form['nb_step']) == 0:
            table = {'table': build_table(request.args['table'])}

        # Gather context and render template
        context = {k: Markup(v) for k, v in web.items() + table.items()}
        html = render_template(custom_template, **context)

    return html


@app.route('/exports', methods=['GET', 'POST'])
def export():
    if 'username' not in session:
        return redirect(url_for('log_in'))

    if request.method == 'GET':
        if request.args:

            # Build title
            title = "Exporter la table: {}".format(request.args['table'])

            # Get template
            custom_template = Template(
                render_template('export.html', export=Markup(boostrap.get_export_layout(title)))
            )

            # Get form
            web, data = download.DownloadForm(request, deform_template_path).process_form()

            # Get Table
            table = {'table': build_table(request.args['table'], reduced=False, load_jQuery=True,
                                          head_class='table-active')}

            # Gather context and render template
            context = {k: Markup(v) for k, v in web.items() + table.items()}
            html = render_template(custom_template, **context)

        else:
            export = Markup('<h1>Page des Exports</h1>'
                            '<p class="lead"> Choisissez un onglet pour explorer et exporter les tables</p>')
            html = render_template("export.html", **{'export': export})
    else:
        # return xlsx of the table
        from facileapp.models.affaire import Affaire

        driver = FileDriver('tmp_test', '')

        df = Affaire.load_db()
        tmpdir = driver.TempDir(create=True)

        df.to_csv(driver.join(tmpdir.path, 'test.csv'))

        return send_file(driver.join(tmpdir.path, 'test.csv'))

    return html


@app.route('/documents', methods=['GET', 'POST'])
def document():
    if 'username' not in session:
        return redirect(url_for('log_in'))

    if request.method == 'GET':
        if request.args:

            # Build title
            title = "Editer les documents de la table: {}".format(request.args['table'])

            # Get template
            custom_template = Template(
                render_template('document.html', document=Markup(boostrap.get_document_layout(title)))
            )

            # Get form
            web = build_document_form(request.args['table'], request, deform_template_path)

            # Gather context and render template
            context = {k: Markup(v) for k, v in web.items()}
            html = render_template(custom_template, **context)

        else:
            document = Markup('<h1>Page des documents</h1>'
                              '<p class="lead"> Choisissez un onglet pour editer un document</p>')
            html = render_template("document.html", **{'document': document})
    else:
        path, tmpdir = process_document_form(request.args['table'], request.form)
        return send_file(path, as_attachment=True)

    return html


@app.route('/controls', methods=['GET'])
def control():
    if 'username' not in session:
        return redirect(url_for('log_in'))

    if request.args:

        # render controls
        html = build_controls(table_key=request.args['table'])

    else:
        control = Markup('<div class="jumbotron">'
                         '<h1>Page des controles</h1>'
                         '<p class="lead"> Choisissez un onglet pour visualiser un control</p></div>')
        html = render_template("control.html", **{'control': control})

    return html


@app.route('/url_download_form', methods=['POST'])
def url_download_form():
    return jsonify({'url': '/send_file_form', 'data': '?' + '&'.join(['='.join(t) for t in request.form.items()])})


@app.route('/send_file_form', methods=['GET'])
def send_file_form():
    # Create document from args
    path, tmpdir = process_document_form(request.args['table_key'], request.args)
    return send_file(path, as_attachment=True)
