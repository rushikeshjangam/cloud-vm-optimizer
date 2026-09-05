# 9. Viva Guide

## Core questions and short answers

**What problem does the project solve?**  It forecasts near-future cloud demand
and recommends enough VM capacity while balancing estimated cost and energy.

**Why XGBoost?**  It performs well on structured data, captures non-linear
relationships, trains quickly on a small dataset, and is easier to demonstrate
than a deep neural network.

**What are lag features?**  Previous values, such as CPU one hour ago, supplied
as model inputs for predicting the current or next hour.

**What is MAE?**  The average absolute distance between actual and predicted values.

**What is RMSE?**  A square-error metric that penalizes large misses more than MAE.

**What is PSO?**  A population-based search algorithm where candidate solutions
move toward their own best result and the swarm's best result.

**What is a particle?**  One candidate vector of small, medium, and large VM counts.

**What is an objective function?**  A numeric score the optimizer minimizes; here
it is a weighted combination of normalized cost and estimated energy.

**Why optimize both cost and energy?**  The cheapest allocation is not always the
lowest-power allocation, so weights make that tradeoff visible.

**How is energy estimated?**  Catalog watts × utilization factor × hours / 1000.
It is a simulation, not physical AWS telemetry.

**How does baseline differ from PSO?**  Baseline adds medium VMs only. PSO searches
mixed VM types and shares discoveries across particles.

**How are constraints enforced?**  Any allocation below forecast CPU, RAM, or job
capacity receives a very large objective penalty.

**Why use a chronological train/test split?**  A real forecast predicts later
times from earlier data; random mixing could leak future patterns backward.

**What is the difference between simulation and real AWS?**  The optimizer uses a
generic catalog and estimated formulas. AWS only hosts the dashboard and can
optionally show safely tagged EC2 state.

**Why not create hundreds of EC2 instances?**  It is costly, risky, and unnecessary
to prove the allocation algorithm. Simulation is repeatable and budget-safe.

**What does boto3 do?**  It is the official AWS SDK for Python. Here it is loaded
only in explicitly enabled read-only demo mode and uses standard IAM credentials.

**What happens if AWS is unavailable?**  Forecasting, PSO, and the dashboard still
work locally because AWS is not part of the academic computation.

**What are the main limitations?**  Synthetic data, demo prices, simplified
energy, recursive forecast error, and PSO's lack of a global-optimum guarantee.

