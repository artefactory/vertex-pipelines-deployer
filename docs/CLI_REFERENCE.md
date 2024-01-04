# `vertex-deployer`

**Usage**:

```console
$ vertex-deployer [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--log-level, -log [TRACE|DEBUG|INFO|SUCCESS|WARNING|ERROR|CRITICAL]`: Set the logging level. [default: INFO]
* `--version, -v`: Display the version number and exit.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `check`: Check that pipelines are valid.
* `config`: Display the configuration from pyproject.toml.
* `create`: Create files structure for a new pipeline.
* `deploy`: Compile, upload, run and schedule pipelines.
* `init`: Initialize the deployer with default settings and folder structure.
* `list`: List all pipelines.

## `vertex-deployer check`

Check that pipelines are valid.

Checking that a pipeline is valid includes:

* Checking that the pipeline can be imported. It must be a valid python module with a
`pipeline` function decorated with `@kfp.dsl.pipeline`.

* Checking that the pipeline can be compiled using `kfp.compiler.Compiler`.

* Checking that config files in `{CONFIG_ROOT_PATH}/{pipeline_name}` are corresponding to the
pipeline parameters definition, using Pydantic.

---

**This command can be used to check pipelines in a Continuous Integration workflow.**

**Usage**:

```console
$ vertex-deployer check [OPTIONS]
```

**Options**:

* `--pipeline-name []`
* `--all, -a / --no-all`: Whether to check all pipelines. [default: no-all]
* `--config-filepath, -cfp PATH`: Path to the json/py file with parameter values and input artifacts to check. If not specified, all config files in the pipeline dir will be checked.
* `--raise-error, -re / --no-raise-error, -nre`: Whether to raise an error if the pipeline is not valid. [default: no-raise-error]
* `--help`: Show this message and exit.

## `vertex-deployer config`

Display the configuration from pyproject.toml.

**Usage**:

```console
$ vertex-deployer config [OPTIONS]
```

**Options**:

* `--all, -a`: Whether to display all configuration values.
* `--help`: Show this message and exit.

## `vertex-deployer create`

Create files structure for a new pipeline.

**Usage**:

```console
$ vertex-deployer create [OPTIONS] PIPELINE_NAME
```

**Arguments**:

* `PIPELINE_NAME`: The name of the pipeline to create. [required]

**Options**:

* `--config-type, -ct [json|py|toml]`: The type of the config to create. [default: json]
* `--help`: Show this message and exit.

## `vertex-deployer deploy`

Compile, upload, run and schedule pipelines.

**Usage**:

```console
$ vertex-deployer deploy [OPTIONS] PIPELINE_NAME
```

**Arguments**:

* `PIPELINE_NAME`: The name of the pipeline to deploy. [required]

**Options**:

* `--env-file PATH`: The environment file to use.
* `--compile, -c / --no-compile, -nc`: Whether to compile the pipeline. [default: compile]
* `--upload, -u / --no-upload, -nu`: Whether to upload the pipeline to Google Artifact Registry. [default: no-upload]
* `--run, -r / --no-run, -nr`: Whether to run the pipeline. [default: no-run]
* `--schedule, -s / --no-schedule, -ns`: Whether to create a schedule for the pipeline. [default: no-schedule]
* `--cron TEXT`: Cron expression for scheduling the pipeline. To pass it to the CLI, use hyphens e.g. `0-10-*-*-*`.
* `--delete-last-schedule, -dls / --no-delete-last-schedule`: Whether to delete the previous schedule before creating a new one. [default: no-delete-last-schedule]
* `--tags TEXT`: The tags to use when uploading the pipeline. [default: latest]
* `--config-filepath, -cfp PATH`: Path to the json/py file with parameter values and input artifacts to use when running the pipeline.
* `--config-name, -cn TEXT`: Name of the json/py file with parameter values and input artifacts to use when running the pipeline. It must be in the pipeline config dir. e.g. `config_dev.json` for `./vertex/configs/{pipeline-name}/config_dev.json`.
* `--enable-caching, -ec / --no-enable-caching`: Whether to enable caching when running the pipeline. [default: no-enable-caching]
* `--experiment-name, -en TEXT`: The name of the experiment to run the pipeline in. Defaults to '{pipeline_name}-experiment'.
* `--local-package-path, -lpp PATH`: Local dir path where pipelines will be compiled. [default: vertex/pipelines/compiled_pipelines]
* `--help`: Show this message and exit.

## `vertex-deployer init`

Initialize the deployer with default settings and folder structure.

**Usage**:

```console
$ vertex-deployer init
```

**Options**:

* `--help`: Show this message and exit.

## `vertex-deployer list`

List all pipelines.

**Usage**:

```console
$ vertex-deployer list [OPTIONS]
```

**Options**:

* `--with-configs, -wc / --no-with-configs, -nc`: Whether to list config files. [default: no-with-configs]
* `--help`: Show this message and exit.
