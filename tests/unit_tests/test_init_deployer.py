from unittest.mock import patch

import pytest

from deployer.init_deployer import _create_file_from_template, _generate_templates_mapping
from deployer.utils.exceptions import TemplateFileCreationError


class TestCreateFileFromTemplate:
    def test_create_file_from_template_valid_inputs(self, templates_path_fixture, tmp_path):
        # Arrange
        path = tmp_path / "test_file.txt"
        template_path = templates_path_fixture / "template1.txt.jinja"
        kwargs = {"name": "John", "age": 30}

        # Act
        _create_file_from_template(path, template_path, **kwargs)

        # Assert
        assert path.exists()
        assert path.read_text() == "My name is John and I am 30 years old."

    def test_create_file_template_not_exist(self, templates_path_fixture, tmp_path):
        # Arrange
        path = tmp_path / "test_file.txt"
        template_path = templates_path_fixture / "nonexistent_template.txt"
        kwargs = {"name": "John", "age": 30}

        # Act and Assert
        with pytest.raises(TemplateFileCreationError):
            _create_file_from_template(path, template_path, **kwargs)


class TestGenerateTemplatesMapping:
    def test_generate_templates_mapping_with_and_without_variables(
        self, templates_path_fixture, tmp_path
    ):
        # Arrange
        templates_dict = {
            "template1": templates_path_fixture / "template1.txt.jinja",
            "template2": templates_path_fixture / "folder/template2.yaml.jinja",
            "template3": templates_path_fixture / "template3.env.jinja",
        }
        output_folder_path = tmp_path / "output"
        mapping_variables = {
            "name": "John",
            "age": 30,
        }

        with patch("deployer.init_deployer.TEMPLATES_PATH", templates_path_fixture):
            # Act
            result = _generate_templates_mapping(
                templates_dict, mapping_variables, output_folder_path
            )

            # Assert
            assert len(result) == len(templates_dict)
            for _, template_path in templates_dict.items():
                output_path = output_folder_path / str(
                    template_path.relative_to(templates_path_fixture)
                ).replace(".jinja", "")
                assert output_path in result
                assert result[output_path][0].resolve() == template_path.resolve()
                expected_variables = (
                    mapping_variables if template_path == templates_dict["template1"] else {}
                )
                assert result[output_path][1] == expected_variables
