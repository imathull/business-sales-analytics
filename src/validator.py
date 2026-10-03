"""
Validator module for Business Sales & Performance Analytics System.
Performs pre-cleaning data quality checks and generates a structured Validation Report.
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger("SalesAnalyticsPipeline")

REQUIRED_COLUMNS = [
    "transaction_id", "transaction_date", "branch_id", "branch_name",
    "salesperson_id", "salesperson_name", "product_id", "product_name",
    "category", "quantity", "unit_price", "discount", "payment_method",
    "customer_type", "region"
]


def validate_schema(df: pd.DataFrame) -> bool:
    """Verifies that all required business columns exist in the DataFrame."""
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        logger.error(f"Schema Validation Failed! Missing columns: {missing_cols}")
        return False
    logger.info("Schema Validation Passed: All required columns present.")
    return True


def run_data_validation(df: pd.DataFrame) -> dict:
    """
    Executes practical validation rules on the dataset and returns a validation summary report.
    
    :param df: DataFrame loaded from raw source.
    :return: Dictionary containing key validation metrics and issue indices.
    """
    logger.info("Running Data Validation checks...")
    total_records = len(df)
    
    # 1. Duplicate Checks
    exact_duplicates_count = df.duplicated().sum()
    duplicate_tx_ids_count = df["transaction_id"].duplicated().sum()

    # 2. Missing Values Check
    missing_counts = df[REQUIRED_COLUMNS].isnull().sum().to_dict()
    total_missing_cells = sum(missing_counts.values())

    # 3. Numeric Field Validation
    # Coerce numeric columns temporarily for validation
    qty_series = pd.to_numeric(df["quantity"], errors="coerce")
    price_series = pd.to_numeric(df["unit_price"], errors="coerce")
    discount_series = pd.to_numeric(df["discount"], errors="coerce")

    invalid_qty_mask = (qty_series.isna()) | (qty_series <= 0) | (qty_series > 500)
    invalid_price_mask = (price_series.isna()) | (price_series <= 0)
    invalid_discount_mask = (discount_series.isna()) | (discount_series < 0) | (discount_series > 100)

    invalid_qty_count = invalid_qty_mask.sum()
    invalid_price_count = invalid_price_mask.sum()
    invalid_discount_count = invalid_discount_mask.sum()
    total_invalid_numeric = (invalid_qty_mask | invalid_price_mask | invalid_discount_mask).sum()

    # 4. Date Format Validation (Check YYYY-MM-DD parsing)
    parsed_dates = pd.to_datetime(df["transaction_date"], format="%Y-%m-%d", errors="coerce")
    invalid_dates_mask = parsed_dates.isna()
    invalid_dates_count = invalid_dates_mask.sum()

    # Composite Invalid Mask (records that break at least 1 rule)
    invalid_records_mask = (
        df.duplicated() |
        df["transaction_id"].duplicated() |
        df[REQUIRED_COLUMNS].isnull().any(axis=1) |
        invalid_qty_mask |
        invalid_price_mask |
        invalid_discount_mask |
        invalid_dates_mask
    )

    invalid_records_count = invalid_records_mask.sum()
    valid_records_count = total_records - invalid_records_count

    report = {
        "total_records": total_records,
        "valid_records": valid_records_count,
        "invalid_records": invalid_records_count,
        "exact_duplicates": int(exact_duplicates_count),
        "duplicate_tx_ids": int(duplicate_tx_ids_count),
        "total_missing_cells": int(total_missing_cells),
        "invalid_quantities": int(invalid_qty_count),
        "invalid_unit_prices": int(invalid_price_count),
        "invalid_discounts": int(invalid_discount_count),
        "malformed_dates": int(invalid_dates_count),
        "missing_details": missing_counts
    }

    logger.info(f"Validation Completed: {total_records} Total Records | {valid_records_count} Valid | {invalid_records_count} Flawed")
    return report
