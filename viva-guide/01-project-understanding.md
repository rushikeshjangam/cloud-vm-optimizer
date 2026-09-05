# 1. Understand the Project Before the Viva

## Problem statement

Cloud demand changes hour by hour. If capacity is too small, jobs may queue or
applications may slow down. If capacity is much larger than demand, money and
estimated energy are wasted. The project answers two connected questions:

1. What CPU, RAM, and job demand is likely during the next 1–24 hours?
2. What mixture of small, medium, and large virtual machines can satisfy the
   predicted peak while balancing cost and estimated energy?

The output is a recommendation: `SCALE UP`, `SCALE DOWN`, or `NO CHANGE`. It is
not an autonomous production autoscaler.

## End-to-end pipeline

```text
720 hourly observations
  -> validated chronological data
  -> time, lag, and rolling features
  -> three XGBoost regression models
  -> future CPU, RAM, and job forecasts
  -> peak demand over the chosen horizon
  -> medium-only baseline allocation
  -> discrete Particle Swarm Optimization
  -> cost and estimated-energy comparison
  -> scaling recommendation in Streamlit
```

AWS hosts the dashboard. AWS is not used to train the models or simulate a
large cluster. This separation keeps the demonstration affordable and safe.

## Dataset

`data/demo_workload.csv` contains 720 hourly rows, representing 30 days. Its
columns are `timestamp`, `cpu_usage`, `ram_usage`, and `job_count`. It is a
deterministic synthetic dataset with daily cycles, business-hour peaks, weekday
effects, a small trend, relationships between jobs and resource use, and seeded
noise. It is reproducible, but it must not be described as real company data.

`data/vm_catalog.csv` defines three generic choices:

| Type | vCPU | RAM | Demo USD/hour | Watts | Jobs/hour |
|---|---:|---:|---:|---:|---:|
| small | 2 | 4 GB | 0.06 | 50 | 25 |
| medium | 4 | 8 GB | 0.13 | 80 | 60 |
| large | 8 | 16 GB | 0.25 | 130 | 140 |

These values are academic assumptions. The deployed `t3.small` is merely the
host running Streamlit; it is different from the generic simulated VM catalog.

## Feature engineering and leakage prevention

Each target model receives hour of day, day of week, lags 1–3, and rolling means
over the previous 3 and 6 values. A lag is an earlier observation used as an
input. Every rolling window is shifted by one row, so the current target cannot
appear in its own feature calculation. This is important because target leakage
would create unrealistically good evaluation scores.

The first 80% of feature rows train the models and the last 20% test them. The
split remains chronological. A random split would mix future patterns into the
training data and would not represent the real forecasting task.

## Why XGBoost

The system trains one XGBoost regressor for each signal: CPU, RAM, and jobs.
XGBoost adds decision trees sequentially, with each new tree reducing errors
left by earlier trees. It is suitable here because the input is tabular, the
relationships are non-linear, training is fast, and the result is easier to
demonstrate than a deep neural network on only 720 rows.

Future prediction is recursive. Predicted hour 1 becomes part of the lag history
for hour 2. This permits multi-hour forecasting but also means errors may
accumulate, which is one reason the UI limits the horizon to 24 hours.

## Accuracy metrics

```text
MAE  = mean(|actual - predicted|)
RMSE = sqrt(mean((actual - predicted)^2))
```

Lower is better. MAE is easy to interpret as average absolute error. RMSE gives
larger errors more influence because errors are squared. Dashboard scores are
computed from unseen chronological hold-out rows; they are not hardcoded.

## From percentages to capacity

The demonstration assumes the workload percentages describe a reference
cluster with 16 vCPUs and 32 GB RAM:

```text
required vCPU = peak predicted CPU / 100 * 16
required RAM  = peak predicted RAM / 100 * 32
required jobs = peak predicted job count
```

The maximum of each signal across the selected horizon becomes a hard
constraint. Using peaks is conservative: the selected allocation can cover all
predicted hours even if CPU, RAM, and jobs peak at different times.

## Baseline and Particle Swarm Optimization

The baseline adds only medium VMs. It independently calculates how many are
needed for CPU, RAM, and jobs, rounds each value upward, and takes the largest
count. It is simple, feasible, and useful as a comparison.

A PSO particle is an integer vector such as `[small=1, medium=0, large=2]`.
Particles change velocity and position using:

- inertia: continue part of the previous movement;
- cognitive component: move toward the particle's personal best;
- social component: move toward the swarm's global best.

Positions are rounded to non-negative counts. An allocation that fails any CPU,
RAM, or job constraint receives a very large penalty. The baseline and
all-one-type candidates are seeded into the swarm. A fixed random seed makes
the classroom result repeatable. PSO is a heuristic and does not prove a global
optimum.

## Dual objective

```text
objective = cost_weight * (cost / baseline_cost)
          + energy_weight * (energy / baseline_energy)
energy_weight = 1 - cost_weight
```

Normalization prevents dollars and kWh from being combined as incomparable raw
units. Moving the cost slider demonstrates a tradeoff. A negative improvement
for one metric is possible when the weighted solution improves the other.

```text
cost = sum(VM count * demo hourly price * forecast hours)
energy kWh = total catalog watts * utilization factor * hours / 1000
improvement % = (baseline - optimized) / baseline * 100
```

The utilization factor is the busiest of CPU, RAM, and job-capacity fractions,
bounded from 20% to 100%. Energy is an estimate, not AWS hardware telemetry.

## Architecture and security decisions

- One Python/Streamlit process runs on one Ubuntu EC2 instance.
- Terraform creates the instance, encrypted EBS root disk, security group, IAM
  roles, private artifact bucket, state bucket support, OIDC provider, and budget.
- Port 8501 serves Streamlit. Port 22 is not opened.
- Administration and deployment use AWS Systems Manager.
- GitHub OIDC supplies short-lived deployment credentials; no AWS key is stored
  in GitHub.
- The application’s optional AWS feature is read-only and tag-restricted.
- The three safety tags are `Project=cloud-vm-optimizer`,
  `Owner=college-demo`, and `Environment=demo`.

## Honest limitations

- Synthetic data may not represent seasonal or production behavior.
- One chronological split is less rigorous than walk-forward validation.
- Demo prices, VM capacities, watts, and throughput are assumptions.
- Recursive forecasts can accumulate error.
- Peak-based capacity can over-provision compared with probabilistic planning.
- PSO is heuristic and stochastic, despite the fixed demonstration seed.
- Energy omits cooling, PUE, carbon intensity, shared hosts, and non-linear power.
- Scaling advice compares total VM counts and does not mutate AWS resources.

