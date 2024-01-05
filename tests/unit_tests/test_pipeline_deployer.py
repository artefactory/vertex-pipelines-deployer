from unittest.mock import patch

import pytest
from google.cloud import aiplatform

from deployer.pipeline_deployer import VertexPipelineDeployer


class TestCreatePipelineJob:
    def test_create_pipeline_job_with_all_parameters(self, test_pipeline_fixture, tmp_path):
        # Given
        pipeline_name = "test_pipeline"
        template_path = tmp_path / f"{pipeline_name}.yaml"
        enable_caching = True
        parameter_values = {"name": "johndoe"}
        input_artifacts = {"input1": "path/to/input1", "input2": "path/to/input2"}

        deployer = VertexPipelineDeployer(
            pipeline_name=pipeline_name,
            pipeline_func=test_pipeline_fixture,
            project_id="my_project",
            region="us-central1",
            staging_bucket_name="my_bucket",
            service_account="my_service_account",
            local_package_path=tmp_path,
        )
        deployer.compile()

        # When
        job = deployer._create_pipeline_job(
            template_path=str(template_path),
            enable_caching=enable_caching,
            parameter_values=parameter_values,
            input_artifacts=input_artifacts,
        )

        # Then
        assert isinstance(job, aiplatform.pipeline_jobs.PipelineJob)
        assert job._gca_resource.display_name == "test_pipeline"
        assert job.location == "us-central1"

    @pytest.mark.parametrize(
        "template_filename, pipeline_name",
        [
            ("template.yaml", "test_pipeline"),
            ("", "test_pipeline"),
            ("template.yaml", ""),
            ("template.yaml", None),
            ("another_pipeline_name.yaml", "another_pipeline_name"),
        ],
    )
    def test_create_pipeline_job_with_wrong_template_path_raises_error(
        self, template_filename, pipeline_name, test_pipeline_fixture, tmp_path
    ):
        # Given
        template_path = tmp_path / template_filename
        enable_caching = True
        parameter_values = {"param1": "value1", "param2": "value2"}
        input_artifacts = {"input1": "path/to/input1", "input2": "path/to/input2"}

        deployer = VertexPipelineDeployer(
            pipeline_name=pipeline_name,
            pipeline_func=test_pipeline_fixture,
            project_id="my_project",
            region="us-central1",
            staging_bucket_name="my_bucket",
            service_account="my_service_account",
        )

        # Then
        with pytest.raises((FileNotFoundError, IsADirectoryError)):
            # When
            deployer._create_pipeline_job(
                template_path=str(template_path),
                enable_caching=enable_caching,
                parameter_values=parameter_values,
                input_artifacts=input_artifacts,
            )


class TestUploadToRegistry:
    def test_upload_to_registry_with_all_parameters(
        self, test_pipeline_fixture, tmp_path, registry_client_response
    ):
        # Given
        pipeline_name = "test_pipeline"

        deployer = VertexPipelineDeployer(
            pipeline_name=pipeline_name,
            pipeline_func=test_pipeline_fixture,
            project_id="my_project",
            region="us-central1",
            staging_bucket_name="my_bucket",
            service_account="my_service_account",
            local_package_path=tmp_path,
            gar_location="europe-west1",
            gar_repo_id="test-pipelines",
        )
        deployer.compile()

        # When
        with patch("requests.post", return_value=registry_client_response) as mock_post:
            deployer.upload_to_registry(tags=["tag1", "tag2"])

        # Then
        mock_post.assert_called_once()
        template_name, version_name = registry_client_response.text.split("/")
        assert deployer.template_name == template_name
        assert deployer.version_name == version_name


class TestRun:
    def test_default_parameters_shallow(self, test_pipeline_fixture, tmp_path, monkeypatch):
        # Given
        deployer = VertexPipelineDeployer(
            pipeline_name=test_pipeline_fixture.pipeline_func.__name__,
            pipeline_func=test_pipeline_fixture,
            project_id="my_project",
            region="us-central1",
            staging_bucket_name="my_staging_bucket",
            service_account="my_service_account",
            gar_location="europe-west1",
            gar_repo_id="test-pipelines",
            local_package_path=tmp_path,
        )
        deployer.compile()

        # When
        with patch.object(aiplatform.pipeline_jobs.PipelineJob, "submit") as mock_submit:
            deployer.run()

        # Then
        mock_submit.assert_called_once_with(
            experiment="test-pipeline-experiment", service_account="my_service_account"
        )

    def test_with_all_parameters_shallow(self, test_pipeline_fixture, tmp_path, monkeypatch):
        # Given
        deployer = VertexPipelineDeployer(
            pipeline_name=test_pipeline_fixture.pipeline_func.__name__,
            pipeline_func=test_pipeline_fixture,
            project_id="my_project",
            region="us-central1",
            staging_bucket_name="my_staging_bucket",
            service_account="my_service_account",
            local_package_path=tmp_path,
        )
        deployer.compile()

        # When
        with patch.object(aiplatform.pipeline_jobs.PipelineJob, "submit") as mock_submit:
            deployer.run(
                enable_caching=True,
                parameter_values={"name": "johndoe"},
                # input_artifacts={"input1": "path/to/input1"},
                experiment_name="my_experiment",
                tag="my_tag",
            )

        # Then
        mock_submit.assert_called_once_with(
            experiment="my-experiment",
            service_account="my_service_account",
        )
