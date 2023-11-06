from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, List, Optional

from google.cloud import aiplatform
from google.cloud.aiplatform import PipelineJobSchedule
from kfp import compiler
from kfp.registry import RegistryClient
from loguru import logger
from requests import HTTPError

from deployer.constants import DEFAULT_LOCAL_PACKAGE_PATH
from deployer.utils.exceptions import (
    MissingGoogleArtifactRegistryHostError,
    TagNotFoundError,
)


class VertexPipelineDeployer:
    """Deployer for Vertex Pipelines"""

    def __init__(
        self,
        pipeline_name: str,
        pipeline_func: Callable,
        project_id: Optional[str] = None,
        region: Optional[str] = None,
        staging_bucket_name: Optional[str] = None,
        service_account: Optional[str] = None,
        gar_location: Optional[str] = None,
        gar_repo_id: Optional[str] = None,
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

        self.template_name = None
        self.version_name = None

        aiplatform.init(
            project=self.project_id,
            staging_bucket=f"gs://{self.staging_bucket_name}",
        )

    @property
    def gar_host(self) -> Optional[str]:
        """Return the Artifact Registry host if the location and repo ID are provided"""
        if self.gar_location is not None and self.gar_repo_id is not None:
            return os.path.join(
                f"https://{self.gar_location}-kfp.pkg.dev", self.project_id, self.gar_repo_id
            )
        logger.debug(
            "No Artifact Registry location or repo ID provided: not using Artifact Registry"
        )
        return None

    @property
    def staging_bucket_uri(self) -> str:  # noqa: D102
        return f"gs://{self.staging_bucket_name}/root"

    def _get_template_path(self, tag: Optional[str] = None) -> str:
        """Return the path to the pipeline template

        If the Artifact Registry host is provided, return the path to the pipeline template in
        the Artifact Registry. Otherwise, return the path to the pipeline template in the
        local package.
        """
        if self.gar_host is not None:
            if tag:
                return os.path.join(self.gar_host, self.pipeline_name.replace("_", "-"), tag)

            if self.template_name is not None and self.version_name is not None:
                return os.path.join(self.gar_host, self.template_name, self.version_name)

            logger.warning(
                "tag or template_name and version_name not provided."
                " Falling back to local package."
            )

        return os.path.join(str(self.local_package_path), f"{self.pipeline_name}.yaml")

    def _check_gar_host(self) -> None:
        if self.gar_host is None:
            raise MissingGoogleArtifactRegistryHostError(
                "Google Artifact Registry host is missing. "
                "Please provide gar_location and gar_repo_id."
            )

    def _check_experiment_name(self, experiment_name: Optional[str] = None) -> str:
        if experiment_name is None:
            experiment_name = f"{self.pipeline_name}-experiment".replace("_", "-")
            logger.info(f"Experiment name not provided, using {experiment_name}")
        else:
            experiment_name = experiment_name.replace("_", "-")

        return experiment_name

    def _create_pipeline_job(
        self,
        template_path: str,
        enable_caching: bool = False,
        parameter_values: Optional[dict] = None,
        input_artifacts: Optional[dict] = None,
    ) -> aiplatform.PipelineJob:
        job = aiplatform.PipelineJob(
            display_name=self.pipeline_name,
            template_path=template_path,
            pipeline_root=self.staging_bucket_uri,
            location=self.region,
            enable_caching=enable_caching,
            parameter_values=parameter_values,
            input_artifacts=input_artifacts,
        )
        return job

    def compile(self) -> VertexPipelineDeployer:
        """Compile pipeline and save it to the local package path using kfp compiler"""
        self.local_package_path.mkdir(parents=True, exist_ok=True)
        pipeline_filepath = self.local_package_path / f"{self.pipeline_name}.yaml"

        compiler.Compiler().compile(
            pipeline_func=self.pipeline_func,
            package_path=str(pipeline_filepath),
        )
        logger.info(f"Pipeline {self.pipeline_name} compiled to {pipeline_filepath}")

        return self

    def upload_to_registry(
        self,
        tags: List[str] = ["latest"],  # noqa: B006
    ) -> VertexPipelineDeployer:
        """Upload pipeline to Artifact Registry"""
        self._check_gar_host()
        client = RegistryClient(host=self.gar_host)
        template_name, version_name = client.upload_pipeline(
            file_name=self.local_package_path / f"{self.pipeline_name}.yaml",
            tags=tags,
        )
        logger.info(f"Pipeline {self.pipeline_name} uploaded to {self.gar_host} with tags {tags}")
        self.template_name = template_name
        self.version_name = version_name
        return self

    def run(
        self,
        enable_caching: bool = False,
        parameter_values: Optional[dict] = None,
        input_artifacts: Optional[dict] = None,
        experiment_name: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> VertexPipelineDeployer:
        """Run pipeline on Vertex AI Pipelines

        If the experiment name is not provided, use the pipeline name with the suffix
        "-experiment". Compiled pipeline file is the one uploaded on artifact registry if the
        host is provided, and if either the tag or the template_name and version_name are
        provided. Otherwise, use the pipeline file in the local package.

        Args:
            enable_caching (bool, optional): Whether to enable caching. Defaults to False.
            parameter_values (dict, optional): Pipeline parameter values. Defaults to None.
            input_artifacts (dict, optional): Pipeline input artifacts. Defaults to None.
            experiment_name (str, optional): Experiment name. Defaults to None.
            tag (str, optional): Tag of the pipeline template. Defaults to None.
        """
        experiment_name = self._check_experiment_name(experiment_name)

        template_path = self._get_template_path(tag)

        job = self._create_pipeline_job(
            template_path=template_path,
            enable_caching=enable_caching,
            parameter_values=parameter_values,
            input_artifacts=input_artifacts,
        )

        job.submit(
            experiment=experiment_name,
            service_account=self.service_account,
        )
        return self

    def compile_upload_run(
        self,
        enable_caching: bool = False,
        parameter_values: Optional[dict] = None,
        experiment_name: Optional[str] = None,
        tags: List[str] = ["latest"],  # noqa: B006
    ) -> VertexPipelineDeployer:
        """Compile, upload and run pipeline on Vertex AI Pipelines"""
        self.compile()

        if self.gar_host is not None:
            self.upload_to_registry(tags)

        self.run(
            enable_caching=enable_caching,
            parameter_values=parameter_values,
            experiment_name=experiment_name,
            tag=tags[0] if tags else None,
        )
        return self

    def schedule(
        self,
        cron: str,
        enable_caching: bool = False,
        parameter_values: Optional[dict] = None,
        tag: Optional[str] = None,
        delete_last_schedule: bool = False,
        scheduler_timezone: str = "Europe/Paris",
    ) -> VertexPipelineDeployer:
        """Create pipeline schedule on Vertex AI Pipelines

        Compiled pipeline file is the one uploaded on artifact registry if the host is provided,
        and if either the tag or the template_name and version_name are provided.

        Args:
            cron (str): Cron expression without TZ.
            enable_caching (bool, optional): Whether to enable caching. Defaults to False.
            parameter_values (dict, optional): Pipeline parameter values. Defaults to None.
            tag (str, optional): Tag of the pipeline template. Defaults to None.
            delete_last_schedule (bool, optional): Whether to delete previous schedule.
                Defaults to False.
            scheduler_timezone (str, optional): Scheduler timezone. Must be a valid string from
                IANA time zone database. Defaults to 'Europe/Paris'.
        """
        self._check_gar_host()

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
            package_name = self.pipeline_name.replace("_", "-")
            try:
                tag_metadata = client.get_tag(package_name=package_name, tag=tag)
            except HTTPError as e:
                tags_list = client.list_tags(package_name)
                tags_list_parsed = [x["name"].split("/")[-1] for x in tags_list]
                raise TagNotFoundError(
                    f"Tag {tag} not found for package {self.gar_host}/{package_name}.\
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

        pipeline_job_schedule.create(
            cron=f"TZ={scheduler_timezone} {cron}",
            service_account=self.service_account,
        )

        return self
