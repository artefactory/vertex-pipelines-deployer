<br />
<div align="center">
    <h1 align="center">Vertex Pipelines Deployer</h1>
    <h3 align="center">Deploy Vertex Pipelines within minutes</h3>
        <p align="center">
        This tool is a wrapper aound <a href="https://www.kubeflow.org/docs/components/pipelines/v2/hello-world/">kfp</a> and <a href="https://cloud.google.com/python/docs/reference/aiplatform/latest">google-cloud-aiplatform</a> that allows you to check, compile, upload, run and schedule Vertex Pipelines to a Vertex AI Pipelines endpoint in a standardized manner.
        </p>
</div>
</br>

<!-- PROJECT SHIELDS -->
<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.8_3.9_3.10-blue?logo=python)](#supported-python-versions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Linting: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-informational?logo=pre-commit&logoColor=white)](https://github.com/ornikar/vertex-eduscore/blob/develop/.pre-commit-config.yaml)
<!-- [![License](https://img.shields.io/github/license/artefactory/vertex-pipelines-deployer)](https://github.com/artefactory/vertex-pipelines-deployer/blob/develop/LICENSE) -->

[![CI](https://github.com/artefactory/vertex-pipelines-deployer/actions/workflows/ci.yaml/badge.svg?branch%3Adevelop&event%3Apush)](https://github.com/artefactory/vertex-pipelines-deployer/actions/workflows/ci.yaml/badge.svg?query=branch%3Adevelop)

</div>


## Table of Contents
- [Why this tool?](#why-this-tool)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
    - [From git repo](#from-git-repo)
    - [From GCS (not available in PyPI yet)](#from-gcs-not-available-in-pypi-yet)
- [Usage](#usage)
  - [Setup](#setup)
  - [Folder Structure](#folder-structure)
  - [CLI: Deploying a Pipeline](#cli-deploying-a-pipeline)
  - [CLI: Checking Pipelines are valid](#cli-checking-pipelines-are-valid)
  - [CLI: Other commands](#cli-other-commands)
    - [`create`](#create)
    - [`list`](#list)
  - [CLI: Options](#cli-options)


## Why this tool?

Two uses cases:
- quickly iterate over your pipelines by compiling and running them in multiple environments (test, dev, staging, etc) without duplicating code or looking for the right kfp / aiplatform snippet.
- deploy your pipelines to Vertex Pipelines in a standardized manner in your CD with Cloud Build or GitHub Actions.
- check pipeline validity in your CI.

Commands:
- `check`: check your pipelines (imports, compile, check configs validity against pipeline definition).
- `deploy`: compile, upload to Artifact Registry, run and schedule your pipelines.
- `create`: create a new pipeline and config files.
- `list`: list all pipelines in the `vertex/pipelines` folder.

## Prerequisites

- Unix-like environment (Linux, macOS, WSL, etc...)
- Python 3.8 to 3.10
- Google Cloud SDK
- A GCP project with Vertex Pipelines enabled

## Installation


### From git repo

Stable version:
```bash
pip install git+https://github.com/artefactory/vertex-pipelines-deployer.git@main
```

Develop version:
```bash
pip install git+https://github.com/artefactory/vertex-pipelines-deployer.git@develop
```

If you want to test this package on examples from this repo:
```bash
git clone git@github.com:artefactory/vertex-pipelines-deployer.git
poetry install
cd example
```

### From GCS (not available in PyPI yet)

Install a specific version:
```bash
export VERSION=0.1.0
gsutil -m cp  gs://vertex-pipelines-deployer/vertex_deployer-$VERSION.tar.gz .
pip install ./vertex_deployer-$VERSION.tar.gz
```

List available versions:
```bash
gsutil ls gs://vertex-pipelines-deployer
```

### Add to requirements

It's better to get the .tar.gz archive from gcs, and version it.

Then add the following line to your `requirements.in` file:
```bash
file:my/path/to/vertex_deployer-$VERSION.tar.gz
```

## Usage

### Setup

1. Setup your GCP environment:

```bash
export PROJECT_ID=<gcp_project_id>
gcloud config set project $PROJECT_ID
gcloud auth login
gcloud auth application-default login
```
2. You need the following APIs to be enabled:
    - Cloud Build API
    - Artifact Registry API
    - Cloud Storage API
    - Vertex AI API

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    storage.googleapis.com \
    aiplatform.googleapis.com
```
3. Create an artifact registry repository for your base images (Docker format):
```bash
export GAR_DOCKER_REPO_ID=<your_gar_repo_id_for_images>
export GAR_LOCATION=<your_gar_location>
gcloud artifacts repositories create ${GAR_DOCKER_REPO_ID} \
    --location=${GAR_LOCATION} \
    --repository-format=docker
```
4. Build and upload your base images to the repository. To do so, please follow Google Cloud Build documentation.
5. Create an artifact registry repository for your pipelines (KFP format):
```bash
export GAR_PIPELINES_REPO_ID=<your_gar_repo_id_for_pipelines>
gcloud artifacts repositories create ${GAR_PIPELINES_REPO_ID} \
    --location=${GAR_LOCATION} \
    --repository-format=kfp
```
6. Create a GCS bucket for Vertex Pipelines staging:
```bash
export GCP_REGION=<your_gcp_region>
export VERTEX_STAGING_BUCKET_NAME=<your_bucket_name>
gcloud storage buckets create gs://${VERTEX_STAGING_BUCKET_NAME} --location=${GCP_REGION}
```
7. Create a service account for Vertex Pipelines: # TODO: complete iam bindings
```bash
export VERTEX_SERVICE_ACCOUNT_NAME=foobar
export VERTEX_SERVICE_ACCOUNT="${VERTEX_SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create ${VERTEX_SERVICE_ACCOUNT_NAME}

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${VERTEX_SERVICE_ACCOUNT}" \
    --role="roles/aiplatform.user"

gcloud storage buckets add-iam-policy-binding gs://${VERTEX_STAGING_BUCKET_NAME} \
    --member="serviceAccount:${VERTEX_SERVICE_ACCOUNT}" \
    --role="roles/storage.objectUser"

gcloud artifacts repositories add-iam-policy-binding ${GAR_PIPELINES_REPO_ID} \
   --location=${GAR_LOCATION} \
   --member="serviceAccount:${VERTEX_SERVICE_ACCOUNT}" \
   --role="roles/artifactregistry.admin"
```

You can use the deployer CLI (see example below) or import [`VertexPipelineDeployer`](deployer/pipeline_deployer.py) in your code (try it yourself).

### Folder Structure

You must respect the following folder structure. If you already follow the
[Vertex Pipelines Starter Kit folder structure](https://github.com/artefactory/vertex-pipeline-starter-kit), it should be pretty smooth to use this tool:

```
vertex
├─ configs/
│  └─ {pipeline_name}
│     └─ {config_name}.json
└─ pipelines/
   └─ {pipeline_name}.py
```

> [!NOTE]
> You must have at lease these files. If you need to share some config elements between pipelines,
> you can have a `shared` folder in `configs` and import them in your pipeline configs.

#### Pipelines

You file `{pipeline_name}.py` must contain a function called `pipeline` decorated using `kfp.dsl.pipeline`.


#### Configs

Config file can be either `.py` files or `.json` files.
They must be located in the `config/{pipeline_name}` folder.

**Why two formats?**

`.py` files are useful to define complex configs (e.g. a list of dicts) while `.json` files are useful to define simple configs (e.g. a string).

**How to format them?**
- `.json` files must be valid json files containing only one dict of key: value.
- `.py` files must be valid python files with two important elements:
    - `parameter_values` to pass arguments to your pipeline
    - `input_artifacts` if you want to retrieve and create input artifacts to your pipeline.
        See [Vertex Documentation](https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.PipelineJob) for more information.

**How to name them?**

`{config_name}.json` or `{config_name}.py`. config_name is free but must be unique for a given pipeline.


#### Settings

You will also need the following ENV variables, either exported or in a `.env` file (see example in `example.env`):

```bash
PROJECT_ID=YOUR_PROJECT_ID  # GCP Project ID
GCP_REGION=europe-west1  # GCP Region

GAR_LOCATION=europe-west1  # Google Artifact Registry Location
GAR_PIPELINES_REPO_ID=YOUR_GAR_KFP_REPO_ID  # Google Artifact Registry Repo ID (KFP format)

VERTEX_STAGING_BUCKET_NAME=YOUR_VERTEX_STAGING_BUCKET_NAME  # GCS Bucket for Vertex Pipelines staging
VERTEX_SERVICE_ACCOUNT=YOUR_VERTEX_SERVICE_ACCOUNT  # Vertex Pipelines Service Account
```

> **Note**
> We're using env files and dotenv to load the environment variables.
> No default value for `--env-file` argument is provided to ensure that you don't accidentally deploy to the wrong project.
> An [`example.env`](./example/example.env) file is provided in this repo.
> This also allows you to work with multiple environments thanks to env files (`test.env`, `dev.env`, `prod.env`, etc)

### CLI: Deploying a Pipeline

Let's say you defines a pipeline in `dummy_pipeline.py` and a config file named `config_test.json`. You can deploy your pipeline using the following command:
```bash
vertex-deployer deploy dummy_pipeline \
    --compile \
    --upload \
    --run \
    --env-file example.env \
    --local-package-path . \
    --tags my-tag \
    --parameter-values-filepath vertex/configs/dummy_pipeline/config_test.json \
    --experiment-name my-experiment \
    --enable-caching
```

### CLI: Checking Pipelines are valid

To check that your pipelines are valid, you can use the `check` command. It uses a pydantic model to:
- check that your pipeline imports and definition are valid
- check that your pipeline can be compiled
- generate a pydantic model from the pipeline parameters definition and check that all configs related to the pipeline are valid

To validate one specific pipeline:
```bash
vertex-deployer check dummy_pipeline
```

To validate all pipelines in the `vertex/pipelines` folder:
```bash
vertex-deployer check --all
```


### CLI: Other commands

#### `create`

You can create all files needed for a pipeline using the `create` command:
```bash
vertex-deployer create my_new_pipeline --config-type py
```

This will create a `my_new_pipeline.py` file in the `vertex/pipelines` folder and a `vertex/config/my_new_pipeline/` folder with mutliple config files in it.

#### `list`

You can list all pipelines in the `vertex/pipelines` folder using the `list` command:
```bash
vertex-deployer list --with-configs
```

### CLI: Options

```bash
vertex-deployer --help
```

To adapt log level, use the `--log-level` option. Default is `INFO`.
```bash
vertex-deployer --log-level DEBUG deploy ...
```

## Repository Structure

```
├─ .github
│  ├─ ISSUE_TEMPLATE/
│  ├─ workflows
│  │  └─ ci.yaml
│  ├─ CODEOWNERS
│  └─ PULL_REQUEST_TEMPLATE.md
├─ deployer
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ constants.py
│  ├─ pipeline_checks.py
│  ├─ pipeline_deployer.py
│  └─ utils
│     ├─ config.py
│     ├─ exceptions.py
│     ├─ logging.py
│     ├─ models.py
│     └─ utils.py
├─ tests/
├─ example
|   ├─ example.env
│   └─ vertex
│      ├─ components
│      │  └─ dummy.py
│      ├─ configs
│      │  ├─ broken_pipeline
│      │  │  └─ config_test.json
│      │  └─ dummy_pipeline
│      │     └─ config_test.json
│      ├─ deployment
│      ├─ lib
│      └─ pipelines
│         ├─ broken_pipeline.py
│         └─ dummy_pipeline.py
├─ .gitignore
├─ .pre-commit-config.yaml
├─ LICENSE
├─ Makefile
├─ pyproject.toml
└─ README.md
```
