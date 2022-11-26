import io
import json
import os

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from socketio import ASGIApp, AsyncServer
from starlette.middleware.cors import CORSMiddleware

from .config import settings
from .routes import main_router
from .services.connection_manager import ConnectionManager


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("VERSION")
    """
    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


description = """
ContentAPI helps you do awesome stuff. 🚀
"""

version = read("VERSION")

sio = AsyncServer(async_mode="asgi", cors_allowed_origins="*")
sio.register_namespace(ConnectionManager("/"))
socket_app = ASGIApp(sio)
app = FastAPI(title="ContentAPI", description=description, version=version)

env = settings.as_dict(internal=True).get("ENV", "development")
print(
    f"\033[32mINFO\033[0m:\t  ContentAPI@{version} has just started working ({env})"  # noqa: E501
)

if settings.server:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.server.get(
            "cors_origins", ["*"]
        ),  # just to allow any origin
        allow_credentials=settings.get("server.cors_allow_credentials", True),
        allow_methods=settings.get("server.cors_allow_methods", ["*"]),
        allow_headers=settings.get("server.cors_allow_headers", ["*"]),
    )

# Main router for the API.
app.include_router(main_router)

# add websocket
app.mount("/", socket_app)

with open("openapi.json", "w") as f:
    json.dump(
        get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        ),
        f,
    )
