from ast import literal_eval
from enum import Enum
from inspect import isclass
from pathlib import Path
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
    exclude_fields = ["pipelines_root_path", "config_root_path"]

    for field_name, field_info in model.model_fields.items():
        if field_name in exclude_fields:
            continue
        elif isclass(field_info.annotation) and issubclass(field_info.annotation, BaseModel):
            answer = Confirm.ask(f"Do you want to configure command {field_name}?", default=False)
            if answer:
                set_fields[field_name] = ask_user_for_model_fields(field_info.annotation)

        else:
            annotation = field_info.annotation
            default = field_info.default
            choices = None

            if isclass(annotation) and issubclass(annotation, Enum):
                choices = list(annotation.__members__)

            if isclass(annotation) and annotation == bool:
                answer = Confirm.ask(field_name, default=default)
            else:
                answer = Prompt.ask(field_name, default=str(default), choices=choices)

            # Attempt to evaluate the answer as a Python literal if it's a string
            if isinstance(answer, str):
                try:
                    answer = literal_eval(answer)
                except (ValueError, SyntaxError):
                    # If literal_eval fails, keep the string as is
                    pass

            if answer != default:
                set_fields[field_name] = answer

    # TODO: This is a hack to set the pipelines_root_path and config_root_path
    # to the correct values. This should be done with a Pydantic validator.
    set_fields["pipelines_root_path"] = Path(set_fields["vertex_folder_path"]) / "pipelines"
    set_fields["config_root_path"] = Path(set_fields["vertex_folder_path"]) / "configs"

    return set_fields
