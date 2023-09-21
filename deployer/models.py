from inspect import signature

import kfp.components.graph_component
from pydantic import BaseModel, ConfigDict, create_model

from deployer.constants import PIPELINE_ROOT_PATH
from deployer.utils import make_pipeline_names_enum_from_dir


class CustomBaseModel(BaseModel):
    """Base model for all pipeline dynamic configs."""

    model_config = ConfigDict(extra="forbid")


def create_model_from_pipeline(
    pipeline: kfp.components.graph_component.GraphComponent,
) -> CustomBaseModel:
    """Create a Pydantic model from pipeline parameters."""
    pipeline_signature = signature(pipeline.pipeline_func)
    pipeline_typing = {p.name: p.annotation for p in pipeline_signature.parameters.values()}

    pipeline_model = create_model(
        __model_name=pipeline.pipeline_spec.pipeline_info.name,
        __base__=CustomBaseModel,
        **{name: (annotation, ...) for name, annotation in pipeline_typing.items()}
    )

    return pipeline_model


PipelineName = make_pipeline_names_enum_from_dir(PIPELINE_ROOT_PATH)
