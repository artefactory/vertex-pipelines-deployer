.PHONY: deploy-local
deploy-local:
	@gcloud builds submit --config ./vertex/deployment/cloudbuild_local.yaml \
	--substitutions=_GAR_LOCATION=${GAR_LOCATION},_GAR_DOCKER_REPO_ID=${GAR_DOCKER_REPO_ID},_GAR_VERTEX_BASE_IMAGE_NAME=${GAR_VERTEX_BASE_IMAGE_NAME},_TAG=${TAG}

.PHONY: get-latest-vertex-deployer
get-latest-vertex-deployer:
	@gsutil cp $(shell gsutil ls gs://vertex-pipelines-deployer | tail -n1) .
