import importlib
import json
from pathlib import Path
from typing import List, Optional, Tuple, Union

import tomlkit.items
import yaml
from loguru import logger
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.prompt import Confirm
from rich.table import Table
from tomlkit import TOMLDocument
from tomlkit.toml_file import TOMLFile

from deployer.constants import ConfigType
from deployer.utils.console import console
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


def validate_or_log_settings(
    settings: VertexPipelinesSettings,
    skip_validation: bool,
    env_file: Optional[Path] = None,
) -> None:
    """Validate the settings or log them if validation is skipped.

    Args:
        settings (VertexPipelinesSettings): The settings to validate or log.
        skip_validation (bool): Whether to skip validation.
        env_file (Optional[Path], optional): The path to the environment file. Defaults to None.

    Raises:
        ValueError: If the user chooses to exit.
    """
    msg = "Loaded settings from environment"
    if env_file is not None:
        msg += f" and `.env` file: `{env_file}`."

    if skip_validation:
        msg += "\nLoaded settings for Vertex:"
        msg += "\n" + "\n".join(f"  {k:<30} {v:<30}" for k, v in settings.model_dump().items())
        logger.info(msg)
    else:
        table = Table(show_header=True, header_style="bold", show_lines=True)
        table.add_column("Setting Name")
        table.add_column("Value")
        for k, v in settings.model_dump().items():
            table.add_row(k, v)

        console.print(msg)
        console.print(table)
        if not Confirm.ask("Do you want to continue with these settings? ", console=console):
            raise ValueError("User chose to exit")


def list_config_filepaths(configs_root_path: Path, pipeline_name: str) -> List[Path]:
    """List the config filepaths for a pipeline.

    Args:
        configs_root_path (Path): A `Path` object representing the root path of the configs.
        pipeline_name (str): The name of the pipeline.

    Returns:
        List[Path]: A list of `Path` objects representing the config filepaths.
    """
    configs_dirpath = Path(configs_root_path) / pipeline_name
    config_filepaths = [
        x
        for config_type in ConfigType.__members__.keys()
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

    if config_filepath.suffix == ".toml":
        parameter_values = _load_config_toml(config_filepath)
        return parameter_values, None

    if config_filepath.suffix == ".yaml" or config_filepath.suffix == ".yml":
        parameter_values = _load_config_yaml(config_filepath)
        return parameter_values, None

    if config_filepath.suffix == ".py":
        parameter_values, input_artifacts = _load_config_python(config_filepath)
        return parameter_values, input_artifacts

    raise UnsupportedConfigFileError(
        f"{config_filepath}: Config file extension '{config_filepath.suffix}' is not supported."
        f" Supported config file types are: {', '.join(ConfigType.__members__.values())}"
    )


def _load_config_python(config_filepath: Path) -> Tuple[Optional[dict], Optional[dict]]:
    """Load the parameter values and input artifacts from a Python config file.

    Args:
        config_filepath (Path): A `Path` object representing the path to the config file.

    Returns:
        Tuple[Optional[dict], Optional[dict]]: A tuple containing the loaded parameter values
            (or `None` if not available) and input artifacts (or `None` if not available).

    Raises:
        ValueError: If the config file does not contain a `parameter_values` and/or
            `input_artifacts` dict.
        ValueError: If the config file contains common keys in `parameter_values` and
            `input_artifacts` dict.
    """
    spec = importlib.util.spec_from_file_location("module.name", config_filepath)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        raise BadConfigError(
            f"{config_filepath}: invalid Python config file.\n{e.__class__.__name__}: {e}"
        ) from e

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


def _load_config_toml(config_filepath: Path) -> dict:
    """Load the parameter values from a TOML config file.

    Args:
        config_filepath (Path): A `Path` object representing the path to the config file.

    Returns:
        dict: The loaded parameter values.
    """

    def flatten_toml_document(
        d_: Union[TOMLDocument, tomlkit.items.Table],
        parent_key: Optional[str] = None,
        sep: str = ".",
    ) -> dict:
        """Flatten a tomlkit.TOMLDocument. Inline tables are not flattened"""
        items = []
        for k, v in d_.items():
            child_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, tomlkit.items.Table):
                # inline tables will not be flattened
                items.extend(flatten_toml_document(v, child_key, sep=sep).items())
            else:
                items.append((child_key, v))
        return dict(items)

    config_file = TOMLFile(config_filepath)

    try:
        config = config_file.read()
        parameter_values = flatten_toml_document(config, sep="_")
    except Exception as e:
        raise BadConfigError(
            f"{config_filepath}: invalid TOML config file.\n{e.__class__.__name__}: {e}"
        ) from e

    return parameter_values


def _load_config_yaml(config_filepath: Path) -> dict:
    """Load the parameter values from a YAML config file.

    Args:
        config_filepath (Path): A `Path` object representing the path to the config file.

    Returns:
        dict: The loaded parameter values.
    """
    with open(config_filepath, "r") as f:
        try:
            parameter_values = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise BadConfigError(
                f"{config_filepath}: invalid YAML config file.\n{e.__class__.__name__}: {e}"
            ) from e
    return parameter_values
