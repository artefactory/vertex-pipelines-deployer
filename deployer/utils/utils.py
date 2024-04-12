import importlib
import traceback
import warnings
from collections import defaultdict
from enum import Enum
from pathlib import Path
from types import TracebackType
from typing import Any, Callable, Dict, List, Mapping, Optional, Protocol, Union

from loguru import logger
from pydantic import BaseModel, ValidationError
from rich.table import Table

from deployer.constants import PIPELINE_CHECKS_TABLE_COLUMNS
from deployer.utils.console import console
from deployer.utils.models import ChecksTableRow


def make_enum_from_python_package_dir(dir_path: Path, raise_if_not_found: bool = False) -> Enum:
    """Create an Enum of file names without extention from a directory of python modules."""
    dir_path_ = Path(dir_path)
    if raise_if_not_found and not dir_path_.exists():
        raise FileNotFoundError(f"Directory {dir_path_} not found.")
    file_paths = dir_path_.glob("*.py")
    enum_dict = {x.stem: x.stem for x in file_paths if x.stem != "__init__"}
    file_names_enum = Enum(dir_path_.stem, enum_dict)
    return file_names_enum


class GraphComponentType(Protocol):
    """Protocol for a kfp.dsl.graph_component.GraphComponent"""

    component_spec: Any
    pipeline_func: Callable
    name: str
    description: str

    def __call__(  # noqa: D102
        self, component_spec: Any, pipeline_func: Callable, display_name: Optional[str] = None
    ): ...


def filter_lines_from(tb: TracebackType, target_file: Union[Path, str]) -> str:
    """Filters a traceback object to only show the lines from a specific file.

    Traceback objects can contain lines from multiple files (e.g. when a function is called from a
    different module).This function removes all the lines that are not related to the target file.

    Example:
        >>> traceback.print_tb(tb)
            File "path/to/file3.py", line 30, in <module>
                call_function_from_file2()
            File "path/to/file2.py", line 20, in call_function_from_file2
                call_function_from_file1()
            File "path/to/file1.py", line 10, in call_function_from_file1
                raise ValueError("Something went wrong.")
        >>> filter_lines_from(tb, "path/to/file2.py")
            File "path/to/file2.py", line 20, in call_function_from_file2
                call_function_from_file1()

    Args:
        tb (TracebackType): the traceback object to be filtered.
        target_file (Path | str): the file from which to show the traceback lines.

    Raises:
        TypeError: if target_file is not a Path or a str.

    Returns:
        str: a string containing the filtered traceback.
    """
    # ensure that the path is absolute
    if isinstance(target_file, Path):
        target_file = str(target_file.resolve())
    elif isinstance(target_file, str):
        target_file = str(Path(target_file).resolve())
    else:
        raise TypeError(f"target_file should be a Path or a str, but got {type(target_file)}.")

    filtered_traceback: list[traceback.FrameSummary] = [
        frame for frame in traceback.extract_tb(tb) if target_file in frame.filename
    ]

    if filtered_traceback:
        string_filtered_traceback = "".join(traceback.format_list(filtered_traceback))
    else:
        string_filtered_traceback = "Could not find potential source of error."

    return string_filtered_traceback


def import_pipeline_from_dir(dirpath: Path, pipeline_name: str) -> GraphComponentType:
    """Import a pipeline from a directory."""
    dirpath_ = Path(dirpath).resolve().relative_to(Path.cwd())
    parent_module = ".".join(dirpath_.parts)
    module_import_path = f"{parent_module}.{pipeline_name}"  # used with import statements
    module_folder_path = dirpath_ / f"{pipeline_name}.py"  # used as a path to a file

    try:
        pipeline_module = importlib.import_module(module_import_path)
    except ModuleNotFoundError as e:
        raise e
    except Exception as e:
        raise ImportError(
            f"Error while importing pipeline from {module_import_path}: \n    {type(e).__name__}:"
            f"{e} \n\nPotential sources of error:\n"
            f"{filter_lines_from(e.__traceback__, module_folder_path)}"
        ) from e

    try:
        pipeline: GraphComponentType = getattr(pipeline_module, pipeline_name, None)
        if pipeline is None:
            pipeline = pipeline_module.pipeline
            warnings.warn(
                f"Pipeline in `{module_import_path}` is named `pipeline` instead of "
                f"`{pipeline_name}`. This is deprecated and will be removed in a future version. "
                f"Please rename your pipeline to `{pipeline_name}`.",
                FutureWarning,
                stacklevel=1,
            )
    except AttributeError as e:
        raise ImportError(
            f"Pipeline object not found in `{module_import_path}`. "
            "Please check that the pipeline is correctly defined and named."
            f"It should be named `{pipeline_name}` or `pipeline` (deprecated)."
        ) from e

    logger.debug(f"Pipeline {module_import_path} imported successfully.")

    return pipeline


