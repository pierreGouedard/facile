# Global import
from facileapp import app
from flask import render_template
from flask import Markup, session, redirect, url_for, request
import pandas as pd
import numpy as np
from jinja2 import Template
from bokeh import resources
from bokeh.embed import file_html

# Local import
from facile.forms import login_form, realytics, other_widget
from facile.graphs import bokeh_plots
from facile.layout import boostrap
from facile.tables import table

from settings import deform_template_path

l_cats = ['web,desktop',
          'web,mobile',
          'web,tablet',
          'web,smarttv',
          'mobileapp,mobile',
          'mobileappinstall,mobile']


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

    return render_template("form.html")


@app.route('/explore', methods=['GET', 'POST'])
def explore():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template("explore.html")


@app.route('/test-other', methods=['GET', 'POST'])
def test():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Create page global layout
    custom_template = Template(render_template('test-other.html', custom_html=Markup(boostrap.get_other_layout())))

    # process request
    web, data = other_widget.OtherForm(request, deform_template_path).process_form()

    html = render_template(custom_template, **{k: Markup(v) for k, v in web.items()})

    return html


####################################### REALYTICS #####################################################


@app.route('/series', methods=['GET', 'POST'])
def series():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Create page global layout
    custom_template = Template(render_template('series.html', custom_html=Markup(boostrap.get_series_layout())))

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
    custom_template = Template(render_template('baseline.html', custom_html=Markup(boostrap.get_baseline_layout())))

    # Create form
    web, data = realytics.BaselineForm(request, deform_template_path, l_cats, []).process_form()

    # Generate plot if form correctly submitted
    if request.method == 'POST' and data.pop('success'):

        form_data = data.pop('form_data')
        l_dates = [form_data['dateStart'], form_data['dateEnd']]

        # Generate fake spots
        s_spots = generate_fake_spot_id(l_dates[0], l_dates[1])

        if len(form_data['spotid']) > 0:
            # Get spot ids
            s_spots = s_spots.loc[set(form_data['spotid']).intersection(set(s_spots.index))]
            l_spotids = map(str, s_spots.index)

        else:
            # Get spots ids
            l_spotids = map(str, s_spots.index)
            s_spots = pd.Series()

        # Generate new form (with spotids selecction
        web, data = realytics.BaselineForm(request, deform_template_path, l_cats, l_spotids)\
            .process_form()

        fig = bokeh_plots.plot_series_and_event(generate_fake_plot(form_data['dateStart'], form_data['dateEnd']),
                                                s_spots)

        html = file_html(fig, resources=resources.CDN, template=custom_template,
                         template_variables={k: Markup(v) for k, v in web.items()})
    else:

        html = render_template(custom_template, plot_div=Markup('NO DATA TO PLOT'),
                               **{k: Markup(v) for k, v in web.items()})

    return html


@app.route('/impact', methods=['GET', 'POST'])
def impact():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Create page global layout
    custom_template = Template(render_template('impact.html', custom_html=Markup(boostrap.get_impact_layout())))

    # Create form
    web, data = realytics.ImpactForm(request, deform_template_path, l_cats, []).process_form()

    # Generate plot if form correctly submitted
    if request.method == 'POST' and data.pop('success'):

        form_data = data.pop('form_data')
        l_dates = [form_data['dateStart'], form_data['dateEnd']]

        # Generate fake spots
        s_spots = generate_fake_spot_id(l_dates[0], l_dates[1])

        if len(form_data['spotid']) > 0:
            # Get spot ids
            s_spots = s_spots.loc[set(form_data['spotid']).intersection(set(s_spots.index))]
            l_spotids = map(str, s_spots.index)

        else:
            # Get spots ids
            l_spotids = map(str, s_spots.index)
            s_spots = pd.Series()

        # Render table
        df_table, (is_fh, is_fi), d_sizes = generate_fake_metrics(l_spotids)
        tbl = table.Table(df_table.columns, fixed_header=is_fh, fixed_index=is_fi, index_name=df_table.index.name,
                          d_sizes=d_sizes)
        html_table = tbl.render_table_from_pandas(df_table)

        # Generate new form (with spotids selecction
        web, data = realytics.BaselineForm(request, deform_template_path, l_cats, l_spotids) \
            .process_form()

        fig = bokeh_plots.plot_series_and_event(generate_fake_plot(form_data['dateStart'], form_data['dateEnd']),
                                                s_spots)

        context = dict([(k, Markup(v)) for k, v in web.items()] + [('table', Markup(html_table))])
        html = file_html(fig, resources=resources.CDN, template=custom_template, template_variables=context)

    else:

        # Render table
        df_table, (is_fh, is_fi), d_sizes = generate_fake_metrics()
        tbl = table.Table(df_table.columns, fixed_header=is_fh, fixed_index=is_fi, index_name=df_table.index.name,
                          d_sizes=d_sizes)
        html_table = tbl.render_table_from_pandas(df_table)
        print type(html_table)

        html = render_template(custom_template, plot_div=Markup('NO DATA TO PLOT'), table=Markup(html_table),
                               **{k: Markup(v) for k, v in web.items()})

    return html


def generate_fake_plot(date_start, date_end):
    # Generate fake data for bokeh plot
    di = pd.DatetimeIndex(start=date_start, end=date_end, freq='t')

    # Create fake dataframe
    df = pd.DataFrame(np.random.randn(len(di), 2), index=di, columns=['series_{}'.format(i) for i in range(2)])

    return df


def generate_fake_spot_id(start, end):
    np.random.seed(1001)

    n = int((end - start).total_seconds() / 600)

    s_spots = pd.Series(name='spotid')

    for d in np.random.randint(0, high=n, size=int(0.6 * n)):
        spotid = np.random.randint(10000, high=99999)
        s_spots.loc[spotid] = start + pd.Timedelta(minutes=d * 10)

    return s_spots


def generate_fake_metrics(spotids=None):

    # List of metrics name
    l_metrics = ['R2 norm', 'Signal last minute', 'Total diff', 'Significance coefs', 'Significance model']

    if spotids is not None:
        # generate fake table of metrics for each spots on the specific traffic cat
        df_metrics = pd.DataFrame(np.random.randn(len(spotids), len(l_metrics)), index=spotids, columns=l_metrics)
        df_metrics = df_metrics.rename_axis('Spot ID')
        d_sizes = {c: '200px' for c in l_metrics}

        return df_metrics, (True, False), d_sizes
    else:
        l_agg = ['Last week', 'Last month', 'Last year', 'All time']
        l_cols = sum([['{} - {}'.format(cat, m) for m in l_metrics] for cat in l_cats], [])

        # generate fake table of metrics for the last 5 campaigns of the client
        df_metrics = pd.DataFrame(np.random.randn(len(l_agg), len(l_cols)), index=l_agg, columns=l_cols)
        df_metrics = df_metrics.rename_axis('Aggregation')
        d_sizes = {c: '500px' for c in l_cols}

        return df_metrics, (False, True), d_sizes


