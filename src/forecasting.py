"""
Forecasting module for Business Sales & Performance Analytics System.
Implements simple, interview-friendly sales forecasting methods:
1. 3-Month Moving Average
2. Simple Linear Regression (scikit-learn / numpy)
"""

import logging
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

logger = logging.getLogger("SalesAnalyticsPipeline")


def forecast_next_months(monthly_df: pd.DataFrame, periods: int = 3) -> pd.DataFrame:
    """
    Forecasts next N months revenue using Linear Regression and 3-Month Moving Average.
    
    :param monthly_df: DataFrame with 'year_month' and 'total_revenue'.
    :param periods: Number of future months to forecast (default 3).
    :return: Combined DataFrame with historical and forecasted monthly revenues.
    """
    logger.info(f"Generating simple sales forecast for next {periods} months...")
    df = monthly_df.copy()
    
    # Sort chronologically
    df = df.sort_values("year_month").reset_index(drop=True)
    df["time_index"] = np.arange(len(df))

    # 1. Linear Regression Fit
    X = df[["time_index"]].values
    y = df["total_revenue"].values

    model = LinearRegression()
    model.fit(X, y)

    # In-sample predictions
    df["linear_trend"] = model.predict(X).round(2)
    
    # 2. 3-Month Moving Average (In-sample)
    df["moving_avg_3m"] = df["total_revenue"].rolling(window=3, min_periods=1).mean().round(2)
    df["is_forecast"] = False

    # Build Future Period Strings
    last_period = pd.Period(df["year_month"].iloc[-1], freq="M")
    future_rows = []
    
    last_3m_avg = float(df["total_revenue"].iloc[-3:].mean())
    last_idx = len(df) - 1

    for i in range(1, periods + 1):
        future_period = (last_period + i).strftime("%Y-%m")
        future_idx = last_idx + i
        
        # Predict Linear Regression
        pred_lr = float(model.predict([[future_idx]])[0])
        
        future_rows.append({
            "year_month": future_period,
            "total_revenue": np.nan,  # Actual revenue unknown
            "time_index": future_idx,
            "linear_trend": round(pred_lr, 2),
            "moving_avg_3m": round(last_3m_avg, 2),
            "is_forecast": True
        })

    df_future = pd.DataFrame(future_rows)
    df_combined = pd.concat([df, df_future], ignore_index=True)

    logger.info(f"Forecast complete for upcoming periods: {list(df_future['year_month'])}")
    return df_combined
