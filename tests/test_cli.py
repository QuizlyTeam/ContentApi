import pytest

given = pytest.mark.parametrize


def test_help(cli_client, cli):
    result = cli_client.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "--port INTEGER" in result.stdout
    assert "--host TEXT" in result.stdout
    assert "--log-level TEXT" in result.stdout
    assert "--reload / --no-reload" in result.stdout
