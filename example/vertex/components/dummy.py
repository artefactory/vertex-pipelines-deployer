from kfp.dsl import component


@component(base_image="python:3.10-slim-buster")
def dummy_component(name: str):
    """This component is a dummy"""
    print(f"Hello, {name}!")


@component(base_image="python:3.10-slim-buster")
def broken_component(name: str):
    """This component is broken!"""
    print(f"Hello, {name}!")
    raise ValueError("This component is broken!")
