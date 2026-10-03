"""
Unit tests for Validator module (src/validator.py) using Pytest.
"""

import pytest
import pandas as pd
import numpy as np
from src.validator import validate_schema, run_data_validation


@pytest.fixture
def sample_valid_dataframe():
    """Provides a sample valid raw DataFrame."""
    return pd.DataFrame([{
        "transaction_id": "TXN-10001",
        "transaction_date": "2025-05-15",
        "branch_id": "BR-101",
        "branch_name": "NYC Downtown",
        "salesperson_id": "SP-101",
        "salesperson_name": "Alice Johnson",
        "product_id": "PRD-001",
        "product_name": "Pro Laptop 15in",
        "category": "Electronics",
        "quantity": "2",
        "unit_price": "1299.99",
        "discount": "10.0",
        "payment_method": "Credit Card",
        "customer_type": "Corporate",
        "region": "East"
    }])


def test_validate_schema_success(sample_valid_dataframe):
    """Test that a complete schema passes validation."""
    assert validate_schema(sample_valid_dataframe) is True


def test_validate_schema_missing_column(sample_valid_dataframe):
    """Test that schema validation fails when a required column is missing."""
    df_missing = sample_valid_dataframe.drop(columns=["unit_price"])
    assert validate_schema(df_missing) is False


def test_validation_duplicate_detection(sample_valid_dataframe):
    """Test that duplicate records and duplicate transaction IDs are counted accurately."""
    df_dup = pd.concat([sample_valid_dataframe, sample_valid_dataframe], ignore_index=True)
    report = run_data_validation(df_dup)
    
    assert report["total_records"] == 2
    assert report["exact_duplicates"] == 1
    assert report["duplicate_tx_ids"] == 1


def test_validation_invalid_quantity():
    """Test that negative, zero, and outlier quantities are flagged as invalid."""
    df_bad_qty = pd.DataFrame([
        {"transaction_id": "TXN-1", "transaction_date": "2025-01-01", "quantity": "-5", "unit_price": "100.00", "discount": "0"},
        {"transaction_id": "TXN-2", "transaction_date": "2025-01-01", "quantity": "0", "unit_price": "100.00", "discount": "0"},
        {"transaction_id": "TXN-3", "transaction_date": "2025-01-01", "quantity": "9999", "unit_price": "100.00", "discount": "0"},
        {"transaction_id": "TXN-4", "transaction_date": "2025-01-01", "quantity": "5", "unit_price": "100.00", "discount": "0"}
    ])
    # Add dummy missing columns so validator doesn't crash on column checks
    for col in ["branch_id", "branch_name", "salesperson_id", "salesperson_name", 
                "product_id", "product_name", "category", "payment_method", "customer_type", "region"]:
        df_bad_qty[col] = "sample"

    report = run_data_validation(df_bad_qty)
    assert report["invalid_quantities"] == 3


def test_validation_malformed_dates():
    """Test that malformed date strings are flagged correctly."""
    df_dates = pd.DataFrame([
        {"transaction_id": "TXN-1", "transaction_date": "2025-05-15"},
        {"transaction_id": "TXN-2", "transaction_date": "2025/13/45"},
        {"transaction_id": "TXN-3", "transaction_date": "INVALID_DATE"}
    ])
    for col in ["quantity", "unit_price", "discount", "branch_id", "branch_name", 
                "salesperson_id", "salesperson_name", "product_id", "product_name", 
                "category", "payment_method", "customer_type", "region"]:
        df_dates[col] = "10" if col in ["quantity", "unit_price", "discount"] else "sample"

    report = run_data_validation(df_dates)
    assert report["malformed_dates"] == 2
