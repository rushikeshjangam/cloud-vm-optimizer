# 5. Particle Swarm Optimization Explained

Particle Swarm Optimization imitates a group searching together.

- A **particle** is one possible allocation.
- Its **position** is a vector such as `[small=1, medium=0, large=2]`.
- Its **velocity** controls how that vector changes.
- Its **personal best** is the best allocation that particle has found.
- The **global best** is the best allocation found by the whole swarm.

Each iteration updates velocity using three terms: momentum (inertia), movement
toward the personal best (cognitive), and movement toward the global best
(social). Counts are rounded to non-negative integers before evaluation.

```text
objective = cost_weight × (cost / baseline_cost)
          + energy_weight × (energy / baseline_energy)
```

Normalization makes dollars and kWh comparable. The two UI weights always sum
to 1. Any allocation short of required CPU, RAM, or jobs receives a penalty over
1000, so a feasible allocation is preferred. The baseline and each all-one-type
solution are seeded into the swarm, giving it sensible starting points and
ensuring the baseline remains available.

PSO is a heuristic: it finds a good result but does not mathematically prove the
global optimum. A fixed random seed makes the classroom demonstration repeatable.

