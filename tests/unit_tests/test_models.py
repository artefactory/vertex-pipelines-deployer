import pytest
from kfp.dsl import Artifact, Dataset, Input, Metrics, Model, Output

from deployer.models import convert_artifact_type_to_str


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
    result = convert_artifact_type_to_str(input_annotation)

    # Then
    assert result == expected_annotation
