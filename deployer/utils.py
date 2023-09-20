import importlib
import json
from enum import Enum
from pathlib import Path

from kfp.components import graph_component
from loguru import logger

from deployer.constants import CONFIG_ROOT_PATH


class LoguruLevel(str, Enum):  # noqa: D101
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def make_pipeline_names_enum_from_dir(dir_path: Path) -> Enum:
    """Create an Enum of pipeline names from a directory of pipelines."""
    pipeline_names = Path(dir_path).glob("*.py")
    pipeline_enum_dict = {x.stem: x.stem for x in pipeline_names if x.stem != "__init__"}
    PipelineNames = Enum("PipelineNames", pipeline_enum_dict)
    return PipelineNames


def import_pipeline_from_dir(dirpath: Path, pipeline_name: str) -> graph_component.GraphComponent:
    """Import a pipeline from a directory."""
    dirpath_clean = Path(dirpath).resolve().relative_to(get_project_root())
    parent_module = ".".join(dirpath_clean.parts)
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
            f"Pipeline {module_path}.pipeline not found. "
            "Please check that the pipeline is correctly defined and named."
        ) from e

    logger.debug(f"Pipeline {module_path} imported successfully.")

    return pipeline


def get_project_root() -> str:
    """Get the project root."""
    project_root = str(Path(__file__).parent.parent.resolve())
    return project_root


def load_config(config_name: str, pipeline_name: str | None = None) -> dict:
    """Load a config file."""
    if pipeline_name:
        config_filepath = CONFIG_ROOT_PATH / pipeline_name / f"{config_name}.json"
    else:
        config_filepath = CONFIG_ROOT_PATH / f"{config_name}.json"
    with open(config_filepath) as f:
        config = json.load(f)
    return config


# def import_pipelines_from_dir(dir_path: Path) -> None:
#     pipeline_names = Path(dir_path).glob("*.py")
#     pipelines_mapping = {}
#     for p in pipeline_names:
#         if p.stem != "__init__":
#             setattr(
#                 sys.modules[__name__],
#                 p.stem,
#                 importlib.import_module(f"vertex.pipelines.{p.stem}"),
#             )
#             pipelines_mapping[p.stem] = getattr(sys.modules[__name__], p.stem).pipeline

#     return pipelines_mapping
