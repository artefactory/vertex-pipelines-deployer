# --8<-- [start:build-base-image]
.PHONY: build-base-image
build-base-image:
	@gcloud builds submit --config ./vertex/deployment/cloudbuild_local.yaml \
	--substitutions=_GAR_LOCATION=${GAR_LOCATION},_GAR_DOCKER_REPO_ID=${GAR_DOCKER_REPO_ID},_GAR_VERTEX_BASE_IMAGE_NAME=${GAR_VERTEX_BASE_IMAGE_NAME},_TAG=${TAG}
# --8<-- [end:build-base-image]

# --8<-- [start:deploy-pipeline]
.PHONY: deploy-pipeline
deploy-pipeline:
	@gcloud builds submit --config ./vertex/deployment/cloudbuild_cd.yaml \
	--project=${PROJECT_ID} \
	--substitutions=_GCP_REGION=${GCP_REGION},_GAR_LOCATION=${GAR_LOCATION},_GAR_DOCKER_REPO_ID=${GAR_DOCKER_REPO_ID},_GAR_VERTEX_BASE_IMAGE_NAME=${GAR_VERTEX_BASE_IMAGE_NAME},_TAG=${TAG},_GAR_PIPELINES_REPO_ID=${GAR_PIPELINES_REPO_ID},_VERTEX_STAGING_BUCKET_NAME=${VERTEX_STAGING_BUCKET_NAME},_VERTEX_SERVICE_ACCOUNT=${VERTEX_SERVICE_ACCOUNT}
# --8<-- [end:deploy-pipeline]


# --8<-- [start:create-trigger-cd]
.PHONY: create-trigger-cd
create-trigger-cd:
	@gcloud builds triggers create github \
	--repo-owner="artefactory" \
	--repo-name="test-vertex-deployer" \
	--name="test-vertex-deployer-trigger" \
	--branch-pattern="main" \
	--build-config=./vertex/deployment/cloudbuild_cd.yaml \
	--project=${PROJECT_ID} \
	--substitutions=_GCP_REGION=${GCP_REGION},_GAR_LOCATION=${GAR_LOCATION},_GAR_DOCKER_REPO_ID=${GAR_DOCKER_REPO_ID},_GAR_VERTEX_BASE_IMAGE_NAME=${GAR_VERTEX_BASE_IMAGE_NAME},_TAG=${TAG},_GAR_PIPELINES_REPO_ID=${GAR_PIPELINES_REPO_ID},_VERTEX_STAGING_BUCKET_NAME=${VERTEX_STAGING_BUCKET_NAME},_VERTEX_SERVICE_ACCOUNT=${VERTEX_SERVICE_ACCOUNT}
# --8<-- [end:create-trigger-cd]
