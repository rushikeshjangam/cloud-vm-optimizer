# 1. Project Overview

## Problem

Cloud workloads change over time. Too few virtual machines can cause slow
service; too many waste money and estimated energy. This project predicts a
short future workload and recommends a feasible VM combination while balancing
two objectives: operational cost and estimated energy.

## End-to-end method

```text
hourly history → clean data → time/lag features → XGBoost forecast
→ peak horizon demand → baseline and PSO allocation
→ cost/energy comparison → scaling recommendation → Streamlit
```

The baseline is intentionally simple and creates medium VMs until all capacity
requirements are met. PSO searches mixed counts of small, medium, and large VMs.
Both must satisfy CPU, memory, and job capacity.

## Scope

This is a transparent academic simulation, not a production autoscaler. It uses
fictional prices and estimated energy. The AWS section is optional and read-only
in Milestone A. The core demonstration continues to work without AWS.

