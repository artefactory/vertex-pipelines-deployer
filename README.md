# vertex-pipelines-deployer

Repository for the Vertex Pipelines Deployer. This is a tool is a wrapper aound `kfp` and `google-cloud-aiplatform` that allows you to deploy Vertex Pipelines to a Vertex AI Pipelines endpoint in a standardized manner.


## Installation

## Usage

## Repository Structure


# TODO
1. Features
    1. handle multiple config files formats (toml, json, yaml)
    2. allow for multiple config files as inputs
    3. CLI to typer to have multiple commands (check, deploy, init, etc)
    4. Possibility to store env variables in a env class stored somewhere
    5. Dynamic config checks using pydantic
    6. Scheduling with cloud function instead of cloud scheduler
    7. versioning of config files on a gcs bucket
2. Add more documentation
3. Add review flow
4. Add PR and Issue templates
5. publish on Pypi
