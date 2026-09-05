# Project Plan

## Milestone A — working vertical MVP (complete)

- [x] Modular Python 3.12 package and deterministic demo dataset
- [x] Hour/day, lag 1–3, and shifted rolling mean 3/6 features
- [x] XGBoost models for CPU, RAM, and jobs
- [x] Chronological hold-out MAE and RMSE
- [x] Medium-only baseline allocation
- [x] Handwritten discrete PSO with cost/energy weights and hard constraints
- [x] Cost, estimated energy, improvement, and scaling calculations
- [x] Streamlit click-through dashboard and viva explanations
- [x] Disabled-by-default, read-only AWS service boundary
- [x] Unit and end-to-end tests
- [x] Single-EC2 setup assets and student documentation

## Milestone B — controlled AWS demonstration (complete with Actions caveat)

- [x] Add reproducible Terraform for a budget-approved small EC2 host
- [x] Apply `Project=cloud-vm-optimizer`, `Owner=college-demo`, and
  `Environment=demo` tags
- [x] Define EC2 SSM/artifact permissions and a branch-restricted GitHub OIDC role
- [x] Add automated tests and application deployment with GitHub Actions
- [x] Add a repeatable fresh-account bootstrap and Terraform state protection
- [x] Deploy and record the actual URL and region in `HANDOVER.md`
- [x] Verify security-group access to port 8501 from the intended audience
- [ ] Add start/stop only if the team still needs it, with tag checks and explicit UI confirmation

The public health endpoint was verified after deployment. GitHub Actions is
fully configured but GitHub currently returns `startup_failure` before a runner
job starts; the equivalent S3 + Systems Manager deployment was verified locally.

## Milestone C — evaluation and final report (future work)

- [ ] Compare forecast models and horizons on a larger or public dataset
- [ ] Run repeated optimizer trials and document convergence
- [ ] Add exportable result tables/plots if required by the college report
- [ ] Perform a rehearsal using the exact AWS URL and offline fallback

Out of scope until explicitly approved: ABC, Whale Optimization, MDVMA,
CloudSim, Power BI, RDS, EKS, SageMaker, OpenSearch, unrestricted EC2 creation,
and production-grade autoscaling.
