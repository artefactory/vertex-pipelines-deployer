from pathlib import Path

import typer
from jinja2 import Environment, FileSystemLoader
from rich.prompt import Prompt

from deployer.constants import TEMPLATES_PATH
from deployer.settings import (
    DeployerSettings,
    find_pyproject_toml,
    update_pyproject_toml,
)
from deployer.utils.config import (
    VertexPipelinesSettings,
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


def _create_file_or_dir(path: Path, text: str = ""):
    """Create a file (if text is provided) or a directory at path. Warn if path exists."""
    if path.exists():
        console.print(f"Path '{path}' already exists. Skipping creation of path.", style="yellow")
    else:
        if text:
            path.touch()
            path.write_text(text)
        else:
            path.mkdir(parents=True)


def _create_file_from_template(path: Path, template_path: Path, **kwargs):
    """Create a file at path from a template file."""
    env = Environment(loader=FileSystemLoader(str(template_path.parent)), autoescape=True)
    template = env.get_template(template_path.name)
    if path.exists():
        console.print(f"Path '{path}' already exists. Skipping creation of path.", style="yellow")
    else:
        path.write_text(template.render(**kwargs))


def build_default_folder_structure(deployer_settings: DeployerSettings):
    """Create the default folder structure for the Vertex Pipelines project."""
    vertex_folder_path = deployer_settings.pipelines_root_path.parent
    dockerfile_path = vertex_folder_path / "deployment" / "Dockerfile"
    cloud_build_path = vertex_folder_path / "deployment" / "cloudbuild.yaml"
    build_base_image_path = vertex_folder_path / "deployment" / "build_base_image.sh"

    # Create the folder structure
    _create_file_or_dir(deployer_settings.pipelines_root_path)
    _create_file_or_dir(deployer_settings.config_root_path)
    for folder in ["components", "deployment", "lib"]:
        _create_file_or_dir(vertex_folder_path / folder)

    # Create the files
    env_content = "\n".join(
        f"{field}=" for field in VertexPipelinesSettings.model_json_schema()["required"]
    )
    _create_file_or_dir(Path("./template.env"), env_content)
    _create_file_or_dir(
        Path("requirements.txt"), (TEMPLATES_PATH / "requirements.txt").read_text()
    )

    template_files_mapping = [
        ("cloudbuild_local.jinja", cloud_build_path, {"dockerfile_path": dockerfile_path}),
        ("build_base_image.jinja", build_base_image_path, {"cloud_build_path": cloud_build_path}),
        ("Dockerfile.jinja", dockerfile_path, {"vertex_folder_path": vertex_folder_path}),
    ]

    for template_name, path, context in template_files_mapping:
        _create_file_from_template(
            path=path, template_path=TEMPLATES_PATH / template_name, **context
        )

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
    vertex_folder_path = deployer_settings.pipelines_root_path.parent
    build_base_image_path = vertex_folder_path / "deployment" / "build_base_image.sh"

    instructions = (
        "Now that your deployer is configured, make sure that you're also done with the setup:\n"
        "You should have:\n"
        "- Set up your GCP project and enabled the correct APIs\n"
        "- Created an artifact repository (Docker format) for your images "
        "and an artifact repository (KFP format) for your pipelines\n"
        "- Created a GCS bucket for Vertex Pipeline staging\n"
        "- Created a service account with the correct permissions for your pipelines\n"
        "Now you can write the code for your components pipelines, Dockerfile, and requirements\n"
        "If you have done all of this, you're ready to start building your pipelines! :tada:\n"
        "Here are the commands you need to run to build your project:\n"
        "1. Build the base image:\n"
        "```bash\n"
        f"bash {build_base_image_path}\n"
        "```"
    )

    console.print(instructions, style="blue")
