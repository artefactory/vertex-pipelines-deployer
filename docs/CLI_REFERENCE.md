# `vertex-deployer`

**Usage**:

```console
$ vertex-deployer [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-log, --log-level [TRACE|DEBUG|INFO|SUCCESS|WARNING|ERROR|CRITICAL]`: Set the logging level.  [default: INFO]
* `-v, --version`: Display the version number and exit.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `check`: Check that pipelines are valid.
* `config`: Display the configuration from...
* `create`: Create files structure for a new pipeline.
* `deploy`: Compile, upload, run and schedule pipelines.
* `init`: Initialize the deployer.
* `list`: List all pipelines.

## `vertex-deployer check`

Check that pipelines are valid.

Checking that a pipeline is valid includes:

* Checking that the pipeline can be imported. It must be a valid python module with a
`{pipeline_name}` function decorated with `@kfp.dsl.pipeline`.

* Checking that the pipeline can be compiled using `kfp.compiler.Compiler`.

* Checking that config files in `{configs_root_path}/{pipeline_name}` are corresponding to the
pipeline parameters definition, using Pydantic.

---

**This command can be used to check pipelines in a Continuous Integration workflow.**

**Usage**:

```console
$ vertex-deployer check [OPTIONS] [PIPELINE_NAMES]...
```

**Arguments**:

* `[PIPELINE_NAMES]...`: The names of the pipeline to check.

**Options**:

* `-a, --all`: Whether to check all pipelines.
* `-cfp, --config-filepath FILE`: Path to the json/py file with parameter values and input artifactsto check. If not specified, all config files in the pipeline dir will be checked.
* `-re, --raise-error / -nre, --no-raise-error`: Whether to raise an error if the pipeline is not valid.  [default: no-raise-error]
* `-wd, --warn-defaults / -nwd, --no-warn-defaults`: Whether to warn when a default value is used.and not overwritten in config file.  [default: warn-defaults]
* `-rfd, --raise-for-defaults / -nrfd, --no-raise-for-defaults`: Whether to raise an validation error when a default value is used.and not overwritten in config file.  [default: no-raise-for-defaults]
* `--help`: Show this message and exit.

## `vertex-deployer config`

Display the configuration from pyproject.toml.

**Usage**:

```console
$ vertex-deployer config [OPTIONS]
```

**Options**:

* `-a, --all`: Whether to display all configuration values.
* `--help`: Show this message and exit.

## `vertex-deployer create`

Create files structure for a new pipeline.

**Usage**:

```console
$ vertex-deployer create [OPTIONS] PIPELINE_NAMES...
```

**Arguments**:

* `PIPELINE_NAMES...`: The names of the pipeline to create.  [required]

**Options**:

* `-ct, --config-type [json|py|toml|yaml]`: The type of the config to create.  [default: py]
* `--help`: Show this message and exit.

## `vertex-deployer deploy`

Compile, upload, run and schedule pipelines.

**Usage**:

```console
$ vertex-deployer deploy [OPTIONS] PIPELINE_NAMES...
```

**Arguments**:

* `PIPELINE_NAMES...`: The names of the pipeline to run.  [required]

**Options**:

* `--env-file FILE`: The environment file to use.
* `-c, --compile / -nc, --no-compile`: Whether to compile the pipeline.  [default: compile]
* `-u, --upload / -nu, --no-upload`: Whether to upload the pipeline to Google Artifact Registry.  [default: no-upload]
* `-r, --run / -nr, --no-run`: Whether to run the pipeline.  [default: no-run]
* `-s, --schedule / -ns, --no-schedule`: Whether to create a schedule for the pipeline.  [default: no-schedule]
* `--cron TEXT`: Cron expression for scheduling the pipeline. To pass it to the CLI, use hyphens e.g. '0-10-*-*-*'.
* `-dls, --delete-last-schedule`: Whether to delete the previous schedule before creating a new one.
* `--scheduler-timezone TEXT`: Timezone for scheduling the pipeline. Must be a valid string from IANA time zone database  [default: Europe/Paris]
* `--tags TEXT`: The tags to use when uploading the pipeline.
* `-cfp, --config-filepath FILE`: Path to the json/py file with parameter values and input artifacts to use when running the pipeline.
* `-cn, --config-name TEXT`: Name of the json/py file with parameter values and input artifacts to use when running the pipeline. It must be in the pipeline config dir. e.g. `config_dev.json` for `./vertex/configs/{pipeline-name}/config_dev.json`.
* `-ec, --enable-caching / -nec, --no-cache`: Whether to turn on caching for the run.If this is not set, defaults to the compile time settings, which are True for alltasks by default, while users may specify different caching options for individualtasks. If this is set, the setting applies to all tasks in the pipeline.Overrides the compile time settings. Defaults to None.
* `-en, --experiment-name TEXT`: The name of the experiment to run the pipeline in.Defaults to '{pipeline_name}-experiment'.
* `-rn, --run-name TEXT`: The pipeline's run name. Displayed in the UI.Defaults to '{pipeline_name}-{tags}-%Y%m%d%H%M%S'.
* `-y, --skip-validation / -n, --no-skip`: Whether to continue without user validation of the settings.  [default: skip-validation]
* `--help`: Show this message and exit.

## `vertex-deployer init`

Initialize the deployer.

**Usage**:

```console
$ vertex-deployer init [OPTIONS]
```

**Options**:

* `-d, --default`: Instantly creates the full vertex structure and files without configuration prompts
* `--help`: Show this message and exit.

## `vertex-deployer list`

List all pipelines.

**Usage**:

```console
$ vertex-deployer list [OPTIONS]
```

**Options**:

* `-wc, --with-configs / -nc , --no-configs`: Whether to list config files.  [default: no-configs]
* `--help`: Show this message and exit.
