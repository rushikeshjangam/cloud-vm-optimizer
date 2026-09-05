from cloud_vm_optimizer.data.generator import generate_demo_workload
from cloud_vm_optimizer.domain.models import VMType
from cloud_vm_optimizer.services.optimization_service import optimize_forecast, run_forecast


def test_vertical_slice_runs_end_to_end() -> None:
    history = generate_demo_workload(periods=240)
    forecast = run_forecast(history, horizon_hours=3, n_estimators=12)
    catalog = [
        VMType("small", 2, 4, 0.06, 50, 25),
        VMType("medium", 4, 8, 0.13, 80, 60),
        VMType("large", 8, 16, 0.25, 130, 140),
    ]
    comparison = optimize_forecast(forecast, catalog, current_vms=4)

    assert len(forecast.points) == 3
    assert comparison.baseline.feasible
    assert comparison.optimized.feasible
    assert comparison.recommendation.action in {"SCALE UP", "SCALE DOWN", "NO CHANGE"}

