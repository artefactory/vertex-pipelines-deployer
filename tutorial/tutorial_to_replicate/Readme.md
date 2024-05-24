# Tutorial - Creating a real pipeline from scratch

## Init
```
vertex-deployer init
```

## Requirements

- Create a requirements.txt with your requirements.
- install the packages, if they are not already using `poetry add [package_name]`

## Amend the structure

**Delete**
- dummy_pipeline.py
- dummy_component.py
-
**Config**

- Delete `config/dev.py`,`config/prod.py`
- In the `config/test.py`, keep only the parameter values
    - Add the project_id

**Env**
- Fill in the `deployer.env` file

## Check

```
vertex-deployer check
```
Checks that the config is correct

## Build and upload the base image
- Build and upload image:

```
bash vertex/deployment/build_base_image.sh
```

## gcloud

### Iam and authorizations
```
gcloud services enable bigquery.googleapis.com
```

```
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${VERTEX_SERVICE_ACCOUNT}" \
    --role=roles/bigquery.dataEditor

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${VERTEX_SERVICE_ACCOUNT}" \
    --role=roles/bigquery.jobUser

```

### BigQuery
```
bq mk --dataset --location=${GCP_REGION} ${PROJECT_ID}:tutorial_dataset

bq mk --table --location=${GCP_REGION} --description "This is a fake table for testing" \
${PROJECT_ID}:tutorial_dataset.input \
name:string,age:integer,weight:float

bq query --use_legacy_sql=false \
"INSERT INTO \`${PROJECT_ID}.tutorial_dataset.input\` (name, age, weight) VALUES (\"John Doe\", 30, 72.5)"
```
