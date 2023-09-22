import sys
from pathlib import Path

import typer
from loguru import logger
from typing_extensions import Annotated

from deployer.constants import (
    DEFAULT_LOCAL_PACKAGE_PATH,
    DEFAULT_TAGS,
    PIPELINE_ROOT_PATH,
)
from deployer.pipeline_checks import Pipelines
from deployer.pipelines_deployer import VertexPipelineDeployer
from deployer.utils import (
    LoguruLevel,
    import_pipeline_from_dir,
    load_config,
    load_vertex_settings,
    make_pipeline_names_enum_from_dir,
)

app = typer.Typer(no_args_is_help=True, rich_help_panel="rich", rich_markup_mode="markdown")


@app.callback(name="set_logger")
def cli_set_logger(
    log_level: Annotated[LoguruLevel, typer.Option("--log-level", "-log")] = LoguruLevel.INFO
):
    logger.configure(handlers=[{"sink": sys.stderr, "level": log_level}])


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
    parameter_values_filepath: Annotated[
        Path,
        typer.Option(
            "--parameter-values-filepath",
            "-pv",
            help="Path to the json configuration file to use when running the pipeline.",
            exists=True,
            dir_okay=False,
            file_okay=True,
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
            help="Local dir path where pipelines will be compiled.",
            dir_okay=True,
            file_okay=False,
            resolve_path=True,
        ),
    ] = DEFAULT_LOCAL_PACKAGE_PATH,
):
    """Deploy and manage Vertex AI Pipelines."""
    if env_file is not None:
        vertex_settings = load_vertex_settings(env_file=env_file)

    pipeline_func = import_pipeline_from_dir(PIPELINE_ROOT_PATH, pipeline_name.value)

    deployer = VertexPipelineDeployer(
        project_id=vertex_settings.PROJECT_ID,
        region=vertex_settings.GCP_REGION,
        staging_bucket_name=vertex_settings.VERTEX_STAGING_BUCKET_NAME,
        service_account=vertex_settings.VERTEX_SERVICE_ACCOUNT,
        pipeline_name=pipeline_name.value,
        pipeline_func=pipeline_func,
        gar_location=vertex_settings.GAR_LOCATION,
        gar_repo_id=vertex_settings.GAR_PIPELINES_REPO_ID,
        local_package_path=local_package_path,
    )

    if run or schedule:
        if parameter_values_filepath is None:
            raise ValueError(
                "`parameter_values_filepath` must be specified"
                " when running or scheduling the pipeline"
            )
        parameter_values = load_config(parameter_values_filepath)

    if compile:
        deployer.compile()

    if upload:
        deployer.upload_to_registry(tags=tags)

    if run:
        deployer.run(
            enable_caching=enable_caching,
            parameter_values=parameter_values,
            experiment_name=experiment_name,
        )

    if schedule:
        if cron is None:
            raise ValueError("`cron` must be specified when scheduling the pipeline")
        cron = cron.replace("-", " ")  # ugly fix to allow cron expression as env variable
        deployer.create_pipeline_schedule(
            cron=cron,
            enable_caching=enable_caching,
            parameter_values=parameter_values,
            tag=tags[0] if tags else None,
            delete_last_schedule=delete_last_schedule,
        )


@app.command(no_args_is_help=True)
def check(
    pipeline_name: Annotated[
        PipelineName,
        typer.Argument(..., help="The name of the pipeline to run."),
    ] = None,
    all: Annotated[
        bool, typer.Option("--all", "-a", help="Whether to check all pipelines.")
    ] = False,
):
    """Check that all pipelines are valid.

    Checking that a pipeline is valid includes:

    * Checking that the pipeline can be imported. It must be a valid python module with a
    `pipeline` function decorated with `@kfp.dsl.pipeline`.

    * Checking that the pipeline can be compiled using `kfp.compiler.Compiler`.

    * Checking that config files in `{CONFIG_ROOT_PATH}/{pipeline_name}` are corresponding to the
    pipeline parameters definition, using Pydantic.

    ---

    **This command can be used to check pipelines in a Continuous Integration workflow.**
    """
    if len(PipelineName.__members__) == 0:
        raise ValueError(
            "No pipeline found. Please check that the pipeline root path is correct"
            f" ('{PIPELINE_ROOT_PATH}')"
        )

    if all:
        logger.info("Checking all pipelines")
        pipelines_to_check = PipelineName.__members__.values()
    elif pipeline_name is not None:
        logger.info(f"Checking pipeline {pipeline_name}")
        pipelines_to_check = [pipeline_name]
    else:
        raise ValueError("Please specify either --all or a pipeline name")

    pipelines = Pipelines.model_validate(
        {"pipelines": {p.value: {"pipeline_name": p.value} for p in pipelines_to_check}}
    )

    log_message = "Checked pipelines and config paths:\n"
    for pipeline in pipelines.pipelines.values():
        log_message += f"- {pipeline.pipeline_name.value}:\n"
        for config_path in pipeline.config_paths:
            log_message += f"  - {config_path}\n"
    logger.success(log_message)
