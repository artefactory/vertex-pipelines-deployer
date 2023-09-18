import logging
import os
from pathlib import Path

import typer
from dotenv import find_dotenv, load_dotenv
from typing_extensions import Annotated

from deployer.constants import (
    DEFAULT_LOCAL_PACKAGE_PATH,
    DEFAULT_TAGS,
    PIPELINE_ROOT_PATH,
)
from deployer.deployer import VertexPipelineDeployer
from deployer.utils import (
    import_pipeline_from_dir,
    load_config,
    make_pipeline_names_enum_from_dir,
)

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

app = typer.Typer(no_args_is_help=True, rich_help_panel="rich")

PipelineName = make_pipeline_names_enum_from_dir(PIPELINE_ROOT_PATH)


@app.command(no_args_is_help=True)
def deploy(
    pipeline_name: Annotated[
        PipelineName, typer.Argument(..., help="The name of the pipeline to run.")
    ],
    env_file: Annotated[
        Path,
        typer.Option(
            help="The environment file to use.",
            exists=True,
            dir_okay=False,
            file_okay=True,
            resolve_path=True,
        ),
    ] = None,
    compile: Annotated[
        bool,
        typer.Option("--compile/--no-compile", "-c/-nc", help="Whether to compile the pipeline."),
    ] = True,
    upload: Annotated[
        bool,
        typer.Option(
            "--upload/--no-upload",
            "-u/-nu",
            help="Whether to upload the pipeline to Google Artifact Registry.",
        ),
    ] = False,
    run: Annotated[
        bool, typer.Option("--run/--no-run", "-r/-nr", help="Whether to run the pipeline.")
    ] = False,
    schedule: Annotated[
        bool,
        typer.Option(
            "--schedule/--no-schedule",
            "-s/-ns",
            help="Whether to create a schedule for the pipeline.",
        ),
    ] = False,
    cron: Annotated[str, typer.Option(help="Cron expression for scheduling the pipeline.")] = None,
    delete_last_schedule: Annotated[
        bool,
        typer.Option(
            "--delete-last-schedule",
            "-dls",
            help="Whether to delete the previous schedule before creating a new one.",
        ),
    ] = False,
    tags: Annotated[
        list[str], typer.Option(help="The tags to use when uploading the pipeline.")
    ] = DEFAULT_TAGS,
    config_name: Annotated[
        str,
        typer.Option(
            "--config-name",
            "-cn",
            help="The name of the configuration file to use when running the pipeline.",
        ),
    ] = None,
    enable_caching: Annotated[
        bool,
        typer.Option(
            "--enable-caching", "-ec", help="Whether to enable caching when running the pipeline."
        ),
    ] = False,
    experiment_name: Annotated[
        str,
        typer.Option(
            "--experiment-name",
            "-en",
            help="The name of the experiment to run the pipeline in."
            "Defaults to '{pipeline_name}-experiment'.",
        ),
    ] = None,
    local_package_path: Annotated[
        Path,
        typer.Option(
            "--local-package-path",
            "-lpp",
            help="The path to the local package to upload.",
            dir_okay=True,
            file_okay=False,
            resolve_path=True,
        ),
    ] = DEFAULT_LOCAL_PACKAGE_PATH,
):
    """Deploy and manage Vertex AI Pipelines."""
    if env_file is not None:
        find_dotenv(env_file, raise_error_if_not_found=True)
        load_dotenv(env_file)

    project_id = os.environ["PROJECT_ID"]
    region = os.environ["GCP_REGION"]
    staging_bucket_name = os.environ["VERTEX_STAGING_BUCKET_NAME"]
    service_account = os.environ["VERTEX_SERVICE_ACCOUNT"]
    pipeline_func = import_pipeline_from_dir(
        PIPELINE_ROOT_PATH, pipeline_name.value.replace("-", "_")
    )
    gar_location = os.environ["GAR_LOCATION"] if (upload or schedule) else None
    gar_repo_id = f"{os.environ['GAR_REPO_ID']}-kfp" if (upload or schedule) else None

    deployer = VertexPipelineDeployer(
        project_id=project_id,
        region=region,
        staging_bucket_name=staging_bucket_name,
        service_account=service_account,
        pipeline_name=pipeline_name.value,
        pipeline_func=pipeline_func,
        gar_location=gar_location,
        gar_repo_id=gar_repo_id,
        local_package_path=local_package_path,
    )

    if run or schedule:
        if config_name is None:
            raise ValueError(
                "`config_name` must be specified when running or scheduling the pipeline"
            )
        SELECTED_CONFIGURATION = load_config(
            config_name=config_name, pipeline_name=pipeline_name.replace("-", "_")
        )

    if compile:
        deployer.compile()

    if upload:
        deployer.upload_to_registry(tags=tags)

    if run:
        deployer.run(
            enable_caching=enable_caching,
            parameter_values=SELECTED_CONFIGURATION,
            experiment_name=experiment_name,
        )

    if schedule:
        if cron is None:
            raise ValueError("`cron` must be specified when scheduling the pipeline")
        cron = cron.replace("-", " ")  # ugly fix to allow cron expression as env variable
        deployer.create_pipeline_schedule(
            cron=cron,
            enable_caching=enable_caching,
            parameter_values=SELECTED_CONFIGURATION,
            tag=tags[0] if tags else None,
            delete_last_schedule=delete_last_schedule,
        )
