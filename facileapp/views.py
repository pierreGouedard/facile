from facileapp import app
from flask import render_template
from flask import templating
from flask import Markup, session, redirect, url_for, request
import pandas as pd
import numpy as np

from jinja2 import Template
from bokeh import plotting, resources
from bokeh.embed import file_html
import dominate
from dominate.tags import *

from facile.forms import login_form, realytics
from facile.graphs import bokeh_plots
from facile.layout import layout
from settings import deform_template_path

l_cats = ['accessMethod=web,deviceType=0,eventName=ry_c_ry_session_server',
          'accessMethod=web,deviceType=1,eventName=ry_c_ry_session_server',
          'accessMethod=web,deviceType=2,eventName=ry_c_ry_session_server',
          'accessMethod=web,deviceType=3,eventName=ry_c_ry_session_server',
          'accessMethod=mobileapp,deviceType=1,eventName=ry_c_ry_session_server',
          'accessMethod=mobileappinstall,deviceType=1,eventName=ry_c_ry_session_server'
          ]


@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Create page global layout
    custom_template = Template(render_template('login.html', custom_html=Markup(layout.get_login_layout())))

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


@app.route('/series', methods=['GET', 'POST'])
def series():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Create page global layout
    custom_template = Template(render_template('series.html', custom_html=Markup(layout.get_series_layout())))

    # Create form
    web, data = realytics.SeriesForm(request, deform_template_path, l_cats).process_form()

    # Generate plot if form correctly submitted
    if request.method == 'POST' and data.pop('success'):

        form_data = data.pop('form_data')
        fig = bokeh_plots.plot_series(generate_fake_plot(form_data['dateStart'], form_data['dateEnd']))

        html = file_html(fig, resources=resources.CDN, template=custom_template,
                         template_variables={k: Markup(v) for k, v in web.items()})

    else:
        html = render_template(custom_template, plot_div=Markup('NO DATA TO PLOT'),
                               **{k: Markup(v) for k, v in web.items()})

    return html


@app.route('/baseline', methods=['GET', 'POST'])
def baseline():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Create page global layout
    custom_template = Template(render_template('baseline.html', custom_html=Markup(layout.get_baseline_layout())))

    # Create form
    web, data = realytics.BaselineForm(request, deform_template_path, l_cats).process_form()

    # Generate plot if form correctly submitted
    if request.method == 'POST' and data.pop('success'):

        form_data = data.pop('form_data')
        fig = bokeh_plots.plot_series(generate_fake_plot(form_data['dateStart'], form_data['dateEnd']))

        html = file_html(fig, resources=resources.CDN, template=custom_template,
                         template_variables={k: Markup(v) for k, v in web.items()})
        return html

    else:
        html = render_template(custom_template, plot_div=Markup('NO DATA TO PLOT'),
                               **{k: Markup(v) for k, v in web.items()})

        return templating.render_template_string(html)


def generate_fake_plot(date_start, date_end):
    # Generate fake data for bokeh plot
    di = pd.DatetimeIndex(start=date_start, end=date_end, freq='t')

    # Create fake dataframe
    df = pd.DataFrame(np.random.randn(len(di), 2), index=di, columns=['series_{}'.format(i) for i in range(2)])

    return df
