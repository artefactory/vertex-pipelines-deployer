from typing import Optional

import pytest

from deployer.pipeline_checks import _convert_artifact_type_to_str
from deployer.utils.models import CustomBaseModel, create_model_from_func


class TestCreateModelFromPipeline:
    def test_create_model_from_func_success(self):
        # Given
        def func(a: Optional[int], b: str) -> bool:
            return True

        expected_properties = {
            "a": {"anyOf": [{"type": "integer"}, {"type": "null"}], "title": "A"},
            "b": {"title": "B", "type": "string"},
        }

        # When
        result = create_model_from_func(func)

        # Then
        assert issubclass(result, CustomBaseModel)
        assert result.__name__ == "func"
        assert result.model_json_schema()["properties"] == expected_properties

    def test_create_model_from_pipeline_success(self, dummy_pipeline_fixture):
        # Given
        pipeline = dummy_pipeline_fixture

        # When
        result = create_model_from_func(pipeline.pipeline_func)

        # Then
        assert issubclass(result, CustomBaseModel)
        assert result.__name__ == "dummy_pipeline"

    def test_create_model_from_func_none_pipeline(self):
        # Given
        pipeline = None

        # When / Then
        with pytest.raises(AttributeError):
            create_model_from_func(pipeline)

    def test_create_model_from_func_none_pipeline_func(self, dummy_pipeline_fixture):
        # Given
        pipeline = dummy_pipeline_fixture
        pipeline.pipeline_func = None

        # When / Then
        with pytest.raises(TypeError):
            create_model_from_func(pipeline.pipeline_func)

    def test_create_model_from_func_types_are_good(self, dummy_pipeline_fixture):
        # Given
        pipeline = dummy_pipeline_fixture
        expected_properties = {
            "name": {"title": "Name", "type": "string"},
            "artifact": {"title": "Artifact", "type": "string"},
        }

        # When
        result = create_model_from_func(
            pipeline.pipeline_func, type_converter=_convert_artifact_type_to_str
        )

        # Then
        assert result.model_json_schema()["properties"] == expected_properties
