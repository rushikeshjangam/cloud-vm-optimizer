"""A compact, discrete Particle Swarm Optimizer students can explain."""

from __future__ import annotations

import math

import numpy as np

from cloud_vm_optimizer.allocation.baseline import build_allocation_result
from cloud_vm_optimizer.allocation.cost import calculate_cost
from cloud_vm_optimizer.allocation.energy import allocation_capacity, calculate_energy_kwh
from cloud_vm_optimizer.domain.models import AllocationResult, ResourceDemand, VMType


def _integer_counts(position: np.ndarray, maximum_count: int) -> np.ndarray:
    return np.clip(np.rint(position), 0, maximum_count).astype(int)


def _counts_by_name(counts: np.ndarray, catalog: list[VMType]) -> dict[str, int]:
    return {vm.name: int(count) for vm, count in zip(catalog, counts, strict=True) if count > 0}


def optimize_with_pso(
    demand: ResourceDemand,
    catalog: list[VMType],
    execution_hours: float,
    reference: AllocationResult,
    cost_weight: float = 0.5,
    energy_weight: float = 0.5,
    particles: int = 32,
    iterations: int = 70,
    seed: int = 42,
) -> AllocationResult:
    """Search integer VM counts using personal-best and global-best movement.

    Each particle's position represents one count per VM type. Infeasible
    particles receive a large penalty. Feasible scores combine cost and energy,
    each normalized by the baseline so unlike units can be compared.
    """

    if not catalog:
        raise ValueError("The VM catalog cannot be empty.")
    if cost_weight < 0 or energy_weight < 0 or cost_weight + energy_weight <= 0:
        raise ValueError("Optimization weights must be non-negative and not both zero.")
    total_weight = cost_weight + energy_weight
    cost_weight /= total_weight
    energy_weight /= total_weight
    particles = max(particles, len(catalog) + 2)
    maximum_count = max(reference.total_vms * 2 + 2, 6)
    rng = np.random.default_rng(seed)

    positions = rng.uniform(0, maximum_count, size=(particles, len(catalog)))
    velocities = rng.uniform(-1, 1, size=positions.shape)

    # Seed known feasible candidates so PSO can never return worse than baseline.
    baseline_vector = np.array([reference.vm_counts.get(vm.name, 0) for vm in catalog])
    positions[0] = baseline_vector
    for index, vm in enumerate(catalog):
        count = max(
            math.ceil(demand.vcpus / vm.vcpus),
            math.ceil(demand.memory_gb / vm.memory_gb),
            math.ceil(demand.jobs / vm.job_capacity),
            1,
        )
        candidate = np.zeros(len(catalog))
        candidate[index] = min(count, maximum_count)
        positions[index + 1] = candidate

    reference_cost = max(reference.cost_usd, 1e-9)
    reference_energy = max(reference.energy_kwh, 1e-9)

    def objective(position: np.ndarray) -> float:
        counts = _integer_counts(position, maximum_count)
        allocation = _counts_by_name(counts, catalog)
        vcpus, memory, jobs, _ = allocation_capacity(allocation, catalog)
        deficits = (
            max(0.0, demand.vcpus - vcpus) / max(demand.vcpus, 1e-9)
            + max(0.0, demand.memory_gb - memory) / max(demand.memory_gb, 1e-9)
            + max(0.0, demand.jobs - jobs) / max(demand.jobs, 1e-9)
        )
        if deficits > 0:
            return 1_000.0 + 100.0 * deficits
        cost = calculate_cost(allocation, catalog, execution_hours)
        energy, _ = calculate_energy_kwh(allocation, catalog, demand, execution_hours)
        return cost_weight * (cost / reference_cost) + energy_weight * (
            energy / reference_energy
        )

    scores = np.array([objective(position) for position in positions])
    personal_best = positions.copy()
    personal_scores = scores.copy()
    best_index = int(np.argmin(personal_scores))
    global_best = personal_best[best_index].copy()
    global_score = float(personal_scores[best_index])

    inertia, cognitive, social = 0.65, 1.45, 1.45
    for _ in range(iterations):
        random_personal = rng.random(size=positions.shape)
        random_global = rng.random(size=positions.shape)
        velocities = (
            inertia * velocities
            + cognitive * random_personal * (personal_best - positions)
            + social * random_global * (global_best - positions)
        )
        positions = np.clip(positions + velocities, 0, maximum_count)
        scores = np.array([objective(position) for position in positions])
        improved = scores < personal_scores
        personal_best[improved] = positions[improved]
        personal_scores[improved] = scores[improved]
        candidate_index = int(np.argmin(personal_scores))
        if personal_scores[candidate_index] < global_score:
            global_best = personal_best[candidate_index].copy()
            global_score = float(personal_scores[candidate_index])

    best_counts = _counts_by_name(_integer_counts(global_best, maximum_count), catalog)
    return build_allocation_result(
        method="PSO optimized",
        vm_counts=best_counts,
        catalog=catalog,
        demand=demand,
        execution_hours=execution_hours,
        objective_score=global_score,
    )

