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

[![Python Version](https://img.shields.io/badge/Python-3.10-informational.svg)](#supported-python-versions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Linting: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-informational?logo=pre-commit&logoColor=white)](https://github.com/ornikar/vertex-eduscore/blob/develop/.pre-commit-config.yaml)
<!-- [![License](https://img.shields.io/github/license/artefactory/vertex-pipelines-deployer)](https://github.com/artefactory/vertex-pipelines-deployer/blob/develop/LICENSE) -->

[![CI](https://github.com/artefactory/vertex-pipelines-deployer/actions/workflows/ci.yaml/badge.svg?branch%3Adevelop&event%3Apush)](https://github.com/artefactory/vertex-pipelines-deployer/actions/workflows/ci.yaml/badge.svg?query=branch%3Adevelop)

</div>


> **Warning**
> This is a work in progress and is not ready for production use.


## Table of Contents
- [Why this tool?](##why-this-tool)
- [Prerequisites](##prerequisites)
- [Installation](##installation)
- [Usage](##usage)
  - [Setup](###setup)
  - [Folder Structure](###folder-structure)
  - [Deploying a Pipeline](###deploying-a-pipeline)


## Why this tool?

Two uses cases:
- quickly iterate over your pipelines by compiling and running them in multiple environments (test, dev, staging, etc) without duplicating code or looking for the right kfp / aiplatform snippet.
- deploy your pipelines to Vertex Pipelines in a standardized manner in your CD with Cloud Build or GitHub Actions.
- check pipeline validity in your CI.

Commands:
- `check`: check your pipelines (imports, compile, check configs validity against pipeline definition).
- `deploy`: compile, upload to Artifact Registry, run and schedule your pipelines.

## Prerequisites

- Unix-like environment (Linux, macOS, WSL, etc...)
- Python 3.10
- Google Cloud SDK
- A GCP project with Vertex Pipelines enabled

## Installation

```bash
pip install git+https://github.com/artefactory/vertex-pipelines-deployer.git@develop
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
export VERTEX_SERVICE_ACCOUNT=<foobar@PROJECT_ID.iam.gserviceaccount.com>
gcloud iam service-accounts create ${VERTEX_SERVICE_ACCOUNT}
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${VERTEX_SERVICE_ACCOUNT}" \
    --role="roles/aiplatform.user"
```

You can use the deployer CLI (see example below) or import [`VertexPipelineDeployer`](deployer/deployer.py) in your code (try it yourself).

### Folder Structure

You must respect the following folder structure. If you already follow the
[Vertex Pipelines Starter Kit folder structure](https://github.com/artefactory/vertex-pipeline-starter-kit), it should be pretty smooth to use this tool:

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
GAR_PIPELINES_REPO_ID=YOUR_GAR_KFP_REPO_ID  # Google Artifact Registry Repo ID (KFP format)

VERTEX_STAGING_BUCKET_NAME=YOUR_VERTEX_STAGING_BUCKET_NAME  # GCS Bucket for Vertex Pipelines staging
VERTEX_SERVICE_ACCOUNT=YOUR_VERTEX_SERVICE_ACCOUNT  # Vertex Pipelines Service Account
```

> **Note**
> We're using env files and dotenv to load the environment variables. No default env file is provided to ensure that you don't accidentally deploy to the wrong project.
> This also allows you to work with multiple environments thanks to env files (`test.env``, `dev.env`, `prod.env`, etc)

### Deploying a Pipeline

Let's say you defines a pipeline in `dummy_pipeline.py` and a config file named `config_test.json`. You can deploy your pipeline using the following command:
```bash
vertex-deployer deploy dummy_pipeline \
    --compile \
    --upload \
    --run \
    --config-name config_test \
    --env-file example.env \
    --tags my-tag \
    --experiment-name my-experiment \
    --enable-caching
```

To see all available options, run:
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
│  ├─ workflows
│  │  └─ ci.yaml
│  └─ CODEOWNERS
├─ .gitignore
├─ deployer
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ deployer.py
│  └─ utils.py
├─ tests/
├─ vertex
│  ├─ components
│  │  └─ dummy.py
│  ├─ configs
│  │  ├─ broken_pipeline
│  │  │  └─ config_test.json
│  │  └─ dummy_pipeline
│  │     └─ config_test.json
│  ├─ deployment
│  ├─ lib
│  ├─ pipelines
│  │  ├─ broken_pipeline.py
│  │  └─ dummy_pipeline.py
├─ .pre-commit-config.yaml
├─ LICENSE
├─ Makefile
├─ pyproject.toml
└─ README.md
```
