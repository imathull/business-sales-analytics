"""
Data Cleaner module for Business Sales & Performance Analytics System.
Transforms raw DataFrame into a cleaned, normalized, and feature-engineered dataset.
"""

import logging
from pathlib import Path
import pandas as pd
import numpy as np

logger = logging.getLogger("SalesAnalyticsPipeline")


def standardize_categories(cat_str: str) -> str:
    """Standardizes messy/inconsistent category strings to canonical business names."""
    if pd.isna(cat_str):
        return "Unknown"
    
    clean_cat = str(cat_str).strip().lower()
    
    if "electr" in clean_cat:
        return "Electronics"
    elif "office" in clean_cat and "supply" in clean_cat or "supplies" in clean_cat:
        return "Office Supplies"
    elif "office" in clean_cat and "furn" in clean_cat or "furnit" in clean_cat:
        return "Office Furniture"
    elif "peripher" in clean_cat or "computer" in clean_cat:
        return "Computer Peripherals"
    elif "smart" in clean_cat or "device" in clean_cat:
        return "Smart Devices"
    else:
        return str(cat_str).strip().title()


def clean_dataset(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw dataframe through pipeline steps:
    1. Coerce numeric and date types
    2. Drop missing essential fields
    3. Filter out invalid quantities/prices
    4. Deduplicate records & duplicate transaction_ids
    5. Standardize text & categorical fields
    6. Compute gross_amount, discount_amount, net_sales
    
    :param df_raw: Raw loaded DataFrame.
    :return: Cleaned pandas DataFrame.
    """
    logger.info("Starting Data Cleaning Process...")
    df = df_raw.copy()
    initial_count = len(df)

    # 1. Deduplicate Exact Duplicate Rows
    df = df.drop_duplicates()
    dedup_rows_removed = initial_count - len(df)
    logger.info(f"Removed {dedup_rows_removed} exact duplicate rows.")

    # 2. Parse & Standardize Dates
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], format="%Y-%m-%d", errors="coerce")
    bad_dates_count = df["transaction_date"].isna().sum()
    df = df.dropna(subset=["transaction_date"])
    logger.info(f"Dropped {bad_dates_count} records with malformed transaction dates.")

    # Convert date back to clean string format YYYY-MM-DD for database export consistency
    df["transaction_date"] = df["transaction_date"].dt.strftime("%Y-%m-%d")

    # 3. Coerce Numeric Types & Filter Invalid Quantities/Prices
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0.0)

    # Filter rules: quantity between 1 and 500, price > 0, discount between 0 and 100
    valid_numeric_mask = (
        (df["quantity"] > 0) & (df["quantity"] <= 500) &
        (df["unit_price"] > 0) &
        (df["discount"] >= 0) & (df["discount"] <= 100)
    )
    invalid_num_count = (~valid_numeric_mask).sum()
    df = df[valid_numeric_mask].copy()
    logger.info(f"Dropped {invalid_num_count} records with invalid numeric values (qty <= 0 or > 500, price <= 0).")

    # 4. Handle Missing Values in Required Categorical Fields
    cat_cols_required = ["transaction_id", "branch_id", "product_id", "salesperson_id"]
    df = df.dropna(subset=cat_cols_required)

    # Fill missing salesperson name from ID if possible or default to "Unknown"
    df["salesperson_name"] = df["salesperson_name"].fillna("Unknown Salesperson").astype(str).str.strip().str.title()
    df["branch_name"] = df["branch_name"].astype(str).str.strip().str.title()
    df["product_name"] = df["product_name"].astype(str).str.strip()
    df["payment_method"] = df["payment_method"].astype(str).str.strip().str.title()
    df["customer_type"] = df["customer_type"].astype(str).str.strip().str.title()
    df["region"] = df["region"].astype(str).str.strip().str.title()

    # 5. Standardize Categories
    df["category"] = df["category"].apply(standardize_categories)

    # 6. Deduplicate by Transaction ID (keep first valid record)
    tx_dup_count = df.duplicated(subset=["transaction_id"]).sum()
    df = df.drop_duplicates(subset=["transaction_id"], keep="first")
    logger.info(f"Removed {tx_dup_count} duplicate transaction_id records.")

    # 7. Create Calculated Business Columns
    # Ensure types
    df["quantity"] = df["quantity"].astype(int)
    df["unit_price"] = df["unit_price"].astype(float)
    df["discount"] = df["discount"].astype(float)

    df["gross_amount"] = (df["quantity"] * df["unit_price"]).round(2)
    df["discount_amount"] = (df["gross_amount"] * (df["discount"] / 100.0)).round(2)
    df["net_sales"] = (df["gross_amount"] - df["discount_amount"]).round(2)

    final_count = len(df)
    logger.info(f"Data Cleaning Complete! Final Cleaned Records: {final_count} (Removed total {initial_count - final_count} flawed records).")

    return df


def save_cleaned_data(df: pd.DataFrame, output_path: Path):
    """Exports cleaned DataFrame to CSV file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Cleaned dataset successfully saved to: {output_path}")
