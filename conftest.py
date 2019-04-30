import pytest
import requests
import json

from tests.settings import USERNAME, PASSWORD, ARX_ENDPOINT, \
    WIREMOCK_SERVER, WIREMOCK_START_RECORDING, WIREMOCK_STOP_RECORDING
from steelscript.common.service import UserAuth
from steelscript.appresponse.core.appresponse import AppResponse


@pytest.fixture(scope="module")
def user_auth():
    return UserAuth(USERNAME, PASSWORD)


@pytest.fixture()
def app(user_auth):
    return AppResponse(WIREMOCK_SERVER, auth=user_auth)


def pytest_configure(config):
    start_api = "%s/%s" % (WIREMOCK_SERVER, WIREMOCK_START_RECORDING)
    req = requests.post(start_api, data=json.dumps({'targetBaseUrl': ARX_ENDPOINT}))
    print("Started WireMock Recording for ARX. Response from server: %s" % req.content)


def pytest_unconfigure(config):
    stop_api = "%s/%s" % (WIREMOCK_SERVER, WIREMOCK_STOP_RECORDING)
    req = requests.post(stop_api, data=json.dumps({'targetBaseUrl': ARX_ENDPOINT}))
    print("Stopped WireMock Recording for ARX. Response from server: %s" % req.content)
