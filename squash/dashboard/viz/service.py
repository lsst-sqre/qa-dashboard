import os
import json
import requests
from datetime import datetime

SQUASH_API_URL = os.environ.get('SQUASH_API_URL',
                                'http://localhost:8000/dashboard/api')


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
    api = requests.get(SQUASH_API_URL).json()
    datasets = requests.get(api['datasets']).json()

    default = None
    if datasets:
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

    api = requests.get(SQUASH_API_URL).json()
    r = requests.get(api['metrics']).json()

    metrics = [m['metric'] for m in r['results']]

    default = None
    if len(metrics)>0:
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

    api = requests.get(SQUASH_API_URL).json()
    r = requests.get(api['metrics']).json()

    unit = str()
    description = str()
    specs = []

    for m in r['results']:
        if m['metric'] == name:
            unit = m['unit']
            description = m['description']
            specs = eval(m['specs'])
            break

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
    api = requests.get(SQUASH_API_URL).json()

    # http://localhost:8000/dashboard/api/measurements/?job__ci_dataset=cfht&metric=AM1

    r = requests.get(api['measurements'],
                     params={'job__ci_dataset': selected_dataset,
                             'metric': selected_metric}).json()

    # results are paginated, walk through each page

    # TODO: figure out how to retrieve the number of pages in DRF
    count = r['count']
    page_size = len(r['results'])

    measurements = []
    if page_size > 0:
        # ceiling integer
        num_pages = int(count/page_size) + (count % page_size > 0)

        initial_page = get_initial_page(page_size, num_pages, window)

        for page in range(initial_page, num_pages + 1):
            measurements.extend(requests.get(
                api['measurements'],
                params={'job__ci_dataset': selected_dataset,
                        'metric': selected_metric,
                        'page': page}).json()['results'])

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


def to_str(value_or_list):
    """Convert unicode or list to str
    """

    if isinstance(value_or_list, list):
        value = value_or_list[0]
    else:
        value = value_or_list

    if isinstance(value, bytes):
        _str = value.decode('utf-8')
    else:
        _str = str(value)

    return _str


def get_args(doc, defaults):
    """Return URL args from a bokeh document, if args are not present
    return default values
    """

    tmp = doc().session_context.request.arguments
    args = {}

    for key, value in defaults:
        if key in tmp:
            args[key] = to_str(tmp[key])
        else:
            args[key] = to_str(value)

    return args
