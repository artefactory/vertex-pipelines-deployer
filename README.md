<br />
<div align="center">
    <h1 align="center">Vertex Pipelines Deployer</h1>
    <h3 align="center">Deploy Vertex Pipelines within minutes</h3>
        <p align="center">
        This tool is a wrapper around <a href="https://www.kubeflow.org/docs/components/pipelines/v2/hello-world/">kfp</a> and <a href="https://cloud.google.com/python/docs/reference/aiplatform/latest">google-cloud-aiplatform</a> that allows you to check, compile, upload, run and schedule Vertex Pipelines in a standardized manner.
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
[![License](https://img.shields.io/github/license/artefactory/vertex-pipelines-deployer)](https://github.com/artefactory/vertex-pipelines-deployer/blob/main/LICENSE)

[![CI](https://github.com/artefactory/vertex-pipelines-deployer/actions/workflows/ci.yaml/badge.svg?branch%3Amain&event%3Apush)](https://github.com/artefactory/vertex-pipelines-deployer/actions/workflows/ci.yaml/badge.svg?query=branch%3Amain)
[![Release](https://github.com/artefactory/vertex-pipelines-deployer/actions/workflows/release.yaml/badge.svg?branch%3Amain&event%3Apush)](https://github.com/artefactory/vertex-pipelines-deployer/actions/workflows/release.yaml/badge.svg?query=branch%3Amain)

</div>


<details>
  <summary>📚 Table of Contents</summary>
  <ul>
    <li><a href="#-why-this-tool">Why this tool?</a></li>
    <li><a href="#-prerequisites">Prerequisites</a></li>
    <li><a href="#-installation">Installation</a></li>
        <ul>
            <li><a href="#from-git-repo">From git repo</a></li>
            <li><a href="#from-artifact-registry-not-available-in-pypi-yet">From Artifact Registry (not available in PyPI yet)</a></li>
            <li><a href="#add-to-requirements">Add to requirements</a></li>
        </ul>
    <li><a href="#-usage">Usage</a></li>
        <ul>
            <li><a href="#-setup">Setup</a></li>
            <li><a href="#-folder-structure">Folder Structure</a></li>
            <li><a href="#-cli-deploying-a-pipeline-with-deploy">CLI: Deploying a Pipeline with `deploy`</a></li>
            <li><a href="#-cli-checking-pipelines-are-valid-with-check">CLI: Checking Pipelines are valid with `check`</a></li>
            <li><a href="#-cli-other-commands">CLI: Other commands</a></li>
                <ul>
                    <li><a href="#create">`create`</a></li>
                    <li><a href="#list">`list`</a></li>
                    <li><a href="#config">`config`</a></li>
                </ul>
        </ul>
    <li><a href="#cli-options">CLI: Options</a></li>
    <li><a href="#configuration">Configuration</a></li>
  </ul>
</details>


[Full CLI documentation](docs/CLI_REFERENCE.md)

<!-- --8<-- [start:why] -->
## ❓ Why this tool?


Three uses cases:

1. **CI:** check pipeline validity.
1. **Dev mode:** duickly iterate over your pipelines by compiling and running them in multiple environments (test, dev, staging, etc) without duplicating code or looking for the right kfp / aiplatform snippet.
2. **CD:** deploy your pipelines to Vertex Pipelines in a standardized manner in your CD with Cloud Build or GitHub Actions.


Four commands:

- `check`: check your pipelines (imports, compile, check configs validity against pipeline definition).
- `deploy`: compile, upload to Artifact Registry, run and schedule your pipelines.
- `create`: create a new pipeline and config files.
- `list`: list all pipelines in the `vertex/pipelines` folder.
<!-- --8<-- [end:why] -->

## 📋 Prerequisites
<!-- --8<-- [start:prerequisites] -->

- Unix-like environment (Linux, macOS, WSL, etc...)
- Python 3.8 to 3.10
- Google Cloud SDK
- A GCP project with Vertex Pipelines enabled
<!-- --8<-- [end:prerequisites] -->

## 📦 Installation
<!-- --8<-- [start:installation] -->

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

### From Artifact Registry (not available in PyPI yet)

The package is available on a public Google Artifact Registry repo. You need to specify a
[pip extra index url](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-extra-index-url) to install it.

Install latest version:
```bash
pip install --extra-index-url https://europe-west1-python.pkg.dev/vertex-deployer-sandbox-3a8a/vertex-deployer/simple vertex-deployer
```

List available versions:
```bash
pip index versions --extra-index-url https://europe-west1-python.pkg.dev/vertex-deployer-sandbox-3a8a/vertex-deployer/simple vertex-deployer
```

### Add to requirements

It's better to get the .tar.gz archive from gcs, and version it.

Then add the following lines to your `requirements.in` file:
```bash
--extra-index-url https://europe-west1-python.pkg.dev/vertex-deployer-sandbox-3a8a/vertex-deployer/simple

vertex-deployer==0.3.1
```
<!-- --8<-- [end:installation] -->

## 🚀 Usage
<!-- --8<-- [start:setup] -->
### 🛠️ Setup

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

7. Create a service account for Vertex Pipelines:
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

### 📁 Folder Structure

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

!!! tip "About folder structure"
    You must have at least these files. If you need to share some config elements between pipelines,
    you can have a `shared` folder in `configs` and import them in your pipeline configs.

    If you're following a different folder structure, you can change the default paths in the `pyproject.toml` file.
    See [Configuration](#configuration) section for more information.

#### Pipelines

You file `{pipeline_name}.py` must contain a function called `{pipeline_name}` decorated using `kfp.dsl.pipeline`.
In previous versions, the functions / object used to be called `pipeline` but it was changed to `{pipeline_name}` to avoid confusion with the `kfp.dsl.pipeline` decorator.

```python
# vertex/pipelines/dummy_pipeline.py
import kfp.dsl

# New name to avoid confusion with the kfp.dsl.pipeline decorator
@kfp.dsl.pipeline()
def dummy_pipeline():
    ...

# Old name
@kfp.dsl.pipeline()
def pipeline():
    ...
```

#### Configs

Config file can be either `.py`, `.json` or `.toml` files.
They must be located in the `config/{pipeline_name}` folder.

**Why three formats?**

`.py` files are useful to define complex configs (e.g. a list of dicts) while `.json` / `.toml` files are useful to define simple configs (e.g. a string).

**How to format them?**

- `.json` and `.toml` files must be valid json files containing only one dict of key: value representing parameter values.
- `.py` files must be valid python files with two important elements:

    * `parameter_values` to pass arguments to your pipeline
    * `input_artifacts` if you want to retrieve and create input artifacts to your pipeline.
        See [Vertex Documentation](https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.PipelineJob) for more information.

**How to name them?**

`{config_name}.py` or `{config_name}.json` or `{config_name}.toml`. config_name is free but must be unique for a given pipeline.


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

!!! note "About env files"
    We're using env files and dotenv to load the environment variables.
    No default value for `--env-file` argument is provided to ensure that you don't accidentally deploy to the wrong project.
    An [`example.env`](./example/example.env) file is provided in this repo.
    This also allows you to work with multiple environments thanks to env files (`test.env`, `dev.env`, `prod.env`, etc)
<!-- --8<-- [end:setup] -->

<!-- --8<-- [start:usage] -->
### 🚀 CLI: Deploying a Pipeline with `deploy`

Let's say you defines a pipeline in `dummy_pipeline.py` and a config file named `config_test.json`. You can deploy your pipeline using the following command:
```bash
vertex-deployer deploy dummy_pipeline \
    --compile \
    --upload \
    --run \
    --env-file example.env \
    --local-package-path . \
    --tags my-tag \
    --config-filepath vertex/configs/dummy_pipeline/config_test.json \
    --experiment-name my-experiment \
    --enable-caching
```

### ✅ CLI: Checking Pipelines are valid with `check`

To check that your pipelines are valid, you can use the `check` command. It uses a pydantic model to:
- check that your pipeline imports and definition are valid
- check that your pipeline can be compiled
- check that all configs related to the pipeline are respecting the pipeline definition (using a Pydantic model based on pipeline signature)

To validate one specific pipeline:
```bash
vertex-deployer check dummy_pipeline
```

To validate all pipelines in the `vertex/pipelines` folder:
```bash
vertex-deployer check --all
```


### 🛠️ CLI: Other commands

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

#### `config`

You can check your `vertex-deployer` configuration options using the `config` command.
Fields set in `pyproject.toml` will overwrite default values and will be displayed differently:
```bash
vertex-deployer config --all
```

### 🍭 CLI: Options

```bash
vertex-deployer --help
```

To see package version:
```bash
vertex-deployer --version
```

To adapt log level, use the `--log-level` option. Default is `INFO`.
```bash
vertex-deployer --log-level DEBUG deploy ...
```

<!-- --8<-- [end:usage] -->

## Configuration

You can configure the deployer using the `pyproject.toml` file to better fit your needs.
This will overwrite default values. It can be usefull if you always use the same options, e.g. always the same `--scheduler-timezone`

```toml
[tool.vertex-deployer]
pipelines_root_path = "my/path/to/vertex/pipelines"
configs_root_path = "my/path/to/vertex/configs"
log_level = "INFO"

[tool.vertex-deployer.deploy]
scheduler_timezone = "Europe/Paris"
```

You can display all the configurable parameterss with default values by running:
```bash
$ vertex-deployer config --all
'*' means the value was set in config file

* pipelines_root_path=my/path/to/vertex/pipelines
* config_root_path=my/path/to/vertex/configs
* log_level=INFO
deploy
  env_file=None
  compile=True
  upload=False
  run=False
  schedule=False
  cron=None
  delete_last_schedule=False
  * scheduler_timezone=Europe/Paris
  tags=['latest']
  config_filepath=None
  config_name=None
  enable_caching=False
  experiment_name=None
  local_package_path=vertex/pipelines/compiled_pipelines
check
  all=False
  config_filepath=None
  raise_error=False
list
  with_configs=True
create
  config_type=json
```

## Repository Structure

```
├─ .github
│  ├─ ISSUE_TEMPLATE/
│  ├─ workflows
│  │  ├─ ci.yaml
│  │  ├─ pr_agent.yaml
│  │  └─ release.yaml
│  ├─ CODEOWNERS
│  └─ PULL_REQUEST_TEMPLATE.md
├─ deployer                                     # Source code
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ configuration.py
│  ├─ constants.py
│  ├─ pipeline_checks.py
│  ├─ pipeline_deployer.py
│  └─ utils
│     ├─ config.py
│     ├─ exceptions.py
│     ├─ logging.py
│     ├─ models.py
│     └─ utils.py
├─ docs/                                        # Documentation folder (mkdocs)
├─ templates/                                   # Semantic Release templates
├─ tests/
├─ example                                      # Example folder with dummy pipeline and config
|   ├─ example.env
│   └─ vertex
│      ├─ components
│      │  └─ dummy.py
│      ├─ configs
│      │  ├─ broken_pipeline
│      │  │  └─ config_test.json
│      │  └─ dummy_pipeline
│      │     ├─ config_test.json
│      │     ├─ config.py
│      │     └─ config.toml
│      ├─ deployment
│      ├─ lib
│      └─ pipelines
│         ├─ broken_pipeline.py
│         └─ dummy_pipeline.py
├─ .gitignore
├─ .pre-commit-config.yaml
├─ catalog-info.yaml                            # Roadie integration configuration
├─ CHANGELOG.md
├─ CONTRIBUTING.md
├─ LICENSE
├─ Makefile
├─ mkdocs.yml                                   # Mkdocs configuration
├─ pyproject.toml
└─ README.md
```
