import kfp.dsl

from vertex.components.dummy import broken_component


@kfp.dsl.pipeline(name="broken-pipeline")
def pipeline(name: str):
    """This pipeline is broken!"""
    broken_component(name=name)
