from cloud_vm_optimizer.data.generator import generate_demo_workload
from cloud_vm_optimizer.forecasting.predictor import forecast_future
from cloud_vm_optimizer.forecasting.trainer import train_forecaster


def test_xgboost_trains_scores_and_forecasts() -> None:
    history = generate_demo_workload(periods=240)
    trained = train_forecaster(history, n_estimators=12)
    future = forecast_future(trained, history, horizon_hours=3)

    assert len(future) == 3
    assert set(trained.metrics) == {"cpu_usage", "ram_usage", "job_count"}
    assert all(score.mae >= 0 and score.rmse >= score.mae for score in trained.metrics.values())
    assert future["cpu_usage"].between(0, 100).all()
    assert future["ram_usage"].between(0, 100).all()
    assert (future["job_count"] >= 0).all()
    assert future["timestamp"].iloc[0] > history["timestamp"].iloc[-1]

