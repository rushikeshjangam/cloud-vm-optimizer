# 4. Viva-Day Runbook

## One day before

- Confirm the AWS account can sign in and billing has no restriction.
- Confirm the GitHub repository and Actions page are accessible.
- Start the tagged EC2 instance if it is stopped.
- Wait until EC2 shows `running`, both status checks pass, and Systems Manager
  shows the node online.
- Copy the current public IPv4 URL; it may have changed after start.
- Run the health check and one full browser rehearsal.
- Prepare a laptop-local fallback and screenshots of a successful result.
- Stop the instance after rehearsing, then start it early on viva day.

## Ten minutes before presentation

```bash
aws sts get-caller-identity --profile cloud-vm-optimizer
eval "$(aws configure export-credentials \
  --profile cloud-vm-optimizer --format env)"
terraform -chdir=infra/terraform output
```

Then verify:

1. application URL opens;
2. `/_stcore/health` returns `ok`;
3. horizon is 6 hours;
4. current VM count is 4;
5. cost weight is 0.50;
6. browser zoom makes charts readable;
7. no AWS credentials or private console tabs are projected.

## Suggested 7-minute presentation

### 0:00–0:45 — problem and scope

“Cloud workloads vary over time. Under-provisioning risks poor service, while
over-provisioning wastes money and estimated energy. Our system forecasts CPU,
RAM, and jobs, then recommends a feasible VM mix using a cost-energy tradeoff.
It is an academic decision-support simulation, not an automatic AWS scaler.”

### 0:45–1:30 — data and architecture

Show the historical charts. Explain that 720 synthetic hourly rows contain
daily, business-hour, weekday, trend, and noise patterns. Mention the single
Streamlit EC2 host and that computation remains independent of AWS APIs.

### 1:30–2:45 — forecasting

Select 6 hours and click **Run Forecast**. Explain time features, lags 1–3,
shifted rolling means 3/6, three XGBoost regressors, and the chronological 80/20
split. Point to the future curves and peak values.

### 2:45–3:30 — evaluation

Open the MAE/RMSE explanation. State that MAE is average absolute error and RMSE
penalizes larger misses. Emphasize that metrics come from unseen later rows.

### 3:30–5:00 — optimization

Click **Optimize VM Allocation** at 0.50/0.50. Compare the medium-only baseline
with the mixed PSO result. Explain particles, personal/global best, hard capacity
constraints, normalized dual objective, fixed seed, and lack of global-optimum
guarantee.

### 5:00–6:00 — cost, energy, and scaling

Show both comparison charts and the recommendation. Explain the cost and energy
formulas and clearly label all catalog prices/watts as assumptions. Change the
cost weight only if time permits, then rerun optimization and describe the
tradeoff.

### 6:00–7:00 — AWS safety and limitations

Show AWS demo mode disabled/read-only behavior. Explain Terraform, GitHub OIDC,
private S3 artifacts, Systems Manager, no SSH, mandatory tags, and no automatic
EC2 mutation. Close with synthetic-data and simplified-energy limitations plus
real data and walk-forward validation as future work.

## If the panel asks for a different scenario

- Increase horizon: discuss recursive error and conservative peak demand.
- Change current VM count: show why the action changes but optimized capacity
  is driven by forecast demand.
- Move the cost slider: rerun optimization; energy weight is the complement.
- Ask about a surprising result: confirm all constraints, then explain that a
  weighted heuristic may trade one metric for another.
- Ask for AWS instances: use only the optional tagged, read-only inspection; do
  not create resources live.

## Offline fallback

The academic pipeline requires no AWS credentials. On a prepared laptop:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
streamlit run streamlit_app.py
```

On Windows PowerShell, activation is `.venv\Scripts\Activate.ps1`. Open
`http://localhost:8501`. Explain honestly that AWS normally hosts the same app,
but the ML and optimization logic is deliberately portable.

## Immediately after the viva

In EC2, select the instance with all three project tags and choose **Instance
state → Stop instance**. Do not terminate it until grading and evidence backup
are complete. Remember that EBS and public IPv4-related charges may still apply.
