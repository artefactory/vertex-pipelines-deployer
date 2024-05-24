from loguru import logger


def add_constant_column(df, column_name, constant_value):
    """Add a new column to a dataframe with a constant value"""
    df[column_name] = constant_value
    logger.info(f"added '{column_name}' column with constant value: {constant_value}")
    return df
