import pandas as pd

from cloud_vm_optimizer.forecasting.features import create_feature_frame


def test_features_use_only_prior_values() -> None:
    frame = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=10, freq="h"),
            "cpu_usage": range(10),
            "ram_usage": range(10, 20),
            "job_count": range(20, 30),
        }
    )
    featured = create_feature_frame(frame)
    first = featured.iloc[0]  # Original row 6 because rolling_mean_6 needs six past rows.
    assert first["cpu_usage"] == 6
    assert first["cpu_usage_lag_1"] == 5
    assert first["cpu_usage_lag_3"] == 3
    assert first["cpu_usage_rolling_mean_3"] == 4
    assert first["cpu_usage_rolling_mean_6"] == 2.5

