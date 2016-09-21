# Dashboard API tests
# TODO: DM-6990 Improve testing in SQuaSH prototype

import os
import requests

# Username and password for testing, they must be the same used
# to set up the database. See run.sh

TEST_USER = os.environ.get("TEST_USER", None)
TEST_PASSWD = os.environ.get("TEST_PASSWD", None)

# Not necessarily localhost if your test env is deployed somewhere else
TEST_API_URL = os.environ.get("TEST_API_URL",
                              "http://localhost:8000/dashboard/api")


def test_api_root():
    """Access to the api root
    """
    r = requests.get(TEST_API_URL)
    assert r.status_code == requests.codes.ok


def test_auth():
    """API endpoints are read only, so a GET must work
    without authentication
    """
    r = requests.get(TEST_API_URL)
    api = r.json()

    for endpoint in api:
        r = requests.get(api[endpoint])
        assert r.status_code == 200


def test_post_metric():
    """ Test Metric endpoint
    """
    metric = {
                "metric": "test1",
                "description": "Test metric insertion",
                "units": "test",
                "minimum": "8",
                "design": "5",
                "stretch": "3",
                "user": "5"
             }

    r = requests.get(TEST_API_URL)
    api = r.json()

    r = requests.post(api['metrics'], json=metric,
                      auth=(TEST_USER, TEST_PASSWD))
    assert r.status_code == 201

    r.close()
