# Architecture

## Runtime view

```text
Student's browser
       |
       v
Streamlit dashboard (single EC2 host, port 8501)
       |
       +-- data loader --> demo_workload.csv + vm_catalog.csv
       +-- feature engineering --> leak-safe lags and rolling means
       +-- XGBoost --> CPU, RAM, and job forecasts + MAE/RMSE
       +-- optimization service
              +-- medium-only baseline
              +-- discrete PSO
              +-- cost and estimated energy models
              +-- SCALE UP / SCALE DOWN / NO CHANGE
       +-- optional read-only EC2 service (off by default)
```

All application logic runs in one Python process. This is intentional: a
single-process design is easier to deploy cheaply, demonstrate, and explain in
a viva than microservices.

## Source responsibilities

```text
src/cloud_vm_optimizer/
├── domain/models.py                 shared dataclasses
├── data/generator.py                reproducible synthetic history
├── data/loader.py                   CSV validation
├── forecasting/features.py         temporal, lag, rolling features
├── forecasting/trainer.py          XGBoost and chronological split
├── forecasting/predictor.py        recursive future predictions
├── forecasting/metrics.py          MAE and RMSE
├── allocation/baseline.py          simple comparison allocator
├── allocation/cost.py              price × count × time
├── allocation/energy.py            estimated kWh model
├── optimization/pso.py             PSO search and constraints
├── services/optimization_service.py end-to-end orchestration
├── aws/safety.py                    mandatory project tags
├── aws/ec2_service.py               opt-in read-only EC2 inspection
└── ui/app.py                        Streamlit presentation
```

## Data flow and boundaries

Training and test rows remain time ordered. Every lag and rolling feature is
shifted, so the target row cannot leak into its own inputs. Future predictions
are recursive: the first predicted hour becomes history for the second.

Forecast percentages are converted to absolute demonstration demand using a
16-vCPU, 32-GB reference cluster. The peak CPU, RAM, and jobs over the horizon
form three hard allocation constraints. Both allocators must satisfy all three.

AWS is a boundary, not a dependency of the academic pipeline. In safe mode the
service returns without importing boto3 or making a network call.

