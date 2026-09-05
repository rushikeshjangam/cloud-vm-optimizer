"""Forecast evaluation helpers."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

from cloud_vm_optimizer.domain.models import MetricScore


def calculate_metrics(actual: np.ndarray, predicted: np.ndarray) -> MetricScore:
    """Calculate MAE and RMSE from genuine hold-out predictions."""

    return MetricScore(
        mae=float(mean_absolute_error(actual, predicted)),
        rmse=float(np.sqrt(mean_squared_error(actual, predicted))),
    )

