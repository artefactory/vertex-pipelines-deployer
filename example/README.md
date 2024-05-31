# `vertex-deployer` usage examples

This folder can be used as a template repo.

You can either copy paste snippets from different parts, or push it and test it with your own GCP project.

To do so, setup your gcp project and create your own repo from this folder:
```bash
# TODO: replace with your own repo url
git clone https://github.com/artefactory/vertex-pipelines-deployer.git
cd vertex-pipelines-deployer
cd example
git init
git add .
git commit -m "first commit"
git remote add origin "your_repo_url"
git push -u origin master
```

# Running the example

In this section we detail how to run basic commands in the example folder.

* Before the start, add this environment variable, so the pipelines are found: `export PYTHONPATH=.`

* You must also add the required environment variables in the [example.env](example.env) file.

## Check pipeline validity

The following command will check if your pipeline is valid (notably, that the pipeline can be compiled and the config files are correctly defined).

```bash
vertex-deployer check dummy_pipeline
```

## Build the custom image

To build and upload the custom image to Artifact Registry, you can use the following make command:

```bash
export $(cat example.env | xargs)
make build-base-image
```

## Deploy the dummy pipeline via Cloud Build

For the `vertex-deployer deploy` command to work within cloudbuild (and not simply locally), you will need to give additional IAM rights, to the service account used in Cloud Build Jobs.
\
\
By default, the service account used is the following:
* `[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`

```bash
export CLOUDBUILD_SERVICE_ACCOUNT = [PROJECT_NUMBER]@cloudbuild.gserviceaccount.com

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${CLOUDBUILD_SERVICE_ACCOUNT}" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${CLOUDBUILD_SERVICE_ACCOUNT}" \
    --role="roles/iam.serviceAccountUser"
```

Once this is done, you can launch the make command.

If you do not modify the [cloudbuild_cd.yaml](cloudbuild.yaml) file, it should:
- rebuild the base image
- deploy a scheduled Vertex AI pipeline

```bash
export $(cat example.env | xargs)
make deploy-pipeline
```
