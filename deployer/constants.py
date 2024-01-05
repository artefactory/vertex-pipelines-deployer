from pathlib import Path

DEFAULT_PIPELINE_ROOT_PATH = Path("vertex/pipelines")
DEFAULT_CONFIG_ROOT_PATH = Path("vertex/configs")

DEFAULT_SCHEDULER_TIMEZONE = "Europe/Paris"
DEFAULT_LOCAL_PACKAGE_PATH = Path("vertex/pipelines/compiled_pipelines")
DEFAULT_TAGS = None

TEMP_LOCAL_PACKAGE_PATH = ".vertex-deployer-temp"


PIPELINE_MINIMAL_TEMPLATE = """import kfp.dsl


@kfp.dsl.pipeline(name="{pipeline_name}")
def {pipeline_name}():
    pass

"""

PYTHON_CONFIG_TEMPLATE = """from kfp.dsl import Artifact, Dataset, Input, Output, Metrics

parameter_values = {}
input_artifacts = {}

"""
