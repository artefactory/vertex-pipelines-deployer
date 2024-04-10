import shutil
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar

import kfp.dsl
from loguru import logger
from pydantic import Field, ValidationError, computed_field, model_validator
from pydantic.functional_validators import ModelWrapValidatorHandler
from pydantic_core import PydanticCustomError
from pydantic_core.core_schema import ValidationInfo
from typing_extensions import Annotated, _AnnotatedAlias

try:
    from kfp.dsl import graph_component  # since 2.1
except ImportError:
    from kfp.components import graph_component  # until 2.0.1

from deployer.constants import TEMP_LOCAL_PACKAGE_PATH
from deployer.pipeline_deployer import VertexPipelineDeployer
from deployer.utils.config import list_config_filepaths, load_config
from deployer.utils.exceptions import BadConfigError
from deployer.utils.logging import DisableLogger
from deployer.utils.models import CustomBaseModel, create_model_from_func
from deployer.utils.utils import import_pipeline_from_dir

PipelineConfigT = TypeVar("PipelineConfigT")


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

    pipeline_name: str
    config_paths: Annotated[List[Path], Field(validate_default=True)] = None
    pipelines_root_path: Path
    configs_root_path: Path
    configs: Optional[Dict[str, ConfigDynamicModel]] = None  # Optional because populated after

    @model_validator(mode="before")
    @classmethod
    def populate_config_names(cls, data: Any) -> Any:
        """Populate config names before validation"""
        if data.get("config_paths") is None:
            data["config_paths"] = list_config_filepaths(
                str(data["configs_root_path"]), data["pipeline_name"]
            )
        return data

    @computed_field
    @property
    def pipeline(self) -> graph_component.GraphComponent:
        """Import pipeline"""
        if getattr(self, "_pipeline", None) is None:
            with DisableLogger("deployer.utils.utils"):
                self._pipeline = import_pipeline_from_dir(
                    str(self.pipelines_root_path), self.pipeline_name
                )
        return self._pipeline

    @model_validator(mode="after")
    def import_pipeline(self):
        """Validate that the pipeline can be imported by calling pipeline computed field"""
        logger.debug(f"Importing pipeline {self.pipeline_name}")
        try:
            _ = self.pipeline
        except (ImportError, ModuleNotFoundError) as e:
            raise ValueError(f"Pipeline import failed: {e}") from e
        return self

    @model_validator(mode="after")
    def compile_pipeline(self):
        """Validate that the pipeline can be compiled"""
        logger.debug(f"Compiling pipeline {self.pipeline_name}")
        try:
            with DisableLogger("deployer.pipeline_deployer"):
                VertexPipelineDeployer(
                    pipeline_name=self.pipeline_name,
                    pipeline_func=self.pipeline,
                    local_package_path=TEMP_LOCAL_PACKAGE_PATH,
                ).compile()
        except Exception as e:
            raise ValueError(f"Pipeline compilation failed: {e.__repr__()}")  # noqa: B904
        return self

    @model_validator(mode="after")
    def validate_configs(self, info: ValidationInfo):
        """Validate configs against pipeline parameters definition"""
        logger.debug(f"Validating configs for pipeline {self.pipeline_name}")
        pipelines_dynamic_model = create_model_from_func(
            self.pipeline.pipeline_func,
            type_converter=_convert_artifact_type_to_str,
            exclude_defaults=info.context.get("raise_for_defaults", False),
        )
        config_model = ConfigsDynamicModel[pipelines_dynamic_model]
        self.configs = config_model.model_validate(
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


def _convert_artifact_type_to_str(annotation: type) -> type:
    """Convert a kfp.dsl.Artifact type to a string.

    This is mandatory for type checking, as kfp.dsl.Artifact types should be passed as strings
    to VertexAI. See https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.PipelineJob
    for details.
    """
    if isinstance(annotation, _AnnotatedAlias):
        if issubclass(annotation.__origin__, kfp.dsl.Artifact):
            return str
    return annotation
