import os
import sys
import pytest
import asyncio
import uvicorn
import socketio
import requests
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typer.testing import CliRunner
from requests_mock.mocker import Mocker
from typing import List, Optional

# This next line ensures tests uses its own settings environment
os.environ["FORCE_ENV_FOR_DYNACONF"] = "testing"  # noqa

from api import sio, app, settings  # noqa
from api.cli import cli  # noqa
from api.utils.points import points_function
from api.utils.parse_url import parse_url

# deactivate monitoring task in python-socketio to avoid errores during shutdown
sio.eio.start_service_task = False

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


@pytest.fixture(scope="function", name="points_function")
def _points_function():
    return points_function


@pytest.fixture(scope="function", name="parse_url")
def _parse_url():
    return parse_url


class MockRequests:
    """Mock http requests"""

    def __init__(self, requests_mock: Mocker) -> None:
        self.req = requests_mock
        self.req.real_http = True

    def get(self, url: str, json: dict, status_code: int):
        self.req.get(url, json=json, status_code=status_code)


@pytest.fixture(scope="function")
def mock_request(requests_mock: Mocker):
    return MockRequests(requests_mock)


class UvicornTestServer(uvicorn.Server):
    """Uvicorn test server"""

    def __init__(
        self, app: FastAPI = app, host: str = "127.0.0.1", port: int = 8080
    ):
        """Create a Uvicorn test server

        Args:
            app (FastAPI, optional): the FastAPI app. Defaults to app.
            host (str, optional): the host ip. Defaults to '127.0.0.1'.
            port (int, optional): the port. Defaults to 8080.
        """
        self._startup_done = asyncio.Event()
        super().__init__(config=uvicorn.Config(app, host=host, port=port))

    async def startup(self, sockets: Optional[List] = None) -> None:
        """Override uvicorn startup"""
        await super().startup(sockets=sockets)
        self.config.setup_event_loop()
        self._startup_done.set()

    async def up(self) -> None:
        """Start up server asynchronously"""
        self._serve_task = asyncio.create_task(self.serve())
        await self._startup_done.wait()

    async def down(self) -> None:
        """Shut down server asynchronously"""
        self.should_exit = True
        await self._serve_task


@pytest.fixture(scope="function")
def server():
    return UvicornTestServer()
