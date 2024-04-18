import tempfile
from pathlib import Path

import toml
from typer.testing import CliRunner

from deployer.cli import app

runner = CliRunner()


def test_init_command_with_defaults():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Change the current working directory to the temporary directory
        with runner.isolated_filesystem(temp_dir=tmp_dir):
            # Given
            result = runner.invoke(app, ["init", "--default"])

            # Then
            assert result.exit_code == 0
            assert "Default initialization done" in result.stdout
            assert Path("vertex").is_dir()
            assert (Path("vertex") / "pipelines" / "dummy_pipeline.py").is_file()
            assert (Path("vertex") / "configs" / "dummy_pipeline" / "test.py").is_file()
            assert (Path("vertex") / "configs" / "dummy_pipeline" / "dev.py").is_file()
            assert (Path("vertex") / "configs" / "dummy_pipeline" / "prod.py").is_file()
            assert (Path("vertex") / "deployment" / "cloudbuild_local.yaml").is_file()
            assert (Path("vertex") / "deployment" / "Dockerfile").is_file()
            assert (Path("vertex") / "deployment" / "build_base_image.sh").is_file()
            assert (Path("vertex") / "lib").is_dir()
            assert (Path("vertex") / "components").is_dir()
            assert (Path("vertex") / "components" / "dummy_component.py").is_file()
            assert Path("pyproject.toml").is_file()
            assert not Path("pyproject.toml").read_text()
            assert Path("deployer.env").is_file()
            assert Path("requirements-vertex.txt").is_file()

            # No need for explicit cleanup, the temporary directory will be deleted automatically


def test_init_command_with_user_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with runner.isolated_filesystem(temp_dir=tmp_dir):
            # Given
            # Provide user inputs for the interactive prompts
            user_inputs = "\n".join(
                [
                    "n",
                    "y",
                    "custom_value",
                    "",
                    "y",
                    "",
                    "n",
                    "y",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "json",
                    "",
                    "y",
                    "y",
                    "pipe",
                    "n",
                ]
            )

            result = runner.invoke(app, ["init"], input=user_inputs)
            # Then
            assert result.exit_code == 0
            # Pay attention to the assertions if the user inputs are changed
            assert Path("pyproject.toml").is_file()
            parsed_toml = toml.loads(Path("pyproject.toml").read_text())
            assert parsed_toml["tool"]["vertex_deployer"]["vertex_folder_path"] == "custom_value"
            assert parsed_toml["tool"]["vertex_deployer"]["deploy"]["upload"] is True
            assert parsed_toml["tool"]["vertex_deployer"]["deploy"]["compile"] is False
            assert parsed_toml["tool"]["vertex_deployer"]["create"]["config_type"] == "json"
            assert "env_file" not in parsed_toml["tool"]["vertex_deployer"]["deploy"]
            assert "cron" not in parsed_toml["tool"]["vertex_deployer"]["deploy"]
            assert "check" not in parsed_toml["tool"]["vertex_deployer"]

            # No need for explicit cleanup, the temporary directory will be deleted automatically
