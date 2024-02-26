from enum import Enum
from unittest.mock import patch

from pydantic import BaseModel

from deployer.utils.console import ask_user_for_model_fields


class TestAskUserForModelFields:
    def test_ask_user_for_input_for_each_field(self):
        # Given
        class TestModel(BaseModel):
            field1: str
            field2: int
            field3: bool = False

        # When
        with patch("rich.prompt.Prompt.ask") as mock_prompt:
            with patch("rich.prompt.Confirm.ask") as mock_confirm:
                mock_confirm.side_effect = [True]
                mock_prompt.side_effect = ["value1", 2]
                result = ask_user_for_model_fields(TestModel)

        # Then
        assert result == {"field1": "value1", "field2": 2, "field3": True}

    def test_ask_user_with_boolean_fields(self):
        # Given
        class TestModel(BaseModel):
            field1: bool
            field2: bool = True

        # When
        with patch("rich.prompt.Confirm.ask") as mock_confirm:
            mock_confirm.side_effect = [True, False]
            result = ask_user_for_model_fields(TestModel)

        # Then
        assert result == {"field1": True, "field2": False}

    def test_ask_user_with_enum_fields(self):
        # Given
        class TestEnum(Enum):
            OPTION1 = "Option 1"
            OPTION2 = "Option 2"
            OPTION3 = "Option 3"

        class TestModel(BaseModel):
            field1: TestEnum

        # When
        with patch("rich.prompt.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = ["Option 2"]
            result = ask_user_for_model_fields(TestModel)

        # Then
        assert result == {"field1": "Option 2"}

    def test_ask_user_with_nested_models(self):
        # Given
        class NestedModel(BaseModel):
            nested_field1: str
            nested_field2: int

        class TestModel(BaseModel):
            field1: NestedModel

        # When
        with patch("rich.prompt.Prompt.ask") as mock_prompt:
            with patch("rich.prompt.Confirm.ask") as mock_confirm:
                mock_confirm.side_effect = [True]
                mock_prompt.side_effect = ["value1", 2]
                result = ask_user_for_model_fields(TestModel)

        # Then
        assert result == {"field1": {"nested_field1": "value1", "nested_field2": 2}}

    def test_ask_user_with_no_fields(self):
        # Given
        class TestModel(BaseModel):
            pass

        # When
        result = ask_user_for_model_fields(TestModel)

        # Then
        assert result == {}

    def test_ask_user_with_no_default_value_and_no_valid_choices(self):
        # Given
        class TestModel(BaseModel):
            field1: str

        # When
        with patch("rich.prompt.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = ["value1"]
            result = ask_user_for_model_fields(TestModel)

        # Then
        assert result == {"field1": "value1"}

    def test_ask_user_with_default_value_and_no_valid_choices(self):
        # Given
        class TestModel(BaseModel):
            field1: str = "default"

        # When
        with patch("rich.prompt.Prompt.ask") as mock_prompt:
            mock_prompt.side_effect = ["value1"]
            result = ask_user_for_model_fields(TestModel)

        # Then
        assert result == {"field1": "value1"}
