import importlib
from enum import Enum
from pathlib import Path
from typing import Optional

from kfp.components import graph_component
from loguru import logger
from pydantic import ValidationError
from rich.table import Table

from deployer.utils.logging import console


def make_enum_from_python_package_dir(dir_path: Path, raise_if_not_found: bool = False) -> Enum:
    """Create an Enum of file names without extention from a directory of python modules."""
    dir_path_ = Path(dir_path)
    if raise_if_not_found and not dir_path_.exists():
        raise FileNotFoundError(f"Directory {dir_path_} not found.")
    file_paths = dir_path_.glob("*.py")
    enum_dict = {x.stem: x.stem for x in file_paths if x.stem != "__init__"}
    FileNamesEnum = Enum("PipelineNames", enum_dict)
    return FileNamesEnum


def import_pipeline_from_dir(dirpath: Path, pipeline_name: str) -> graph_component.GraphComponent:
    """Import a pipeline from a directory."""
    if dirpath.startswith("."):
        dirpath = dirpath[1:]
    parent_module = ".".join(Path(dirpath).parts)
    module_path = f"{parent_module}.{pipeline_name}"

    try:
        pipeline_module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        raise e
    except Exception as e:
        raise ImportError(
            f"Error while importing pipeline from {module_path}: {e.__repr__()}"
        ) from e

    try:
        pipeline: Optional[graph_component.GraphComponent] = pipeline_module.pipeline
    except AttributeError as e:
        raise ImportError(
            f"Pipeline {module_path}:pipeline not found. "
            "Please check that the pipeline is correctly defined and named."
        ) from e

    logger.debug(f"Pipeline {module_path} imported successfully.")

    return pipeline


def print_check_results_table(to_check: dict[str, list], validation_error: ValidationError = None):
    """This function prints a table of check results.

    Args:
        to_check (dict[str, list]): A dictionary containing the pipelines to check.
        validation_error (ValidationError): The validation error if any occurred during the check.
    """
    val_error_dict = validation_error.errors() if validation_error else {}
    parsed_val_error_dict = {
        p: [v for v in val_error_dict if v["loc"][1] == p] for p in to_check.keys()
    }

    table = Table(
        show_header=True,
        header_style="bold",
        show_lines=True,
    )

    table.add_column("Pipeline")
    table.add_column("Pipeline Error Message")
    table.add_column("Config Path")
    table.add_column("Config Error Type")
    table.add_column("Attribute")
    table.add_column("Config Error Message")

    for pipeline_name, config_filepaths in to_check.items():
        errors = parsed_val_error_dict[pipeline_name]
        if len(errors) == 0:
            for config_filepath in config_filepaths:
                table.add_row(
                    pipeline_name, None, config_filepath.name, None, None, None, style="green"
                )
            if len(config_filepaths) == 0:
                table.add_row(
                    pipeline_name, None, "No configs found", None, None, None, style="bold yellow"
                )
        elif len(errors) == 1 and len(errors[0]["loc"]) == 2:
            table.add_row(pipeline_name, errors[0]["msg"], None, None, None, None, style="red")
        else:
            for config_filepath in config_filepaths:
                printed = False
                for error in errors:
                    if error["loc"][3] == config_filepath.name:
                        table.add_row(
                            pipeline_name,
                            None,
                            config_filepath.name,
                            error["type"],
                            error["loc"][4],
                            error["msg"],
                            style="red",
                        )
                        printed = True
                if not printed:
                    table.add_row(
                        pipeline_name, None, config_filepath.name, None, None, None, style="green"
                    )

    table.columns = [c for c in table.columns if "".join(c._cells) != ""]

    console.print(table)
