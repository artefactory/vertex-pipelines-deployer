import argparse
import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

from deployer.deployer import VertexPipelineDeployer
from deployer.utils import (
    import_pipeline_from_dir,
    load_config,
    make_pipeline_names_enum_from_dir,
)

PIPELINE_ROOT_PATH = Path(__file__).parent.parent / "pipelines"

PipelineNames = make_pipeline_names_enum_from_dir(PIPELINE_ROOT_PATH)


def get_args():  # noqa: D103
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "pipeline_name",
        type=str,
        choices=[e.value for e in PipelineNames],
        help="The name of the pipeline to run.",
    )
    parser.add_argument(
        "--env-file",
        "-e",
        type=str,
        default=argparse.SUPPRESS,
        help="The environment to run the pipeline in.",
    )
    parser.add_argument(
        "--compile",
        "-c",
        action="store_true",
        help="Whether to compile the pipeline.",
    )
    parser.add_argument(
        "--upload",
        "-u",
        action="store_true",
        help="Whether to upload the pipeline to the registry.",
    )
    parser.add_argument(
        "--run",
        "-r",
        action="store_true",
        help="Whether to run the pipeline.",
    )
    parser.add_argument(
        "--schedule",
        "-s",
        action="store_true",
        help="Whether to create a schedule for the pipeline.",
    )
    parser.add_argument(
        "--cron",
        type=str,
        default=argparse.SUPPRESS,
        help="Cron expression for scheduling the pipeline.",
    )
    parser.add_argument(
        "--delete-last-schedule",
        "-dls",
        action="store_true",
        help="Whether to delete the previous schedule before creating a new one.",
    )
    parser.add_argument(
        "--tags",
        type=str,
        nargs="*",
        help="The tags to use when uploading the pipeline.",
    )
    parser.add_argument(
        "--config-name",
        "-cn",
        type=str,
        default=argparse.SUPPRESS,
        help="The name of the configuration file to use when running the pipeline.",
    )
    parser.add_argument(
        "--enable-caching",
        "-ec",
        action="store_true",
        help="Whether to enable caching when running the pipeline.",
    )
    parser.add_argument(
        "--experiment-name",
        "-exp",
        type=str,
        default=argparse.SUPPRESS,
        help="The name of the experiment to run the pipeline in.",
    )
    parser.add_argument(
        "--local-package-path",
        "-lpp",
        type=Path,
        default=argparse.SUPPRESS,
        help="The path to the local package to upload.",
    )
    return parser.parse_args()


def main(  # noqa: D103
    pipeline_name: PipelineNames,
    env_file: str | None = None,
    compile: bool = True,
    upload: bool = False,
    run: bool = True,
    schedule: bool = False,
    cron: str | None = None,
    delete_last_schedule: bool = False,
    tags: list = ["latest"],  # noqa: B006
    config_name: str | None = None,
    enable_caching: bool = False,
    experiment_name: str | None = None,
    local_package_path: Path = Path("."),
) -> None:
    if env_file is not None:
        find_dotenv(env_file, raise_error_if_not_found=True)
        load_dotenv(env_file)

    project_id = os.environ["PROJECT_ID"]
    region = os.environ["GCP_REGION"]
    staging_bucket_name = os.environ["VERTEX_STAGING_BUCKET_NAME"]
    service_account = os.environ["VERTEX_SERVICE_ACCOUNT"]
    pipeline_func = import_pipeline_from_dir(PIPELINE_ROOT_PATH, pipeline_name.replace("-", "_"))
    gar_location = os.environ["GAR_LOCATION"] if (upload or schedule) else None
    gar_repo_id = f"{os.environ['GAR_REPO_ID']}-kfp" if (upload or schedule) else None

    deployer = VertexPipelineDeployer(
        project_id=project_id,
        region=region,
        staging_bucket_name=staging_bucket_name,
        service_account=service_account,
        pipeline_name=pipeline_name,
        pipeline_func=pipeline_func,
        gar_location=gar_location,
        gar_repo_id=gar_repo_id,
        local_package_path=local_package_path,
    )

    if run or schedule:
        if config_name is None:
            raise ValueError(
                "`config_name` must be specified when running or scheduling the pipeline"
            )
        SELECTED_CONFIGURATION = load_config(
            config_name=config_name, pipeline_name=pipeline_name.replace("-", "_")
        )

    if compile:
        deployer.compile()

    if upload:
        deployer.upload_to_registry(tags=tags)

    if run:
        deployer.run(
            enable_caching=enable_caching,
            parameter_values=SELECTED_CONFIGURATION,
            experiment_name=experiment_name,
        )

    if schedule:
        if cron is None:
            raise ValueError("`cron` must be specified when scheduling the pipeline")
        cron = cron.replace("-", " ")  # ugly fix to allow cron expression as env variable
        deployer.create_pipeline_schedule(
            cron=cron,
            enable_caching=enable_caching,
            parameter_values=SELECTED_CONFIGURATION,
            tag=tags[0] if tags else None,
        )


def cli():  # noqa: D103
    import logging

    logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

    args = get_args()

    main(**vars(args))
