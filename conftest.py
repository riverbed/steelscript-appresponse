import pytest
from tests.settings import USERNAME, PASSWORD, ARX_ENDPOINT
from steelscript.common.service import UserAuth
from steelscript.appresponse.core.appresponse import AppResponse


@pytest.fixture(scope="module")
def user_auth():
    return UserAuth(USERNAME, PASSWORD)


@pytest.fixture()
def app(user_auth):
    return AppResponse(ARX_ENDPOINT, auth=user_auth)
