import enum
import re
import sys
from pathlib import Path
from typing import List, Optional, Union

import rich.traceback
import typer
from loguru import logger
from pydantic import ValidationError
from rich.prompt import Confirm, Prompt
from typing_extensions import Annotated

from deployer import constants
from deployer.settings import (
    DeployerSettings,
    find_pyproject_toml,
    load_deployer_settings,
    update_pyproject_toml,
)
from deployer.utils.config import (
    ConfigType,
    VertexPipelinesSettings,
    list_config_filepaths,
    load_config,
    load_vertex_settings,
    validate_or_log_settings,
)
from deployer.utils.console import ask_user_for_model_fields, console
from deployer.utils.logging import LoguruLevel
from deployer.utils.utils import (
    dict_to_repr,
    import_pipeline_from_dir,
    make_enum_from_python_package_dir,
    print_check_results_table,
    print_pipelines_list,
)

rich.traceback.install()


def display_version_and_exit(value: bool):
    if value:
        from deployer import __version__

        typer.echo(f"version: {__version__}")
        raise typer.Exit()


app = typer.Typer(
    no_args_is_help=True,
    rich_help_panel="rich",
    rich_markup_mode="markdown",
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    log_level: Annotated[
        LoguruLevel, typer.Option("--log-level", "-log", help="Set the logging level.")
    ] = constants.DEFAULT_LOG_LEVEL,
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

    deployer_settings = load_deployer_settings()
    ctx.obj = {
        "settings": deployer_settings,
        "pipeline_names": make_enum_from_python_package_dir(deployer_settings.pipelines_root_path),
    }
    ctx.default_map = deployer_settings.model_dump(exclude_unset=True)


def pipeline_name_callback(ctx: typer.Context, value: Union[str, bool]) -> Union[str, bool]:
    """Callback to check that the pipeline name is valid."""
    if value is None:  # None is allowed for optional arguments
        return []

    pipeline_names: enum.Enum = ctx.obj["pipeline_names"]

    if len(pipeline_names.__members__) == 0:
        raise ValueError(
            "No pipelines found. Please check that the pipeline root path is correct: "
            f"'{ctx.obj['settings'].pipelines_root_path}'"
        )

    if ctx.params.get("all", False):
        to_check = [x.value for x in pipeline_names.__members__.values()]
    elif isinstance(value, str):
        to_check = [value]
    elif isinstance(value, list):
        if len(value) == 0:
            raise typer.BadParameter("No pipeline names specified.")
        to_check = value
    else:
        raise typer.BadParameter(f"Invalid value for pipeline_names: {value}")

    to_raise = [v for v in to_check if v not in pipeline_names.__members__]
    if len(to_raise) > 0:
        raise typer.BadParameter(
            f"Pipelines {to_raise} not found at '{ctx.obj['settings'].pipelines_root_path}'."
            f"\nAvailable pipelines: {list(pipeline_names.__members__)}"
        )
    return value


@app.command(no_args_is_help=True)
def deploy(  # noqa: C901
    ctx: typer.Context,
    pipeline_names: Annotated[
        List[str],
        typer.Argument(
            ..., help="The names of the pipeline to run.", callback=pipeline_name_callback
        ),
    ],
    env_file: Annotated[
        Optional[Path],
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
        Optional[str],
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
    scheduler_timezone: Annotated[
        str,
        typer.Option(
            help="Timezone for scheduling the pipeline."
            " Must be a valid string from IANA time zone database",
        ),
    ] = constants.DEFAULT_SCHEDULER_TIMEZONE,
    tags: Annotated[
        Optional[List[str]], typer.Option(help="The tags to use when uploading the pipeline.")
    ] = constants.DEFAULT_TAGS,
    config_filepath: Annotated[
        Optional[Path],
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
        Optional[str],
        typer.Option(
            "--config-name",
            "-cn",
            help="Name of the json/py file with parameter values and input artifacts"
            " to use when running the pipeline. It must be in the pipeline config dir."
            " e.g. `config_dev.json` for `./vertex/configs/{pipeline-name}/config_dev.json`.",
        ),
    ] = None,
    enable_caching: Annotated[
        Optional[bool],
        typer.Option(
            "--enable-caching / --no-cache",
            "-ec / -nec",
            help="Whether to turn on caching for the run."
            "If this is not set, defaults to the compile time settings, which are True for all"
            "tasks by default, while users may specify different caching options for individual"
            "tasks. If this is set, the setting applies to all tasks in the pipeline."
            "Overrides the compile time settings. Defaults to None.",
        ),
    ] = None,
    experiment_name: Annotated[
        Optional[str],
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
    ] = constants.DEFAULT_LOCAL_PACKAGE_PATH,
    skip_validation: Annotated[
        bool,
        typer.Option(
            "--skip-validation / --no-skip",
            "-y / -n",
            help="Whether to continue without user validation of the settings.",
        ),
    ] = True,
):
    """Compile, upload, run and schedule pipelines."""
    vertex_settings = load_vertex_settings(env_file=env_file)
    validate_or_log_settings(vertex_settings, skip_validation=skip_validation, env_file=env_file)

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
        if config_filepath is not None and len(pipeline_names) > 1:
            raise typer.BadParameter(
                "Multiple pipelines specified with --config-filepath."
                " Please specify a --config-name that will be used for each pipeline."
                " Or specify a single pipeline to use the --config-filepath."
            )

    deployer_settings: DeployerSettings = ctx.obj["settings"]

    from deployer.pipeline_deployer import VertexPipelineDeployer

    for pipeline_name in pipeline_names:
        pipeline_func = import_pipeline_from_dir(
            deployer_settings.pipelines_root_path, pipeline_name
        )

        deployer = VertexPipelineDeployer(
            project_id=vertex_settings.PROJECT_ID,
            region=vertex_settings.GCP_REGION,
            staging_bucket_name=vertex_settings.VERTEX_STAGING_BUCKET_NAME,
            service_account=vertex_settings.VERTEX_SERVICE_ACCOUNT,
            pipeline_name=pipeline_name,
            pipeline_func=pipeline_func,
            gar_location=vertex_settings.GAR_LOCATION,
            gar_repo_id=vertex_settings.GAR_PIPELINES_REPO_ID,
            local_package_path=local_package_path,
        )

        if run or schedule:
            if config_name is not None:
                config_filepath = (
                    Path(deployer_settings.config_root_path) / pipeline_name / config_name
                )
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
                    scheduler_timezone=scheduler_timezone,
                )


@app.command()
def check(
    ctx: typer.Context,
    pipeline_names: Annotated[
        Optional[List[str]],
        typer.Argument(
            ..., help="The names of the pipeline to check.", callback=pipeline_name_callback
        ),
    ] = None,
    all: Annotated[
        bool,
        typer.Option("--all", "-a", help="Whether to check all pipelines."),
    ] = False,
    config_filepath: Annotated[
        Optional[Path],
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
    warn_defaults: Annotated[
        bool,
        typer.Option(
            "--warn-defaults / --no-warn-defaults",
            "-wd / -nwd",
            help="Whether to warn when a default value is used."
            "and not overwritten in config file.",
        ),
    ] = True,
    raise_for_defaults: Annotated[
        bool,
        typer.Option(
            "--raise-for-defaults / --no-raise-for-defaults",
            "-rfd / -nrfd",
            help="Whether to raise an validation error when a default value is used."
            "and not overwritten in config file.",
        ),
    ] = False,
):
    """Check that pipelines are valid.

    Checking that a pipeline is valid includes:

    * Checking that the pipeline can be imported. It must be a valid python module with a
    `{pipeline_name}` function decorated with `@kfp.dsl.pipeline`.

    * Checking that the pipeline can be compiled using `kfp.compiler.Compiler`.

    * Checking that config files in `{config_root_path}/{pipeline_name}` are corresponding to the
    pipeline parameters definition, using Pydantic.

    ---

    **This command can be used to check pipelines in a Continuous Integration workflow.**
    """
    if all and pipeline_names:
        raise typer.BadParameter("Please specify either --all or a pipeline name")

    from deployer.pipeline_checks import Pipelines

    deployer_settings: DeployerSettings = ctx.obj["settings"]

    if all:
        # unpack enum to get list of pipeline names
        pipeline_names = [x.value for x in ctx.obj["pipeline_names"]]
    logger.info(f"Checking pipelines {pipeline_names}")

    if config_filepath is None:
        to_check = {
            p: list_config_filepaths(deployer_settings.config_root_path, p) for p in pipeline_names
        }
    else:
        to_check = {p: [config_filepath] for p in pipeline_names}

    try:
        with console.status("Checking pipelines..."):
            pipelines_model = Pipelines.model_validate(
                {
                    "pipelines": {
                        p: {
                            "pipeline_name": p,
                            "config_paths": config_filepaths,
                            "pipelines_root_path": deployer_settings.pipelines_root_path,
                            "config_root_path": deployer_settings.config_root_path,
                        }
                        for p, config_filepaths in to_check.items()
                    }
                },
                context={"raise_for_defaults": raise_for_defaults},
            )
    except ValidationError as e:
        if raise_error:
            raise e
        print_check_results_table(to_check, validation_error=e)
        sys.exit(1)
    else:
        print_check_results_table(
            to_check, pipelines_model=pipelines_model, warn_defaults=warn_defaults
        )


@app.command(name="list")
def list_pipelines(
    ctx: typer.Context,
    with_configs: Annotated[
        bool,
        typer.Option(
            "--with-configs / --no-configs", "-wc / -nc ", help="Whether to list config files."
        ),
    ] = False,
):
    """List all pipelines."""
    if with_configs:
        pipelines_dict = {
            p.name: list_config_filepaths(ctx.obj["settings"].config_root_path, p.name)
            for p in ctx.obj["pipeline_names"].__members__.values()
        }
    else:
        pipelines_dict = {p.name: [] for p in ctx.obj["pipeline_names"].__members__.values()}

    print_pipelines_list(pipelines_dict, with_configs)


@app.command(name="create")
def create_pipeline(
    ctx: typer.Context,
    pipeline_names: Annotated[
        List[str],
        typer.Argument(..., help="The names of the pipeline to create."),
    ],
    config_type: Annotated[
        ConfigType,
        typer.Option("--config-type", "-ct", help="The type of the config to create."),
    ] = ConfigType.json,
):
    """Create files structure for a new pipeline."""
    invalid_pipelines = [p for p in pipeline_names if not re.match(r"^[a-zA-Z0-9_]+$", p)]
    if invalid_pipelines:
        raise typer.BadParameter(
            f"Invalid Pipeline name(s): '{invalid_pipelines}'\n"
            "Pipeline name must only contain alphanumeric characters and underscores"
        )

    deployer_settings: DeployerSettings = ctx.obj["settings"]

    for path in [deployer_settings.pipelines_root_path, deployer_settings.config_root_path]:
        if not Path(path).is_dir():
            raise FileNotFoundError(
                f"Path '{path}' does not exist."
                " Please check that the root path is correct"
                f" or create it with 'mkdir -p {path}'."
            )

    existing_pipelines = [
        p for p in pipeline_names if (deployer_settings.pipelines_root_path / f"{p}.py").exists()
    ]
    if existing_pipelines:
        raise typer.BadParameter(f"Pipelines {existing_pipelines} already exist.")

    console.print(
        f"Creating pipeline {pipeline_names} with config type: [bold]{config_type}[/bold]"
    )

    for pipeline_name in pipeline_names:
        pipeline_filepath = deployer_settings.pipelines_root_path / f"{pipeline_name}.py"
        pipeline_filepath.touch(exist_ok=False)
        pipeline_filepath.write_text(
            constants.PIPELINE_MINIMAL_TEMPLATE.format(pipeline_name=pipeline_name)
        )

        try:
            config_dirpath = Path(deployer_settings.config_root_path) / pipeline_name
            config_dirpath.mkdir(exist_ok=True)
            for config_name in ["test", "dev", "prod"]:
                config_filepath = config_dirpath / f"{config_name}.{config_type}"
                config_filepath.touch(exist_ok=False)
                if config_type == ConfigType.py:
                    config_filepath.write_text(constants.PYTHON_CONFIG_TEMPLATE)
        except Exception as e:
            pipeline_filepath.unlink()
            raise e

        console.print(
            f"Pipeline '{pipeline_name}' created at '{pipeline_filepath}'"
            f" with config files: {[str(p) for p in config_dirpath.glob('*')]}. :sparkles:",
            style="blue",
        )


@app.command(name="init")
def init_deployer(ctx: typer.Context):  # noqa: C901
    deployer_settings: DeployerSettings = ctx.obj["settings"]

    console.print("Welcome to Vertex Deployer!", style="blue")
    console.print("This command will help you getting fired up.", style="blue")

    if Confirm.ask("Do you want to configure the deployer?"):
        pyproject_toml_filepath = find_pyproject_toml(Path.cwd().resolve())

        if pyproject_toml_filepath is None:
            console.print(
                "No pyproject.toml file found. Creating one in current directory.",
                style="yellow",
            )
            pyproject_toml_filepath = Path("./pyproject.toml")
            pyproject_toml_filepath.touch()

        set_fields = ask_user_for_model_fields(DeployerSettings)

        new_deployer_settings = DeployerSettings(**set_fields)

        update_pyproject_toml(pyproject_toml_filepath, new_deployer_settings)
        console.print("Configuration saved in pyproject.toml :sparkles:", style="blue")

    if Confirm.ask("Do you want to build default folder structure"):

        def create_file_or_dir(path: Path, text: str = ""):
            """Create a file (if text is provided) or a directory at path. Warn if path exists."""
            if path.exists():
                console.print(
                    f"Path '{path}' already exists. Skipping creation of path.", style="yellow"
                )
            else:
                if text:
                    path.touch()
                    path.write_text(text)
                else:
                    path.mkdir(parents=True)

        create_file_or_dir(deployer_settings.pipelines_root_path)
        create_file_or_dir(deployer_settings.config_root_path)
        create_file_or_dir(
            Path("./.env"), "=\n".join(VertexPipelinesSettings.model_json_schema()["required"])
        )

    if Confirm.ask("Do you want to create a pipeline?"):
        wrong_name = True
        while wrong_name:
            pipeline_name = Prompt.ask("What is the name of the pipeline?")

            try:
                create_pipeline(ctx, pipeline_names=[pipeline_name])
            except typer.BadParameter as e:
                console.print(e, style="red")
            except FileExistsError:
                console.print(
                    f"Pipeline '{pipeline_name}' already exists. Skipping creation.",
                    style="yellow",
                )
            else:
                wrong_name = False

    console.print("All done :sparkles:", style="blue")


@app.command(name="config")
def list_deployer_settings(
    ctx: typer.Context,
    all: Annotated[
        bool, typer.Option("--all", "-a", help="Whether to display all configuration values.")
    ] = False,
):
    """Display the configuration from pyproject.toml."""
    deployer_settings: DeployerSettings = ctx.obj["settings"]

    if all:
        config_repr = dict_to_repr(
            dict_=deployer_settings.model_dump(),
            subdict=deployer_settings.model_dump(exclude_unset=True),
        )
        config_str = "[italic]'*' means the value was set in config file[/italic]\n\n"
        config_str += "\n".join(config_repr)
    else:
        config_repr = dict_to_repr(dict_=deployer_settings.model_dump(exclude_unset=True))
        config_str = "\n".join(config_repr)

    console.print(config_str)