def dict_to_repr(
    dict_: dict, subdict: Optional[dict] = None, depth: int = 0, indent: int = 2
) -> List[str]:
    """Convert a dictionary to a list of strings for printing, recursively.

    Args:
        dict_ (dict): The dictionary to convert.
        subdict (dict, optional): A subdictionary to highlight in the output.
            Defaults to {}.
        depth (int, optional): The depth of the dictionary. Defaults to 0.
        indent (int, optional): The indentation level. Defaults to 2.

    Returns:
        list[str]: A list of strings representing the dictionary.
    """
    if subdict is None:
        subdict = {}

    dict_repr = []
    for k, v in dict_.items():
        if isinstance(v, Mapping):
            v_ref = subdict.get(k, {})
            dict_repr.append(" " * indent * depth + f"{k}")
            dict_repr.extend(dict_to_repr(v, v_ref, depth=depth + 1, indent=indent))
        else:
            if subdict.get(k) is not None:
                v_str = " " * indent * depth + f"[cyan]* {k}={v}[/cyan]"
            else:
                v_str = " " * indent * depth + f"[white]{k}={v}[/white]"
            dict_repr.append(v_str)
    return dict_repr


def print_pipelines_list(pipelines_dict: Dict[str, list], with_configs: bool = False) -> None:
    """This function prints a table of pipelines to the console.

    Args:
        pipelines_dict (dict[str, list]): A dictionary containing the pipelines as keys
            and the config filepaths as values.
        with_configs (bool, optional): Whether to print the config filepaths or not.
            Defaults to False.
    """
    table = Table(show_header=True, header_style="bold", show_lines=True)

    table.add_column("Pipeline")
    table.add_column("Config Files")

    for pipeline_name, config_filepaths in pipelines_dict.items():
        config_paths_str = "\n".join([c.name for c in config_filepaths])
        style = None

        if len(config_filepaths) == 0 and with_configs:
            config_paths_str = "No config files found"
            style = "yellow"

        table.add_row(pipeline_name, config_paths_str, style=style)

    if not with_configs:
        table.columns = table.columns[:1]

    console.print(table)


