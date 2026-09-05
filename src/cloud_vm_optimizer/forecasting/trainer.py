"""Train one understandable XGBoost regressor per predicted signal."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from xgboost import XGBRegressor

from cloud_vm_optimizer.domain.models import MetricScore
from cloud_vm_optimizer.forecasting.features import (
    TARGET_COLUMNS,
    create_feature_frame,
    feature_column_names,
)
from cloud_vm_optimizer.forecasting.metrics import calculate_metrics


@dataclass
class TrainedForecaster:
    models: dict[str, XGBRegressor]
    feature_columns: list[str]
    metrics: dict[str, MetricScore]
    train_rows: int
    test_rows: int


def train_forecaster(
    data: pd.DataFrame,
    test_fraction: float = 0.2,
    n_estimators: int = 120,
    random_state: int = 42,
) -> TrainedForecaster:
    """Use a chronological split so reported scores represent future-like data."""

    if not 0.1 <= test_fraction <= 0.4:
        raise ValueError("test_fraction must be between 0.1 and 0.4.")

    supervised = create_feature_frame(data)
    split_index = int(len(supervised) * (1 - test_fraction))
    if split_index < 30 or len(supervised) - split_index < 8:
        raise ValueError("Not enough rows for a meaningful chronological train/test split.")

    features = feature_column_names()
    train = supervised.iloc[:split_index]
    test = supervised.iloc[split_index:]
    models: dict[str, XGBRegressor] = {}
    scores: dict[str, MetricScore] = {}

    for target in TARGET_COLUMNS:
        model = XGBRegressor(
            objective="reg:squarederror",
            n_estimators=n_estimators,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=random_state,
            n_jobs=1,
        )
        model.fit(train[features], train[target])
        prediction = model.predict(test[features])
        models[target] = model
        scores[target] = calculate_metrics(test[target].to_numpy(), prediction)

    return TrainedForecaster(
        models=models,
        feature_columns=features,
        metrics=scores,
        train_rows=len(train),
        test_rows=len(test),
    )

