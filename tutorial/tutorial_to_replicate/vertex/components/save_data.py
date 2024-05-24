import os

from kfp.dsl import Dataset, Input, component


@component(
    base_image=f'{os.getenv("GAR_LOCATION")}-docker.pkg.dev/{os.getenv("PROJECT_ID")}/{os.getenv("GAR_DOCKER_REPO_ID")}/{os.getenv("GAR_VERTEX_BASE_IMAGE_NAME")}:{os.getenv("TAG")}'
)
def save_data_component(
    df_transformed: Input[Dataset],
    output_table: str,
):
    """This component saves data into a specific storage system (here a BQ table)

    Args:
        df_transformed (Input[Dataset]): Input dataset to read
        output_table (str): name of the output bq table
    """
    import os

    import pandas as pd

    from vertex.lib.bigquery import save_data_bq

    project_id = os.getenv("PROJECT_ID")

    # vertex specific way of loading data
    df_transformed = pd.read_csv(df_transformed.uri)

    # saving data into BQ, note that contrarily to other components we are not using
    # the vertex specific file system for saving our data
    save_data_bq(df_transformed, project_id, output_table)
