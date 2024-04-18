from pathlib import Path

import jinja2
from jinja2 import Environment, FileSystemLoader, meta
from rich.tree import Tree

from deployer.__init__ import __version__ as deployer_version
from deployer.constants import INSTRUCTIONS, TEMPLATES_DEFAULT_STRUCTURE, TEMPLATES_PATH
from deployer.settings import (
    DeployerSettings,
    find_pyproject_toml,
    update_pyproject_toml,
)
from deployer.utils.console import ask_user_for_model_fields, console
from deployer.utils.exceptions import TemplateFileCreationError


def ensure_pyproject_toml():
    """Ensure that a pyproject.toml file exists in the current directory."""
    pyproject_toml_filepath = find_pyproject_toml(Path.cwd().resolve())

    if pyproject_toml_filepath is None:
        console.print(
            "No pyproject.toml file found. Creating one in the current directory.",
            style="yellow",
        )
        pyproject_toml_filepath = Path("./pyproject.toml")
        pyproject_toml_filepath.touch()

    return pyproject_toml_filepath


def configure_deployer():
    """Configure the deployer settings."""
    pyproject_toml_filepath = ensure_pyproject_toml()

    set_fields = ask_user_for_model_fields(DeployerSettings)

    tags = set_fields.get("deploy", {}).get("tags", None)
    if tags:
        set_fields["deploy"]["tags"] = [tags]

    new_deployer_settings = DeployerSettings(**set_fields)

    update_pyproject_toml(pyproject_toml_filepath, new_deployer_settings)
    console.print("\n Configuration saved in pyproject.toml :sparkles:\n", style="bold blue")

    return new_deployer_settings


def _create_dir(path: Path):
    """Create a directory at path. Warn if path exists."""
    if path.exists():
        console.print(f"Directory '{path}' already exists. Skipping creation.", style="yellow")
    else:
        path.mkdir(parents=True)


def _create_file_from_template(path: Path, template_path: Path, **kwargs):
    """Create a file at path from a template file.

    Raises:
        TemplateFileCreationError: Raised when the file cannot be created from the template.
    """
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
    except (KeyError, jinja2.TemplateError, jinja2.TemplateNotFound) as e:
        raise TemplateFileCreationError(
            f"An error occurred while creating the file from template: {e}"
        ) from e
    except Exception as e:
        console.print(f"An unexpected error occurred: {e}", style="red")


def _generate_templates_mapping(
    templates_dict: dict, mapping_variables: dict, vertex_folder_path: Path
):
    """Generate the mapping of a list of templates to create and their variables."""
    templates_mapping = {}
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_PATH)), autoescape=True)
    for template, template_path in templates_dict.items():
        template_name = str(template_path.relative_to(TEMPLATES_PATH))
        template_source = env.loader.get_source(env, template_name)[0]
        parsed_content = env.parse(template_source)
        variables = meta.find_undeclared_variables(parsed_content)
        if template in [
            "deployer_env",
            "requirements_vertex",
        ]:
            new_file_path = Path(template_name.replace(".jinja", ""))
        else:
            new_file_path = vertex_folder_path / template_name.replace(".jinja", "")
        if variables:
            template_variables = {variable: mapping_variables[variable] for variable in variables}
            templates_mapping[new_file_path] = (template_path, template_variables)
        else:
            templates_mapping[new_file_path] = (template_path, {})
    return templates_mapping


def build_default_folder_structure(deployer_settings: DeployerSettings):
    """Create the default folder structure for the Vertex Pipelines project."""
    vertex_folder_path = deployer_settings.vertex_folder_path
    dockerfile_path = vertex_folder_path / str(
        TEMPLATES_DEFAULT_STRUCTURE["dockerfile"].relative_to(TEMPLATES_PATH)
    ).replace(".jinja", "")
    cloud_build_path = vertex_folder_path / str(
        TEMPLATES_DEFAULT_STRUCTURE["cloudbuild_local"].relative_to(TEMPLATES_PATH)
    ).replace(".jinja", "")

    # Create the folder structure
    for folder in ["configs", "components", "deployment", "lib", "pipelines"]:
        _create_dir(vertex_folder_path / folder)

    mapping_variables = {
        "cloud_build_path": cloud_build_path,
        "dockerfile_path": dockerfile_path,
        "vertex_folder_path": vertex_folder_path,
        "deployer_version": deployer_version,
    }

    templates_mapping = _generate_templates_mapping(
        TEMPLATES_DEFAULT_STRUCTURE, mapping_variables, vertex_folder_path
    )

    # Create the files
    for new_file_path, (template_path, content) in templates_mapping.items():
        _create_file_from_template(new_file_path, template_path, **content)

    console.print("\n Complete folder structure created :sparkles: \n", style="bold blue")

    tree = generate_tree(vertex_folder_path)
    console.print(tree, "\n")


def generate_tree(vertex_folder_path: Path):
    """Generate a tree of the folder structure."""
    root = Tree("your_project_root", style="blue", guide_style="bold green")
    vertex_node = root.add(
        f":file_folder: [bold magenta]{vertex_folder_path.name}", guide_style="bold magenta"
    )

    folder_structure = {
        "configs": ["your_pipeline"],
        "components": ["your_component.py"],
        "deployment": ["Dockerfile", "cloudbuild_local.yaml", "build_base_image.sh"],
        "lib": ["your_lib.py"],
        "pipelines": ["your_pipeline.py"],
    }

    for folder, files in folder_structure.items():
        folder_node = vertex_node.add(f":file_folder: [yellow]{folder}", guide_style="yellow")
        for file in files:
            if folder == "configs":
                folder_node.add(file).add("config.type")
            else:
                folder_node.add(file)

    root.add("deployer.env")
    root.add("requirements-vertex.txt")
    root.add("pyproject.toml")
    return root


def show_commands(deployer_settings: DeployerSettings):
    """Show the commands to run to build the project."""
    vertex_folder_path = deployer_settings.vertex_folder_path
    build_base_image_path = vertex_folder_path / "deployment" / "build_base_image.sh"

    console.print(INSTRUCTIONS.format(build_base_image_path=build_base_image_path), style="blue")
