import pytest

from deployer.utils.config import _load_config_toml
from deployer.utils.exceptions import BadConfigError


class TestLoadConfigToml:
    # Loads parameter values from a valid TOML file
    def test_valid_toml_file(self, tmp_path):
        # Given
        toml_data = """
        [parameters]
        param1 = "value1"
        param2 = 123
        """
        config_filepath = tmp_path / "config.toml"
        config_filepath.write_text(toml_data, encoding="utf-8")

        # When
        parameter_values = _load_config_toml(config_filepath)

        # Then
        assert parameter_values == {"parameters_param1": "value1", "parameters_param2": 123}

    # Loads parameter values from a TOML file with nested tables
    def test_nested_tables(self, tmp_path):
        # Given
        toml_data = """
        [parameters]
        param1 = "value1"

        [parameters.nested]
        param1 = "nested_value1"
        param2 = 456
        """
        config_filepath = tmp_path / "config.toml"
        config_filepath.write_text(toml_data, encoding="utf-8")

        # When
        parameter_values = _load_config_toml(config_filepath)

        # Then
        assert parameter_values == {
            "parameters_param1": "value1",
            "parameters_nested_param1": "nested_value1",
            "parameters_nested_param2": 456,
        }

    # Loads parameter values from a TOML file with inline tables
    def test_array(self, tmp_path):
        # Given
        toml_data = """
        [parameters]
        param1 = "value1"

        [[nested]]
        nested_param1 = "nested_value1"
        nested_param2 = 456

        [[nested]]
        nested_param1 = "nested_value2"
        nested_param2 = 789
        """
        config_filepath = tmp_path / "config.toml"
        config_filepath.write_text(toml_data, encoding="utf-8")

        # When
        parameter_values = _load_config_toml(config_filepath)

        # Then
        assert parameter_values == {
            "parameters_param1": "value1",
            "nested": [
                {"nested_param1": "nested_value1", "nested_param2": 456},
                {"nested_param1": "nested_value2", "nested_param2": 789},
            ],
        }

    def test_invalid_char_toml_file(self, tmp_path):
        # Given
        toml_data = """
        [parameters]
        param1 = "value1
        param2 = 123
        """
        config_filepath = tmp_path / "config.toml"
        config_filepath.write_text(toml_data, encoding="utf-8")

        # When/Then
        with pytest.raises(BadConfigError):
            _load_config_toml(config_filepath)

    # Raises BadConfigError if the TOML file is empty
    def test_invalid_space_toml_file(self, tmp_path):
        # Given
        config_filepath = tmp_path / "config.toml"
        config_filepath.write_text("hello world", encoding="utf-8")

        # When/Then
        with pytest.raises(BadConfigError):
            _load_config_toml(config_filepath)

    def test_load_config_toml_empty_values(self, tmp_path):
        # Given
        toml_data = ""
        config_filepath = tmp_path / "config.toml"
        config_filepath.write_text(toml_data, encoding="utf-8")

        # When
        parameter_values = _load_config_toml(config_filepath)

        # Then
        assert parameter_values == {}

    def test_toml_file_with_inline_tables(self, tmp_path):
        # Given
        toml_data = """
        [parameters]
        param1 = "value1"
        param2 = 123

        [parameters.inline_tables]
        first_table = {key1 = "value1", key2 = 123}
        second_table = {key1 = "value2", key2 = 456}
        """
        config_filepath = tmp_path / "config.toml"
        config_filepath.write_text(toml_data, encoding="utf-8")

        # When
        parameter_values = _load_config_toml(config_filepath)

        # Then
        assert parameter_values == {
            "parameters_param1": "value1",
            "parameters_param2": 123,
            "parameters_inline_tables_first_table": {"key1": "value1", "key2": 123},
            "parameters_inline_tables_second_table": {"key1": "value2", "key2": 456},
        }
