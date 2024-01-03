import difflib
from collections import defaultdict
from inspect import signature
from typing import Type
from unittest.mock import patch

import typer
from pydantic import BaseModel
from rich.pretty import pretty_repr
from typing_extensions import _AnnotatedAlias

from deployer.settings import DeployerSettings


def get_model_recursive_signature(model: Type[BaseModel]):
    config_parameters = signature(model).parameters
    model_signature = {}
    for param in config_parameters.values():
        if isinstance(param.default, BaseModel):
            model_signature[param.name] = get_model_recursive_signature(param.default.__class__)
        else:
            if isinstance(param.annotation, _AnnotatedAlias):
                annotation = param.annotation.__origin__
            else:
                annotation = param.annotation
            info = {"type": annotation, "default": param.default}
            model_signature[param.name] = info
    return model_signature


def get_typer_app_signature(app: typer.Typer):
    registered_commands = app.registered_commands
    parameters = defaultdict(dict)
    for cmd in registered_commands:
        cmd_func = cmd.callback
        cmd_parameters = signature(cmd_func).parameters
        cmd_name = cmd_func.__name__

        for param in cmd_parameters.values():
            annotation = param.annotation
            if isinstance(annotation, _AnnotatedAlias):
                if isinstance(annotation.__metadata__[0], typer.models.OptionInfo):
                    info = {"type": annotation.__origin__, "default": param.default}
                    parameters[cmd_name][param.name] = info

    return dict(parameters)


def compare_dicts(d1, d2):
    return "\n" + "\n".join(
        difflib.ndiff(
            pretty_repr(d1, expand_all=True).splitlines(),
            pretty_repr(d2, expand_all=True).splitlines(),
        )
    )


def test_deployer_cli_and_settings_consistency():
    # Given

    # patch deployer.settings:load_deployer_settings
    with patch("deployer.settings.load_deployer_settings") as mock:
        mock.return_value = DeployerSettings()
        from deployer.cli import app

    configured_parameters = {
        k: v
        for k, v in get_model_recursive_signature(DeployerSettings).items()
        if k not in ["pipelines_root_path", "config_root_path", "log_level"]
    }
    cli_parameters = get_typer_app_signature(app)

    # When
    diff = None
    if cli_parameters != configured_parameters:
        diff = compare_dicts(cli_parameters, configured_parameters)

    # Then
    assert not diff, f"CLI and configuration are diverging, {diff}"
