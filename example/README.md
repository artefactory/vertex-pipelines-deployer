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

Running inside example/

Before the start, add this environment variable, so the pipelines are found: `export PYTHONPATH=.`

**Check pipeline validity**
```
vertex-deployer check dummy_pipeline
```

**Build the custom image**

```
set -a && source example.env && set +a && make build-base-image
```

**Schedule the dummy pipeline**

For this step to work, you will need to give additional IAM rights, to the service account used in Cloud Build Jobs.
By default, the service account used is the following: `[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`

```
export CLOUDBUILD_SERVICE_ACCOUNT = [PROJECT_NUMBER]@cloudbuild.gserviceaccount.com

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${CLOUDBUILD_SERVICE_ACCOUNT}" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${CLOUDBUILD_SERVICE_ACCOUNT}" \
    --role="roles/iam.serviceAccountUser"
```

Once this is done, you can launch the make command:

```
set -a && source example.env && set +a && make deploy-pipeline
```
