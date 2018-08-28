# Global import
from facileapp import app
from flask import render_template
from flask import Markup, session, redirect, url_for, request
from jinja2 import Template

# Local import
from facile.forms import login_form
from facile.utils.forms import build_form, process_form, get_args_forms, get_title_from_step
from facile.layout import boostrap
from settings import deform_template_path


@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Create page global layout
    custom_template = Template(render_template('login.html', custom_html=Markup(boostrap.get_login_layout())))

    # process request
    web, data = login_form.LoginForm(request, deform_template_path).process_form()

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
def logout():
   # Remove the username from the session if it is there
   session.pop('username', None)
   session.pop('rights', None)

   return redirect(url_for('home'))


@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        if request.args:
            # Get template
            custom_template = Template(render_template('form.html',
                                                       form=Markup(boostrap.get_form_layout('Choisissez une action'))))

            # Get form
            web, data = build_form(request.args['table'], request, deform_template_path)

            # Get Table
            table = {'table': ''}

            # Gather context and render template
            context = {k: Markup(v) for k, v in web.items() + table.items()}
            html = render_template(custom_template, **context)

        else:
            form = Markup('<h1>Page des Formulaires</h1>'
                          '<p class="lead"> Choisissez un onglet et ajoutez, modifiez '
                          "ou suprimez un element d'une table</p>")
            html = render_template("form.html", **{'form': form})
    else:
        # Get data from form
        web, data = build_form(request.args['table'], request, deform_template_path, step=int(request.form['step']),
                               force_get=False, validate='Retour' not in request.form.keys(),
                               data={k: request.form.get(k, '') for k in ['step', 'action']})

        if data['success']:

            # Get args that enable to know which form to display
            step, action, title = get_args_forms(data['form_data'])
            data['form_data'].update({'step': step})

            # Create template
            custom_template = Template(render_template('form.html', form=Markup(boostrap.get_form_layout(title))))

            # Process for if final step of action
            if step > 0 and step % int(request.form['nb_step']) == 0 and 'Suivant' in request.form.keys():
                process_form(request.args['table'], data['form_data'], action)

            # Generate new form
            web, data = build_form(request.args['table'], request, deform_template_path, step=step, force_get=True,
                                   data=data['form_data'])
        else:
            title = get_title_from_step(step, {k: request.form.get(k, '') for k in ['step', 'action', 'nb_step', 'index']})
            custom_template = Template(render_template('form.html', form=Markup(boostrap.get_form_layout(title))))

        # Generate table
        table = {'table': ''}

        # Gather context and render template
        context = {k: Markup(v) for k, v in web.items() + table.items()}
        html = render_template(custom_template, **context)

    return html


@app.route('/explore', methods=['GET', 'POST'])
def explore():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template("explore.html")