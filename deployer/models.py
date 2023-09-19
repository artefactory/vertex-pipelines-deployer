from inspect import signature

import kfp.components.graph_component
from pydantic import BaseModel, ConfigDict, create_model


class CustomBaseModel(BaseModel):
    """Base model for all pipeline dynamic configs."""

    model_config = ConfigDict(extra="forbid")


def to_title(snake_str):
    """Convert a snake string to title case."""
    snake_str = snake_str.replace("-", "_").replace(" ", "_")
    components = snake_str.split("_")
    return "".join(x.title() for x in components)


def create_model_from_pipeline(
    pipeline: kfp.components.graph_component.GraphComponent,
) -> CustomBaseModel:
    """Create a Pydantic model from pipeline parameters."""
    pipeline_signature = signature(pipeline.pipeline_func)
    pipeline_typing = {p.name: p.annotation for p in pipeline_signature.parameters.values()}

    pipeline_name = to_title(pipeline.pipeline_spec.pipeline_info.name)

    pipeline_model = create_model(
        __model_name=pipeline_name,
        __base__=CustomBaseModel,
        **{name: (annotation, ...) for name, annotation in pipeline_typing.items()}
    )

    return pipeline_model
