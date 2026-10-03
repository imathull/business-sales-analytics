"""
Data Generator for Business Sales & Performance Analytics System.
Generates synthetic raw sales dataset with realistic business features
and intentional data quality flaws (missing values, duplicates, bad dates, invalid numbers).
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


def generate_synthetic_data(num_records=7500, seed=42):
    random.seed(seed)
    np.random.seed(seed)

    # Master Data definitions
    branches = [
        {"branch_id": "BR-101", "branch_name": "NYC Downtown", "region": "East"},
        {"branch_id": "BR-102", "branch_name": "Brooklyn North", "region": "East"},
        {"branch_id": "BR-103", "branch_name": "Chicago Central", "region": "Midwest"},
        {"branch_id": "BR-104", "branch_name": "Boston Harbor", "region": "East"},
        {"branch_id": "BR-105", "branch_name": "SF Bay Area", "region": "West"},
        {"branch_id": "BR-106", "branch_name": "Austin Hub", "region": "South"},
        {"branch_id": "BR-107", "branch_name": "Miami Beach", "region": "South"},
        {"branch_id": "BR-108", "branch_name": "Seattle Metro", "region": "West"}
    ]

    categories = [
        "Electronics",
        "Office Furniture",
        "Computer Peripherals",
        "Smart Devices",
        "Office Supplies"
    ]

    products = [
        {"product_id": "PRD-001", "product_name": "Pro Laptop 15in", "category": "Electronics", "unit_price": 1299.99},
        {"product_id": "PRD-002", "product_name": "UltraBook 13in", "category": "Electronics", "unit_price": 999.50},
        {"product_id": "PRD-003", "product_name": "4K Curved Monitor 32in", "category": "Electronics", "unit_price": 499.99},
        {"product_id": "PRD-004", "product_name": "Ergonomic Office Chair", "category": "Office Furniture", "unit_price": 349.00},
        {"product_id": "PRD-005", "product_name": "Standing Desk Electric", "category": "Office Furniture", "unit_price": 599.00},
        {"product_id": "PRD-006", "product_name": "Executive Leather Armchair", "category": "Office Furniture", "unit_price": 450.00},
        {"product_id": "PRD-007", "product_name": "Wireless Mechanical Keyboard", "category": "Computer Peripherals", "unit_price": 89.99},
        {"product_id": "PRD-008", "product_name": "Ergonomic Vertical Mouse", "category": "Computer Peripherals", "unit_price": 49.99},
        {"product_id": "PRD-009", "product_name": "HD Webcam 1080p", "category": "Computer Peripherals", "unit_price": 75.00},
        {"product_id": "PRD-010", "product_name": "Noise Cancelling Headset", "category": "Computer Peripherals", "unit_price": 149.99},
        {"product_id": "PRD-011", "product_name": "Smart Tablet 11in", "category": "Smart Devices", "unit_price": 649.00},
        {"product_id": "PRD-012", "product_name": "Smart Watch Series V", "category": "Smart Devices", "unit_price": 299.99},
        {"product_id": "PRD-013", "product_name": "Wireless Charging Pad", "category": "Smart Devices", "unit_price": 29.99},
        {"product_id": "PRD-014", "product_name": "Portable Power Bank 20k", "category": "Smart Devices", "unit_price": 45.00},
        {"product_id": "PRD-015", "product_name": "Laser Jet Printer", "category": "Office Supplies", "unit_price": 279.99},
        {"product_id": "PRD-016", "product_name": "High Volume Paper Reams", "category": "Office Supplies", "unit_price": 39.99},
        {"product_id": "PRD-017", "product_name": "Document Shredder", "category": "Office Supplies", "unit_price": 85.00},
        {"product_id": "PRD-018", "product_name": "Whiteboard 4x3ft", "category": "Office Supplies", "unit_price": 110.00},
        {"product_id": "PRD-019", "product_name": "USB-C Docking Station", "category": "Computer Peripherals", "unit_price": 189.99},
        {"product_id": "PRD-020", "product_name": "External SSD 2TB", "category": "Electronics", "unit_price": 179.99},
        {"product_id": "PRD-021", "product_name": "Conference Speakerphone", "category": "Electronics", "unit_price": 220.00},
        {"product_id": "PRD-022", "product_name": "Filing Cabinet 3-Drawer", "category": "Office Furniture", "unit_price": 195.00},
        {"product_id": "PRD-023", "product_name": "LED Desk Lamp Wireless", "category": "Office Furniture", "unit_price": 55.00},
        {"product_id": "PRD-024", "product_name": "Label Printer Thermal", "category": "Office Supplies", "unit_price": 125.00}
    ]

    salespeople = [
        {"salesperson_id": f"SP-{100 + i}", "salesperson_name": name}
        for i, name in enumerate([
            "Alice Johnson", "Bob Smith", "Charlie Davis", "Diana Prince", "Ethan Hunt",
            "Fiona Gallagher", "George Clark", "Hannah Abbott", "Ian Malcolm", "Julia Roberts",
            "Kevin Bacon", "Laura Croft", "Michael Scott", "Nina Williams", "Oscar Martinez",
            "Pam Beesly", "Quentin Tarantino", "Rachel Green", "Steve Rogers", "Tony Stark",
            "Una Stubbs", "Victor Vance", "Wanda Maximoff", "Xander Cage", "Yara Shahidi",
            "Zachary Levi", "Amy Adams", "Bruce Wayne", "Clark Kent", "David Bowie",
            "Emma Watson", "Frank Castle", "Grace Hopper", "Harry Potter", "Iris West",
            "Jack Sparrow", "Karen Page", "Luke Skywalker", "Mary Jane", "Nathan Drake"
        ])
    ]

    payment_methods = ["Credit Card", "Wire Transfer", "PayPal", "Cash"]
    customer_types = ["Corporate", "Wholesale", "Retail"]

    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 3, 31)
    days_range = (end_date - start_date).days

    records = []
    
    print(f"Generating {num_records} base sales records...")
    for i in range(1, num_records + 1):
        tx_id = f"TXN-{100000 + i}"
        
        # Date generation with seasonal weight (higher sales Q4 and month ends)
        random_days = random.randint(0, days_range)
        tx_date = start_date + timedelta(days=random_days)
        date_str = tx_date.strftime("%Y-%m-%d")

        branch = random.choice(branches)
        prod = random.choice(products)
        sp = random.choice(salespeople)
        
        # Realistic quantity distribution (1-10 normally)
        quantity = random.randint(1, 10)
        # Occasional bulk purchase for Wholesale
        cust_type = random.choice(customer_types)
        if cust_type == "Wholesale":
            quantity = random.randint(5, 25)

        unit_price = prod["unit_price"]
        # Discount between 0% and 25% (in percentage format e.g. 5.0, 10.0)
        discount = round(random.choice([0.0, 0.0, 0.0, 5.0, 10.0, 15.0, 20.0]), 1)
        
        pay_method = random.choice(payment_methods)

        records.append({
            "transaction_id": tx_id,
            "transaction_date": date_str,
            "branch_id": branch["branch_id"],
            "branch_name": branch["branch_name"],
            "salesperson_id": sp["salesperson_id"],
            "salesperson_name": sp["salesperson_name"],
            "product_id": prod["product_id"],
            "product_name": prod["product_name"],
            "category": prod["category"],
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "payment_method": pay_method,
            "customer_type": cust_type,
            "region": branch["region"]
        })

    df = pd.DataFrame(records)

    # -------------------------------------------------------------
    # INTENTIONALLY INTRODUCE REALISTIC DATA QUALITY FLAWS (~6-7%)
    # -------------------------------------------------------------
    print("Introducing controlled data quality flaws into dataset...")

    # 1. Exact Duplicate Rows (~75 rows)
    dups = df.sample(75, random_state=42).copy()
    df = pd.concat([df, dups], ignore_index=True)

    # 2. Duplicate Transaction IDs with slightly altered values (~50 rows)
    dup_tx_rows = df.sample(50, random_state=101).copy()
    dup_tx_rows["quantity"] = dup_tx_rows["quantity"] + 1
    dup_tx_rows["discount"] = 0.0
    df = pd.concat([df, dup_tx_rows], ignore_index=True)

    # 3. Missing values (~100 instances)
    null_idx_qty = df.sample(30, random_state=202).index
    df.loc[null_idx_qty, "quantity"] = np.nan

    null_idx_price = df.sample(25, random_state=303).index
    df.loc[null_idx_price, "unit_price"] = np.nan

    null_idx_cat = df.sample(25, random_state=404).index
    df.loc[null_idx_cat, "category"] = np.nan

    null_idx_sp = df.sample(20, random_state=505).index
    df.loc[null_idx_sp, "salesperson_name"] = np.nan

    # 4. Invalid quantities (negative or zero or insane outlier e.g. -5, 0, 9999) (~50 rows)
    bad_qty_neg_idx = df.sample(25, random_state=606).index
    df.loc[bad_qty_neg_idx, "quantity"] = -3

    bad_qty_zero_idx = df.sample(15, random_state=707).index
    df.loc[bad_qty_zero_idx, "quantity"] = 0

    bad_qty_outlier_idx = df.sample(10, random_state=808).index
    df.loc[bad_qty_outlier_idx, "quantity"] = 8888

    # 5. Invalid Unit Prices (negative or zero) (~35 rows)
    bad_price_neg_idx = df.sample(25, random_state=909).index
    df.loc[bad_price_neg_idx, "unit_price"] = -150.00

    bad_price_zero_idx = df.sample(10, random_state=1010).index
    df.loc[bad_price_zero_idx, "unit_price"] = 0.00

    # 6. Inconsistent Category Formatting (~80 rows)
    cat_flaw_1 = df.sample(30, random_state=1111).index
    df.loc[cat_flaw_1, "category"] = "electrONics"

    cat_flaw_2 = df.sample(25, random_state=1212).index
    df.loc[cat_flaw_2, "category"] = "Office-Supplies"

    cat_flaw_3 = df.sample(25, random_state=1313).index
    df.loc[cat_flaw_3, "category"] = "FURNITURE "

    # 7. Malformed Date strings (~40 rows)
    bad_dates_1 = df.sample(20, random_state=1414).index
    df.loc[bad_dates_1, "transaction_date"] = "2025/13/45"

    bad_dates_2 = df.sample(10, random_state=1515).index
    df.loc[bad_dates_2, "transaction_date"] = "INVALID_DATE"

    bad_dates_3 = df.sample(10, random_state=1616).index
    df.loc[bad_dates_3, "transaction_date"] = "05-12-2025" # DD-MM-YYYY ambiguous format

    # Shuffle the dataset to mix flawed rows naturally
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)

    print(f"Generated dataset with total {len(df)} rows.")
    return df


def main():
    root_dir = Path(__file__).resolve().parent.parent
    raw_dir = root_dir / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    df = generate_synthetic_data(num_records=7500)
    
    csv_path = raw_dir / "raw_sales_data.csv"
    excel_path = raw_dir / "raw_sales_data.xlsx"

    print(f"Saving raw CSV to {csv_path}...")
    df.to_csv(csv_path, index=False)

    print(f"Saving raw Excel to {excel_path}...")
    df.to_excel(excel_path, index=False, engine="openpyxl")

    print("Raw dataset generation complete!")


if __name__ == "__main__":
    main()
