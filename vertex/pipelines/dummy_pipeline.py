from kfp.dsl import pipeline

from vertex.components.dummy import dummy_component


@pipeline(name="dummy-pipeline")
def pipeline(name: str):
    """This pipeline prints hello {name}"""
    dummy_component(name=name)
