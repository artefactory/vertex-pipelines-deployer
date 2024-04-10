from pathlib import Path

TEMPLATES_PATH = Path(__file__).parent / "_templates"

DEFAULT_VERTEX_FOLDER_PATH = Path("vertex")
DEFAULT_LOG_LEVEL = "INFO"

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

PIPELINE_CHECKS_TABLE_COLUMNS = [
    "Status",
    "Pipeline",
    "Pipeline Error Message",
    "Config File",
    "Attribute",
    "Config Error Type",
    "Config Error Message",
]
