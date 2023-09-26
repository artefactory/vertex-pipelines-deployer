import pytest
from kfp.dsl import Artifact, Dataset, Input, Metrics, Model, Output

from deployer.utils.models import (
    CustomBaseModel,
    _convert_artifact_type_to_str,
    create_model_from_pipeline,
)


@pytest.mark.parametrize(
    ("input_annotation", "expected_annotation"),
    [
        (Input[Artifact], str),
        (Output[Artifact], str),
        (Input[Model], str),
        (Output[Model], str),
        (Input[Dataset], str),
        (Output[Dataset], str),
        (Input[Metrics], str),
        (Output[Metrics], str),
        (str, str),
        (int, int),
        (float, float),
        (bool, bool),
    ],
)
def test_artifact_type_to_str(input_annotation, expected_annotation):
    # Given

    # When
    result = _convert_artifact_type_to_str(input_annotation)

    # Then
    assert result == expected_annotation


class TestCreateModelFromPipeline:
    def test_create_model_from_pipeline_success(self, dummy_pipeline_fixture):
        # Given
        pipeline = dummy_pipeline_fixture

        # When
        result = create_model_from_pipeline(pipeline)

        # Then
        assert issubclass(result, CustomBaseModel)
        assert result.__name__ == "dummy-pipeline"

    def test_create_model_from_pipeline_none_pipeline(self):
        # Given
        pipeline = None

        # When / Then
        with pytest.raises(AttributeError):
            create_model_from_pipeline(pipeline)

    def test_create_model_from_pipeline_none_pipeline_func(self, dummy_pipeline_fixture):
        # Given
        pipeline = dummy_pipeline_fixture
        pipeline.pipeline_func = None

        # When / Then
        with pytest.raises(TypeError):
            create_model_from_pipeline(pipeline)

    def test_create_model_from_pipeline_types_are_good(self, dummy_pipeline_fixture):
        # Given
        pipeline = dummy_pipeline_fixture
        expected_properties = {
            "name": {"title": "Name", "type": "string"},
            "artifact": {"title": "Artifact", "type": "string"},
        }

        # When
        result = create_model_from_pipeline(pipeline)

        # Then
        assert result.model_json_schema()["properties"] == expected_properties
