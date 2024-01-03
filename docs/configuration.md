## Three types of settings

There are three types of settings in the project:

- [**Vertex Deployer configuration**](#vertex-deployer-configuration): settings of the deployer itself, which is used to deploy the project.
- [**Pipelines config files**](#pipelines-config-files): configuration of the pipelines, in TOML/JSON/Python format. These files are the arguments to your pipelines.
- [**Vertex deployment settings**](#vertex-deployment-settings): used only by the deploy command, it consists of a few env variables to declare / add to `.env` file to deploy a pipeline, such as `PROJECT_ID`, `GCP_REGION`, `VERTEX_STAGING_BUCKET_NAME`, etc.

## Vertex Deployer configuration

You can override default options for specific CLI commands in the pyproject.toml file, under the `[tool.vertex_deployer]` section.
You can also override global deployer options such as logging level, or pipelines / config root path to better fit your repo structure.

```toml title="pyproject.toml"
[tool.vertex-deployer]
log-level = "INFO"
pipelines-root-path = "./vertex/pipelines"
config-root-path = "./configs"

[tool.vertex-deployer.deploy]
enable-cache = true
env-file = "example.env"
compile = true
upload = true
run = true
tags = ["my-tag"]
experiment-name = "my-experiment"
local-package-path = "."
config-filepath = "vertex/configs/dummy_pipeline/config_test.json"
```

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
These variables include the GCP project ID, region, and other settings related to the Google Cloud resources used by Vertex Pipelines.

These settings can be specified in an `.env` file or exported as environment variables. An example `.env` file might look like this:
```bash
PROJECT_ID=your-gcp-project-id
GCP_REGION=europe-west1
GAR_LOCATION=europe-west1
GAR_PIPELINES_REPO_ID=your-gar-kfp-repo-id
VERTEX_STAGING_BUCKET_NAME=your-vertex-staging-bucket-name
VERTEX_SERVICE_ACCOUNT=your-vertex-service-account
```

It is important to ensure that these settings are correctly configured before deploying a pipeline, as they will affect where and how the pipeline is executed.
