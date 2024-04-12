from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml
import tomlkit
from loguru import logger
from pydantic import ValidationError
from tomlkit.toml_file import TOMLFile

from deployer import __version__, constants
from deployer.utils.config import ConfigType
from deployer.utils.exceptions import InvalidPyProjectTOMLError
from deployer.utils.models import CustomBaseModel


class _DeployerDeploySettings(CustomBaseModel):
    """Settings for Vertex Deployer `deploy` command."""

    env_file: Optional[Path] = None
    compile: bool = True
    upload: bool = False
    run: bool = False
    schedule: bool = False
    cron: Optional[str] = None
    delete_last_schedule: bool = False
    scheduler_timezone: str = constants.DEFAULT_SCHEDULER_TIMEZONE
    tags: Optional[List[str]] = constants.DEFAULT_TAGS
    config_filepath: Optional[Path] = None
    config_name: Optional[str] = None
    enable_caching: Optional[bool] = None
    experiment_name: Optional[str] = None
    local_package_path: Path = constants.DEFAULT_LOCAL_PACKAGE_PATH
    skip_validation: bool = True


class _DeployerCheckSettings(CustomBaseModel):
    """Settings for Vertex Deployer `check` command."""

    all: bool = False
    config_filepath: Optional[Path] = None
    raise_error: bool = False
    warn_defaults: bool = True
    raise_for_defaults: bool = False


class _DeployerListSettings(CustomBaseModel):
    """Settings for Vertex Deployer `list` command."""

    with_configs: bool = False


class _DeployerCreateSettings(CustomBaseModel):
    """Settings for Vertex Deployer `create` command."""

    config_type: ConfigType = ConfigType.json


class _DeployerConfigSettings(CustomBaseModel):
    """Settings for Vertex Deployer `config` command."""

    all: bool = False


class DeployerSettings(CustomBaseModel):
    """Settings for Vertex Deployer."""

    pipelines_root_path: Path = constants.DEFAULT_PIPELINE_ROOT_PATH
    config_root_path: Path = constants.DEFAULT_CONFIG_ROOT_PATH
    log_level: str = "INFO"
    deploy: _DeployerDeploySettings = _DeployerDeploySettings()
    check: _DeployerCheckSettings = _DeployerCheckSettings()
    list: _DeployerListSettings = _DeployerListSettings()
    create: _DeployerCreateSettings = _DeployerCreateSettings()
    config: _DeployerConfigSettings = _DeployerConfigSettings()


def find_pyproject_toml(path_project_root: Path) -> Optional[str]:
    """Find the pyproject.toml file."""
    path_pyproject_toml = path_project_root / "pyproject.toml"
    if path_pyproject_toml.is_file():
        if path_pyproject_toml.exists():
            return str(path_pyproject_toml)
    return None


def parse_pyproject_toml(path_pyproject_toml: str) -> Dict[str, Any]:
    """Parse a pyproject toml file, pulling out relevant parts for Deployer."""
    pyproject_toml = toml.load(path_pyproject_toml)
    settings: dict[str, Any] = pyproject_toml.get("tool", {}).get("vertex_deployer", {})
    settings = {k.replace("--", "").replace("-", "_"): v for k, v in settings.items()}
    return settings


def update_pyproject_toml(path_pyproject_toml: str, deployer_settings: DeployerSettings) -> None:
    """Update the pyproject.toml file with the non-default fields from the deployer configuration.

    Args:
        path_pyproject_toml (str): The file path to the pyproject.toml file.
        deployer_settings (DeployerSettings): The deployer configuration instance with potential
            updates.
    """
    toml_file = TOMLFile(path_pyproject_toml)
    toml_document = toml_file.read()

    non_default_fields = deployer_settings.model_dump(mode="json", exclude_unset=True)

    root_keys = ["tool", "vertex_deployer"]

    section = toml_document
    for key in root_keys:
        if key not in section:
            # if section is OutOfOrderTableProxy, no append method is available
            # Then it can mess up the order of the keys
            # But no other solution found
            section[key] = tomlkit.table(is_super_table=True)
        section = section[key]

    section.update(non_default_fields)

    toml_file.write(toml_document)


@lru_cache()
def load_deployer_settings() -> DeployerSettings:
    """Load the settings for Vertex Deployer."""
    path_project_root = Path.cwd().resolve()
    path_pyproject_toml = find_pyproject_toml(path_project_root)

    if path_pyproject_toml is None:
        logger.debug("No pyproject.toml file found. Using default settings for Vertex Deployer.")
        settings = {}
    else:
        settings = parse_pyproject_toml(path_pyproject_toml)

    try:
        settings = DeployerSettings(**settings)
    except ValidationError as e:
        msg = f"Invalid section tools.vertex_deployer:\n{e}\n"
        msg += f"\nPlease check your configuration file: {path_pyproject_toml}"
        msg += f" and check settings are compatible with deployer version (current: {__version__})"

        raise InvalidPyProjectTOMLError(msg) from e

    return settings
