# ContentApi

ContentApi is a REST API, which expose interfaces for our mobile application.

## Installation

```bash
git clone https://github.com/QuizlyTeam/ContentApi.git
cd ContentApi
make install
```

## Executing

```bash
contentapi --help
Usage: contentapi [OPTIONS]

  Run the API server.

Options:
  --port INTEGER                  [default: 8000]
  --host TEXT                     [default: 127.0.0.1]
  --log-level TEXT                [default: debug]
  --reload / --no-reload          [default: True]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.
```

## API

Run with `contentapi` and access http://127.0.0.1:8000/docs

## Make

```bash
make help
Usage: make <target>

Targets:
help:             ## Show the help.
show:             ## Show the current environment (only for venv)
install:          ## Install the project in dev mode.
fmt:              ## Format code using black & isort.
lint:             ## Run pep8, black, mypy linters.
test:             ## Run tests and generate coverage report.
watch:            ## Run tests on every change.
clean:            ## Clean unused files.
virtualenv:       ## Create a virtual environment.
docs:             ## Build the documentation.
switch-to-poetry: ## Switch to poetry package manager.
```

## Python Virtual Environment

```bash
source .venv/bin/activate # Activate virtual environment
deactivate # Deactivate virtual environment
```

## Configuration

This project uses Dynaconf to manage configuration.

```python
from api.config import settings
```

### Acessing variables

```python
settings.get("SECRET_KEY", default="sdnfjbnfsdf")
settings["SECRET_KEY"]
settings.SECRET_KEY
settings.db.uri
settings["db"]["uri"]
settings["db.uri"]
settings.DB__uri
```

### Defining variables

#### settings.toml

```toml
[development]
dynaconf_merge = true

[development.db]
echo = true
```

> `dynaconf_merge` is a boolean that tells if the settings should be merged with the default settings defined in api/default.toml.

### Switching environments

```bash
CONTENTAPI_ENV=production contentapi
```

Read more on https://dynaconf.com

## Project structure

```bash
├── .github                  # Github metadata for repository
│   └── workflows            # The CI pipeline for Github Actions
├── docs                     # Documentation site (add more .md files here)
│   └── index.md             # The index page for the docs site
├── .gitignore               # A list of files to ignore when pushing to Github
├── LICENSE                  # The license for the project
├── Makefile                 # A collection of utilities to manage the project
├── MANIFEST.in              # A list of files to include in a package
├── mkdocs.yml               # Configuration for documentation site
├── api                      # The main python package for the project
│   ├── routes               # A list of routes available through API
│   ├── schemas              # Pydantic models
│   ├── services             # Contains files responsible for working to external APIs, database, etc.
│   ├── app.py               # The base module for the project
│   ├── __init__.py          # This tells Python that this is a package
│   ├── __main__.py          # The entry point for the project
│   └── VERSION              # The version for the project is kept in a static file
├── README.md                # The main readme for the project
├── setup.py                 # The setup.py file for installing and packaging the project
├── requirements.txt         # An empty file to hold the requirements for the project
├── requirements-test.txt    # List of requirements for testing and devlopment
├── setup.py                 # The setup.py file for installing and packaging the project
└── tests                    # Unit tests for the project
    ├── conftest.py          # Configuration, hooks and fixtures for pytest
    ├── __init__.py          # This tells Python that this is a test package
    └── test_base.py         # The base test case for the project
```