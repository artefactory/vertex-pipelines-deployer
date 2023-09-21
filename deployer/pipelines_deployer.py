from pathlib import Path
from typing import Callable
from urllib.parse import urljoin

from google.cloud import aiplatform
from google.cloud.aiplatform import PipelineJobSchedule
from kfp import compiler
from kfp.registry import RegistryClient
from loguru import logger
from requests import HTTPError

from deployer.constants import DEFAULT_LOCAL_PACKAGE_PATH, DEFAULT_SCHEDULER_TIMEZONE
from deployer.exceptions import TagNotFoundError


def check_gar_host(func):
    """Decorator to check that the Artifact Registry host is provided"""

    def wrapper(self, *args, **kwargs):
        if self.gar_host is None:
            raise ValueError("Artifact Registry host not provided.")
        return func(self, *args, **kwargs)

    return wrapper


class VertexPipelineDeployer:
    """Deployer for Vertex Pipelines"""

    def __init__(
        self,
        pipeline_name: str,
        pipeline_func: Callable,
        project_id: str | None = None,
        region: str | None = None,
        staging_bucket_name: str | None = None,
        service_account: str | None = None,
        gar_location: str | None = None,
        gar_repo_id: str | None = None,
        local_package_path: Path = DEFAULT_LOCAL_PACKAGE_PATH,
    ) -> None:
        """I don't want to write a dostring here but ruff wants me to"""
        self.project_id = project_id
        self.region = region
        self.staging_bucket_name = staging_bucket_name
        self.service_account = service_account

        self.pipeline_name = pipeline_name
        self.pipeline_func = pipeline_func

        self.gar_location = gar_location
        self.gar_repo_id = gar_repo_id
        self.local_package_path = Path(local_package_path)

        self.gar_host = self._get_artifact_registry_host()

        self.template_name = None
        self.version_name = None

        aiplatform.init(
            project=self.project_id,
            staging_bucket=f"gs://{self.staging_bucket_name}",
        )

    def _get_artifact_registry_host(self) -> str | None:
        """Return the Artifact Registry host if the location and repo ID are provided"""
        if self.gar_location is not None and self.gar_repo_id is not None:
            return urljoin(
                f"https://{self.gar_location}-kfp.pkg.dev", self.project_id, self.gar_repo_id
            )
        logger.debug(
            "No Artifact Registry location or repo ID provided: not using Artifact Registry"
        )
        return None

    def _get_template_path(self, tag: str | None = None) -> str:
        """Return the path to the pipeline template

        If the Artifact Registry host is provided, return the path to the pipeline template in
        the Artifact Registry. Otherwise, return the path to the pipeline template in the
        local package.
        """
        if self.gar_host is not None:
            if tag:
                return f"{self.gar_host}/{self.pipeline_name}/{tag}"

            if self.template_name is not None and self.version_name is not None:
                return f"{self.gar_host}/{self.template_name}/{self.version_name}"

            raise ValueError("tag or template_name and version_name must be provided")

        return str(self.local_package_path / f"{self.pipeline_name}.yaml")

    def _create_pipeline_job(
        self,
        template_path: str,
        enable_caching: bool = False,
        parameter_values: dict | None = None,
    ) -> aiplatform.PipelineJob:
        job = aiplatform.PipelineJob(
            display_name=self.pipeline_name,
            template_path=template_path,
            pipeline_root=f"gs://{self.staging_bucket_name}/root",
            location=self.region,
            enable_caching=enable_caching,
            parameter_values=parameter_values,
        )
        return job

    def compile(self) -> "VertexPipelineDeployer":
        """Compile pipeline and save it to the local package path using kfp compiler"""
        self.local_package_path.mkdir(parents=True, exist_ok=True)
        pipeline_filepath = self.local_package_path / f"{self.pipeline_name}.yaml"

        compiler.Compiler().compile(
            pipeline_func=self.pipeline_func,
            package_path=str(pipeline_filepath),
        )
        logger.info(f"Pipeline {self.pipeline_name} compiled to {pipeline_filepath}")

        return self

    @check_gar_host
    def upload_to_registry(
        self,
        tags: list[str] = ["latest"],  # noqa: B006
    ) -> "VertexPipelineDeployer":
        """Upload pipeline to Artifact Registry"""
        client = RegistryClient(host=self.gar_host)
        template_name, version_name = client.upload_pipeline(
            file_name=f"{self.pipeline_name}.yaml",
            tags=tags,
        )
        logger.info(f"Pipeline {self.pipeline_name} uploaded to {self.gar_host} with tags {tags}")
        self.template_name = template_name
        self.version_name = version_name
        return self

    def run(
        self,
        enable_caching: bool = False,
        parameter_values: dict | None = None,
        experiment_name: str | None = None,
        tag: str | None = None,
    ) -> "VertexPipelineDeployer":
        """Run pipeline on Vertex AI Pipelines

        If the experiment name is not provided, use the pipeline name with the suffix
        "-experiment". Compiled pipeline file is the one uploaded on artifact registry if the
        host is provided, and if either the tag or the template_name and version_name are
        provided. Otherwise, use the pipeline file in the local package.

        Args:
            enable_caching (bool, optional): Whether to enable caching. Defaults to False.
            parameter_values (dict, optional): Pipeline parameter values. Defaults to None.
            experiment_name (str, optional): Experiment name. Defaults to None.
            tag (str, optional): Tag of the pipeline template. Defaults to None.
        """
        if experiment_name is None:
            experiment_name = f"{self.pipeline_name}-experiment".replace("_", "-")
            logger.info(f"Experiment name not provided, using {experiment_name}")

        template_path = self._get_template_path(tag)

        job = self._create_pipeline_job(
            template_path=template_path,
            enable_caching=enable_caching,
            parameter_values=parameter_values,
        )

        job.submit(
            experiment=experiment_name,
            service_account=self.service_account,
        )
        return self

    def deploy_and_run(
        self,
        enable_caching: bool = False,
        parameter_values: dict | None = None,
        experiment_name: str | None = None,
        tags: list[str] = ["latest"],  # noqa: B006
    ) -> "VertexPipelineDeployer":
        """Compile, upload and run pipeline on Vertex AI Pipelines"""
        self.compile()

        if self.gar_host is not None:
            self.upload_to_registry(tags)

        self.run(
            enable_caching=enable_caching,
            parameter_values=parameter_values,
            experiment_name=experiment_name,
        )
        return self

    @check_gar_host
    def create_pipeline_schedule(
        self,
        cron: str,
        enable_caching: bool = False,
        parameter_values: dict | None = None,
        tag: str | None = None,
        delete_last_schedule: bool = False,
    ) -> "VertexPipelineDeployer":
        """Create pipeline schedule on Vertex AI Pipelines

        Compiled pipeline file is the one uploaded on artifact registry if the host is provided,
        and if either the tag or the template_name and version_name are provided.

        Args:
            cron (str): Cron expression without TZ. TZ is hardcoded to 'TZ=Europe/Paris'.
            enable_caching (bool, optional): Whether to enable caching. Defaults to False.
            parameter_values (dict, optional): Pipeline parameter values. Defaults to None.
            tag (str, optional): Tag of the pipeline template. Defaults to None.
            delete_last_schedule (bool, optional): Whether to delete previous schedule.
                Defaults to False.
        """
        schedule_display_name = f"schedule-{self.pipeline_name}"
        schedules_list = PipelineJobSchedule.list(
            filter=f'display_name="{schedule_display_name}"',
            order_by="create_time desc",
            location=self.region,
        )

        logger.info(
            f"There are {len(schedules_list)} schedules defined for pipeline {self.pipeline_name}"
        )
        if len(schedules_list) > 0 and delete_last_schedule:
            logger.info(
                f"Deleting schedule {schedules_list[0].display_name}"
                f" for pipeline {self.pipeline_name} at {schedules_list[0].cron}"
            )
            schedules_list[0].delete()

        if tag:
            client = RegistryClient(host=self.gar_host)
            try:
                tag_metadata = client.get_tag(package_name=self.pipeline_name, tag=tag)
            except HTTPError as e:
                tags_list = client.list_tags(self.pipeline_name)
                tags_list_parsed = [x["name"].split("/")[-1] for x in tags_list]
                raise TagNotFoundError(
                    f"Tag {tag} not found for package {self.gar_host}/{self.pipeline_name}.\
                        Available tags: {tags_list_parsed}"
                ) from e

            pipeline_version_sha = tag_metadata["version"].split("/")[-1]

            template_path = self._get_template_path(pipeline_version_sha)
        else:
            template_path = self._get_template_path()

        logger.info(
            f"Creating schedule for pipeline {self.pipeline_name} at {cron}"
            f" with template {template_path}"
        )

        job = self._create_pipeline_job(
            template_path=template_path,
            enable_caching=enable_caching,
            parameter_values=parameter_values,
        )

        # HACK: Must set location or it will default to "us-central1" (or project default)
        pipeline_job_schedule = PipelineJobSchedule(
            pipeline_job=job,
            display_name=schedule_display_name,
            location=self.region,
        )
        # TZ must be a valid string from IANA time zone database
        pipeline_job_schedule.create(
            cron=f"TZ={DEFAULT_SCHEDULER_TIMEZONE} {cron}",
            service_account=self.service_account,
        )

        return self
