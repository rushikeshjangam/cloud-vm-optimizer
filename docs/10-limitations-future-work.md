# 10. Limitations and Future Work

## Current limitations

- The workload is synthetic and covers only 30 days.
- Generic VM capacities, job throughput, prices, and watts are assumptions.
- A fixed 16-vCPU/32-GB reference cluster converts percentages to demand.
- The energy formula omits cooling, carbon intensity, shared hardware, and
  non-linear idle/load power curves.
- Recursive forecasts can accumulate error over longer horizons.
- One train/test split does not describe variation across seasons or datasets.
- PSO is stochastic and heuristic, although a seed makes this demo repeatable.
- Current VM count has no per-type state; scale advice compares total counts.
- AWS mode is read-only and has not been deployed or account-tested in Milestone A.

## Sensible future work

1. Evaluate an openly licensed real workload dataset and document provenance.
2. Add walk-forward validation and compare XGBoost against a naive last-value model.
3. Calibrate reference capacity and job throughput from measured experiments.
4. Run PSO across several seeds and graph convergence and variability.
5. Add a carbon-intensity estimate clearly separated from physical energy.
6. Deploy one tagged EC2 host and validate least-privilege read-only IAM.
7. Add guarded start/stop only if needed, requiring exact tags and UI confirmation.

Complex algorithms or AWS services should be added only when they answer a clear
academic question and remain within the project budget.

