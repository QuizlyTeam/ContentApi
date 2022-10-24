import io
import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .config import settings

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

version = read('VERSION')

app = FastAPI(
    title="ContentAPI",
    description=description,
    version=version
)

if settings.server and settings.server.get("cors_origins", None):
    env = settings.as_dict(internal=True).get('ENV', 'development')
    print(f"\033[32mINFO\033[0m:\tContentAPI@{version} has just started working ({env})")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.server.cors_origins,
        allow_credentials=settings.get("server.cors_allow_credentials", True),
        allow_methods=settings.get("server.cors_allow_methods", ["*"]),
        allow_headers=settings.get("server.cors_allow_headers", ["*"]),
    )

# app.include_router(main_router)