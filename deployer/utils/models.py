from inspect import signature
from typing import Literal

import kfp.components.graph_component
from pydantic import BaseModel, ConfigDict, create_model
from typing_extensions import _AnnotatedAlias


class CustomBaseModel(BaseModel):
    """Base model for all pipeline dynamic configs."""

    # FIXME: arbitrary_types_allowed is a workaround to allow to pass
    #        Vertex Pipelines Artifacts as parameters to a pipeline.
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)


def _convert_artifact_type_to_str(annotation: type) -> type:
    """Convert a kfp.dsl.Artifact type to a string.

    This is mandatory for type checking, as kfp.dsl.Artifact types should be passed as strings
    to VertexAI. See https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.PipelineJob
    for details.
    """  # noqa: E501
    if isinstance(annotation, _AnnotatedAlias):
        if issubclass(annotation.__origin__, kfp.dsl.Artifact):
            return str
    return annotation


def create_model_from_pipeline(
    pipeline: kfp.components.graph_component.GraphComponent,
) -> CustomBaseModel:
    """Create a Pydantic model from pipeline parameters."""
    pipeline_signature = signature(pipeline.pipeline_func)
    pipeline_typing = {
        p.name: _convert_artifact_type_to_str(p.annotation)
        for p in pipeline_signature.parameters.values()
    }

    pipeline_model = create_model(
        __model_name=pipeline.pipeline_spec.pipeline_info.name,
        __base__=CustomBaseModel,
        **{name: (annotation, ...) for name, annotation in pipeline_typing.items()}
    )

    return pipeline_model


class ChecksTableRow(CustomBaseModel):
    """A class to represent a row of the check results table."""

    status: Literal["✅", "⚠️", "❌"]
    pipeline: str
    pipeline_error_message: str = None
    config_path: str
    attribute: str = None
    config_error_type: str = None
    config_error_message: str = None
