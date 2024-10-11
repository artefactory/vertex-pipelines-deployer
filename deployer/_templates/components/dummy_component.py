from kfp.dsl import Artifact, Output, component


@component(base_image="python:3.10-slim-buster")
def dummy_component(
    name: str,
    # my_input_artifact: Input[Artifact],
    my_output_artifact: Output[Artifact],
):
    """This component is a dummy"""
    print(f"Hello, {name}!")

    my_output_artifact.metadata["name"] = name
