import sys
from pathlib import Path
from typing import List

import typer
from loguru import logger
from pydantic import ValidationError
from typing_extensions import Annotated

from deployer.constants import (
    CONFIG_ROOT_PATH,
    DEFAULT_LOCAL_PACKAGE_PATH,
    DEFAULT_TAGS,
    PIPELINE_MINIMAL_TEMPLATE,
    PIPELINE_ROOT_PATH,
    PYTHON_CONFIG_TEMPLATE,
)
from deployer.utils.config import (
    ConfigType,
    list_config_filepaths,
    load_config,
    load_vertex_settings,
)
from deployer.utils.logging import LoguruLevel, console
from deployer.utils.utils import (
    import_pipeline_from_dir,
    make_enum_from_python_package_dir,
    print_check_results_table,
    print_pipelines_list,
)


def display_version_and_exit(value: bool):
    if value:
        from deployer import __version__

        typer.echo(f"version: {__version__}")
        raise typer.Exit()


app = typer.Typer(no_args_is_help=True, rich_help_panel="rich", rich_markup_mode="markdown")


@app.callback(name="set_logger")
def cli_set_logger(
    ctx: typer.Context,
    log_level: Annotated[
        LoguruLevel, typer.Option("--log-level", "-log", help="Set the logging level.")
    ] = LoguruLevel.INFO,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            callback=display_version_and_exit,
            help="Display the version number and exit.",
        ),
    ] = False,
):
    logger.configure(handlers=[{"sink": sys.stderr, "level": log_level}])


PipelineName = make_enum_from_python_package_dir(PIPELINE_ROOT_PATH)


