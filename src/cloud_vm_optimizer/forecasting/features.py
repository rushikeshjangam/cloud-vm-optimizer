"""Leak-safe feature engineering for hourly workload data."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

TARGET_COLUMNS = ("cpu_usage", "ram_usage", "job_count")
LAGS = (1, 2, 3)
ROLLING_WINDOWS = (3, 6)


def feature_column_names() -> list[str]:
    names = ["hour", "day_of_week"]
    for target in TARGET_COLUMNS:
        names.extend(f"{target}_lag_{lag}" for lag in LAGS)
        names.extend(f"{target}_rolling_mean_{window}" for window in ROLLING_WINDOWS)
    return names


def create_feature_frame(data: pd.DataFrame) -> pd.DataFrame:
    """Build training features using only observations before each target row."""

    required = {"timestamp", *TARGET_COLUMNS}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Cannot build features; missing columns: {sorted(missing)}")

    frame = data.copy().sort_values("timestamp").reset_index(drop=True)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    frame["hour"] = frame["timestamp"].dt.hour
    frame["day_of_week"] = frame["timestamp"].dt.dayofweek

    for target in TARGET_COLUMNS:
        past_values = frame[target].shift(1)
        for lag in LAGS:
            frame[f"{target}_lag_{lag}"] = frame[target].shift(lag)
        for window in ROLLING_WINDOWS:
            frame[f"{target}_rolling_mean_{window}"] = past_values.rolling(window).mean()

    return frame.dropna().reset_index(drop=True)


def build_future_feature_row(
    history: pd.DataFrame, timestamp: datetime | pd.Timestamp
) -> pd.DataFrame:
    """Build one recursive forecast row from known or previously predicted history."""

    if len(history) < max(ROLLING_WINDOWS):
        raise ValueError("At least six historical rows are needed for forecasting.")

    values: dict[str, float] = {
        "hour": float(timestamp.hour),
        "day_of_week": float(timestamp.weekday()),
    }
    for target in TARGET_COLUMNS:
        series = history[target].astype(float)
        for lag in LAGS:
            values[f"{target}_lag_{lag}"] = float(series.iloc[-lag])
        for window in ROLLING_WINDOWS:
            values[f"{target}_rolling_mean_{window}"] = float(series.iloc[-window:].mean())
    return pd.DataFrame([values], columns=feature_column_names())
