import kfp.dsl

from vertex.components.load_data import load_data_component
from vertex.components.save_data import save_data_component
from vertex.components.transform_data import transform_data_component


@kfp.dsl.pipeline(name="starter-pipeline")
def my_first_pipeline(
    input_table: str, output_table: str, new_column_name: str, new_column_value: str
):
    """This is a pipeline that performs a simple ETL operation,
    adding a column to a BQ table with a default value
    """
    load_data_task = load_data_component(
        input_table=input_table,
    )

    transform_data_task = transform_data_component(
        df=load_data_task.outputs["df_dataset"],
        column_name=new_column_name,
        constant_value=new_column_value,
    )

    save_data_component(
        df_transformed=transform_data_task.outputs["df_transformed_dataset"],
        output_table=output_table,
    )
