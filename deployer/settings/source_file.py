"""Code in this module is heavily copy-pasted / inspired from poetry config file management
https://github.com/python-poetry/poetry/blob/69717d8eab5e004f21e01de81b3be2987f57fcb8/src/poetry/toml/file.py#L17
"""
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import tomlkit
from loguru import logger
from tomlkit.toml_file import TOMLFile

from deployer.settings.validation import DeployerSettings


class ConfigFileSource:
    """Base class for config file sources."""

    def __init__(self, filepath: Path) -> None:
        self.__path = Path(filepath)
        self._file = TOMLFile(self.__path)

    @property
    def file(self) -> TOMLFile:
        return self._file

    def add_property(self, key: str, value: Any) -> None:
        """Adds a property to the configuration file."""
        with self.secure() as config:
            keys = key.split(".")

            for i, key in enumerate(keys):
                if key not in config and i < len(keys) - 1:
                    config[key] = tomlkit.table()

                if i == len(keys) - 1:
                    config[key] = value
                    break

                config = config[key]

    def remove_property(self, key: str) -> None:
        """Removes a property from the configuration file."""
        with self.secure() as config:
            keys = key.split(".")

            current_config = config
            parent_config = current_config
            for i, key in enumerate(keys):
                if key not in current_config:
                    return

                if i == len(keys) - 1:
                    del current_config[key]
                    if current_config == {}:
                        del parent_config[keys[i - 1]]
                    break

                parent_config = current_config
                current_config = current_config[key]

    @contextmanager
    def secure(self) -> Iterator[tomlkit.TOMLDocument]:
        """Context manager ensuring that the config file is only readable and writable by the current user."""  # noqa: E501
        new_file = not self.__path.exists()

        if not new_file:
            initial_config = self.file.read()
            config = self.file.read()
        else:
            initial_config = tomlkit.document()
            config = tomlkit.document()

        yield config

        try:
            # Ensuring the file is only readable and writable
            # by the current user
            mode = 0o600

            if new_file:
                self.file.path.touch(mode=mode)

            self.file.write(config)
        except Exception:
            self.file.write(initial_config)

            raise


def find_pyproject_toml(path_project_root: Path) -> str:
    """Find the pyproject.toml file."""
    path_pyproject_toml = path_project_root / "pyproject.toml"
    if path_pyproject_toml.is_file():
        if not path_pyproject_toml.exists():
            logger.debug("No pyproject.toml file found. Will create one if need be.")
    return str(path_pyproject_toml)


class DeployerSettingsSource(ConfigFileSource):
    """Source for Deployer settings."""

    root_key = "tool.vertex_deployer"

    def __init__(self) -> None:
        path_project_root = Path.cwd().resolve()
        path_pyproject_toml = find_pyproject_toml(path_project_root)
        super().__init__(path_pyproject_toml)

    def load_settings(self) -> DeployerSettings:
        """Read and validate Deployer settings from pyproject.toml."""
        return DeployerSettings(**self.read())

    def read(self) -> dict:
        """Read Deployer settings from pyproject.toml."""
        with self.secure() as config:
            for k in self.root_key.split("."):
                config = config[k]
            return dict(config)

    def add_property(self, key: str, value: Any) -> None:
        """Adds a property to the configuration file."""
        keys = key.split(".")
        config = {keys.pop(): value}
        for key in reversed(keys):
            config = {key: config}

        DeployerSettings(**config)

        return super().add_property(f"{self.root_key}.{key}", value)

    def remove_property(self, key: str) -> None:
        """Removes a property from the configuration file."""
        config = self.load_settings()
        config = config.model_dump(exclude_unset=True)

        for k in key.split("."):
            if k not in config:
                logger.warning(f"No key '{key}' found in config '{self.__path}:{self.root_key}'")
                return
            config = config[k]

        super().remove_property(f"{self.root_key}.{key}")
