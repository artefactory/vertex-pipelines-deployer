from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import toml

from deployer import constants
from deployer.utils.models import CustomBaseModel


class VertexDeployerConfig(CustomBaseModel):
    """Configuration for Vertex Deployer."""

    pipelines_root_path: Path = constants.PIPELINE_ROOT_PATH
    config_root_path: Path = constants.CONFIG_ROOT_PATH


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
