import importlib
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from kfp.components import graph_component
from loguru import logger
from pydantic import ValidationError
from rich.table import Table

from deployer.utils.logging import console
from deployer.utils.models import ChecksTableRow


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


def print_check_results_table(
    to_check: Dict[str, list], validation_error: Optional[ValidationError] = None
) -> None:
    """This function prints a table of check results to the console.

    Args:
        to_check (dict[str, list]): A dictionary containing the pipelines to check
            as keys and the config filepaths as values.
        validation_error (ValidationError): The validation error if any occurred during the check.
    """
    val_error_dict = validation_error.errors() if validation_error else {}
    parsed_val_error_dict = {
        p: [v for v in val_error_dict if v["loc"][1] == p] for p in to_check.keys()
    }

    table = Table(show_header=True, header_style="bold", show_lines=True)

    table.add_column("Status", justify="center")
    table.add_column("Pipeline")
    table.add_column("Pipeline Error Message")
    table.add_column("Config Path")
    table.add_column("Attribute")
    table.add_column("Config Error Type")
    table.add_column("Config Error Message")

    for pipeline_name, config_filepaths in to_check.items():
        errors = parsed_val_error_dict[pipeline_name]
        if len(errors) == 0:
            for config_filepath in config_filepaths:
                row = ChecksTableRow(
                    status="✅",
                    pipeline=pipeline_name,
                    config_path=config_filepath.name,
                )
                table.add_row(*row.model_dump().values(), style="green")
            if len(config_filepaths) == 0:
                row = ChecksTableRow(
                    status="⚠️",
                    pipeline=pipeline_name,
                    config_path="No configs found",
                )
                table.add_row(*row.model_dump().values(), style="bold yellow")

        elif len(errors) == 1 and len(errors[0]["loc"]) == 2:
            print(errors)
            row = ChecksTableRow(
                status="❌",
                pipeline=pipeline_name,
                pipeline_error_message=errors[0]["msg"],
                config_path="Could not check config files due to pipeline error.",
            )
            table.add_row(*row.model_dump().values(), style="red")

        else:
            for config_filepath in config_filepaths:
                error_rows = []
                for error in errors:
                    if error["loc"][3] == config_filepath.name:
                        error_row = {
                            "type": error["type"],
                            "attribute": error["loc"][4],
                            "msg": error["msg"],
                        }
                        error_rows.append(error_row)
                if error_rows:
                    row = ChecksTableRow(
                        status="❌",
                        pipeline=pipeline_name,
                        config_path=config_filepath.name,
                        config_error_type="\n".join([er["type"] for er in error_rows]),
                        attribute="\n".join([er["attribute"] for er in error_rows]),
                        config_error_message="\n".join([er["msg"] for er in error_rows]),
                    )
                    table.add_row(*row.model_dump().values(), style="red")
                else:
                    row = ChecksTableRow(
                        status="✅",
                        pipeline=pipeline_name,
                        config_path=config_filepath.name,
                    )
                    table.add_row(*row.model_dump().values(), style="green")

    table.columns = [c for c in table.columns if "".join(c._cells) != ""]

    console.print(table)
