import logging

from deployer.constants import PIPELINE_ROOT_PATH
from deployer.models import create_model_from_pipeline
from deployer.pipelines_deployer import VertexPipelineDeployer
from deployer.utils import import_pipeline_from_dir, load_config


def check_pipeline(pipeline_name: str, config_names: list[str]) -> bool:
    """Check that the pipeline is valid and that the config is valid against the pipeline."""
    pipeline_func = import_pipeline_from_dir(PIPELINE_ROOT_PATH, pipeline_name)
    logging.debug(f"Pipeline {pipeline_name} - import successfull")

    VertexPipelineDeployer(
        pipeline_name=pipeline_name,
        pipeline_func=pipeline_func,
        local_package_path="./temp",
    ).compile()
    logging.debug(f"Pipeline {pipeline_name} - compilation successfull")

    PipelineDynamicConfig = create_model_from_pipeline(pipeline_func)
    for config_name in config_names:
        config = load_config(config_name=config_name, pipeline_name=pipeline_name)
        PipelineDynamicConfig.model_validate(config)
        logging.debug(
            f"Pipeline {pipeline_name} | Config {config_name} - config validation successfull"
        )

    return True
