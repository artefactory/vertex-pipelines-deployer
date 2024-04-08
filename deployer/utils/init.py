from pathlib import Path

import typer
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


def build_default_folder_structure(deployer_settings: DeployerSettings):
    """Create the default folder structure for the Vertex Pipelines project."""
    vertex_folder = deployer_settings.pipelines_root_path.parent

    _create_file_or_dir(deployer_settings.pipelines_root_path)
    _create_file_or_dir(deployer_settings.config_root_path)
    for folder in ["components", "lib"]:
        _create_file_or_dir(vertex_folder / folder)

    env_content = "\n".join(
        f"{field}=" for field in VertexPipelinesSettings.model_json_schema()["required"]
    )
    _create_file_or_dir(Path("./template.env"), env_content)
    _create_file_or_dir(vertex_folder / "Makefile", (TEMPLATES_PATH / "Makefile").read_text())
    for template_file in ["cloudbuild_local.yaml", "Dockerfile"]:
        _create_file_or_dir(
            vertex_folder / "deployment" / template_file,
            (TEMPLATES_PATH / template_file).read_text(),
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
