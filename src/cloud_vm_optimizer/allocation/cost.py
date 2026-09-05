"""Operational cost calculation for the demonstration catalog."""

from __future__ import annotations

from cloud_vm_optimizer.domain.models import VMType


def calculate_cost(
    vm_counts: dict[str, int], catalog: list[VMType], execution_hours: float
) -> float:
    """Cost = sum(VM count x demo hourly price x execution hours)."""

    if execution_hours <= 0:
        raise ValueError("execution_hours must be positive.")
    by_name = {vm.name: vm for vm in catalog}
    return float(
        sum(count * by_name[name].hourly_cost * execution_hours for name, count in vm_counts.items())
    )

