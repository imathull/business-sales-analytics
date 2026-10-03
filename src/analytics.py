"""
Analytics module for Business Sales & Performance Analytics System.
Computes core business KPIs, group aggregations, and performs statistical anomaly detection.
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger("SalesAnalyticsPipeline")


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calculates executive high-level business KPIs.
    
    :param df: Cleaned sales DataFrame.
    :return: Dictionary of KPI metrics.
    """
    total_revenue = float(df["net_sales"].sum())
    total_transactions = int(len(df))
    total_units_sold = int(df["quantity"].sum())
    aov = float(total_revenue / total_transactions) if total_transactions > 0 else 0.0
    avg_discount = float(df["discount"].mean()) if total_transactions > 0 else 0.0

    kpis = {
        "total_revenue": round(total_revenue, 2),
        "total_transactions": total_transactions,
        "total_units_sold": total_units_sold,
        "average_order_value": round(aov, 2),
        "average_discount_pct": round(avg_discount, 2)
    }
    
    logger.info(f"Calculated Core KPIs: Revenue=${total_revenue:,.2f} | Transactions={total_transactions:,} | AOV=${aov:,.2f}")
    return kpis


def get_monthly_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates monthly sales revenue, transactions, and month-over-month growth %."""
    df_temp = df.copy()
    df_temp["year_month"] = pd.to_datetime(df_temp["transaction_date"]).dt.to_period("M").astype(str)

    monthly = df_temp.groupby("year_month").agg(
        total_revenue=("net_sales", "sum"),
        total_transactions=("transaction_id", "count"),
        units_sold=("quantity", "sum"),
        avg_order_value=("net_sales", "mean")
    ).reset_index().sort_values("year_month")

    # Month-over-Month Growth Calculation
    monthly["prev_month_revenue"] = monthly["total_revenue"].shift(1)
    monthly["mom_growth_pct"] = (
        ((monthly["total_revenue"] - monthly["prev_month_revenue"]) / monthly["prev_month_revenue"]) * 100
    ).fillna(0.0).round(2)

    monthly["total_revenue"] = monthly["total_revenue"].round(2)
    monthly["avg_order_value"] = monthly["avg_order_value"].round(2)

    return monthly


def get_branch_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates sales summary broken down by branch and region."""
    branch_perf = df.groupby(["region", "branch_id", "branch_name"]).agg(
        total_revenue=("net_sales", "sum"),
        total_transactions=("transaction_id", "count"),
        units_sold=("quantity", "sum"),
        avg_order_value=("net_sales", "mean")
    ).reset_index().sort_values(by="total_revenue", ascending=False)

    branch_perf["total_revenue"] = branch_perf["total_revenue"].round(2)
    branch_perf["avg_order_value"] = branch_perf["avg_order_value"].round(2)
    return branch_perf


def get_category_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates performance by product category."""
    cat_perf = df.groupby("category").agg(
        total_revenue=("net_sales", "sum"),
        units_sold=("quantity", "sum"),
        total_transactions=("transaction_id", "count"),
        avg_discount=("discount", "mean")
    ).reset_index().sort_values(by="total_revenue", ascending=False)

    cat_perf["total_revenue"] = cat_perf["total_revenue"].round(2)
    cat_perf["avg_discount"] = cat_perf["avg_discount"].round(2)
    return cat_perf


def get_top_products(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Returns top N products sorted by net sales revenue."""
    top_prod = df.groupby(["product_id", "product_name", "category"]).agg(
        total_revenue=("net_sales", "sum"),
        units_sold=("quantity", "sum"),
        avg_unit_price=("unit_price", "mean")
    ).reset_index().sort_values(by="total_revenue", ascending=False).head(top_n)

    top_prod["total_revenue"] = top_prod["total_revenue"].round(2)
    top_prod["avg_unit_price"] = top_prod["avg_unit_price"].round(2)
    return top_prod


def get_top_salespeople(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Returns top N salespeople by total net sales revenue."""
    top_sp = df.groupby(["salesperson_id", "salesperson_name"]).agg(
        total_revenue=("net_sales", "sum"),
        total_transactions=("transaction_id", "count"),
        avg_order_value=("net_sales", "mean")
    ).reset_index().sort_values(by="total_revenue", ascending=False).head(top_n)

    top_sp["total_revenue"] = top_sp["total_revenue"].round(2)
    top_sp["avg_order_value"] = top_sp["avg_order_value"].round(2)
    return top_sp


def detect_anomalies_iqr(df: pd.DataFrame, column: str = "net_sales") -> (pd.DataFrame, dict):
    """
    Identifies unusually high or low transaction amounts using the Interquartile Range (IQR) method.
    
    Rule:
    IQR = Q3 - Q1
    Upper Bound = Q3 + 1.5 * IQR
    Lower Bound = Q1 - 1.5 * IQR
    
    :param df: Cleaned DataFrame.
    :param column: Column to perform anomaly detection on (default 'net_sales').
    :return: Tuple of (anomalies DataFrame, bounds dict).
    """
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1

    upper_bound = q3 + (1.5 * iqr)
    lower_bound = max(0, q1 - (1.5 * iqr))

    anomalies_df = df[(df[column] > upper_bound) | (df[column] < lower_bound)].copy()
    anomalies_df["anomaly_type"] = np.where(anomalies_df[column] > upper_bound, "High Outlier", "Low Outlier")

    bounds_info = {
        "Q1": round(q1, 2),
        "Q3": round(q3, 2),
        "IQR": round(iqr, 2),
        "upper_bound": round(upper_bound, 2),
        "lower_bound": round(lower_bound, 2),
        "anomaly_count": len(anomalies_df)
    }

    logger.info(f"IQR Anomaly Detection on '{column}': Found {len(anomalies_df)} anomalies (> ${upper_bound:,.2f}).")
    return anomalies_df, bounds_info
