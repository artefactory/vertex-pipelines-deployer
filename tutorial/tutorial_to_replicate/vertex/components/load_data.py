import os

from kfp.dsl import Dataset, Output, component


@component(
    base_image=f'{os.getenv("GAR_LOCATION")}-docker.pkg.dev/{os.getenv("PROJECT_ID")}/{os.getenv("GAR_DOCKER_REPO_ID")}/{os.getenv("GAR_VERTEX_BASE_IMAGE_NAME")}:{os.getenv("TAG")}'
)
def load_data_component(input_table: str, df_dataset: Output[Dataset]):
    """Component which loads a table from BigQuery and saves it as a CSV file.

    Args:
        input_table (str): name of the table to load ('dataset.table_name' format)
        df_dataset (Output[Dataset]): saved vertex dataset
    """
    import os

    from vertex.lib.bigquery import load_data_bq

    project_id = os.getenv("PROJECT_ID")
    gcp_region = os.getenv("GCP_REGION")

    df = load_data_bq(project_id, gcp_region, input_table)

    # vertex specific way of saving data
    df.to_csv(df_dataset.uri, index=False)
