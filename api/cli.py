import string
import typer
import uvicorn

from .config import settings

cli = typer.Typer(name="project_name API")

@cli.command()
def run(
    port: int = settings.server.port,
    host: str = settings.server.host,
    log_level: str = settings.server.log_level,
    reload: bool = settings.server.reload
):
    """Run the API server."""
    uvicorn.run(
        "api.app:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
    )