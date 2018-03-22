from facileapp import app
from flask import render_template
from flask import templating
from flask import Markup, session, redirect, url_for, request, config
import pandas as pd
import numpy as np

from jinja2 import Template
from bokeh import plotting, resources
from bokeh.embed import file_html
import dominate
from dominate.tags import *

from facile.forms import login_form, realytics
from facile.graphs import bokeh_plots
from facileapp.models import Users

from settings import deform_template_path
import deform

@app.route('/')
def home():

    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':

        # The doc is composed of a form and of a bokeh plot
        html_content = dominate.document()
        with html_content:
            with div(cls='row'):
                with div(cls='col-sm-12'):
                    p('{{ form_login }}')

        html_template = Template(render_template("login.html",
                                                 custom_html=Markup(html_content.body.children[0].render())))

        # Create form
        schema = login_form.LoginSchema()
        process_btn = deform.form.Button(name='process', title="Process")
        form = deform.form.Form(schema, buttons=(process_btn,))
        html_string = render_template(html_template, form_login=Markup(form.render()))

        return html_string

    else:
        try:
            user = Users.from_login(request.form['username'], request.form['password'])
        except ValueError:
            return redirect(url_for('login'))

        session['username'] = user.username
        session['rights'] = user.rights

        return redirect(url_for('home'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():

   # remove the username from the session if it is there
   session.pop('username', None)
   session.pop('rights', None)

   return redirect(url_for('home'))


@app.route('/series', methods=['GET', 'POST'])
def series():
    if 'username' not in session:
        return redirect(url_for('login'))

    # The doc is composed of a form and of a bokeh plot
    html_content = dominate.document()
    with html_content:
        with div(cls='row '):
            with div(cls='col-sm-3'):
                p('{{form_css}} {{ form_js }} {{ form }}')
            with div(cls='col-sm-9'):
                p('{{ plot_div }} {{ bokeh_js }} {{ bokeh_css }} {{ plot_script }}')

    html_template = Template(render_template("series.html", custom_html=Markup(html_content.body.children[0].render())))

    # Create form
    web, data = realytics.SeriesForm(request, deform_template_path).process_form()

    # Generate plot if form correctly submitted
    if request.method == 'POST' and data.pop('success'):

        form_data = data.pop('form_data')
        fig = bokeh_plots.plot_series(generate_fake_plot(form_data['dateStart'], form_data['dateEnd']))

        html_string = file_html(fig, resources=resources.CDN, template=html_template,
                                template_variables={k: Markup(v) for k, v in web.items()})

        return html_string
    else:

        html_string = render_template(html_template, plot_div=Markup('NO DATA TO PLOT'),
                                      **{k: Markup(v) for k, v in web.items()})

    return templating.render_template_string(html_string)


def generate_fake_plot(date_start, date_end):
    # Generate fake data for bokeh plot
    di = pd.DatetimeIndex(start=pd.Timestamp('2017-01-01 00:00:00'), end=pd.Timestamp('2017-01-01 00:02:00'),
                          freq='t')

    # Create fake dataframe
    df = pd.DataFrame(np.random.randn(len(di), 2), index=di, columns=['series_{}'.format(i) for i in range(2)])

    return df
