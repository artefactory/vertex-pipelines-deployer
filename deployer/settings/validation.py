from pathlib import Path
from typing import List, Optional

from deployer import constants
from deployer.utils.config import ConfigType
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
    tags: List[str] = constants.DEFAULT_TAGS
    config_filepath: Optional[Path] = None
    config_name: Optional[str] = None
    enable_caching: bool = False
    experiment_name: Optional[str] = None
    local_package_path: Path = constants.DEFAULT_LOCAL_PACKAGE_PATH


class _DeployerCheckSettings(CustomBaseModel):
    """Settings for Vertex Deployer `check` command."""

    all: bool = False
    config_filepath: Optional[Path] = None
    raise_error: bool = False


class _DeployerListSettings(CustomBaseModel):
    """Settings for Vertex Deployer `list` command."""

    with_configs: bool = False


class _DeployerCreateSettings(CustomBaseModel):
    """Settings for Vertex Deployer `create` command."""

    config_type: ConfigType = ConfigType.json


class _DeployerConfigSettings(CustomBaseModel):
    """Settings for Vertex Deployer `config` command."""

    list: bool = False
    all: bool = False
    unset: bool = False


class DeployerSettings(CustomBaseModel):
    """Settings for Vertex Deployer."""

    pipelines_root_path: Path = constants.DEFAULT_PIPELINE_ROOT_PATH
    config_root_path: Path = constants.DEFAULT_CONFIG_ROOT_PATH
    log_level: str = constants.DEFAULT_LOG_LEVEL
    deploy: _DeployerDeploySettings = _DeployerDeploySettings()
    check: _DeployerCheckSettings = _DeployerCheckSettings()
    list: _DeployerListSettings = _DeployerListSettings()
    create: _DeployerCreateSettings = _DeployerCreateSettings()
    config: _DeployerConfigSettings = _DeployerConfigSettings()
