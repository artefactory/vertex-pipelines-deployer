import os

from kfp.dsl import Dataset, Input, Output, component


@component(
    base_image=f'{os.getenv("GAR_LOCATION")}-docker.pkg.dev/{os.getenv("PROJECT_ID")}/{os.getenv("GAR_DOCKER_REPO_ID")}/{os.getenv("GAR_VERTEX_BASE_IMAGE_NAME")}:{os.getenv("TAG")}'
)
def transform_data_component(
    df: Input[Dataset],
    column_name: str,
    constant_value: str,
    df_transformed_dataset: Output[Dataset],
):
    """Super simple ETL component, which reads a dataset, adds a constant column
    and saves the result to a vertex dataset.

    Args:
        df (Input[Dataset]): input vertex dataset
        column_name (str): name of the new column
        constant_value (str): constant string value
        df_transformed_dataset (Output[Dataset]): output vertex dataset
    """
    import pandas as pd

    from vertex.lib.transform_data import add_constant_column

    df = pd.read_csv(df.uri)
    df_transformed = add_constant_column(df, column_name, constant_value)
    df_transformed.to_csv(df_transformed_dataset.uri, index=False)