@app.command(no_args_is_help=True)
def deploy(  # noqa: C901
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
    cron: Annotated[
        str,
        typer.Option(
            help="Cron expression for scheduling the pipeline."
            " To pass it to the CLI, use hyphens e.g. '0-10-*-*-*'."
        ),
    ] = None,
    delete_last_schedule: Annotated[
        bool,
        typer.Option(
            "--delete-last-schedule",
            "-dls",
            help="Whether to delete the previous schedule before creating a new one.",
        ),
    ] = False,
    tags: Annotated[
        List[str], typer.Option(help="The tags to use when uploading the pipeline.")
    ] = DEFAULT_TAGS,
    config_filepath: Annotated[
        Path,
        typer.Option(
            "--config-filepath",
            "-cfp",
            help="Path to the json/py file with parameter values and input artifacts"
            " to use when running the pipeline.",
            exists=True,
            dir_okay=False,
            file_okay=True,
        ),
    ] = None,
    config_name: Annotated[
        str,
        typer.Option(
            "--config-name",
            "-cn",
            help="Name of the json/py file with parameter values and input artifacts"
            " to use when running the pipeline. It must be in the pipeline config dir."
            " e.g. `config_dev.json` for `./vertex/configs/{pipeline-name}/config_dev.json`.",
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
    """Compile, upload, run and schedule pipelines."""
    vertex_settings = load_vertex_settings(env_file=env_file)

    if schedule:
        if cron is None or cron == "":
            raise typer.BadParameter("--cron must be specified to schedule a pipeline")
    if run or schedule:
        if config_filepath is None and config_name is None:
            raise typer.BadParameter(
                "Both --config-filepath and --config-name are missing."
                " Please specify at least one to run or schedule a pipeline."
            )
        if config_filepath is not None and config_name is not None:
            raise typer.BadParameter(
                "Both --config-filepath and --config-name are provided."
                " Please specify only one to run or schedule a pipeline."
            )

    pipeline_func = import_pipeline_from_dir(PIPELINE_ROOT_PATH, pipeline_name.value)

    from deployer.pipeline_deployer import VertexPipelineDeployer

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
        if config_name is not None:
            config_filepath = Path(CONFIG_ROOT_PATH) / pipeline_name.value / config_name
        parameter_values, input_artifacts = load_config(config_filepath)

    if compile:
        with console.status("Compiling pipeline..."):
            deployer.compile()

    if upload:
        with console.status("Uploading pipeline..."):
            deployer.upload_to_registry(tags=tags)

    if run:
        with console.status("Running pipeline..."):
            deployer.run(
                enable_caching=enable_caching,
                parameter_values=parameter_values,
                experiment_name=experiment_name,
                input_artifacts=input_artifacts,
                tag=tags[0] if tags else None,
            )

    if schedule:
        with console.status("Scheduling pipeline..."):
            cron = cron.replace("-", " ")  # ugly fix to allow cron expression as env variable
            deployer.schedule(
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
    config_filepath: Annotated[
        Path,
        typer.Option(
            "--config-filepath",
            "-cfp",
            help="Path to the json/py file with parameter values and input artifacts"
            "to check. If not specified, all config files in the pipeline dir will be checked.",
            exists=True,
            dir_okay=False,
            file_okay=True,
        ),
    ] = None,
    raise_error: Annotated[
        bool,
        typer.Option(
            "--raise-error / --no-raise-error",
            "-re / -nre",
            help="Whether to raise an error if the pipeline is not valid.",
        ),
    ] = False,
):
    """Check that pipelines are valid.

    Checking that a pipeline is valid includes:

    * Checking that the pipeline can be imported. It must be a valid python module with a
    `{pipeline_name}` function decorated with `@kfp.dsl.pipeline`.

    * Checking that the pipeline can be compiled using `kfp.compiler.Compiler`.

    * Checking that config files in `{CONFIG_ROOT_PATH}/{pipeline_name}` are corresponding to the
    pipeline parameters definition, using Pydantic.

    ---

    **This command can be used to check pipelines in a Continuous Integration workflow.**
    """
    if all and pipeline_name is not None:
        raise typer.BadParameter("Please specify either --all or a pipeline name")

    if len(PipelineName.__members__) == 0:
        raise ValueError(
            "No pipeline found. Please check that the pipeline root path is correct"
            f" ('{PIPELINE_ROOT_PATH}')"
        )

    from deployer.pipeline_checks import Pipelines

    if all:
        logger.info("Checking all pipelines")
        pipelines_to_check = PipelineName.__members__.values()
    elif pipeline_name is not None:
        logger.info(f"Checking pipeline {pipeline_name}")
        pipelines_to_check = [pipeline_name]
    if config_filepath is None:
        to_check = {
            p.value: list_config_filepaths(CONFIG_ROOT_PATH, p.value) for p in pipelines_to_check
        }
    else:
        to_check = {p.value: [config_filepath] for p in pipelines_to_check}

    try:
        with console.status("Checking pipelines..."):
            Pipelines.model_validate(
                {
                    "pipelines": {
                        p: {"pipeline_name": p, "config_paths": config_filepaths}
                        for p, config_filepaths in to_check.items()
                    }
                }
            )
    except ValidationError as e:
        if raise_error:
            raise e
        print_check_results_table(to_check, e)
        sys.exit(1)
    else:
        print_check_results_table(to_check)


@app.command()
def list(
    with_configs: Annotated[
        bool,
        typer.Option(
            "--with-configs / --no-configs", "-wc / -nc ", help="Whether to list config files."
        ),
    ] = False
):
    """List all pipelines."""
    if len(PipelineName.__members__) == 0:
        logger.warning(
            "No pipeline found. Please check that the pipeline root path is"
            f" correct (current: '{PIPELINE_ROOT_PATH}')"
        )
        raise typer.Exit()

    if with_configs:
        pipelines_dict = {
            p.name: list_config_filepaths(CONFIG_ROOT_PATH, p.name)
            for p in PipelineName.__members__.values()
        }
    else:
        pipelines_dict = {p.name: [] for p in PipelineName.__members__.values()}

    print_pipelines_list(pipelines_dict, with_configs)


@app.command(no_args_is_help=True)
def create(
    pipeline_name: Annotated[
        str,
        typer.Argument(..., help="The name of the pipeline to create."),
    ],
    config_type: Annotated[
        ConfigType,
        typer.Option("--config-type", "-ct", help="The type of the config to create."),
    ] = ConfigType.json,
):
    """Create files structure for a new pipeline."""
    logger.info(f"Creating pipeline {pipeline_name}")

    pipeline_filepath = Path(PIPELINE_ROOT_PATH) / f"{pipeline_name}.py"
    pipeline_filepath.touch(exist_ok=False)
    pipeline_filepath.write_text(PIPELINE_MINIMAL_TEMPLATE.format(pipeline_name=pipeline_name))

    config_dirpath = Path(CONFIG_ROOT_PATH) / pipeline_name
    config_dirpath.mkdir(exist_ok=False)
    for config_name in ["test", "dev", "prod"]:
        config_filepath = config_dirpath / f"{config_name}.{config_type}"
        config_filepath.touch(exist_ok=False)
        if config_type == ConfigType.py:
            config_filepath.write_text(PYTHON_CONFIG_TEMPLATE)

    logger.info(f"Pipeline {pipeline_name} created with configs in {config_dirpath}")
