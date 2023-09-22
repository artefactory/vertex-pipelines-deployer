import importlib
import json
from enum import Enum
from pathlib import Path

from kfp.components import graph_component
from loguru import logger
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from deployer.exceptions import UnsupportedConfigFileError


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


class VertexPipelinesSettings(BaseSettings):  # noqa: D101
    model_config = SettingsConfigDict(extra="ignore", case_sensitive=True)

    PROJECT_ID: str
    GCP_REGION: str
    GAR_LOCATION: str
    GAR_PIPELINES_REPO_ID: str
    VERTEX_STAGING_BUCKET_NAME: str
    VERTEX_SERVICE_ACCOUNT: str


def load_vertex_settings(env_file: Path | None = None) -> VertexPipelinesSettings:
    """Load the settings from the environment."""
    try:
        settings = VertexPipelinesSettings(_env_file=env_file, _env_file_encoding="utf-8")
    except ValidationError as e:
        msg = "Validation failed for VertexPipelinesSettings. "
        if env_file is not None:
            msg += f"Please check your `.env` file: `{env_file}`"
        else:
            msg += "No `.env` file provided. Please check your environment variables"
        msg += f"\n{e}"
        raise ValueError(msg) from e
    return settings


def load_config(config_filepath: Path) -> tuple[dict | None, dict | None]:
    """Load the parameter values and input artifacts from a config file.

    Config file can be a JSON or Python file.
        - If JSON, it should be a dict of parameter values.
        - If Python, it should contain a `parameter_values` dict
        and / or an `input_artifacts` dict.

    Args:
        config_filepath (Path): A `Path` object representing the path to the config file.

    Returns:
        tuple[dict | None, dict | None]: A tuple containing the loaded parameter values
            and input artifacts (or `None` if not available).

    Raises:
        UnsupportedConfigFileError: If the file has an unsupported extension.
    """
    config_filepath = Path(config_filepath)

    if config_filepath.suffix == ".json":
        with open(config_filepath, "r") as f:
            parameter_values = json.load(f)

        return parameter_values, None

    if config_filepath.suffix == ".py":
        spec = importlib.util.spec_from_file_location("module.name", config_filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        parameter_values = getattr(module, "parameter_values", None)
        input_artifacts = getattr(module, "input_artifacts", None)

        return parameter_values, input_artifacts

    raise UnsupportedConfigFileError(
        f"{config_filepath}: Config file type {config_filepath.suffix} is not supported."
        " Please use a JSON or Python file."
    )


class disable_logger(object):
    """Context manager to disable a loguru logger."""

    def __init__(self, name: str) -> None:  # noqa: D107
        self.name = name

    def __enter__(self) -> None:  # noqa: D105
        logger.disable(self.name)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: D105
        logger.enable(self.name)
