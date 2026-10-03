"""
Data Loader module for reading raw sales data files (CSV/Excel).
"""

import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger("SalesAnalyticsPipeline")


def load_raw_data(file_path: Path) -> pd.DataFrame:
    """
    Loads raw sales dataset from a CSV or Excel file.
    
    :param file_path: Path object or string pointing to raw file.
    :return: pandas DataFrame containing raw data.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        logger.error(f"Raw data file not found at {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    logger.info(f"Loading raw data file from: {file_path}")
    
    try:
        if file_path.suffix.lower() == ".csv":
            df = pd.read_csv(file_path, dtype=str)  # Read initial columns as string to prevent auto coercion
        elif file_path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path, dtype=str, engine="openpyxl")
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        logger.info(f"Successfully loaded file. Total raw records: {len(df)}")
        return df

    except Exception as e:
        logger.error(f"Error loading raw data from {file_path}: {e}")
        raise
