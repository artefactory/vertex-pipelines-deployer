import pandas_gbq
from google.cloud import bigquery
from loguru import logger


def save_data_bq(df, project_id, output_table, bq_table_schema=None):
    """Utils function to save data into BigQuery"""
    pandas_gbq.to_gbq(
        df,
        output_table,
        if_exists="replace",
        project_id=project_id,
        table_schema=bq_table_schema,
        api_method="load_csv",
    )
    logger.info(f"saved_data_in {output_table}")


def load_data_bq(project_id, gcp_region, input_table):
    """Utils function to load data from BigQuery"""
    table_id = f"{project_id}.{input_table}"
    query = "SELECT * FROM `{}`"
    query = query.format(table_id)
    client = bigquery.Client(location=gcp_region, project=project_id)
    df = client.query(query, location=gcp_region).to_dataframe()
    logger.info(f"Size of df: {df.shape}")
    return df
