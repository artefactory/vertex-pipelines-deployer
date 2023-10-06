import importlib
import json
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple, Union

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from deployer.utils.exceptions import BadConfigError, UnsupportedConfigFileError


class VertexPipelinesSettings(BaseSettings):  # noqa: D101
    model_config = SettingsConfigDict(extra="ignore", case_sensitive=True)

    PROJECT_ID: str
    GCP_REGION: str
    GAR_LOCATION: str
    GAR_PIPELINES_REPO_ID: str
    VERTEX_STAGING_BUCKET_NAME: str
    VERTEX_SERVICE_ACCOUNT: str


def load_vertex_settings(env_file: Optional[Path] = None) -> VertexPipelinesSettings:
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


class ConfigType(str, Enum):  # noqa: D101
    json = "json"
    py = "py"


def list_config_filepaths(config_root_path: Union[Path, str], pipeline_name: str) -> List[Path]:
    """List the config filepaths for a pipeline.

    Args:
        config_root_path (Path): A `Path` object representing the root path of the configs.
        pipeline_name (str): The name of the pipeline.

    Returns:
        List[Path]: A list of `Path` objects representing the config filepaths.
    """
    configs_dirpath = Path(config_root_path) / pipeline_name
    config_filepaths = [
        x
        for config_type in ConfigType.__members__.values()
        for x in configs_dirpath.glob(f"*.{config_type}")
    ]
    return config_filepaths


def load_config(config_filepath: Path) -> Tuple[Optional[dict], Optional[dict]]:
    """Load the parameter values and input artifacts from a config file.

    Config file can be a JSON or Python file.
        - If JSON, it should be a dict of parameter values.
        - If Python, it should contain a `parameter_values` dict
        and / or an `input_artifacts` dict.

    Args:
        config_filepath (Path): A `Path` object representing the path to the config file.

    Returns:
        Tuple[Optional[dict], Optional[dict]]:: A tuple containing the loaded parameter values
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
        parameter_values, input_artifacts = _load_config_python(config_filepath)
        return parameter_values, input_artifacts

    raise UnsupportedConfigFileError(
        f"{config_filepath}: Config file type {config_filepath.suffix} is not supported."
        " Please use a JSON or Python file."
    )


def _load_config_python(config_filepath: Path) -> Tuple[Optional[dict], Optional[dict]]:
    """Load the parameter values and input artifacts from a Python config file.

    Args:
        config_filepath (Path): A `Path` object representing the path to the config file.

    Returns:
        Tuple[Optional[dict], Optional[dict]]:: A tuple containing the loaded parameter values
            (or `None` if not available) and input artifacts (or `None` if not available).

    Raises:
        ValueError: If the config file does not contain a `parameter_values` and/or
            `input_artifacts` dict.
        ValueError: If the config file contains common keys in `parameter_values` and
            `input_artifacts` dict.
    """
    spec = importlib.util.spec_from_file_location("module.name", config_filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    parameter_values = getattr(module, "parameter_values", None)
    input_artifacts = getattr(module, "input_artifacts", None)

    if parameter_values is None and input_artifacts is None:
        raise BadConfigError(
            f"{config_filepath}: Python config file must contain a `parameter_values` "
            "and/or `input_artifacts` dict."
        )

    if parameter_values is not None and input_artifacts is not None:
        common_keys = set(parameter_values.keys()).intersection(set(input_artifacts.keys()))
        if common_keys:
            raise BadConfigError(
                f"{config_filepath}: Python config file must not contain common keys in "
                "`parameter_values` and `input_artifacts` dict. Common keys: {common_keys}"
            )

    return parameter_values, input_artifacts
