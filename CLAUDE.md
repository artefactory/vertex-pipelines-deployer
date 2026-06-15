# CLAUDE.md

## Project overview

Vertex Pipelines Deployer (`vertex-deployer`) is a CLI tool to check, compile, upload, run, and schedule Kubeflow Pipelines on GCP Vertex AI. It's a Python library (3.10–3.13) using Typer for the CLI, Pydantic for settings, and kfp/google-cloud-aiplatform for pipeline management.

## Development setup

```bash
make install              # Create venv, sync all deps, install pre-commit hooks
make install-dev-requirements  # Dev deps only (pytest, ruff, pre-commit, etc.)
```

Package manager: **uv** (not pip/poetry). `uv.lock` is not committed (this is a library).

## Common commands

```bash
make run-unit-tests        # pytest tests/unit_tests with coverage
make run-integration-tests # pytest tests/integration_tests
make run-tests             # Both
make format-code           # Run all pre-commit hooks (ruff, codespell, nbstripout)
```

## Code style

- **Formatter/linter**: ruff (configured in pyproject.toml) — handles formatting, isort, linting
- **Line length**: 99
- **Docstrings**: Google convention
- Pre-commit hooks run ruff format, ruff check (with `--fix`, handles isort), codespell, and nbstripout on commit and push
- A push hook auto-generates CLI docs via `typer deployer/cli.py utils docs`

## Project structure

- `deployer/` — main package (CLI in `cli.py`, settings in `settings.py`, pipeline logic in `pipeline_deployer.py`)
- `tests/unit_tests/` and `tests/integration_tests/` — test directories
- `templates/` — project templates
- `docs/` — mkdocs documentation

## Git workflow

- Branch from and merge PRs into **`develop`** (not `main`)
- **Squash and merge only** to keep a linear and condensed git history
- Branch names follow conventional commits: `type/short-description` (e.g. `feat/add-scheduling`, `fix/pipeline-timeout`, `docs/update-readme`)
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) — allowed prefixes: `build`, `chore`, `ci`, `docs`, `enh`, `feat`, `fix`, `perf`, `style`, `refactor`, `test`
- PR titles also follow conventional commits format
- `feat` → minor bump, `build`/`enh`/`fix`/`perf` → patch bump
- Releases: merge `develop` → `main`, which triggers semantic-release via GitHub Actions

## Testing

- Unit tests: `tests/unit_tests/` — run with `make run-unit-tests`
- Integration tests: `tests/integration_tests/` — run with `make run-integration-tests`
- Use pytest; coverage is tracked for the `deployer` package
