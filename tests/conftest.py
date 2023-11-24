import pickle

import kfp.dsl
import pytest
from kfp.dsl import Artifact, Input


@pytest.fixture
def test_pipeline_fixture():
    @kfp.dsl.component(base_image="python:3.10-slim-buster")
    def dummy_component(name: str, artifact: Input[Artifact]) -> None:
        print("Hello ", name)

    @kfp.dsl.pipeline(name="dummy_pipeline")
    def test_pipeline(name: str, artifact: Input[Artifact]) -> None:
        dummy_component(name=name, artifact=artifact)

    return test_pipeline


@pytest.fixture
def registry_client_response():
    with open("tests/samples/registry_client_response.pkl", "rb") as f:
        return pickle.load(f)  # noqa: S301
