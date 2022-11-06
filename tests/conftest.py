import os
import sys
import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner
from requests_mock.mocker import Mocker
import requests

# This next line ensures tests uses its own settings environment
os.environ["FORCE_ENV_FOR_DYNACONF"] = "testing"  # noqa

from api import app, settings  # noqa
from api.cli import cli  # noqa

# each test runs on cwd to its temp dir
@pytest.fixture(autouse=True)
def go_to_tmpdir(request):
    # Get the fixture dynamically by its name.
    tmpdir = request.getfixturevalue("tmpdir")
    # ensure local test created packages can be imported
    sys.path.insert(0, str(tmpdir))
    # Chdir only for the duration of the test.
    with tmpdir.as_cwd():
        yield


@pytest.fixture(scope="function", name="app")
def _app():
    return app


@pytest.fixture(scope="function", name="cli")
def _cli():
    return cli


@pytest.fixture(scope="function", name="settings")
def _settings():
    return settings


@pytest.fixture(scope="function")
def api_client():
    return TestClient(app)


@pytest.fixture(scope="function")
def cli_client():
    return CliRunner()


@pytest.fixture(scope="function", name="requests")
def _requests():
    return requests


class MockRequests:
    def __init__(self, requests_mock: Mocker) -> None:
        self.req = requests_mock
        self.req.real_http = True

    def get(self, url: str, json: dict, status_code: int):
        self.req.get(url, json=json, status_code=status_code)


@pytest.fixture(scope="function")
def mock_request(requests_mock: Mocker):
    return MockRequests(requests_mock)
