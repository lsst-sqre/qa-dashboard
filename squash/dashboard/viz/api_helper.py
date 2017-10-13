import os
import pandas as pd
import requests
from datetime import datetime
from furl import furl

SQUASH_API_URL = os.environ.get('SQUASH_API_URL',
                                'http://localhost:8000/dashboard/api/')


def get_endpoint_urls():
    """
    Lookup API endpoint URLs
    """

    r = requests.get(SQUASH_API_URL)
    r.raise_for_status()

    return r.json()


def get_data(endpoint, params=None):
    """Return data as a dict from
    an API endpoint """

    api = get_endpoint_urls()

    # e.g. http://localhost:8000/AMx?ci_id=1&ci_dataset=cfht&metric=AM1
    r = requests.get(api[endpoint],
                     params=params)
    r.raise_for_status()

    return r.json()


def get_data_as_pandas_df(endpoint, params=None):
    """
    Return data as a pandas dataframe from
    an API endpoint
    """

    result = get_data(endpoint, params)

    data = pd.DataFrame.from_dict(result, orient='index').transpose()

    return data


def get_datasets(default=None):
    """Get a list of datasets from the API
    and a default value
    Returns
    -------
    datasets : list
        list of dataset names
    default : str
        if a valid default value is provided, overwrite
        the default value obtained from the API
    """

    datasets = get_data('datasets')
    default_dataset = get_data('defaults')['ci_dataset']

    if default:
        if default in datasets:
            default_dataset = default

    return {'datasets': datasets, 'default': default_dataset}


def get_metrics(default=None):
    """Get the list of metrics from the API
    and a default value
    Returns
    -------
    metrics : list
        list of metric names
    default : str
        if a valid default value is provided, overwrite
        the default value returned from the API
    """

    r = get_data('metrics')
    metrics = [m['metric'] for m in r['results']]

    default_metric = get_data('defaults')['metric']

    if default:
        if default in metrics:
            default_metric = default

    return {'metrics': metrics, 'default': default_metric}


def get_value(specs, name):
    """ Helper function to unpack metric specification
    values
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
    """Get metric specifications thresholds
    from its name
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

    r = get_data('metrics')

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


def get_url_args(doc, defaults=None):
    """Return url args recovered from django_full_path cookie in
    the bokeh request header.

    If defaults values are provided, overwrite the default values
    obtained from the API
    """

    args = get_data('defaults')

    # overwrite api default values
    if defaults:
        for key in defaults:
            args[key] = defaults[key]

    r = doc().session_context.request
    if r:
        if 'django_full_path' in r.cookies:
            django_full_path = r.cookies['django_full_path'].value
            tmp = furl(django_full_path).args
            for key in tmp:
                # overwrite default values with those passed
                # as url args, make sure the url arg (key) is valid
                if key in args:
                    args[key] = tmp[key]

            # the bokeh app name is the second segment of the url path
            args['bokeh_app'] = furl(django_full_path).path.segments[1]

    return args


# TODO: these functions are used by the monitor app and need refactoring
def get_last_page(page_size, num_pages, window):

    # Page size in hours assuming CI_TIME_INTERVAL

    CI_TIME_INTERVAL = 8

    page_window = page_size * CI_TIME_INTERVAL

    if window == 'weeks':
        last_page = int((24*7)/page_window)
    elif window == 'months':
        # maximum window of 3 months
        last_page = int((24*30*3)/page_window)
    elif window == 'years':
        # maximum window of 1 year
        last_page = int((24*365)/page_window)
    else:
        # everything
        last_page = num_pages

    # Make sure we have enough pages for the input time window
    if last_page < 1:
        last_page = 1

    return last_page


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

        last_page = get_last_page(page_size, num_pages, window)

        if last_page > num_pages:
            last_page = num_pages

        for page in range(1, last_page + 1):
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
