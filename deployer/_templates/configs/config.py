from google.cloud import aiplatform as aip

# You can retrieve an existing Metadata Artifact given a resource name or ID.
# You can check aip documentation for more information:
# https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.Artifact
artifact_name = "projects/123/locations/us-central1/metadataStores/default/artifacts/my-resource"
# or

my_artifact = aip.Artifact(
    artifact_name="my-resource",
    project="my_project",
    location="us-central1",
)

input_artifacts = {"my_input_artifact": my_artifact}
parameter_values = {"name": "John Doe in python config"}
