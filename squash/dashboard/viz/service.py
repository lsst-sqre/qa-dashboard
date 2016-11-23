import os
import requests
from datetime import datetime

SQUASH_API_URL = os.environ.get('SQUASH_API_URL',
                                'http://localhost:8000/dashboard/api')


def get_datasets():
    """Get a list of datasets from the API
    Returns
    -------
    datasets : list
        list of datasets obtained
    default : str
        the default dataset is the first element
        of the list if it exists otherwise it
        assumes None
    """
    api = requests.get(SQUASH_API_URL).json()
    datasets = requests.get(api['datasets']).json()

    default = None
    if datasets:
        default = datasets[0]

    return {'datasets': datasets, 'default': default}


def get_metrics():
    """Get a list of metrics from the API
    Returns
    -------
    metrics : list
        list of metrics obtained
    minimnum : list
        list of dicts where the key is the metric name
        and the value is its minimum specification
    design : list
        list of dicts, where the key is the metric name and the
        value is its design specification
    stretch : list
        list of dicts, where the key is the metric name and the
        value is its stretch goal
    units : list
        list of ditcs, where the key is the metric name and the
        value is its unit
    default : str
        the default metric is the first element of the metrics
        list if it exists otherwhise it assumes None
    """
    api = requests.get(SQUASH_API_URL).json()
    r = requests.get(api['metrics']).json()

    metrics = [x['metric'] for x in r['results']]

    minimum = {}
    design = {}
    stretch = {}
    units = {}
    desc = {}
    default = None
    if metrics:
        minimum = dict(zip(metrics, [x['minimum'] for x in r['results']]))
        design = dict(zip(metrics, [x['design'] for x in r['results']]))
        stretch = dict(zip(metrics, [x['stretch'] for x in r['results']]))
        units = dict(zip(metrics, [x['units'] for x in r['results']]))
        desc = dict(zip(metrics, [x['description'] for x in r['results']]))
        default = metrics[0]

    return {'metrics': metrics, 'minimum': minimum, 'design': design,
            'stretch': stretch, 'units': units, 'description': desc,
            'default': default}


def get_meas_by_dataset_and_metric(selected_dataset, selected_metric):
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
        for page in range(1, num_pages + 1):
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
