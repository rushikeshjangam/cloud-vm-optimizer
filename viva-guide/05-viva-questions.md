# 5. Viva Questions Students Must Prepare

Students should understand these answers and explain them naturally instead of
memorizing exact sentences.

## Problem, data, and design

**What does the project solve?** It predicts near-future cloud workload and
recommends enough simulated VM capacity while balancing demo cost and estimated
energy.

**Who benefits?** A cloud operator evaluating capacity decisions. This prototype
demonstrates the decision pipeline; it is not a production control plane.

**Why forecast before allocating?** Current utilization describes now. Capacity
must cover likely future demand, especially upcoming peaks.

**Why synthetic data?** It is reproducible, safe, free, and contains controlled
patterns. Its weakness is reduced external validity compared with real traces.

**Why three targets?** CPU alone can hide a RAM or throughput bottleneck. All
three constraints must be satisfied.

**Why 720 rows?** Thirty days of hourly observations are enough for a fast,
repeatable demonstration of daily and weekday patterns, though not production
seasonality.

**What validation does the loader perform?** Required columns, timestamps,
numeric values, uniqueness, ordering, and a minimum length.

## Forecasting

**Why XGBoost?** It handles structured non-linear data well, needs less data and
compute than deep learning, and trains quickly during a viva.

**What is boosting?** Trees are added sequentially so later trees reduce errors
made by the existing ensemble.

**What is a lag feature?** A previous signal value, such as CPU one hour earlier,
used to predict a later value.

**Why shift rolling means?** Without shifting, the target row could contribute
to its own feature, causing leakage.

**Why not random train/test split?** Forecasting must train on the past and test
on later data. Random mixing leaks temporal information.

**What is recursive forecasting?** Each newly predicted hour is fed back as lag
history for the next prediction.

**What is its disadvantage?** Earlier prediction errors can propagate and grow
across the horizon.

**MAE versus RMSE?** MAE expresses average absolute error. RMSE squares errors
and is more sensitive to large misses.

**What would improve evaluation?** More real data, seasonal coverage, a naive
baseline, walk-forward validation, and reported variability.

## Allocation and PSO

**What is the baseline?** The minimum count of medium-only VMs required to meet
CPU, RAM, and job demand.

**Why use a baseline?** Optimization improvement has meaning only relative to a
simple, reproducible feasible alternative.

**What is a particle?** One candidate integer allocation `[small, medium, large]`.

**What are personal and global best?** The best score one particle has found and
the best score found by the entire swarm.

**What do inertia, cognitive, and social terms do?** Preserve movement, pull a
particle toward its own best, and pull it toward the swarm’s best.

**How are constraints handled?** Insufficient CPU, RAM, or job capacity receives
a very large objective penalty.

**Why normalize objectives?** Raw dollars and kWh have different units and
scales. Division by baseline values makes their weighted contributions comparable.

**Do weights sum to one?** Yes. Energy weight is `1 - cost weight`.

**Does PSO always find the global optimum?** No. It is a heuristic. Seeding good
candidates and fixing randomness improves reliability and repeatability.

**Why can an improvement be negative?** A dual-objective solution may accept a
worse value for one metric to improve the weighted combined objective.

**Why use peak demand?** It ensures the allocation covers every predicted hour,
although it can be conservative.

**What does SCALE DOWN mean?** The recommended total is below the user-entered
current VM count. It does not stop an actual EC2 instance.

## Cost and energy

**Are prices live AWS prices?** No. They are fictional academic assumptions in
the CSV catalog.

**Is energy measured by AWS?** No. It is a transparent estimate based on catalog
watts, utilization, and duration.

**What is missing from the energy model?** Cooling/PUE, carbon intensity, shared
physical hosts, hardware differences, power-supply loss, and non-linear curves.

**Why still include energy?** It demonstrates sustainable-computing tradeoffs
while keeping the assumptions explicit and reproducible.

## AWS, DevOps, and security

**Why use only one EC2 instance?** It is enough to host the demonstration and
avoids the cost and complexity of unnecessary managed services.

**What does Terraform provide?** Declarative, repeatable, reviewable creation of
the instance, storage, network rule, roles, OIDC, artifact bucket, and budget.

**What is Terraform state?** A mapping between configuration and real resources.
It is stored in a private encrypted/versioned account-specific S3 bucket.

**Why GitHub OIDC?** GitHub exchanges an identity token for short-lived AWS role
credentials, so no permanent AWS key is saved as a secret.

**Why Systems Manager instead of SSH?** It supports controlled administration
without opening port 22 or distributing SSH keys.

**Why are tags important?** They identify ownership/cost and form a safety
boundary for the optional read-only AWS feature.

**Which inbound port is open?** TCP 8501 for Streamlit. SSH port 22 is closed.

**What happens on a push to main?** CI runs tests. Deployment assumes the OIDC
role, uploads a bundle to private S3, and sends an SSM install/restart command.

**What if GitHub or AWS is unavailable?** Run the same app locally. Forecasting
and PSO do not require AWS.

**Why might the URL change?** A normal auto-assigned public IPv4 address is
released on stop and a new one is usually assigned at start.

**Does the budget prevent charges?** No. It monitors spending and can notify;
students must stop or destroy resources themselves.

## Critical-thinking questions

**Why not LSTM?** The dataset is small and tabular; LSTM adds complexity without
demonstrated benefit. It could be compared later on a larger sequence dataset.

**Why not exact integer optimization?** It is a valid future comparison. PSO was
selected to demonstrate metaheuristic search and dual-objective behavior.

**How would this become production-ready?** Use real telemetry, robust feature
pipelines, walk-forward evaluation, uncertainty bounds, calibrated capacities,
exact pricing/carbon data, guarded approvals, observability, authentication,
HTTPS, rollback, and canary deployment.

**What is the strongest claim you can make?** On the included synthetic dataset,
the implemented pipeline produces evaluated forecasts and a feasible,
repeatable allocation recommendation under documented assumptions.

