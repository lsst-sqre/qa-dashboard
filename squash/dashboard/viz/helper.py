import os
import pandas as pd
import requests
from datetime import datetime
from furl import furl

from bokeh.models import Span, Label


SQUASH_API_URL = os.environ.get('SQUASH_API_URL',
                                'http://localhost:8000/dashboard/api/')


def get_endpoint_urls(api_url=SQUASH_API_URL):
    """Lookup endpoint URL(s).
    """

    r = requests.get(api_url)
    r.raise_for_status()

    return r.json()


def get_endpoint(name):
    api = get_endpoint_urls()

    r = requests.get(api[name])
    r.raise_for_status()

    return r.json()


def get_datasets():
    """Get a list of datasets from the API
    Returns
    -------
    datasets : list
        list of dataset names
    default : str
        the default dataset is the first available,
        None otherwise
    """
    datasets = get_endpoint('datasets')

    default = None
    if datasets:
        if 'cfht' in datasets:
            default = 'cfht'
        else:
            default = datasets[0]

    return {'datasets': datasets, 'default': default}


def get_metrics():
    """Get the list of metrics
    Returns
    -------
    metrics : list
        list of metric names
    default : str
        the default metric is the firstavailable,
        None otherwise
    """

    r = get_endpoint('metrics')

    metrics = [m['metric'] for m in r['results']]

    default = None
    if len(metrics) > 0:
        if 'AM1' in metrics:
            default = 'AM1'
        else:
            default = metrics[0]

    return {'metrics': metrics, 'default': default}


def get_value(specs, name):
    """ Unpack metric specification
    Parameters
    ----------
    specs: dict
        a dict with keys value and name
    name: str
        the spec name
    Return
    ------
    value: float or None
        value of the spec if exists, None otherwise
    """

    value = None

    for s in specs:
        if s['name'] == name:
            value = s['value']
            break

    return value


def get_specs(name):
    """Get metric specifications from its name
    Parameters
    ----------
    name: str
        a valid metric name
    Returns
    -------
    unit: str
        metric unit
    description:
        metric description
    minimum: float
        metric minimum specification
    design: float
        metric design specification
    stretch: float
        metric stretch goal
    """

    r = get_endpoint('metrics')

    unit = str()
    description = str()
    specs = []
    minimum = None
    design = None
    stretch = None

    for m in r['results']:
        if m['metric'] == name:
            unit = m['unit']
            description = m['description']
            specs = eval(str(m['specs']))
            break

    if specs:
        minimum = get_value(specs, 'minimum')
        design = get_value(specs, 'design')
        stretch = get_value(specs, 'stretch')

    return {'unit': unit, 'description': description,
            'minimum': minimum, 'design': design, 'stretch': stretch}


def get_initial_page(page_size, num_pages, window):

    # time window in hours corresponding to each page
    # assuming measurements are done every 8 hours in CI

    page_window = page_size * 8

    if window == 'weeks':
        initial_page = num_pages - int((24*7)/page_window)
    elif window == 'months':
        # maximum window of 3 months
        initial_page = num_pages - int((24*30*3)/page_window)
    elif window == 'years':
        # maximum window of 1 year
        initial_page = num_pages - int((24*365)/page_window)
    else:
        # everything
        initial_page = 1

    # Make sure we have enough pages for the input time window
    if initial_page < 1:
        initial_page = 1

    return initial_page


def get_meas_by_dataset_and_metric(selected_dataset, selected_metric, window):
    """ Get measurements for a given dataset and metric from the measurements
    api endpoint

    Parameters
    ----------
    selected_dataset : str
        the current selected dataset
    selected_metric : str
        the current selected metric

    Returns
    -------
    ci_id : list
        list of job ids from the CI system
    dates : list
        list of datetimes for each job  measurement
    measurements : list
        flat list of dicts where the key is the metric and the value
        is its measurement
    ci_url : list
        list of URLs for the jobs in the CI system
    """
    api = get_endpoint_urls()

    # http://localhost:8000/dashboard/api/measurements/?job__ci_dataset=cfht&metric=AM1

    r = requests.get(api['measurements'],
                     params={'job__ci_dataset': selected_dataset,
                             'metric': selected_metric})
    r.raise_for_status()

    results = r.json()

    # results are paginated, walk through each page

    # TODO: figure out how to retrieve the number of pages in DRF
    count = results['count']
    page_size = len(results['results'])

    measurements = []
    if page_size > 0:
        # ceiling integer
        num_pages = int(count/page_size) + (count % page_size > 0)

        initial_page = get_initial_page(page_size, num_pages, window)

        for page in range(initial_page, num_pages + 1):
            r = requests.get(
                api['measurements'],
                params={'job__ci_dataset': selected_dataset,
                        'metric': selected_metric,
                        'page': page})
            r.raise_for_status()
            measurements.extend(r.json()['results'])

    ci_ids = [int(m['ci_id']) for m in measurements]

    # 2016-08-10T05:22:37.700146Z
    # after DM-7517 jobs return is sorted by date and the same is done for
    # the measurements
    dates = [datetime.strptime(m['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
             for m in measurements]

    values = [m['value'] for m in measurements]

    ci_urls = [m['ci_url'] for m in measurements]

    packages = [m['changed_packages'] for m in measurements]

    # list of package names, name is the first element in the tuple
    names = []
    for i, sublist in enumerate(packages):
        names.append([])
        for package in sublist:
            names[i].append(package[0])

    # list of git urls, git package commit sha and base url are the second and
    # third elements in the tuple
    git_urls = []
    for i, sublist in enumerate(packages):
        git_urls.append([])
        for package in sublist:
            git_urls[i].append("{}/commit/{}".format(package[2].strip('.git'),
                                                     package[1]))

    return {'ci_ids': ci_ids, 'dates': dates, 'values': values,
            'ci_urls': ci_urls, 'names': names, 'git_urls': git_urls}


def get_url_args(doc, defaults):
    """Return URL args from a django request to the bokeh app, the
    args are in the Referer URL in the HTTPServerRequest headers.

    Default args are defined in each bokeh app and are used if
    not present in the Referer URL

    """
    # e.g. http://localhost:800/regression?window=weeks&
    # job__ci_dataset=cfht&metric=PA1

    args = defaults
    s = doc().session_context
    if s:
        if s.request:
            tmp = furl(s.request.headers['Referer']).args
            for key in tmp:
                if key in args:
                    args[key] = tmp[key]
    return args


def get_app_data(bokeh_app, metric=None, ci_id=None, ci_dataset=None):
    """Returns a panda dataframe with data consumed by the bokeh apps"""

    api = get_endpoint_urls()

    # e.g. http://localhost:8000/AMx?ci_id=1&job__ci_dataset=cfht&metric=AM1

    r = requests.get(api[bokeh_app],
                     params={'metric': metric,
                             'ci_id': ci_id,
                             'ci_dataset': ci_dataset})
    r.raise_for_status()
    results = r.json()

    data = pd.DataFrame.from_dict(results, orient='index').transpose()

    return data


def add_span_annotation(plot, value, text, color):
    """ Add span annotation, used for metric specification
    thresholds.
    """

    span = Span(location=value, dimension='width',
                line_color=color, line_dash='dotted',
                line_width=2)

    label = Label(x=plot.plot_width-300, y=value+0.5, x_units='screen',
                  y_units='data', text=text, text_color=color,
                  text_font_size='11pt', text_font_style='normal',
                  render_mode='canvas')

    plot.add_layout(span)
    plot.add_layout(label)
