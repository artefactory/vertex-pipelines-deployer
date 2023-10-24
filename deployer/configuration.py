from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml
from pydantic import ValidationError

from deployer import constants
from deployer.utils.config import ConfigType
from deployer.utils.exceptions import InvalidPyProjectTOMLError
from deployer.utils.models import CustomBaseModel


class DeployerDeployConfig(CustomBaseModel):
    """Configuration for Vertex Deployer `deploy` command."""

    env_file: Optional[Path] = None
    compile: bool = True
    upload: bool = False
    run: bool = False
    schedule: bool = False
    cron: Optional[str] = None
    delete_last_schedule: bool = False
    tags: List[str] = ["latest"]
    config_filepath: Optional[Path] = None
    config_name: Optional[str] = None
    enable_caching: bool = False
    experiment_name: Optional[str] = None
    local_package_path: Path = Path("vertex/pipelines/compiled_pipelines")


class DeployerCheckConfig(CustomBaseModel):
    """Configuration for Vertex Deployer `check` command."""

    all: bool = False
    config_filepath: Optional[Path] = None
    raise_error: bool = False


class DeployerListConfig(CustomBaseModel):
    """Configuration for Vertex Deployer `list` command."""

    with_configs: bool = False


class DeployerCreateConfig(CustomBaseModel):
    """Configuration for Vertex Deployer `create` command."""

    config_type: ConfigType = ConfigType.json


class DeployerConfig(CustomBaseModel):
    """Configuration for Vertex Deployer."""

    pipelines_root_path: Path = constants.PIPELINE_ROOT_PATH
    config_root_path: Path = constants.CONFIG_ROOT_PATH
    log_level: str = "INFO"
    deploy: DeployerDeployConfig = DeployerDeployConfig()
    check: DeployerCheckConfig = DeployerCheckConfig()
    list: DeployerListConfig = DeployerListConfig()
    create: DeployerCreateConfig = DeployerCreateConfig()


def find_pyproject_toml(path_project_root: Path) -> Optional[str]:
    """Find the pyproject.toml file."""
    path_pyproject_toml = path_project_root / "pyproject.toml"
    if path_pyproject_toml.is_file():
        return str(path_pyproject_toml)


def parse_pyproject_toml(path_pyproject_toml: str) -> Dict[str, Any]:
    """Parse a pyproject toml file, pulling out relevant parts for Deployer."""
    pyproject_toml = toml.load(path_pyproject_toml)
    config: dict[str, Any] = pyproject_toml.get("tool", {}).get("vertex_deployer", {})
    config = {k.replace("--", "").replace("-", "_"): v for k, v in config.items()}
    return config


@lru_cache()
def load_configuration() -> DeployerConfig:
    """Load the configuration for Vertex Deployer."""
    path_project_root = Path(__file__).parent.parent
    path_pyproject_toml = find_pyproject_toml(path_project_root)
    config = parse_pyproject_toml(path_pyproject_toml)

    try:
        config = DeployerConfig(**config)
    except ValidationError as e:
        msg = f"In {path_pyproject_toml}:\n{e}\n"
        msg += "Please check your configuration file."

        raise InvalidPyProjectTOMLError(msg) from e

    return config
