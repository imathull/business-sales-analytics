"""
Main Entry Point for Business Sales & Performance Analytics System.
Orchestrates raw data generation/loading, validation, cleaning, DB loading, analytics, forecasting, and reporting.
"""

import sys
import logging
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.config import setup_logging, RAW_DATA_PATH, PROCESSED_DATA_PATH, REPORT_OUTPUT_PATH, SQL_DIR
from src.data_loader import load_raw_data
from src.validator import validate_schema, run_data_validation
from src.data_cleaner import clean_dataset, save_cleaned_data
from src.database import initialize_database, load_cleaned_data_to_db, run_sql_query
from src.analytics import (
    calculate_kpis, get_monthly_performance, get_branch_performance,
    get_category_performance, get_top_products, get_top_salespeople,
    detect_anomalies_iqr
)
from src.forecasting import forecast_next_months
from src.reporter import generate_excel_report


def run_pipeline():
    logger = setup_logging()
    logger.info("==================================================================")
    logger.info("  STARTING BUSINESS SALES & PERFORMANCE ANALYTICS DATA PIPELINE  ")
    logger.info("==================================================================")

    # Step 1: Ensure Raw Dataset Exists
    if not RAW_DATA_PATH.exists():
        logger.info("Raw dataset not found. Invoking synthetic raw data generator...")
        from scripts.generate_raw_data import generate_synthetic_data
        df_raw = generate_synthetic_data(num_records=7500)
        RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        df_raw.to_csv(RAW_DATA_PATH, index=False)
        logger.info(f"Generated raw dataset saved to: {RAW_DATA_PATH}")

    # Step 2: Load Raw Data
    logger.info("[Step 1/7] Loading Raw Sales Data...")
    df_raw = load_raw_data(RAW_DATA_PATH)

    # Step 3: Validate Data Structure & Integrity
    logger.info("[Step 2/7] Validating Raw Data Integrity & Schema...")
    if not validate_schema(df_raw):
        logger.error("Pipeline aborted due to schema mismatch.")
        sys.exit(1)

    val_report = run_data_validation(df_raw)
    logger.info(f"Validation Audit: Total={val_report['total_records']}, "
                f"Valid={val_report['valid_records']}, Invalid={val_report['invalid_records']}, "
                f"Duplicates={val_report['exact_duplicates']}")

    # Step 4: Clean Data & Feature Engineering
    logger.info("[Step 3/7] Cleaning Data & Computing Calculated Columns...")
    df_cleaned = clean_dataset(df_raw)
    save_cleaned_data(df_cleaned, PROCESSED_DATA_PATH)

    # Step 5: Database Initialization & Load
    logger.info("[Step 4/7] Initializing Relational Database & Loading Tables...")
    schema_file = SQL_DIR / "schema.sql"
    try:
        initialize_database(str(schema_file))
        load_cleaned_data_to_db(df_cleaned)
    except Exception as e:
        logger.warning(f"Database operation encountered issue: {e}. Proceeding with in-memory analysis.")

    # Step 6: Perform Business Analytics & Anomaly Detection
    logger.info("[Step 5/7] Executing Business Analytics & Statistical Anomaly Detection...")
    kpis = calculate_kpis(df_cleaned)
    monthly_perf = get_monthly_performance(df_cleaned)
    branch_perf = get_branch_performance(df_cleaned)
    cat_perf = get_category_performance(df_cleaned)
    top_products = get_top_products(df_cleaned, top_n=10)
    top_salespeople = get_top_salespeople(df_cleaned, top_n=10)
    anomalies_df, bounds_info = detect_anomalies_iqr(df_cleaned, column="net_sales")

    # Step 7: Sales Forecasting
    logger.info("[Step 6/7] Generating Sales Forecast (Linear Regression & 3M Moving Average)...")
    forecast_df = forecast_next_months(monthly_perf, periods=3)

    # Step 8: Export Summary Excel Report
    logger.info("[Step 7/7] Exporting Business Performance Excel Report...")
    generate_excel_report(
        kpis=kpis,
        branch_df=branch_perf,
        top_prod_df=top_products,
        val_report=val_report,
        anomalies_df=anomalies_df,
        forecast_df=forecast_df,
        output_path=REPORT_OUTPUT_PATH
    )

    logger.info("==================================================================")
    logger.info("     PIPELINE EXECUTED SUCCESSFULLY! ALL OUTPUTS CREATED.        ")
    logger.info(f"  Processed File: {PROCESSED_DATA_PATH}")
    logger.info(f"  Summary Report: {REPORT_OUTPUT_PATH}")
    logger.info(f"  Pipeline Log:   logs/pipeline.log")
    logger.info("==================================================================")


if __name__ == "__main__":
    run_pipeline()
