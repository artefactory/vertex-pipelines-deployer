import importlib
from enum import Enum
from pathlib import Path

from kfp.components import graph_component
from loguru import logger


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
        pipeline: graph_component.GraphComponent | None = pipeline_module.pipeline
    except AttributeError as e:
        raise ImportError(
            f"Pipeline {module_path}:pipeline not found. "
            "Please check that the pipeline is correctly defined and named."
        ) from e

    logger.debug(f"Pipeline {module_path} imported successfully.")

    return pipeline
