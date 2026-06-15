# Using the Python API

While `vertex-deployer` is primarily a CLI tool, you can also use the `VertexPipelineDeployer` class directly in your Python code. This is useful for custom scripts, notebooks, or when you need more control over the deployment process.

## Basic example

```python
from deployer.pipeline_deployer import VertexPipelineDeployer
from my_project.vertex.pipelines.my_pipeline import my_pipeline

deployer = VertexPipelineDeployer(
    pipeline_name="my_pipeline",
    pipeline_func=my_pipeline,
    project_id="my-gcp-project",
    region="europe-west1",
    staging_bucket_name="my-staging-bucket",
    service_account="my-sa@my-gcp-project.iam.gserviceaccount.com",
    gar_location="europe-west1",
    gar_repo_id="my-pipelines-repo",
)

# Compile, upload, and run in one call
deployer.compile_upload_run(
    enable_caching=True,
    parameter_values={"learning_rate": 0.01, "epochs": 10},
    tags=["latest"],
)
```

## Constructor parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `pipeline_name` | `str` | Yes | Name of the pipeline (must match the `@kfp.dsl.pipeline` function name) |
| `pipeline_func` | `Callable` | Yes | The kfp pipeline function decorated with `@kfp.dsl.pipeline` |
| `run_name` | `str` | No | Custom run name displayed in the UI. Defaults to `{pipeline_name}-{tag}-{timestamp}` |
| `project_id` | `str` | No | GCP project ID |
| `region` | `str` | No | GCP region (e.g. `europe-west1`) |
| `staging_bucket_name` | `str` | No | GCS bucket name for pipeline staging (without `gs://` prefix) |
| `service_account` | `str` | No | Service account email for pipeline execution |
| `gar_location` | `str` | No | Google Artifact Registry location |
| `gar_repo_id` | `str` | No | Google Artifact Registry repository ID (KFP format) |
| `local_package_path` | `Path` | No | Local directory for compiled pipeline YAML files |

## Step-by-step usage

Each method returns `self`, so you can chain calls:

```python
# Step by step
deployer.compile()
deployer.upload_to_registry(tags=["latest", "v1.0"])
deployer.run(
    enable_caching=True,
    parameter_values={"model_name": "my-model"},
    experiment_name="my-experiment",
    tag="latest",
)

# Or chained
deployer.compile().upload_to_registry(tags=["latest"]).run(
    parameter_values={"model_name": "my-model"},
    tag="latest",
)
```

## Methods

### `compile()`

Compiles the pipeline function to a YAML file in the `local_package_path` directory using `kfp.compiler.Compiler`.

### `upload_to_registry(tags=["latest"])`

Uploads the compiled pipeline YAML to Google Artifact Registry. Requires `gar_location` and `gar_repo_id` to be set.

### `run(enable_caching, parameter_values, input_artifacts, experiment_name, tag)`

Submits a pipeline run to Vertex AI. The pipeline template is resolved from Artifact Registry if available, otherwise from the local compiled YAML.

- `enable_caching`: `None` uses compile-time defaults. `True`/`False` overrides caching for all tasks.
- `parameter_values`: Dict of pipeline parameter names to values.
- `input_artifacts`: Dict of artifact parameter names to resource IDs (e.g. `{"vertex_model": "456"}`).
- `experiment_name`: Groups runs under a Vertex Experiment. Defaults to `{pipeline_name}-experiment`.
- `tag`: Tag of the uploaded pipeline version to use from Artifact Registry.

### `compile_upload_run(enable_caching, parameter_values, experiment_name, tags)`

Convenience method that calls `compile()`, optionally `upload_to_registry()`, and `run()` in sequence.

### `schedule(cron, enable_caching, parameter_values, tag, delete_last_schedule, scheduler_timezone)`

Creates a recurring schedule for the pipeline on Vertex AI. See [Scheduling Pipelines](scheduling.md) for details.

## Running without Artifact Registry

If you don't need Artifact Registry, omit `gar_location` and `gar_repo_id`. The deployer will use the locally compiled YAML file instead:

```python
deployer = VertexPipelineDeployer(
    pipeline_name="my_pipeline",
    pipeline_func=my_pipeline,
    project_id="my-gcp-project",
    region="europe-west1",
    staging_bucket_name="my-staging-bucket",
    service_account="my-sa@my-gcp-project.iam.gserviceaccount.com",
)

deployer.compile().run(parameter_values={"learning_rate": 0.01})
```

## Full API reference

For the complete API reference with all method signatures, see the [auto-generated API docs](../api/vertex_deployer.md).
