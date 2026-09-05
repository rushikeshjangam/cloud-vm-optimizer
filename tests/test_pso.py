from cloud_vm_optimizer.allocation.baseline import baseline_allocate
from cloud_vm_optimizer.domain.models import ResourceDemand, VMType
from cloud_vm_optimizer.optimization.pso import optimize_with_pso


CATALOG = [
    VMType("small", 2, 4, 0.06, 50, 25),
    VMType("medium", 4, 8, 0.13, 80, 60),
    VMType("large", 8, 16, 0.25, 130, 140),
]


def test_pso_returns_feasible_result_no_worse_than_seeded_baseline_objective() -> None:
    demand = ResourceDemand(12.8, 22, 125, 80, 68.75)
    baseline = baseline_allocate(demand, CATALOG, execution_hours=6)
    optimized = optimize_with_pso(
        demand,
        CATALOG,
        execution_hours=6,
        reference=baseline,
        particles=16,
        iterations=25,
        seed=7,
    )

    assert optimized.feasible
    assert optimized.objective_score is not None
    assert optimized.objective_score <= 1.0 + 1e-9
    assert optimized.total_vms > 0

