# vertex-pipelines-deployer

Repository for the Vertex Pipelines Deployer. This tool is a wrapper aound `kfp` and `google-cloud-aiplatform` that allows you to deploy Vertex Pipelines to a Vertex AI Pipelines endpoint in a standardized manner.

> **Warning**:
> This is a work in progress and is not ready for production use.


## Installation

```bash
pip install git+https://github.com/artefactory/vertex-pipelines-deployer.git@develop
```

This project uses [Poetry](https://python-poetry.org/) for dependency management. To install the project dependencies, run the following command:

```bash
poetry install
```

Or use the make command:
```bash
make install
```

## Usage

You can use the deployer CLI or import [`VertexPipelineDeployer`](deployer/deployer.py) in your code.

### CLI

You must respect the following folder structure:

```
vertex
├─ config/
│  └─ {pipeline_name}
│     └─ {config_name}.json
└─ pipelines/
   └─ {pipeline_name}.py
```

You file `{pipeline_name}.py` must contain a function called `pipeline` decorated using `kfp.dsl.pipeline`.

You will also need the following ENV variables, either exported or in a `.env` file (see example in `example.env`):

```bash
PROJECT_ID=YOUR_PROJECT_ID  # GCP Project ID
GCP_REGION=europe-west1  # GCP Region

GAR_LOCATION=europe-west1  # Google Artifact Registry Location
GAR_REPO_ID=YOUR_GAR_REPO_ID  # Google Artifact Registry Repo ID

VERTEX_STAGING_BUCKET_NAME=YOUR_VERTEX_STAGING_BUCKET_NAME  # GCS Bucket for Vertex Pipelines staging
VERTEX_SERVICE_ACCOUNT=YOUR_VERTEX_SERVICE_ACCOUNT  # Vertex Pipelines Service Account
```

Let's say you have a pipeline named `dummy_pipeline` and config file named `config_test.json`. You can deploy your pipeline using the following command:

```bash
vertex-deployer dummy-pipeline \
    --compile \  # compile pipeline locally
    --upload \  # upload pipeline to Google Artifact Registry
    --run \  # run pipeline
    --config-name config_test \  # config file to use at runtime (without extension) to fill parameter_values
    --env-file example.env \  # env file to use
    --tags my-tag \ # tags to add to the pipeline run
    --experiment-name my-experiment \ # experiment name to use. Will default to {pipeline_name}-experiment if not provided
    --enable-caching \ # enable caching for the pipeline run
```

To see all available options, run:

```bash
vertex-deployer --help
```

## Repository Structure

```
├─ .github
│  ├─ workflows
│  │  └─ ci.yaml
│  └─ CODEOWNERS
├─ .gitignore
├─ deployer
│  └─ __init__.py
├─ tests/
├─ .pre-commit-config.yaml
├─ LICENSE
├─ Makefile
├─ pyproject.toml
├─ README.md



## Backlog
1. Features
    1. handle multiple config files formats (toml, json, yaml)
    2. allow for multiple config files as inputs
    3. CLI to typer to have multiple commands (check, deploy, init, etc)
    4. Possibility to store env variables in a env class stored somewhere
    5. Dynamic config checks using pydantic
    6. Scheduling with cloud function instead of cloud scheduler
    7. versioning of config files on a gcs bucket
2. Add more documentation
3. Add review flow
4. Add PR and Issue templates
5. publish on Pypi
