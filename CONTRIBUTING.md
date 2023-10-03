# 🧑‍💻 Contributing to Vertex Pipelines Deployer

## How to contribute


### Issues, Pull Requests and Code Reviews.

Issues and Pull requests templates are mandatory.

At least one code review is needed to merge. Please merge your feature branches on `develop`.

We try to rebase as much as possible and use squash and merge to keep a linear and condensed git history.

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

> **Note**
> `poetry.lock` is not committed deliberately, as recommended by Poetry's doc. You can read more about it [here](https://python-poetry.org/docs/basic-usage/#as-a-library-developer).

### Codestyle

This projects uses [Black](https://black.readthedocs.io/en/stable/), isort, ruff for codestyle. You can run the following command to format your code. It uses Pre-commit hooks to run the formatters and linters.

```bash
make format-code
```

### Docstring convention

This project uses [Google docstring convention](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

A full example is available in [here](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).


## How to release

This project uses [Python Semantic Versioning](https://python-semantic-release.readthedocs.io/en/latest/automatic-releases/github-actions.html)
and [Poetry](https://python-poetry.org/docs/cli/#build) to create releases and tags.

The release process is automated through GitHub Actions. Here is the process:

- Create a Pull Request from `develop` to `main`.
- Merge the Pull Request. This can be a merge commit or a squash and merge.
- The merge will trigger the Release GitHub Action defined in [this workflow](.github/workflows/release.yaml).

The Release GitHub Action does the following:

- Checks out the code.
- Runs the CI GitHub Action, which runs the tests and linters.
- Runs Python Semantic Release, which takes care of version update, tag creation, and release creation.

The action is triggered by any push to main.

Here is the relevant part of the GitHub Action:

> [!NOTE]
> The release action will be triggered by any push to `main` only if the 'CI' job in the 'release.yaml' workflow succeeds.
> Python Semantic Release will take care of version number update, tag creation and release creation.
