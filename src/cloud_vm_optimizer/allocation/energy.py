"""Estimated energy model; this is not physical AWS telemetry."""

from __future__ import annotations

from cloud_vm_optimizer.domain.models import ResourceDemand, VMType


def allocation_capacity(
    vm_counts: dict[str, int], catalog: list[VMType]
) -> tuple[float, float, float, float]:
    """Return total vCPUs, memory, job capacity, and rated power."""

    by_name = {vm.name: vm for vm in catalog}
    vcpus = sum(count * by_name[name].vcpus for name, count in vm_counts.items())
    memory = sum(count * by_name[name].memory_gb for name, count in vm_counts.items())
    jobs = sum(count * by_name[name].job_capacity for name, count in vm_counts.items())
    watts = sum(count * by_name[name].power_watts for name, count in vm_counts.items())
    return float(vcpus), float(memory), float(jobs), float(watts)


def calculate_utilization_factor(
    demand: ResourceDemand, vcpus: float, memory_gb: float, job_capacity: float
) -> float:
    """Use the most-loaded resource, with 20% idle power as a demo assumption."""

    if min(vcpus, memory_gb, job_capacity) <= 0:
        return 0.0
    busiest_resource = max(
        demand.vcpus / vcpus,
        demand.memory_gb / memory_gb,
        demand.jobs / job_capacity,
    )
    return float(min(1.0, max(0.2, busiest_resource)))


def calculate_energy_kwh(
    vm_counts: dict[str, int],
    catalog: list[VMType],
    demand: ResourceDemand,
    execution_hours: float,
) -> tuple[float, float]:
    """Energy = rated watts x utilization factor x hours / 1000."""

    if execution_hours <= 0:
        raise ValueError("execution_hours must be positive.")
    vcpus, memory, jobs, watts = allocation_capacity(vm_counts, catalog)
    utilization = calculate_utilization_factor(demand, vcpus, memory, jobs)
    return float(watts * utilization * execution_hours / 1000), utilization

