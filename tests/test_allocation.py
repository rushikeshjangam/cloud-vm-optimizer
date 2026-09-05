from cloud_vm_optimizer.allocation.baseline import baseline_allocate
from cloud_vm_optimizer.domain.models import ResourceDemand, VMType


CATALOG = [
    VMType("small", 2, 4, 0.06, 50, 25),
    VMType("medium", 4, 8, 0.13, 80, 60),
    VMType("large", 8, 16, 0.25, 130, 140),
]


def test_baseline_meets_every_constraint_and_calculates_models() -> None:
    demand = ResourceDemand(12, 20, 125, 75, 62.5)
    result = baseline_allocate(demand, CATALOG, execution_hours=6)

    assert result.vm_counts == {"medium": 3}
    assert result.feasible
    assert result.total_vcpus >= demand.vcpus
    assert result.total_memory_gb >= demand.memory_gb
    assert result.total_job_capacity >= demand.jobs
    assert result.cost_usd == 3 * 0.13 * 6
    assert result.energy_kwh > 0

