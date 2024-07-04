from inspect import Parameter, signature
from typing import Callable, Literal, Optional, Protocol

from pydantic import BaseModel, ConfigDict, create_model


class CustomBaseModel(BaseModel):
    """Base model for all pipeline dynamic configs."""

    # FIXME: arbitrary_types_allowed is a workaround to allow to pass
    #        Vertex Pipelines Artifacts as parameters to a pipeline.
    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        protected_namespaces=(),
        validate_default=True,
    )


class TypeConverterType(Protocol):
    """Type converter function type."""

    def __call__(self, annotation: type) -> type:  # noqa: D102
        ...


def _dummy_type_converter(annotation: type) -> type:
    """Dummy type converter function."""
    return annotation


def create_model_from_func(
    func: Callable,
    model_name: Optional[str] = None,
    type_converter: Optional[TypeConverterType] = None,
    exclude_defaults: bool = False,
) -> CustomBaseModel:
    """Create a Pydantic model from pipeline parameters."""
    if model_name is None:
        model_name = func.__name__

    if type_converter is None:
        type_converter = _dummy_type_converter

    func_signature = signature(func)

    func_typing = {
        p.name: (
            type_converter(p.annotation),
            ... if (exclude_defaults or p.default == Parameter.empty) else p.default,
        )
        for p in func_signature.parameters.values()
    }

    func_model = create_model(
        model_name,
        __base__=CustomBaseModel,
        **func_typing,
    )

    return func_model


class ChecksTableRow(CustomBaseModel):
    """A class to represent a row of the check results table."""

    status: Literal["✅", "⚠️", "❌"]
    pipeline: str
    pipeline_error_message: Optional[str] = None
    config_file: str
    attribute: Optional[str] = None
    config_error_type: Optional[str] = None
    config_error_message: Optional[str] = None
