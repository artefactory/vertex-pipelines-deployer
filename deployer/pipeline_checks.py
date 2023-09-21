from pathlib import Path
from typing import Annotated, Any, Generic, TypeVar

from loguru import logger
from pydantic import Field, computed_field, model_validator

from deployer.constants import CONFIG_ROOT_PATH, PIPELINE_ROOT_PATH
from deployer.models import CustomBaseModel, PipelineName, create_model_from_pipeline
from deployer.pipelines_deployer import VertexPipelineDeployer
from deployer.utils import import_pipeline_from_dir, load_config

PipelineConfigT = TypeVar("PipelineConfigT")


class DynamicConfigsModel(CustomBaseModel, Generic[PipelineConfigT]):
    """Model used to generate checks for configs based on pipeline dynamic model"""

    configs: dict[str, PipelineConfigT]


class Pipeline(CustomBaseModel):
    """Validation of one pipeline and its configs"""

    pipeline_name: PipelineName
    config_paths: Annotated[list[Path], Field(validate_default=True)] = None

    @model_validator(mode="before")
    @classmethod
    def populate_config_names(cls, data: Any) -> Any:
        """Populate config names before validation"""
        if data.get("config_paths") is None:
            data["config_paths"] = list(
                (Path(CONFIG_ROOT_PATH) / data["pipeline_name"]).glob("*.json")
            )
        return data

    @computed_field
    def pipeline(self) -> Any:
        """Import pipeline"""
        logger.debug(f"Importing pipeline {self.pipeline_name.value}")
        return import_pipeline_from_dir(PIPELINE_ROOT_PATH, self.pipeline_name.value)

    @computed_field()
    def configs(self) -> Any:
        """Load configs"""
        return [load_config(config_path) for config_path in self.config_paths]

    @model_validator(mode="after")
    def compile_pipeline(self):
        """Validate that the pipeline can be compiled"""
        logger.debug(f"Compiling pipeline {self.pipeline_name.value}")
        try:
            VertexPipelineDeployer(
                pipeline_name=self.pipeline_name.value,
                pipeline_func=self.pipeline,
                local_package_path="./temp",
            ).compile()
        except Exception as e:
            raise ValueError(f"Pipeline compilation failed: {e.__repr__()}")  # noqa: B904
        return self

    @model_validator(mode="after")
    def validate_configs(self):
        """Validate configs against pipeline parameters definition"""
        logger.debug(f"Validating configs for pipeline {self.pipeline_name.value}")
        PipelineDynamicModel = create_model_from_pipeline(self.pipeline)
        ConfigsModel = DynamicConfigsModel[PipelineDynamicModel]
        ConfigsModel.model_validate(
            {"configs": dict(zip([x.name for x in self.config_paths], self.configs))}
        )
        return self


class Pipelines(CustomBaseModel):
    """Model to validate multiple pipelines at once"""

    pipelines: dict[str, Pipeline]