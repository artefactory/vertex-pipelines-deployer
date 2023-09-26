import kfp.dsl
import pytest
from kfp.dsl import Artifact, Input


@pytest.fixture
def dummy_pipeline_fixture():
    @kfp.dsl.component(base_image="python:3.10-slim-buster")
    def dummy_component(name: str, artifact: Input[Artifact]) -> None:
        print("Hello ", name)

    @kfp.dsl.pipeline(name="dummy_pipeline")
    def dummy_pipeline(name: str, artifact: Input[Artifact]) -> None:
        dummy_component(name=name, artifact=artifact)

    return dummy_pipeline
