import kfp.dsl

from vertex.components.dummy import dummy_component


@kfp.dsl.pipeline(name="dummy-pipeline")
def dummy_pipeline(name: str):
    """This pipeline prints hello {name}"""
    dummy_component(name=name)
