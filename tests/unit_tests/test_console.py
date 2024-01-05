from enum import Enum
from unittest.mock import patch

from pydantic import BaseModel

from deployer.utils.console import ask_user_for_model_fields


class TestAskUserForModelFields:
    def test_ask_user_for_input_for_each_field(self):
        # Arrange
        class TestModel(BaseModel):
            field1: str
            field2: int
            field3: bool = False

        # Act
        with patch("rich.prompt.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = ["value1", 2, "y"]
            result = ask_user_for_model_fields(TestModel)

        # Assert
        assert result == {"field1": "value1", "field2": 2, "field3": True}

    def test_ask_user_with_boolean_fields(self):
        # Arrange
        class TestModel(BaseModel):
            field1: bool
            field2: bool = True

        # Act
        with patch("rich.prompt.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = ["y", "n"]
            result = ask_user_for_model_fields(TestModel)

        # Assert
        assert result == {"field1": True, "field2": False}

    def test_ask_user_with_enum_fields(self):
        # Arrange
        class TestEnum(Enum):
            OPTION1 = "Option 1"
            OPTION2 = "Option 2"
            OPTION3 = "Option 3"

        class TestModel(BaseModel):
            field1: TestEnum

        # Act
        with patch("rich.prompt.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = ["Option 2"]
            result = ask_user_for_model_fields(TestModel)

        # Assert
        assert result == {"field1": "Option 2"}

    def test_ask_user_with_nested_models(self):
        # Arrange
        class NestedModel(BaseModel):
            nested_field1: str
            nested_field2: int

        class TestModel(BaseModel):
            field1: NestedModel

        # Act
        with patch("rich.prompt.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = ["y", "value1", 2]
            result = ask_user_for_model_fields(TestModel)

        # Assert
        assert result == {"field1": {"nested_field1": "value1", "nested_field2": 2}}

    def test_ask_user_with_no_fields(self):
        # Arrange
        class TestModel(BaseModel):
            pass

        # Act
        result = ask_user_for_model_fields(TestModel)

        # Assert
        assert result == {}

    def test_ask_user_with_no_default_value_and_no_valid_choices(self):
        # Arrange
        class TestModel(BaseModel):
            field1: str

        # Act
        with patch("rich.prompt.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = ["value1"]
            result = ask_user_for_model_fields(TestModel)

        # Assert
        assert result == {"field1": "value1"}

    def test_ask_user_with_default_value_and_no_valid_choices(self):
        # Arrange
        class TestModel(BaseModel):
            field1: str = "default"

        # Act
        with patch("rich.prompt.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = ["value1"]
            result = ask_user_for_model_fields(TestModel)

        # Assert
        assert result == {"field1": "value1"}
