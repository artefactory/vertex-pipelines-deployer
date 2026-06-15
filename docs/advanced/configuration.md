## Three types of settings

There are three types of settings in the project:

- [**Vertex Deployer configuration**](#vertex-deployer-configuration): settings of the deployer itself, which is used to deploy the project.
- [**Pipelines config files**](#pipelines-config-files): configuration of the pipelines, in TOML/JSON/Python format. These files are the arguments to your pipelines.
- [**Vertex deployment settings**](#vertex-deployment-settings): used only by the deploy command, it consists of a few env variables to declare / add to `.env` file to deploy a pipeline, such as `PROJECT_ID`, `GCP_REGION`, `VERTEX_STAGING_BUCKET_NAME`, etc.

## Vertex Deployer configuration

You can override default options for specific CLI commands in the pyproject.toml file, under the `[tool.vertex_deployer]` section.
You can also override global deployer options such as logging level, or pipelines / config root path to better fit your repo structure.

```toml title="pyproject.toml"
[tool.vertex_deployer]
log-level = "INFO"
vertex-folder-path = "vertex"

[tool.vertex_deployer.deploy]
enable-caching = true
env-file = "example.env"
compile = true
upload = true
run = true
tags = ["my-tag"]
experiment-name = "my-experiment"
config-filepath = "vertex/configs/dummy_pipeline/config_test.json"
scheduler-timezone = "Europe/Paris"

[tool.vertex_deployer.check]
all = false
raise-error = false
warn-defaults = true
raise-for-defaults = false

[tool.vertex_deployer.list]
with-configs = false

[tool.vertex_deployer.create]
config-type = "yaml"
```

### All configurable fields

Below is the full reference of settings you can override in `pyproject.toml`:

| Section | Field | Default | Description |
|---|---|---|---|
| *(root)* | `vertex-folder-path` | `"vertex"` | Root path for pipelines and configs |
| *(root)* | `log-level` | `"INFO"` | Log level (`TRACE`, `DEBUG`, `INFO`, `SUCCESS`, `WARNING`, `ERROR`, `CRITICAL`) |
| `deploy` | `env-file` | `None` | Path to the `.env` file |
| `deploy` | `compile` | `true` | Compile the pipeline before deploying |
| `deploy` | `upload` | `false` | Upload compiled pipeline to Artifact Registry |
| `deploy` | `run` | `false` | Submit a pipeline run |
| `deploy` | `schedule` | `false` | Create a pipeline schedule |
| `deploy` | `cron` | `None` | Cron expression for scheduling |
| `deploy` | `delete-last-schedule` | `false` | Delete previous schedule before creating new one |
| `deploy` | `scheduler-timezone` | `"Europe/Paris"` | IANA timezone for scheduling |
| `deploy` | `tags` | `None` | Tags for Artifact Registry upload |
| `deploy` | `config-filepath` | `None` | Path to a specific config file |
| `deploy` | `config-name` | `None` | Config filename (resolved from pipeline config dir) |
| `deploy` | `enable-caching` | `None` | Enable/disable pipeline caching |
| `deploy` | `experiment-name` | `None` | Vertex Experiment name |
| `deploy` | `run-name` | `None` | Custom run display name |
| `deploy` | `skip-validation` | `true` | Skip interactive settings confirmation |
| `check` | `all` | `false` | Check all pipelines |
| `check` | `config-filepath` | `None` | Path to a specific config file to check |
| `check` | `raise-error` | `false` | Raise error if pipeline is invalid |
| `check` | `warn-defaults` | `true` | Warn when default parameter values are used |
| `check` | `raise-for-defaults` | `false` | Raise error when default values are used |
| `list` | `with-configs` | `false` | Also list config files for each pipeline |
| `create` | `config-type` | `"yaml"` | Default config file format (`json`, `py`, `toml`, `yaml`) |

## Pipelines config files

Config files for pipelines can be in `.py`, `.json`, or `.toml` format and must be located in the `config/{pipeline_name}` folder.
The choice of format depends on the complexity and requirements of the configuration.
Python files allow for complex configurations and dynamic values, while JSON and TOML files are more suitable for static and simple configurations.

For example, you have here the same config file in the three formats:

=== "JSON"
    ```json title="vertex/configs/dummy_pipeline/config_test.json"
    {
        "model_name": "my-model",
        "default_params": {
            "lambda": 0.1,
            "alpha": "hello world"
        },
        "grid_search": {
            "lambda": [0.1, 0.2, 0.3],
            "alpha": ["hello world", "goodbye world"],
            "cv": 3
        }
    }
    ```

    JSON config files are the simplest and most readable, but they are also the most limited.

    They do not allow for dynamic values or complex configurations.

    They are the default.

=== "TOML"
    ```toml title="vertex/configs/dummy_pipeline/config_test.toml"
    [modeling]
    model_name = "my-model"
    default_params = { lambda = 0.1 , alpha = "hello world"}

    [modeling.grid_search]
    lambda = [0.1, 0.2, 0.3]
    alpha = ["hello world", "goodbye world"]
    cv = 3
    ```

    TOML config files are more flexible than JSON files, but they are also more verbose.

    They allow structuring the config file in sections, which can be useful for complex configurations.

    Then, these sections are flattened, except for inline dicts, leading to slightly different parameter names
    (e.g., `modeling_grid_search_lambda` instead of `lambda`).


=== "YAML"
    ```yaml title="vertex/configs/dummy_pipeline/config_test.yaml"
    model_name: my-model
    default_params:
      lambda: 0.1
      alpha: hello world
    grid_search:
      lambda:
        - 0.1
        - 0.2
        - 0.3
      alpha:
        - hello world
        - goodbye world
      cv: 3
    ```

    YAML config files are similar to TOML files in terms of flexibility and verbosity.

    They are more human-readable than TOML files, but they are also more error-prone due to indentation.


=== "Python"
    ```python title="vertex/configs/dummy_pipeline/config_test.py"
    parameter_values = {
        "model_name": "my-model",
        "default_params": {
            "lambda": 0.1,
            "alpha": "hello world"
        },
        "grid_search": {
            "lambda": [0.1, 0.2, 0.3],
            "alpha": ["hello world", "goodbye world"],
            "cv": 3
        }
    }

    input_artifacts = {  # Only available in Python config files
        "artifact1": "gs://bucket/path/to/artifact1"
    }
    ```

    Python config files are the most flexible, as they allow for dynamic values and complex configurations.

    **They are also the only format that allows for the use of input artifacts**.

    However, they are also the most verbose and require more boilerplate code.

## Vertex deployment settings

The deployment settings are environment variables that configure the deployment environment for Vertex Pipelines.
These are loaded by the `deploy` command when it needs to interact with GCP resources.

These settings can be specified in an `.env` file (passed via `--env-file`) or exported as shell environment variables. All variables are **required** — the deploy command will fail with a validation error if any are missing.

```bash title="example.env"
PROJECT_ID=your-gcp-project-id
GCP_REGION=europe-west1
GAR_LOCATION=europe-west1
GAR_PIPELINES_REPO_ID=your-gar-kfp-repo-id
VERTEX_STAGING_BUCKET_NAME=your-vertex-staging-bucket-name
VERTEX_SERVICE_ACCOUNT=your-vertex-service-account
```

### Environment variables reference

| Variable | Example | Description |
|---|---|---|
| `PROJECT_ID` | `my-gcp-project` | GCP project ID where pipelines will run |
| `GCP_REGION` | `europe-west1` | GCP region for Vertex AI pipeline execution |
| `GAR_LOCATION` | `europe-west1` | Google Artifact Registry location (usually the same as `GCP_REGION`) |
| `GAR_PIPELINES_REPO_ID` | `vertex-pipelines` | Artifact Registry repository ID (must be KFP format) |
| `VERTEX_STAGING_BUCKET_NAME` | `my-staging-bucket` | GCS bucket name for pipeline staging, **without** the `gs://` prefix |
| `VERTEX_SERVICE_ACCOUNT` | `my-sa@project.iam.gserviceaccount.com` | Full email of the service account used for pipeline execution |

### How `.env` loading works

The `--env-file` flag uses [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) to load variables from the file.
Variables defined in the `.env` file **override** existing environment variables.
No default value for `--env-file` is provided, so you must explicitly pass it — this prevents accidentally deploying to the wrong project.

!!! tip "Multiple environments"
    Use separate env files for each environment: `dev.env`, `stg.env`, `prd.env`. Then deploy with:
    ```bash
    vertex-deployer deploy my_pipeline --env-file dev.env --run
    vertex-deployer deploy my_pipeline --env-file prd.env --schedule --cron "0_9_*_*_1-5"
    ```
