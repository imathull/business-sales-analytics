"""
Database module for Business Sales & Performance Analytics System.
Handles relational database connections (PostgreSQL / SQLite fallback),
schema creation, dimension & fact table loading, and SQL query execution.
"""

import logging
import pandas as pd
from sqlalchemy import create_engine, text
from src.config import get_db_connection_url, DB_TYPE

logger = logging.getLogger("SalesAnalyticsPipeline")


def get_engine():
    """Returns SQLAlchemy engine instance for DB connection."""
    url = get_db_connection_url()
    # If SQLite, ensure directory exists
    if "sqlite" in url:
        db_path_str = url.replace("sqlite:///", "")
        from pathlib import Path
        Path(db_path_str).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(url, echo=False)


def initialize_database(schema_sql_path: str = "sql/schema.sql"):
    """
    Executes DDL schema file to create relational database tables.
    """
    engine = get_engine()
    logger.info(f"Initializing database schema using engine: {DB_TYPE}...")

    try:
        with open(schema_sql_path, "r", encoding="utf-8") as f:
            sql_statements = f.read()

        with engine.connect() as conn:
            # Split by semicolon for batch execution if needed
            for statement in sql_statements.split(";"):
                stmt = statement.strip()
                if stmt:
                    conn.execute(text(stmt))
            conn.commit()

        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")
        # If PostgreSQL DDL fails due to missing connection, log warning
        if DB_TYPE == "postgresql":
            logger.warning("PostgreSQL connection failed. Ensure local PostgreSQL server is running or set DB_TYPE=sqlite in .env.")
        raise


def load_cleaned_data_to_db(df: pd.DataFrame):
    """
    Normalizes cleaned DataFrame into 3NF dimension tables (branches, salespeople, products)
    and fact table (sales), loading them into the database.
    """
    engine = get_engine()
    logger.info("Loading cleaned dataset into relational database tables...")

    # 1. Dimension: Branches
    branches_df = df[["branch_id", "branch_name", "region"]].drop_duplicates(subset=["branch_id"]).copy()

    # 2. Dimension: Salespeople
    salespeople_df = df[["salesperson_id", "salesperson_name"]].drop_duplicates(subset=["salesperson_id"]).copy()

    # 3. Dimension: Products
    products_df = df[["product_id", "product_name", "category", "unit_price"]].drop_duplicates(subset=["product_id"]).copy()

    # 4. Fact: Sales
    sales_fact_df = df[[
        "transaction_id", "transaction_date", "branch_id", "salesperson_id",
        "product_id", "quantity", "unit_price", "discount",
        "gross_amount", "discount_amount", "net_sales",
        "payment_method", "customer_type"
    ]].copy()

    try:
        with engine.begin() as conn:
            # Write Dimension Tables
            branches_df.to_sql("branches", conn, if_exists="replace", index=False)
            salespeople_df.to_sql("salespeople", conn, if_exists="replace", index=False)
            products_df.to_sql("products", conn, if_exists="replace", index=False)

            # Write Fact Table
            sales_fact_df.to_sql("sales", conn, if_exists="replace", index=False)

        logger.info(f"Successfully loaded DB Tables: "
                    f"branches ({len(branches_df)}), salespeople ({len(salespeople_df)}), "
                    f"products ({len(products_df)}), sales ({len(sales_fact_df)})")

    except Exception as e:
        logger.error(f"Error loading data into database: {e}")
        raise


def run_sql_query(query_str: str) -> pd.DataFrame:
    """Executes a SQL query string and returns results as a pandas DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql_query(text(query_str), conn)
