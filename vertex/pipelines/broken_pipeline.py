from kfp.dsl import pipeline

from vertex.components.dummy import broken_component


@pipeline(name="broken-pipeline")
def pipeline(name: str):
    """This pipeline is broken!"""
    broken_component(name=name)
