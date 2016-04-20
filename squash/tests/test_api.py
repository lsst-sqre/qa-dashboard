"""Tests for the dashboard API"""
import os
import requests

""" Assume username and password for testing """
TEST_USER = os.environ.get("USER")
TEST_USER_PASSWD = os.environ.get("USER")

API_URL = "http://localhost:8000/api"

def test_api_root():
    """Access to the api root"""
    r = requests.get(API_URL)
    assert r.status_code == 200

def test_auth():
    """Attempt to access a resource without authentication"""

    r = requests.get(API_URL)
    api = r.json()

    for endpoint in api:
        r = requests.get(api[endpoint])
        assert r.status_code == 401

def test_post():

    metric ={
                "name": "PA1",
                "description": "Photometric Repeatability",
                "units": "millimag",
                "minimum": "8",
                "design": "5",
                "stretch": "3",
                "user": "5"
            }
    r = requests.get(API_URL)
    api = r.json()

    r = requests.get(api['metric'], auth=(TEST_USER, TEST_USER_PASSWD))
    assert r.status_code == 200

    r = requests.post(api['metric'], data=metric, auth=(TEST_USER, TEST_USER_PASSWD))
    assert r.status_code == 201