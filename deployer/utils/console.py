from enum import Enum
from inspect import isclass
from typing import Type

from pydantic import BaseModel
from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()


def ask_user_for_model_fields(model: Type[BaseModel]) -> dict:
    """Ask user for model fields and return a dictionary with the results.

    Args:
        model (Type[BaseModel]): The pydantic model to configure.

    Returns:
        dict: A dictionary of the set fields.
    """
    set_fields = {}

    for field_name, field_info in model.model_fields.items():
        if isclass(field_info.annotation) and issubclass(field_info.annotation, BaseModel):
            answer = Confirm.ask(f"Do you want to configure command {field_name}?", default=False)
            if answer:
                set_fields[field_name] = ask_user_for_model_fields(field_info.annotation)

        else:
            annotation = field_info.annotation
            default = field_info.default
            choices = None

            if isclass(annotation) and issubclass(annotation, Enum):
                choices = list(annotation.__members__)
            if isclass(annotation) and annotation is bool:
                answer = Confirm.ask(field_name, default=default)
            else:
                answer = Prompt.ask(
                    field_name, default=default if default is not None else "None", choices=choices
                )

            if answer != field_info.default and not (
                answer in [None, "None"] and field_info.default is None
            ):
                set_fields[field_name] = answer

    return set_fields
