from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import toml

from deployer import constants
from deployer.utils.config import ConfigType
from deployer.utils.models import CustomBaseModel


class DeployerDeployConfig(CustomBaseModel):
    """Configuration for Vertex Deployer `deploy` command."""

    env_file: Path | None = None
    compile: bool = True
    upload: bool = False
    run: bool = False
    schedule: bool = False
    cron: str | None = None
    delete_last_schedule: bool = False
    tags: list[str] = ["latest"]
    config_filepath: Path | None = None
    config_name: str | None = None
    enable_caching: bool = False
    experiment_name: str | None = None
    local_package_path: Path = Path("vertex/pipelines/compiled_pipelines")


class DeployerCheckConfig(CustomBaseModel):
    """Configuration for Vertex Deployer `check` command."""

    all: bool = False
    config_filepath: Path | None = None
    raise_error: bool = False


class DeployerListConfig(CustomBaseModel):
    """Configuration for Vertex Deployer `list` command."""

    with_configs: bool = False


class DeployerCreateConfig(CustomBaseModel):
    """Configuration for Vertex Deployer `create` command."""

    config_type: ConfigType = ConfigType.json


class VertexDeployerConfig(CustomBaseModel):
    """Configuration for Vertex Deployer."""

    pipelines_root_path: Path = constants.PIPELINE_ROOT_PATH
    config_root_path: Path = constants.CONFIG_ROOT_PATH
    log_level: str = "INFO"
    deploy: DeployerDeployConfig = DeployerDeployConfig()
    check: DeployerCheckConfig = DeployerCheckConfig()
    list: DeployerListConfig = DeployerListConfig()
    create: DeployerCreateConfig = DeployerCreateConfig()


def find_pyproject_toml(path_project_root: Path) -> str | None:
    """Find the pyproject.toml file."""
    path_pyproject_toml = path_project_root / "pyproject.toml"
    if path_pyproject_toml.is_file():
        return str(path_pyproject_toml)


def parse_pyproject_toml(path_config: str) -> dict[str, Any]:
    """Parse a pyproject toml file, pulling out relevant parts for Deployer."""
    pyproject_toml = toml.load(path_config)
    config: dict[str, Any] = pyproject_toml.get("tool", {}).get("vertex_deployer", {})
    config = {k.replace("--", "").replace("-", "_"): v for k, v in config.items()}
    return config


@lru_cache()
def load_configuration() -> VertexDeployerConfig:
    """Load the configuration for Vertex Deployer."""
    path_project_root = Path(__file__).parent.parent
    path_config = find_pyproject_toml(path_project_root)
    config = parse_pyproject_toml(path_config)
    config = VertexDeployerConfig(**config)
    return config
