"""Recursive short-horizon forecasting."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd

from cloud_vm_optimizer.forecasting.features import TARGET_COLUMNS, build_future_feature_row
from cloud_vm_optimizer.forecasting.trainer import TrainedForecaster


def forecast_future(
    forecaster: TrainedForecaster,
    history: pd.DataFrame,
    horizon_hours: int = 6,
) -> pd.DataFrame:
    """Predict each next hour, feeding each prediction into the following step."""

    if not 1 <= horizon_hours <= 24:
        raise ValueError("Forecast horizon must be between 1 and 24 hours.")

    working = history.copy().sort_values("timestamp").reset_index(drop=True)
    # Normalize to nanoseconds so arithmetic remains stable across CSV and
    # in-memory datetime precisions used by recent pandas/NumPy versions.
    working["timestamp"] = pd.to_datetime(working["timestamp"]).astype("datetime64[ns]")
    next_timestamp = working["timestamp"].iloc[-1].to_pydatetime() + timedelta(hours=1)
    rows: list[dict[str, object]] = []

    for _ in range(horizon_hours):
        features = build_future_feature_row(working, next_timestamp)
        predicted = {
            target: float(forecaster.models[target].predict(features[forecaster.feature_columns])[0])
            for target in TARGET_COLUMNS
        }
        predicted["cpu_usage"] = min(100.0, max(0.0, predicted["cpu_usage"]))
        predicted["ram_usage"] = min(100.0, max(0.0, predicted["ram_usage"]))
        predicted["job_count"] = max(0.0, predicted["job_count"])
        row = {"timestamp": next_timestamp, **predicted}
        rows.append(row)
        working = pd.concat([working, pd.DataFrame([row])], ignore_index=True)
        next_timestamp += timedelta(hours=1)

    return pd.DataFrame(rows)
