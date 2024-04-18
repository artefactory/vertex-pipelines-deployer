from pathlib import Path
from unittest.mock import patch

import pytest

from deployer.constants import TEMPLATES_PATH_TESTS
from deployer.init_deployer import _create_file_from_template, _generate_templates_mapping
from deployer.utils.exceptions import TemplateFileCreationError


class TestCreateFileFromTemplate:
    def test_create_file_from_template_valid_inputs(self):
        # Arrange
        path = Path("tests/unit_tests/test_file.txt")
        template_path = Path("tests/unit_tests/input_files/template1.txt.jinja")
        kwargs = {"name": "John", "age": 30}

        # Act
        _create_file_from_template(path, template_path, **kwargs)

        # Assert
        assert path.exists()
        assert path.read_text() == "My name is John and I am 30 years old."

        # Cleanup
        path.unlink()

    def test_create_file_template_not_exist(self):
        # Arrange
        path = Path("tests/unit_tests/test_file.txt")
        template_path = Path("tests/unit_tests/inputs_files/nonexistent_template.txt")
        kwargs = {"name": "John", "age": 30}

        # Act and Assert
        with pytest.raises(TemplateFileCreationError):
            _create_file_from_template(path, template_path, **kwargs)


class TestGenerateTemplatesMapping:
    def test_generate_templates_mapping_with_and_without_variables(self):
        # Arrange
        templates_dict = {
            "template1": Path(TEMPLATES_PATH_TESTS / "template1.txt.jinja"),
            "template2": Path(TEMPLATES_PATH_TESTS / "folder/template2.yaml.jinja"),
            "template3": Path(TEMPLATES_PATH_TESTS / "template3.env.jinja"),
        }
        output_folder_path = Path("output")
        mapping_variables = {
            "name": "John",
            "age": 30,
        }

        with patch("deployer.init_deployer.TEMPLATES_PATH", TEMPLATES_PATH_TESTS):
            # Act
            result = _generate_templates_mapping(
                templates_dict, mapping_variables, output_folder_path
            )

            # Assert
            assert len(result) == len(templates_dict)
            for _, template_path in templates_dict.items():
                output_path = output_folder_path / str(
                    template_path.relative_to(TEMPLATES_PATH_TESTS)
                ).replace(".jinja", "")
                assert output_path in result
                assert result[output_path][0].resolve() == template_path.resolve()
                expected_variables = (
                    mapping_variables if template_path == templates_dict["template1"] else {}
                )
                assert result[output_path][1] == expected_variables
