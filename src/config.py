"""
Configuration module for Business Sales & Performance Analytics System.
Loads environment variables and sets up project paths and logging constants.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

# Base Project Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"
SQL_DIR = BASE_DIR / "sql"

# File Paths
RAW_DATA_PATH = BASE_DIR / os.getenv("RAW_DATA_PATH", "data/raw/raw_sales_data.csv")
PROCESSED_DATA_PATH = BASE_DIR / os.getenv("PROCESSED_DATA_PATH", "data/processed/cleaned_sales_data.csv")
LOG_FILE_PATH = BASE_DIR / os.getenv("LOG_FILE_PATH", "logs/pipeline.log")
REPORT_OUTPUT_PATH = BASE_DIR / os.getenv("REPORT_OUTPUT_PATH", "reports/business_performance_report.xlsx")

# Database Credentials & Engine Settings
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "sales_analytics_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres_password")

# SQLite fallback path for local database file
SQLITE_DB_PATH = BASE_DIR / "data" / "sales_analytics.db"


def get_db_connection_url() -> str:
    """Builds and returns the database SQLAlchemy connection string based on config."""
    if DB_TYPE == "postgresql":
        return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        # Fallback to local SQLite database
        return f"sqlite:///{SQLITE_DB_PATH}"


def setup_logging():
    """Initializes standard Python logging format to file and stdout."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("SalesAnalyticsPipeline")
