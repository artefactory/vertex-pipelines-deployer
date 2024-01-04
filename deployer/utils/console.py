from enum import Enum
from inspect import isclass
from typing import Type

from pydantic import BaseModel
from rich.prompt import Prompt


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
            answer = Prompt.ask(
                f"Do you want to configure command {field_name}?", choices=["y", "n"], default="n"
            )
            if answer == "y":
                set_fields[field_name] = ask_user_for_model_fields(field_info.default)

        else:
            annotation = field_info.annotation
            default = field_info.default
            choices = None

            if isclass(annotation) and issubclass(annotation, Enum):
                choices = list(annotation.__members__)

            if isinstance(field_info.default, bool):
                choices = ["y", "n"]
                default = "y" if field_info.default else "n"

            answer = Prompt.ask(field_name, default=default, choices=choices)

            if isinstance(field_info.default, bool):
                answer = answer == "y"

            if answer != field_info.default:
                set_fields[field_name] = answer

    return set_fields
