"""Connect forecasting, allocation, optimization, and scale advice."""

from __future__ import annotations

import pandas as pd

from cloud_vm_optimizer.allocation.baseline import baseline_allocate
from cloud_vm_optimizer.domain.models import (
    ForecastPoint,
    ForecastResult,
    OptimizationComparison,
    ResourceDemand,
    ScalingRecommendation,
    VMType,
)
from cloud_vm_optimizer.forecasting.predictor import forecast_future
from cloud_vm_optimizer.forecasting.trainer import train_forecaster
from cloud_vm_optimizer.optimization.pso import optimize_with_pso

# Dataset percentages describe a demonstration cluster with this fixed capacity.
REFERENCE_CLUSTER_VCPUS = 16.0
REFERENCE_CLUSTER_MEMORY_GB = 32.0


def run_forecast(
    history: pd.DataFrame,
    horizon_hours: int = 6,
    n_estimators: int = 120,
) -> ForecastResult:
    trained = train_forecaster(history, n_estimators=n_estimators)
    predictions = forecast_future(trained, history, horizon_hours=horizon_hours)
    points = tuple(
        ForecastPoint(
            timestamp=row.timestamp.to_pydatetime(),
            cpu_usage=float(row.cpu_usage),
            ram_usage=float(row.ram_usage),
            job_count=float(row.job_count),
        )
        for row in predictions.itertuples(index=False)
    )
    return ForecastResult(
        points=points,
        metrics=trained.metrics,
        train_rows=trained.train_rows,
        test_rows=trained.test_rows,
    )


def forecast_result_to_frame(result: ForecastResult) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "timestamp": point.timestamp,
                "cpu_usage": point.cpu_usage,
                "ram_usage": point.ram_usage,
                "job_count": point.job_count,
            }
            for point in result.points
        ]
    )


def demand_from_forecast(result: ForecastResult) -> ResourceDemand:
    """Use horizon peaks as a conservative capacity recommendation."""

    if not result.points:
        raise ValueError("Forecast has no points.")
    peak_cpu = max(point.cpu_usage for point in result.points)
    peak_ram = max(point.ram_usage for point in result.points)
    peak_jobs = max(point.job_count for point in result.points)
    return ResourceDemand(
        vcpus=peak_cpu / 100 * REFERENCE_CLUSTER_VCPUS,
        memory_gb=peak_ram / 100 * REFERENCE_CLUSTER_MEMORY_GB,
        jobs=peak_jobs,
        cpu_percent=peak_cpu,
        ram_percent=peak_ram,
    )


def _improvement(baseline_value: float, optimized_value: float) -> float:
    if baseline_value == 0:
        return 0.0
    return (baseline_value - optimized_value) / baseline_value * 100


def scaling_recommendation(current_vms: int, recommended_vms: int) -> ScalingRecommendation:
    difference = recommended_vms - current_vms
    if difference > 0:
        return ScalingRecommendation("SCALE UP", difference, f"SCALE UP +{difference} VMs")
    if difference < 0:
        return ScalingRecommendation("SCALE DOWN", difference, f"SCALE DOWN {abs(difference)} VMs")
    return ScalingRecommendation("NO CHANGE", 0, "NO CHANGE")


def optimize_forecast(
    forecast: ForecastResult,
    catalog: list[VMType],
    current_vms: int,
    execution_hours: float | None = None,
    cost_weight: float = 0.5,
    energy_weight: float = 0.5,
) -> OptimizationComparison:
    demand = demand_from_forecast(forecast)
    hours = execution_hours or float(len(forecast.points))
    baseline = baseline_allocate(demand, catalog, hours)
    optimized = optimize_with_pso(
        demand,
        catalog,
        hours,
        baseline,
        cost_weight=cost_weight,
        energy_weight=energy_weight,
    )
    return OptimizationComparison(
        demand=demand,
        baseline=baseline,
        optimized=optimized,
        cost_improvement_percent=_improvement(baseline.cost_usd, optimized.cost_usd),
        energy_improvement_percent=_improvement(
            baseline.energy_kwh, optimized.energy_kwh
        ),
        recommendation=scaling_recommendation(current_vms, optimized.total_vms),
    )

