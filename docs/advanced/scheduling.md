# Scheduling Pipelines

Vertex Deployer supports creating recurring pipeline schedules on Vertex AI using cron expressions.

## Basic usage

To schedule a pipeline, use the `--schedule` flag with a `--cron` expression:

```bash
vertex-deployer deploy my_pipeline \
    --compile \
    --upload \
    --schedule \
    --cron "0_9_*_*_1-5" \
    --env-file .env \
    --tags latest
```

!!! note "Cron expression format"
    Because the CLI uses spaces to separate arguments, **replace spaces with underscores** in your cron expression.
    For example, `0 9 * * 1-5` becomes `0_9_*_*_1-5`.

## Cron expression examples

| Expression | Schedule |
|---|---|
| `0_9_*_*_*` | Every day at 9:00 AM |
| `0_9_*_*_1-5` | Every weekday at 9:00 AM |
| `0_0_1_*_*` | First day of every month at midnight |
| `0_*/6_*_*_*` | Every 6 hours |
| `30_14_*_*_1` | Every Monday at 2:30 PM |

## Timezone

By default, schedules use the `Europe/Paris` timezone. You can change this with `--scheduler-timezone`:

```bash
vertex-deployer deploy my_pipeline \
    --schedule \
    --cron "0_9_*_*_*" \
    --scheduler-timezone "US/Eastern" \
    --env-file .env
```

The timezone must be a valid [IANA time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) string (e.g. `Europe/London`, `America/New_York`, `Asia/Tokyo`).

You can set a default timezone in `pyproject.toml` to avoid passing it every time:

```toml title="pyproject.toml"
[tool.vertex_deployer.deploy]
scheduler-timezone = "US/Eastern"
```

## Replacing a previous schedule

By default, creating a schedule does not remove previous schedules for the same pipeline. To delete the most recent existing schedule before creating a new one, use `--delete-last-schedule`:

```bash
vertex-deployer deploy my_pipeline \
    --schedule \
    --cron "0_9_*_*_*" \
    --delete-last-schedule \
    --env-file .env
```

!!! warning
    Only the most recent schedule for the pipeline is deleted. If you have multiple schedules, you may need to clean up older ones manually in the GCP console.

## Requirements

Scheduling requires:

- The pipeline to be uploaded to **Google Artifact Registry** (the `--upload` flag or a previously uploaded version with a `--tags` reference)
- The `GAR_LOCATION` and `GAR_PIPELINES_REPO_ID` environment variables to be set
- A valid `VERTEX_SERVICE_ACCOUNT` with the `aiplatform.user` role

## Programmatic usage

You can also schedule pipelines using the Python API:

```python
from deployer.pipeline_deployer import VertexPipelineDeployer

deployer = VertexPipelineDeployer(
    pipeline_name="my_pipeline",
    pipeline_func=my_pipeline_func,
    project_id="my-project",
    region="europe-west1",
    staging_bucket_name="my-staging-bucket",
    service_account="my-sa@my-project.iam.gserviceaccount.com",
    gar_location="europe-west1",
    gar_repo_id="my-pipelines-repo",
)

deployer.compile().upload_to_registry(tags=["latest"]).schedule(
    cron="0 9 * * 1-5",
    enable_caching=True,
    scheduler_timezone="Europe/Paris",
)
```