def print_check_results_table(
    to_check: Dict[str, list],
    pipelines_model: Optional[Any] = None,
    validation_error: Optional[ValidationError] = None,
    warn_defaults: bool = True,
) -> None:
    """Print a table of check results to the console.

    Args:
        to_check (Dict[str, list]): A dictionary containing the pipelines to check
            as keys and the config filepaths as values.
        pipelines_model (Optional[Any], optional): A Pipelines model used to retrieve default
            field and warn user when default value was used. Defaults to None.
        validation_error (Optional[ValidationError], optional): The validation error if any
            occurred during the check. Defaults to None.
        warn_defaults (bool, optional): whether to warn when default values are used and not
            overwritten in config file. Defaults to True.
    """
    parsed_val_error_dict = _parse_validation_errors(validation_error)
    parsed_warnings_dict = _get_warnings_for_default_value(pipelines_model)

    table = Table(show_header=True, header_style="bold", show_lines=True)
    for column in PIPELINE_CHECKS_TABLE_COLUMNS:
        table.add_column(column)
        table.columns[0].justify = "center"

    for pipeline_name, config_filepaths in to_check.items():
        p_errors = parsed_val_error_dict.get(pipeline_name, {})
        p_warnings = parsed_warnings_dict.get(pipeline_name, {})

        if len(p_errors) == 0 and len(p_warnings) == 0:
            if len(config_filepaths) == 0:
                row = ChecksTableRow(
                    status="⚠️",
                    pipeline=pipeline_name,
                    config_file="No config files found",
                )
                table.add_row(*row.model_dump().values(), style="bold yellow")

            for config_filepath in config_filepaths:
                row = ChecksTableRow(
                    status="✅",
                    pipeline=pipeline_name,
                    config_file=config_filepath.name,
                )
                table.add_row(*row.model_dump().values(), style="green")

        elif len(p_errors) == 1 and p_errors.keys() == {"pipeline level error"}:
            error = p_errors["pipeline level error"]
            row = ChecksTableRow(
                status="❌",
                pipeline=pipeline_name,
                pipeline_error_message=error[0]["msg"],
                config_file="Could not check config files due to pipeline error.",
            )
            table.add_row(*row.model_dump().values(), style="red")

        else:
            for config_filepath in config_filepaths:
                config_error_type_l = []
                attribute_l = []
                config_error_message_l = []
                status, style = "✅", "green"

                warnings_ = p_warnings.get(config_filepath.name)
                if warn_defaults and warnings_ is not None:
                    status, style = "⚠️", "yellow"
                    # yellow styling in error string if there are errors + warnings
                    config_error_type_l.extend(
                        [f"[yellow]{wr['type']}[/yellow]" for wr in warnings_]
                    )
                    attribute_l.extend(
                        [f"[yellow]{wr.get('field', '')}[/yellow]" for wr in warnings_]
                    )
                    config_error_message_l.extend(
                        [f"[yellow]{wr['msg']}[/yellow]" for wr in warnings_]
                    )

                errors_ = p_errors.get(config_filepath.name)
                if errors_ is not None:
                    status, style = "❌", "red"
                    config_error_type_l.extend([f"{er['type']}" for er in errors_])
                    attribute_l.extend([f"{er.get('field', '')}" for er in errors_])
                    config_error_message_l.extend([f"{er['msg']}" for er in errors_])

                row = ChecksTableRow(
                    status=status,
                    pipeline=pipeline_name,
                    config_file=config_filepath.name,
                    config_error_type="\n".join(config_error_type_l),
                    attribute="\n".join(attribute_l),
                    config_error_message="\n".join(config_error_message_l),
                )
                table.add_row(*row.model_dump().values(), style=style)

    table.columns = [c for c in table.columns if "".join(c._cells) != ""]

    console.print(table)


def _parse_validation_errors(
    validation_error: Optional[ValidationError],
) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    """_summary_

    Args:
        validation_error (Optional[ValidationError]): _description_

    Returns:
        Dict[str, Dict[str, List[Dict[str, str]]]]: _description_
    """
    val_errors: List[Dict] = validation_error.errors() if validation_error else {}

    parsed_errors = defaultdict(dict)
    for error in val_errors:
        pipeline_name = error["loc"][1]
        if len(error["loc"]) == 2:
            parsed_errors[pipeline_name]["pipeline level error"] = [
                {"type": error["type"], "msg": error["msg"]}
            ]
        else:
            config_name = error["loc"][3]
            error_row = {"type": error["type"], "msg": error["msg"]}
            parsed_errors[pipeline_name].setdefault(config_name, [])
            if len(error["loc"]) > 4:
                error_row["field"] = error["loc"][5]
            parsed_errors[pipeline_name][config_name].append(error_row)

    return parsed_errors


def _get_warnings_for_default_value(
    pipelines_model: Optional[Any],
) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    """_summary_

    Args:
        pipelines_model (Optional[Any]): _description_

    Returns:
        Dict[str, Dict[str, List[Dict[str, str]]]]: _description_
    """
    if pipelines_model is None:
        return {}

    parsed_warnings = defaultdict(dict)

    for pipeline_name, pipeline_configs in pipelines_model.pipelines.items():
        configs_models = pipeline_configs.configs.configs
        for cfp in pipeline_configs.config_paths:
            unset_fields_with_default = _get_unset_default_fields(configs_models[cfp.name].config)
            if unset_fields_with_default:
                parsed_warnings[pipeline_name][cfp.name] = [
                    {
                        "type": "default_value",
                        "field": f["field"],
                        "msg": f"Using default value from pipeline definition: {f['default']}",
                    }
                    for f in unset_fields_with_default
                ]
    return parsed_warnings


def _get_unset_default_fields(model: BaseModel) -> List[Dict]:
    """_summary_

    Args:
        model (BaseModel): _description_

    Returns:
        List[Dict]: _description_
    """
    if model is None:
        return None
    unset_fields = set(model.model_dump()) - set(model.model_dump(exclude_unset=True))
    unset_fields_with_default = []
    for field in unset_fields:
        if getattr(model, field):
            unset_fields_with_default.append({"field": field, "default": getattr(model, field)})
    return unset_fields_with_default
