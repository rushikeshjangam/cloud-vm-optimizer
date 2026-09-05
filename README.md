# Cloud Resource Usage Forecasting and Dual-Objective VM Allocation System

An AWS-first, browser-first final-year B.Tech CSE demonstration. It forecasts
short-term CPU, RAM, and job demand with XGBoost, compares a simple baseline VM
allocation with Particle Swarm Optimization (PSO), and recommends whether to
scale up, scale down, or make no change.

Milestone A is complete. The application runs entirely from built-in demo data;
AWS integration is read-only, optional, and disabled by default.

## Open the dashboard locally

Python 3.12 or newer is required only for development. The final student
handover is designed around an EC2-hosted browser URL.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
streamlit run streamlit_app.py
```

Open <http://localhost:8501>. No AWS credentials are needed.

## Demo flow

1. Review the built-in historical workload.
2. Choose a 1–24 hour horizon and click **Run Forecast**.
3. Inspect peak demand and real chronological hold-out MAE/RMSE.
4. Choose the cost weight; the energy weight is its complement.
5. Click **Optimize VM Allocation**.
6. Compare the baseline and PSO mix, improvements, and scaling recommendation.
7. Show that **AWS demo mode disabled** keeps the presentation safe offline.

## Important assumptions

- `data/vm_catalog.csv` contains fictional **demo pricing assumptions**, not
  current AWS prices.
- CPU/RAM percentages describe a 16-vCPU, 32-GB demonstration cluster.
- Energy is an estimate from catalog watts, utilization, and time; AWS does not
  expose exact physical-server energy for this app.
- Forecast metrics are calculated from an 80/20 chronological split.
- Allocation uses the maximum predicted demand within the selected horizon.
- The optimizer recommends a plan; it does not automatically scale EC2.

## Commands

```bash
pytest
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
python -m cloud_vm_optimizer.data.generator
```

For the single-EC2 path, see [AWS deployment](docs/08-aws-deployment.md) and
[handover instructions](HANDOVER.md). Architecture and progress are recorded in
[ARCHITECTURE.md](ARCHITECTURE.md) and [PROJECT_PLAN.md](PROJECT_PLAN.md).

For reproducible Terraform + GitHub Actions deployment into a fresh student
account, see [Automated AWS handover](docs/11-automated-aws-handover.md).

## Safety and cost controls

- One small EC2 host; no RDS, NAT Gateway, load balancer, EKS, or SageMaker.
- `AWS_DEMO_ENABLED=false` by default.
- Standard boto3/IAM role credential discovery; credentials are never hardcoded.
- EC2 inspection requires `Project`, `Owner`, and `Environment` tags.
- No EC2 create, terminate, or automatic scale operation exists in Milestone A.
