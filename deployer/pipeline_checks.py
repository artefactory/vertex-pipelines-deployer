import shutil
from pathlib import Path
from typing import Any, Dict, Generic, List, TypeVar

from loguru import logger
from pydantic import Field, ValidationError, computed_field, model_validator
from pydantic.functional_validators import ModelWrapValidatorHandler
from pydantic_core import PydanticCustomError
from typing_extensions import Annotated

from deployer.constants import (
    CONFIG_ROOT_PATH,
    PIPELINE_ROOT_PATH,
    TEMP_LOCAL_PACKAGE_PATH,
)
from deployer.pipeline_deployer import VertexPipelineDeployer
from deployer.utils.config import list_config_filepaths, load_config
from deployer.utils.exceptions import BadConfigError
from deployer.utils.logging import disable_logger
from deployer.utils.models import CustomBaseModel, create_model_from_pipeline
from deployer.utils.utils import (
    import_pipeline_from_dir,
    make_enum_from_python_package_dir,
)

PipelineConfigT = TypeVar("PipelineConfigT")

PipelineName = make_enum_from_python_package_dir(PIPELINE_ROOT_PATH)


class ConfigDynamicModel(CustomBaseModel, Generic[PipelineConfigT]):
    """Model used to generate checks for configs based on pipeline dynamic model"""

    config_path: Path
    config: PipelineConfigT

    @model_validator(mode="before")
    @classmethod
    def load_config_if_empty(cls, data: Any) -> Any:
        """Load config if it is empty"""
        if data.get("config") is None:
            try:
                parameter_values, input_artifacts = load_config(data["config_path"])
            except BadConfigError as e:
                raise PydanticCustomError("BadConfigError", str(e)) from e
            data["config"] = {**(parameter_values or {}), **(input_artifacts or {})}
        return data


class ConfigsDynamicModel(CustomBaseModel, Generic[PipelineConfigT]):
    """Model used to generate checks for configs based on pipeline dynamic model"""

    configs: Dict[str, ConfigDynamicModel[PipelineConfigT]]


class Pipeline(CustomBaseModel):
    """Validation of one pipeline and its configs"""

    pipeline_name: PipelineName
    config_paths: Annotated[List[Path], Field(validate_default=True)] = None

    @model_validator(mode="before")
    @classmethod
    def populate_config_names(cls, data: Any) -> Any:
        """Populate config names before validation"""
        if data.get("config_paths") is None:
            data["config_paths"] = list_config_filepaths(CONFIG_ROOT_PATH, data["pipeline_name"])
        return data

    @computed_field
    def pipeline(self) -> Any:
        """Import pipeline"""
        with disable_logger("deployer.utils.utils"):
            return import_pipeline_from_dir(PIPELINE_ROOT_PATH, self.pipeline_name.value)

    @model_validator(mode="after")
    def import_pipeline(self):
        """Validate that the pipeline can be imported by calling pipeline computed field"""
        logger.debug(f"Importing pipeline {self.pipeline_name.value}")
        try:
            _ = self.pipeline
        except Exception as e:
            raise ValueError(f"Pipeline import failed: {e.__repr__()}")  # noqa: B904
        return self

    @model_validator(mode="after")
    def compile_pipeline(self):
        """Validate that the pipeline can be compiled"""
        logger.debug(f"Compiling pipeline {self.pipeline_name.value}")
        try:
            with disable_logger("deployer.pipeline_deployer"):
                VertexPipelineDeployer(
                    pipeline_name=self.pipeline_name.value,
                    pipeline_func=self.pipeline,
                    local_package_path=TEMP_LOCAL_PACKAGE_PATH,
                ).compile()
        except Exception as e:
            raise ValueError(f"Pipeline compilation failed: {e.__repr__()}")  # noqa: B904
        return self

    @model_validator(mode="after")
    def validate_configs(self):
        """Validate configs against pipeline parameters definition"""
        logger.debug(f"Validating configs for pipeline {self.pipeline_name.value}")
        PipelineDynamicModel = create_model_from_pipeline(self.pipeline)
        ConfigsModel = ConfigsDynamicModel[PipelineDynamicModel]
        ConfigsModel.model_validate(
            {"configs": {x.name: {"config_path": x} for x in self.config_paths}}
        )
        return self


class Pipelines(CustomBaseModel):
    """Model to validate multiple pipelines at once"""

    pipelines: Dict[str, Pipeline]

    @model_validator(mode="wrap")
    def _init_remove_temp_directory(self, handler: ModelWrapValidatorHandler) -> Any:
        """Create and remove temporary directory"""
        Path(TEMP_LOCAL_PACKAGE_PATH).mkdir(exist_ok=True)

        try:
            validated_self = handler(self)
        except ValidationError as e:
            raise e
        finally:
            shutil.rmtree(TEMP_LOCAL_PACKAGE_PATH)

        return validated_self
