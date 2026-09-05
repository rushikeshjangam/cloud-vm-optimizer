"""Small data models shared by the forecasting and allocation modules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class VMType:
    """One VM option in the demonstration catalog."""

    name: str
    vcpus: float
    memory_gb: float
    hourly_cost: float
    power_watts: float
    job_capacity: float


@dataclass(frozen=True)
class ResourceDemand:
    """Absolute capacity required by the forecast horizon."""

    vcpus: float
    memory_gb: float
    jobs: float
    cpu_percent: float
    ram_percent: float


@dataclass(frozen=True)
class MetricScore:
    """Accuracy scores calculated on the chronological hold-out set."""

    mae: float
    rmse: float


@dataclass(frozen=True)
class ForecastPoint:
    timestamp: datetime
    cpu_usage: float
    ram_usage: float
    job_count: float


@dataclass(frozen=True)
class ForecastResult:
    points: tuple[ForecastPoint, ...]
    metrics: dict[str, MetricScore]
    train_rows: int
    test_rows: int


@dataclass(frozen=True)
class AllocationResult:
    """Capacity, cost, and estimated energy for one allocation."""

    method: str
    vm_counts: dict[str, int]
    total_vms: int
    total_vcpus: float
    total_memory_gb: float
    total_job_capacity: float
    cost_usd: float
    energy_kwh: float
    utilization_factor: float
    feasible: bool
    objective_score: float | None = None


@dataclass(frozen=True)
class ScalingRecommendation:
    action: str
    difference: int
    message: str


@dataclass(frozen=True)
class OptimizationComparison:
    demand: ResourceDemand
    baseline: AllocationResult
    optimized: AllocationResult
    cost_improvement_percent: float
    energy_improvement_percent: float
    recommendation: ScalingRecommendation

