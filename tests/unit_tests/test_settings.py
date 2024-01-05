import pytest
import tomlkit

from deployer.settings import DeployerSettings, update_pyproject_toml


class TestUpdatePyprojectToml:
    def test_update_pyproject_toml_no_updates_file_with_default_settings(self, tmp_path):
        # Given
        path_pyproject_toml = tmp_path / "pyproject.toml"
        path_pyproject_toml.write_text(
            """
            [build-system]
            requires = ["poetry-core>=1.0.0"]
            build-backend = "poetry.core.masonry.api"
            """,
            encoding="utf-8",
        )
        deployer_settings = DeployerSettings()

        # When
        update_pyproject_toml(path_pyproject_toml, deployer_settings)

        # Then
        assert path_pyproject_toml.exists()
        toml_document = tomlkit.loads(path_pyproject_toml.read_text())
        assert "tool" not in toml_document
        assert "vertex_deployer" not in toml_document

    def test_update_pyproject_toml_updates_file_with_default_settings_in_existing_sections(
        self, tmp_path
    ):
        # Given
        path_pyproject_toml = tmp_path / "pyproject.toml"
        path_pyproject_toml.write_text(
            """
            [build-system]
            requires = ["poetry-core>=1.0.0"]
            build-backend = "poetry.core.masonry.api"

            [tool.vertex_deployer]
            pipelines_root_path = "pipelines"
            """,
            encoding="utf-8",
        )
        deployer_settings = DeployerSettings(pipelines_root_path="vertex/pipelines")

        # When
        update_pyproject_toml(path_pyproject_toml, deployer_settings)

        # Then
        assert path_pyproject_toml.exists()
        toml_document = tomlkit.loads(path_pyproject_toml.read_text())
        assert toml_document["build-system"]["requires"] == ["poetry-core>=1.0.0"]
        assert toml_document["build-system"]["build-backend"] == "poetry.core.masonry.api"
        assert (
            toml_document["tool"]["vertex_deployer"]["pipelines_root_path"] == "vertex/pipelines"
        )

    def test_update_pyproject_toml_successfully_updates_file_with_non_default_settings(
        self, tmp_path
    ):
        # Given
        path_pyproject_toml = tmp_path / "pyproject.toml"
        path_pyproject_toml.write_text("", encoding="utf-8")
        deployer_settings = DeployerSettings(
            pipelines_root_path=tmp_path / "pipelines",
            config_root_path=tmp_path / "config",
            log_level="DEBUG",
            deploy={
                "env_file": tmp_path / ".env",
                "compile": False,
                "upload": True,
                "run": True,
                "schedule": True,
                "cron": "0 0 * * *",
                "delete_last_schedule": True,
                "scheduler_timezone": "America/New_York",
                "tags": ["tag1", "tag2"],
                "config_filepath": tmp_path / "config.toml",
                "config_name": "config_name",
                "enable_caching": True,
                "experiment_name": "experiment_name",
                "local_package_path": tmp_path / "package",
            },
            check={
                "all": True,
                "config_filepath": tmp_path / "config.toml",
                "raise_error": True,
            },
            list={
                "with_configs": True,
            },
            create={
                "config_type": "json",
            },
            config={
                "all": True,
            },
        )

        # When
        update_pyproject_toml(path_pyproject_toml, deployer_settings)

        # Then
        assert path_pyproject_toml.exists()
        toml_document = tomlkit.loads(path_pyproject_toml.read_text())
        deployer_section = toml_document["tool"]["vertex_deployer"]
        assert deployer_section["pipelines_root_path"] == str(tmp_path / "pipelines")
        assert deployer_section["config_root_path"] == str(tmp_path / "config")
        assert deployer_section["log_level"] == "DEBUG"
        assert deployer_section["deploy"]["env_file"] == str(tmp_path / ".env")
        assert deployer_section["deploy"]["compile"] is False
        assert deployer_section["deploy"]["upload"] is True
        assert deployer_section["deploy"]["run"] is True
        assert deployer_section["deploy"]["schedule"] is True
        assert deployer_section["deploy"]["cron"] == "0 0 * * *"
        assert deployer_section["deploy"]["delete_last_schedule"] is True
        assert deployer_section["deploy"]["scheduler_timezone"] == "America/New_York"
        assert deployer_section["deploy"]["tags"] == ["tag1", "tag2"]
        assert deployer_section["deploy"]["config_filepath"] == str(tmp_path / "config.toml")
        assert deployer_section["deploy"]["config_name"] == "config_name"
        assert deployer_section["deploy"]["enable_caching"] is True
        assert deployer_section["deploy"]["experiment_name"] == "experiment_name"
        assert deployer_section["deploy"]["local_package_path"] == str(tmp_path / "package")
        assert deployer_section["check"]["all"] is True
        assert deployer_section["check"]["config_filepath"] == str(tmp_path / "config.toml")
        assert deployer_section["check"]["raise_error"] is True
        assert deployer_section["list"]["with_configs"] is True
        assert deployer_section["create"]["config_type"] == "json"
        assert deployer_section["config"]["all"] is True

    def test_pyproject_toml_file_not_found(self, tmp_path):
        # Given
        path_pyproject_toml = tmp_path / "pyproject.toml"
        deployer_settings = DeployerSettings()

        # When/Then
        with pytest.raises(FileNotFoundError):
            update_pyproject_toml(path_pyproject_toml, deployer_settings)

    def test_empty_pyproject_toml_file(self, tmp_path):
        # Given
        path_pyproject_toml = tmp_path / "pyproject.toml"
        path_pyproject_toml.write_text("", encoding="utf-8")
        deployer_settings = DeployerSettings()

        # When/Then
        update_pyproject_toml(path_pyproject_toml, deployer_settings)
