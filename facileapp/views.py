from facileapp import app
from flask import render_template
from flask import templating
from flask import request, Markup, session, redirect, url_for
import pandas as pd
import numpy as np
import itertools

from jinja2 import Template
from bokeh import plotting, resources
from bokeh.embed import file_html
import dominate
from dominate.tags import *
import deform
import colander

from facile.forms import login_form, realytics

from facileapp.models import Users

@app.route('/')
def home():

    if 'username' not in session:
        return redirect(url_for('login'))

    print session['username']
    print session['rights']

    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':

        # The doc is composed of a form and of a bokeh plot
        html_content = dominate.document()
        with html_content:
            with div(cls='row '):
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
            print 'mother fucker'
            return redirect(url_for('login'))

        session['username'] = user.username
        session['rights'] = user.rights

        return redirect(url_for('home'))


def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   session.pop('rights', None)

   return redirect(url_for('index'))


@app.route('/series', methods=['GET', 'POST'])
def series():
    if 'username' not in session:
        return redirect(url_for('login'))

    # The doc is composed of a form and of a bokeh plot
    html_content = dominate.document()
    with html_content:
        with div(cls='row '):
            with div(cls='col-sm-3'):
                p('{{ form }}')
            with div(cls='col-sm-9'):
                p('{{ plot_div }} {{bokeh_js}} {{bokeh_css}} {{plot_script}}')

    html_template = Template(render_template("series.html", custom_html=Markup(html_content.body.children[0].render())))

    # Create form
    schema = realytics.SeriesSchema()
    process_btn = deform.form.Button(name='process', title="Process")
    form = deform.form.Form(schema, buttons=(process_btn,))

    # Generate form with dropdown list and tag
    if request.method == 'POST':

        # Generate fake data for bokeh plot
        di = pd.DatetimeIndex(start=pd.Timestamp(request.form['dateStart']),
                              end=pd.Timestamp(request.form['dateEnd']),
                              freq='t')
        x_axis_type = 'datetime'
        # Create fake dataframe
        df = pd.DataFrame(np.random.randn(len(di), 2), index=di, columns=['series_{}'.format(i) for i in range(2)])

        # Create html content
        colors = itertools.cycle(['#1144cc', '#11cc44', '#cc4411', '#11ccff', '#ff11cc', '#ffcc11', '#111111'])
        fig = plotting.figure(width=1066, height=600, x_axis_type=x_axis_type, title='test')
        for c, s in df.iteritems():
            fig.line(df.index, s.values, line_width=1.4, color=colors.next(), legend=c)

        html_string = file_html(fig, resources=resources.CDN, template=html_template,
                                template_variables={'form': Markup(form.render())})
        return html_string
    else:
        #session['custom_session'] = 'sale_pute'
        html_string = render_template(html_template, plot_div=Markup('NO DATA TO PLOT'), form=Markup(form.render()))

    return templating.render_template_string(html_string)