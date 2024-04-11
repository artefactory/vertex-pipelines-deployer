from pathlib import Path

import typer
from jinja2 import Environment, FileSystemLoader
from rich.prompt import Prompt

from deployer import constants
from deployer.settings import (
    DeployerSettings,
    find_pyproject_toml,
    update_pyproject_toml,
)
from deployer.utils.console import ask_user_for_model_fields, console


def configure_deployer():
    """Configure the deployer settings."""
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

    return new_deployer_settings


def _create_dir(path: Path):
    """Create a directory at path. Warn if path exists."""
    if path.exists():
        console.print(f"Directory '{path}' already exists. Skipping creation.", style="yellow")
    else:
        path.mkdir(parents=True)


def _create_file_from_template(path: Path, template_path: Path, **kwargs):
    """Create a file at path from a template file."""
    try:
        env = Environment(loader=FileSystemLoader(str(template_path.parent)), autoescape=True)
        template = env.get_template(template_path.name)
        content = template.render(**kwargs)
        if path.exists():
            console.print(
                f"Path '{path}' already exists. Skipping creation of path.", style="yellow"
            )
        else:
            path.write_text(content)
    except Exception as e:
        console.print(f"An error occurred while creating the file from template: {e}", style="red")


def build_default_folder_structure(deployer_settings: DeployerSettings):
    """Create the default folder structure for the Vertex Pipelines project."""
    vertex_folder_path = deployer_settings.vertex_folder_path
    dockerfile_path = vertex_folder_path / "deployment" / "Dockerfile"
    cloud_build_path = vertex_folder_path / "deployment" / "cloudbuild.yaml"
    build_base_image_path = vertex_folder_path / "deployment" / "build_base_image.sh"
    requirements_path = Path("./deployer-requirements.txt")
    deployer_env_path = Path("./deployer.env")

    # Create the folder structure
    for folder in ["configs", "components", "deployment", "lib", "pipelines"]:
        _create_dir(vertex_folder_path / folder)

    # Create the files
    template_files_mapping = [
        (constants.DEPLOYER_ENV_TEMPLATE, deployer_env_path, {}),
        (constants.DEPLOYER_REQUIREMENTS_TEMPLATE, requirements_path, {}),
        (
            constants.CLOUDBUILD_LOCAL_TEMPLATE,
            cloud_build_path,
            {"dockerfile_path": dockerfile_path},
        ),
        (
            constants.BUILD_BASE_IMAGE_TEMPLATE,
            build_base_image_path,
            {"cloud_build_path": cloud_build_path},
        ),
        (
            constants.DOCKERFILE_TEMPLATE,
            dockerfile_path,
            {"vertex_folder_path": vertex_folder_path},
        ),
    ]

    for template_path, path, context in template_files_mapping:
        _create_file_from_template(path=path, template_path=template_path, **context)

    console.print("Complete folder structure created :sparkles:", style="blue")


def create_initial_pipeline(ctx: typer.Context, deployer_settings: DeployerSettings):
    """Create an initial pipeline with the provided settings."""
    from deployer.cli import create_pipeline

    wrong_name = True
    while wrong_name:
        pipeline_name = Prompt.ask("What is the name of the pipeline?")

        try:
            config_type = deployer_settings.create.config_type.name
            create_pipeline(ctx, pipeline_names=[pipeline_name], config_type=config_type)
        except typer.BadParameter as e:
            console.print(e, style="red")
        except FileExistsError:
            console.print(
                f"Pipeline '{pipeline_name}' already exists. Skipping creation.",
                style="yellow",
            )
        else:
            wrong_name = False


def show_commands(deployer_settings: DeployerSettings):
    """Show the commands to run to build the project."""
    vertex_folder_path = deployer_settings.vertex_folder_path
    build_base_image_path = vertex_folder_path / "deployment" / "build_base_image.sh"

    instructions = (
        "\n"
        "Now that your deployer is configured, make sure that you're also done with the setup!\n"
        "You can find all the instructions in the README.md file.\n"
        "\n"
        "If your setup is complete you're ready to start building your pipelines! :tada:\n"
        "Here are the commands you need to run to build your project:\n"
        "\n"
        "1. Build the base image:\n"
        f"$ bash {build_base_image_path}\n"
        "\n"
        "2. Check all the pipelines:\n"
        "$ vertex-deployer check --all\n"
        "\n"
        "3. Deploy a pipeline and run it:\n"
        "$ vertex-deployer deploy pipeline_name --run\n"
        "If not set during configuration, you will need to provide the config path or name:\n"
        "$ vertex-deployer deploy pipeline_name --cfp=path/to/your/config.type\n"
        "\n"
        "4. Schedule a pipeline:\n"
        "you can add the following flags to the deploy command if not set in your config:\n"
        "--schedule --cron=cron_expression --scheduler-timezone=IANA_time_zone\n"
    )

    console.print(instructions, style="blue")
