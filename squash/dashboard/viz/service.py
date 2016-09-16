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
    default = None
    if metrics:
        minimum = dict(zip(metrics, [x['minimum'] for x in r['results']]))
        design = dict(zip(metrics, [x['design'] for x in r['results']]))
        stretch = dict(zip(metrics, [x['stretch'] for x in r['results']]))
        units = dict(zip(metrics, [x['units'] for x in r['results']]))
        default = metrics[0]

    return {'metrics': metrics, 'minimum': minimum, 'design': design,
            'stretch': stretch, 'units': units, 'default': default}


def get_measurements_by_dataset(selected_dataset, n_metrics):
    """ Get measurements for all metrics for the selected data set

    Parameters
    ----------
    selected_dataset : str
        the current selected dataset
    n_metrics : int
        the number of metrics measured for the selected_dataset, it is
        being used to filter failed jobs while we dont have the job
        status avaiable

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

    # e.g. http://localhost:8000/dashboard/api/jobs/?ci_dataset=cfht
    r = requests.get(api['jobs'],
                     params={'ci_dataset': selected_dataset}).json()

    # results are paginated, walk through each page
    # TODO: figure out how to retrieve the number of pages in DRF
    count = r['count']
    page_size = len(r['results'])

    jobs = []
    if page_size > 0:
        # ceiling integer
        num_pages = int(count/page_size) + (count % page_size > 0)
        for page in range(1, num_pages + 1):
            jobs.extend(requests.get(api['jobs'],
                                     params={'ci_dataset': selected_dataset,
                                             'page': page}).json()['results'])

    # filter out failed jobs, i.e jobs that does not have
    # measurements for each metric.
    # TODO: this should be done by looking at the job status
    jobs = [job for job in jobs
            if len(job['measurements']) == n_metrics]

    ci_id = [int(job['ci_id']) for job in jobs]

    # 2016-08-10T05:22:37.700146Z
    # after DM-7517 job api return is sorted by date
    dates = [datetime.strptime(job['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
             for job in jobs]

    # create a flat list with all measurements
    # [ {"metric" : "AM1", "value" : 3.0}, ... ]
    measurements = []

    for job in jobs:
        for sublist in job['measurements']:
            measurements.append(sublist)

    ci_url = [job['ci_url'] for job in jobs]

    return {'ci_id': ci_id, 'dates': dates,
            'measurements': measurements, 'ci_url': ci_url}
