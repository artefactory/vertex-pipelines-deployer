from pathlib import Path

TEMPLATES_PATH = Path(__file__).parent / "_templates"

DEFAULT_VERTEX_FOLDER_PATH = Path("vertex")
DEFAULT_LOG_LEVEL = "INFO"

DEFAULT_SCHEDULER_TIMEZONE = "Europe/Paris"
DEFAULT_LOCAL_PACKAGE_PATH = Path("vertex/pipelines/compiled_pipelines")
DEFAULT_TAGS = None

TEMP_LOCAL_PACKAGE_PATH = ".vertex-deployer-temp"

PIPELINE_MINIMAL_TEMPLATE = Path(TEMPLATES_PATH / "pipeline_minimal.py.jinja")
PYTHON_CONFIG_TEMPLATE = Path(TEMPLATES_PATH / "python_config.py")
JSON_CONFIG_TEMPLATE = Path(TEMPLATES_PATH / "json_config.json")
TOML_CONFIG_TEMPLATE = Path(TEMPLATES_PATH / "toml_config.toml")
DOCKERFILE_TEMPLATE = Path(TEMPLATES_PATH / "Dockerfile.jinja")
CLOUDBUILD_LOCAL_TEMPLATE = Path(TEMPLATES_PATH / "cloudbuild_local.yaml.jinja")
BUILD_BASE_IMAGE_TEMPLATE = Path(TEMPLATES_PATH / "build_base_image.sh.jinja")

DEPLOYER_ENV_TEMPLATE = Path(TEMPLATES_PATH / "deployer.env.jinja")
DEPLOYER_REQUIREMENTS_TEMPLATE = Path(TEMPLATES_PATH / "deployer-requirements.txt.jinja")

CONFIG_TEMPLATE_MAPPING = {
    "json": JSON_CONFIG_TEMPLATE,
    "toml": TOML_CONFIG_TEMPLATE,
    "py": PYTHON_CONFIG_TEMPLATE,
}

PIPELINE_CHECKS_TABLE_COLUMNS = [
    "Status",
    "Pipeline",
    "Pipeline Error Message",
    "Config File",
    "Attribute",
    "Config Error Type",
    "Config Error Message",
]

DEFAULT_DEPLOYER_SETTINGS = {
    "pipelines_root_path": "vertex/pipelines",
    "configs_root_path": "vertex/configs",
}
