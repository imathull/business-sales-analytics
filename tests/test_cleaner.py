"""
Unit tests for Data Cleaner module (src/data_cleaner.py) using Pytest.
"""

import pytest
import pandas as pd
from src.data_cleaner import standardize_categories, clean_dataset


def test_standardize_categories():
    """Test category standardization helper function."""
    assert standardize_categories("electrONics") == "Electronics"
    assert standardize_categories("Office-Supplies") == "Office Supplies"
    assert standardize_categories("FURNITURE ") == "Office Furniture"
    assert standardize_categories("computer peripherals") == "Computer Peripherals"
    assert standardize_categories("smart_devices") == "Smart Devices"
    assert standardize_categories(None) == "Unknown"


def test_calculated_columns():
    """Test that gross_amount, discount_amount, and net_sales are calculated correctly."""
    df_raw = pd.DataFrame([{
        "transaction_id": "TXN-101",
        "transaction_date": "2025-06-10",
        "branch_id": "BR-101",
        "branch_name": "NYC Downtown",
        "salesperson_id": "SP-101",
        "salesperson_name": "Alice Johnson",
        "product_id": "PRD-001",
        "product_name": "Pro Laptop 15in",
        "category": "Electronics",
        "quantity": "2",
        "unit_price": "1000.00",
        "discount": "10.0",
        "payment_method": "Credit Card",
        "customer_type": "Corporate",
        "region": "East"
    }])

    df_cleaned = clean_dataset(df_raw)

    assert len(df_cleaned) == 1
    row = df_cleaned.iloc[0]
    
    # 2 * 1000.00 = 2000.00 gross
    # 2000.00 * (10 / 100) = 200.00 discount
    # 2000.00 - 200.00 = 1800.00 net
    assert row["gross_amount"] == 2000.00
    assert row["discount_amount"] == 200.00
    assert row["net_sales"] == 1800.00
