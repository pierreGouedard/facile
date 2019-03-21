#!/usr/bin/python
# -*- coding: utf-8 -*-

# Global import
from facileapp import application
from flask import render_template
from flask import Markup, session, redirect, url_for, request, send_file, jsonify
from jinja2 import Template

# Local import
from facile.forms import login, download, example
from facile.utils.forms import build_form, process_form, get_args_forms, get_title_from_step, build_document_form, \
    process_document_form
from facile.utils.tables import build_table, process_table
from facile.utils.controls import build_controls, process_controls
from facile.layout import boostrap
from config import DEFORM_TEMPLATE_PATH


@application.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('log_in'))

    return render_template("home.html")


@application.route('/restricted')
def restricted():
    if 'username' not in session:
        return redirect(url_for('log_in'))

    return render_template("restricted.html")


@application.route('/login', methods=['GET', 'POST'])
def log_in():
    # Create page global layout
    custom_template = Template(render_template('login.html', custom_html=Markup(boostrap.get_login_layout())))

    # process request
    web, data = login.LoginForm(request, DEFORM_TEMPLATE_PATH).process_form()

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


@application.route('/example', methods=['GET', 'POST'])
def test_example():
    # Create page global layout
    custom_template = Template(render_template('example.html', form=Markup(boostrap.get_example_layout())))

    # process request
    web, data = example.ExampleForm(request, DEFORM_TEMPLATE_PATH).process_form()

    if request.method == 'GET':
        html = render_template(custom_template, **{k: Markup(v) for k, v in web.items()})

    else:
        html = render_template(custom_template, **{k: Markup(v) for k, v in web.items()})

    return html


@application.route('/logout', methods=['GET', 'POST'])
def log_out():

   # Remove the username from the session if it is there
   session.pop('username', None)
   session.pop('rights', None)

   return redirect(url_for('home'))


@application.route('/forms', methods=['GET', 'POST'])
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
            web, data = build_form(request.args['table'], request, DEFORM_TEMPLATE_PATH)

            # Get Table
            table = {'table': build_table(request.args['table'])}

            # Gather context and render template
            context = {k: Markup(v) for k, v in web.items() + table.items()}
            html = render_template(custom_template, **context)

        else:
            form = Markup(u'<h1>Page des Formulaires</h1>'
                          u'<p class="lead"> Choisissez un onglet puis ajoutez, modifiez '
                          u"ou suprimez un élément d'une table</p>")
            html = render_template("form.html", **{'form': form})
    else:
        # Get data from form
        web, data = build_form(request.args['table'], request, DEFORM_TEMPLATE_PATH, step=int(request.form['step']),
                               force_get=False, validate='Retour' not in request.form.keys(), session=session,
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
            web, data = build_form(request.args['table'], request, DEFORM_TEMPLATE_PATH, step=step, force_get=True,
                                   data=data['form_data'], script=script, session=session)

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


@application.route('/documents', methods=['GET', 'POST'])
def document():
    if 'username' not in session:
        return redirect(url_for('log_in'))

    if request.method == 'GET':
        if request.args:

            # Build title
            title = u"Editer les documents de la table: {}".format(request.args['table'])

            # Get template
            custom_template = Template(
                render_template('document.html', document=Markup(boostrap.get_document_layout(title)))
            )

            # Get form
            web = build_document_form(request.args['table'], request, DEFORM_TEMPLATE_PATH)

            # Gather context and render template
            context = {k: Markup(v) for k, v in web.items()}
            html = render_template(custom_template, **context)

        else:
            document = Markup(u'<h1>Page des documents</h1>'
                              u'<p class="lead"> Choisissez un onglet pour éditer un document</p>')
            html = render_template("document.html", **{'document': document})
    else:
        path, tmpdir = process_document_form(request.args['table'], request.form)
        return send_file(path, as_attachment=True)

    return html


@application.route('/exports', methods=['GET', 'POST'])
def export():
    if 'username' not in session:
        return redirect(url_for('log_in'))

    elif 'ADMIN' not in session['rights']:
        return redirect(url_for('restricted'))

    if request.method == 'GET':
        if request.args:

            # Build title
            title = u"Exporter la table: {}".format(request.args['table'])

            # Get template
            custom_template = Template(
                render_template('export.html', export=Markup(boostrap.get_export_layout(title)))
            )

            # Get form
            web, data = download.DownloadForm(request, DEFORM_TEMPLATE_PATH).process_form()

            # Get Table
            table = {'table': build_table(request.args['table'], reduced=False, load_jQuery=True,
                                          head_class='table-active')}

            # Gather context and render template
            context = {k: Markup(v) for k, v in web.items() + table.items()}
            html = render_template(custom_template, **context)

        else:
            export = Markup(u'<h1>Page des Exports</h1>'
                            u'<p class="lead"> Choisissez un onglet pour explorer et exporter les tables</p>')
            html = render_template("export.html", **{'export': export})
    else:
        path, tmpdir = process_table(request.args['table'])
        return send_file(path, as_attachment=True)

    return html


@application.route('/controls', methods=['GET', 'POST'])
def control():
    if 'username' not in session:
        return redirect(url_for('log_in'))

    elif session['rights'] == 'STANDARD':
        return redirect(url_for('restricted'))

    if request.method == 'GET':
        if request.args:

            # render controls
            html = build_controls(request, session, DEFORM_TEMPLATE_PATH)

        else:
            control = Markup(u'<div class="jumbotron">'
                             u'<h1>Page des controles</h1>'
                             u'<p class="lead"> Choisissez un onglet pour visualiser un controle</p></div>')
            html = render_template("control.html", **{'control': control})

    else:
        script = process_controls(request, session, DEFORM_TEMPLATE_PATH)
        html = build_controls(request, session, DEFORM_TEMPLATE_PATH, script=script, force_get=True)

    return html


@application.route('/url_success_form', methods=['POST'])
def url_success_form():
    return jsonify({'url': '/send_file_form', 'data': '?' + '&'.join(['='.join(t) for t in request.form.items()])})


@application.route('/send_file_form', methods=['GET'])
def send_file_form():
    # Create document from args
    path, tmpdir = process_document_form(request.args['table_key'], request.args)
    return send_file(path, as_attachment=True)
