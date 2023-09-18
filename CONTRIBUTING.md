# 🧑‍💻 Contributing to Vertex Pipelines Deployer

## How to contribute


### Issues, Pull Requests and Code Reviews.

Issues and Pull requests templates are mandatory.

At least one code review is needed to merge. Please merge your feature branches on `develop`.

### Getting started

This project uses [Poetry](https://python-poetry.org/) for dependency management. Poetry's doc is really good, so you should check it out if you have any questions.

To install poetry:

```bash
make download-poetry
```

You can start by creating a virtual environment (conda or other) or use poetry venv(please check the Makefile first if so, as poetry venv is deactivated there). Then, to install the project dependencies, run the following command:

```bash
make install
```

To develop, you will need dev requirements too. Run:
```bash
make install-dev-requirements
```

### Codestyle

This projects uses [Black](https://black.readthedocs.io/en/stable/), isort, ruff for codestyle. You can run the following command to format your code. It uses Pre-commit hooks to run the formatters and linters.

```bash
make format-code
```

### Docstring convention

This project uses [Google docstring convention](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

A full example is available in [here](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).