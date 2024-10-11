import re
from enum import Enum
from pathlib import Path

TEMPLATES_PATH = Path(__file__).parent / "_templates"

DEFAULT_VERTEX_FOLDER_PATH = "vertex"
DEFAULT_LOG_LEVEL = "INFO"

DEFAULT_SCHEDULER_TIMEZONE = "Europe/Paris"
DEFAULT_TAGS = None

TEMP_LOCAL_PACKAGE_PATH = ".vertex-deployer-temp"

PIPELINE_CHECKS_TABLE_COLUMNS = [
    "Status",
    "Pipeline",
    "Pipeline Error Message",
    "Config File",
    "Attribute",
    "Config Error Type",
    "Config Error Message",
]

PIPELINE_MINIMAL_TEMPLATE = Path(TEMPLATES_PATH / "pipelines/pipeline_minimal.py.jinja")

TEMPLATES_DEFAULT_STRUCTURE = {
    "dummy_component": Path(TEMPLATES_PATH / "components/dummy_component.py"),
    "deployer_env": Path(TEMPLATES_PATH / "deployer.env"),
    "requirements_vertex": Path(TEMPLATES_PATH / "requirements-vertex.txt.jinja"),
    "dockerfile": Path(TEMPLATES_PATH / "deployment/Dockerfile"),
    "cloudbuild_local": Path(TEMPLATES_PATH / "deployment/cloudbuild_local.yaml.jinja"),
    "build_base_image": Path(TEMPLATES_PATH / "deployment/build_base_image.sh.jinja"),
}

INSTRUCTIONS = (
    "\n"
    "Now that your deployer is configured, make sure that you're also done with the setup!\n"
    "You can find all the instructions in the README.md file.\n"
    "\n"
    "If your setup is complete you're ready to start building your pipelines! :tada:\n"
    "Here are the commands you need to run to build your project:\n"
    "\n"
    "1. Build the base image:\n"
    "$ bash {build_base_image_path}\n"
    "\n"
    "2. Check all the pipelines:\n"
    "$ vertex-deployer check --all\n"
    "\n"
    "3. Deploy a pipeline and run it:\n"
    "$ vertex-deployer deploy pipeline_name --run\n"
    "If not set during configuration, you will need to provide the config path or name:\n"
    "$ vertex-deployer deploy pipeline_name --cfp=path/to/your/config.type\n"
    "\n"
    "4. Schedule a pipeline:\n"
    "you can add the following flags to the deploy command if not set in your config:\n"
    "--schedule --cron=cron_expression --scheduler-timezone=IANA_time_zone\n"
)

VALID_RUN_NAME_PATTERN = re.compile("^[a-z][-a-z0-9]{0,127}$", re.IGNORECASE)


class ConfigType(str, Enum):  # noqa: D101
    json = "json"
    py = "py"
    toml = "toml"
    yaml = "yaml"
    yml = "yaml"


class EnvironmentNames(str, Enum):  # noqa: D101
    dev = "dev"
    stg = "stg"
    prd = "prd"
