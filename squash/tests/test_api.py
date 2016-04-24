"""Tests for the dashboard API"""
import os
import requests

""" Assume username and password for testing """
TEST_USER = os.environ.get("USER")
TEST_PASSWD = os.environ.get("USER")

API_URL = "http://localhost:8000/api"


def test_api_root():
    """Access to the api root"""
    r = requests.get(API_URL)
    assert r.status_code == requests.codes.ok


def test_auth():
    """Attempt to access a resource without authentication"""

    r = requests.get(API_URL)
    api = r.json()

    for endpoint in api:
        r = requests.get(api[endpoint])
        assert r.status_code == 401


def test_post_metric():

    metric = {
                "metric": "test1",
                "description": "Test metric insertion",
                "units": "test",
                "minimum": "8",
                "design": "5",
                "stretch": "3",
                "user": "5"
             }

    r = requests.get(API_URL)
    api = r.json()

    r = requests.post(api['metric'], data=metric,
                      auth=(TEST_USER, TEST_PASSWD))
    assert r.status_code == 201

    r.close()


def test_post_job():

    r = requests.get(API_URL)
    api = r.json()

    job = {
            "name": "ci_cfht",
            "build": "1",
            "url": "https://ci.lsst.codes/job/ci_cfht/1/",
            "measurements": [{"metric": "test1", "value": 3.0}],
            "status": 0
          }

    r = requests.post(api['job'], data=job,
                      auth=(TEST_USER, TEST_PASSWD))

    assert r.status_code == 201
