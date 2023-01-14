# ContentApi
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)[![Pytest](https://img.shields.io/static/v1?style=for-the-badge&message=Pytest&color=0A9EDC&logo=Pytest&logoColor=FFFFFF&label=)](https://docs.pytest.org/en/7.2.x/)[![Socket.io](https://img.shields.io/badge/Socket.io-black?style=for-the-badge&logo=socket.io&badgeColor=010101)](https://python-socketio.readthedocs.io/en/latest/)[![Firebase](https://img.shields.io/badge/firebase-%23039BE5.svg?style=for-the-badge&logo=firebase)](https://firebase.google.com/)

ContentAPI power its platform for quizzes. It's divied into Rest API and websockets. First one allows simple queries against categories / quizzes / user's quizzes / tags. Second one is responsible to handle quiz game.

> ❗ **NOTICE** ❗ \
> You need to add `key.json` to access functions that use Firebase

## Installation

```bash
git clone https://github.com/QuizlyTeam/ContentApi.git
cd ContentApi
make install
```

:warning: **if you got errors**: Run `make virtualenv`!

## Executing the API server.

To run API server, you should run `contentapi`. 
Available options with this command:

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

## Documentation 🗎

[REST API](https://quizlyteam.github.io/ContentApi/) - list of available rest api endpoints \
[WEBSOCKETS](https://quizlyteam.github.io/ContentApi/websockets/) - list of available events / messages

You can access live documentation by running `contentapi` and going into one of the websites: 
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

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
switch-to-poetry: ## Switch to poetry package manager.
```

## Python Virtual Environment

```bash
source .venv/bin/activate # Activate virtual environment
deactivate # Deactivate virtual environment
```

### Switching environments

```bash
CONTENTAPI_ENV=production contentapi
```

Available environments: 
- development
- production
- testing

## Docker 🐳

```bash
docker build -t [image-name] .
docker run --name [container-name] -e "[variable-name]=[new-value]" -p [PORT]:8000 [image-name]
```

Example:
```bash
docker build -t contentapi .
docker run --name contentapi_c -e "CONTENTAPI_ENV=production" -p 8000:8000 contentapi
```

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
├── key.json                 # Firebase Admin SDK key
├── api                      # The main python package for the project
│   ├── constants            # A list of constants in API
│   ├── routes               # A list of routes available through API
│   ├── schemas              # Pydantic models
│   ├── services             # Contains files responsible for working to external APIs, database, etc.
│   ├── utils                # Contains helper files 
│   ├── app.py               # The base module for the project
│   ├── cli.py               # CLI config
│   ├── __init__.py          # This tells Python that this is a package
│   ├── __main__.py          # The entry point for the project
│   └── VERSION              # The version for the project is kept in a static file
├── README.md                # The main readme for the project
├── setup.py                 # The setup.py file for installing and packaging the project
├── requirements.txt         # An empty file to hold the requirements for the project
├── requirements-test.txt    # List of requirements for testing and devlopment
├── setup.py                 # The setup.py file for installing and packaging the project
└── tests                    # Unit tests for the project
    ├── routes               # Contains testing files for routes
    ├── services             # Contains testing files for services
    ├── utils                # Contains testing files for utils
    ├── conftest.py          # Configuration, hooks and fixtures for pytest
    ├── __init__.py          # This tells Python that this is a test package
    ├── test_cli.py          # Test CLI config
    └── test_app.py          # Test the base module of the project
```

## License
[![Licence](https://img.shields.io/github/license/QuizlyTeam/ContentApi?style=for-the-badge)](./LICENSE)

