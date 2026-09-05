"""A deliberately simple medium-VM baseline for comparison."""

from __future__ import annotations

import math

from cloud_vm_optimizer.allocation.cost import calculate_cost
from cloud_vm_optimizer.allocation.energy import allocation_capacity, calculate_energy_kwh
from cloud_vm_optimizer.domain.models import AllocationResult, ResourceDemand, VMType


def allocation_is_feasible(
    vm_counts: dict[str, int], catalog: list[VMType], demand: ResourceDemand
) -> bool:
    vcpus, memory, jobs, _ = allocation_capacity(vm_counts, catalog)
    return vcpus >= demand.vcpus and memory >= demand.memory_gb and jobs >= demand.jobs


def build_allocation_result(
    method: str,
    vm_counts: dict[str, int],
    catalog: list[VMType],
    demand: ResourceDemand,
    execution_hours: float,
    objective_score: float | None = None,
) -> AllocationResult:
    clean_counts = {name: int(count) for name, count in vm_counts.items() if count > 0}
    vcpus, memory, jobs, _ = allocation_capacity(clean_counts, catalog)
    energy, utilization = calculate_energy_kwh(
        clean_counts, catalog, demand, execution_hours
    )
    return AllocationResult(
        method=method,
        vm_counts=clean_counts,
        total_vms=sum(clean_counts.values()),
        total_vcpus=vcpus,
        total_memory_gb=memory,
        total_job_capacity=jobs,
        cost_usd=calculate_cost(clean_counts, catalog, execution_hours),
        energy_kwh=energy,
        utilization_factor=utilization,
        feasible=allocation_is_feasible(clean_counts, catalog, demand),
        objective_score=objective_score,
    )


def baseline_allocate(
    demand: ResourceDemand,
    catalog: list[VMType],
    execution_hours: float,
    preferred_vm_name: str = "medium",
) -> AllocationResult:
    """Add identical medium VMs until CPU, RAM, and job needs are all covered."""

    try:
        vm = next(item for item in catalog if item.name == preferred_vm_name)
    except StopIteration as error:
        raise ValueError(f"Baseline VM '{preferred_vm_name}' is not in the catalog.") from error

    count = max(
        math.ceil(demand.vcpus / vm.vcpus),
        math.ceil(demand.memory_gb / vm.memory_gb),
        math.ceil(demand.jobs / vm.job_capacity),
        1,
    )
    return build_allocation_result(
        method="Baseline (medium-only)",
        vm_counts={vm.name: count},
        catalog=catalog,
        demand=demand,
        execution_hours=execution_hours,
    )

