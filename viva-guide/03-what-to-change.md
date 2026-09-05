# 3. Exactly What a New Team Must Change

## Required changes

| Place | Old/example value | New value | Commit it? |
|---|---|---|---|
| Git remote `origin` | current owner's repository | team's repository URL | Git config only |
| `infra/terraform/terraform.tfvars` | example owner/settings | exact new owner, repo, region, budget, CIDR | No |
| Bootstrap environment | `rushikeshjangam` defaults | exact new GitHub owner/repository | No |
| `HANDOVER.md` | current account URL/ID | new URL, account, instance, region, repo | Yes, but no secrets |
| GitHub collaborators | current owner | Ayush/team members | GitHub setting |
| Budget alert | blank | team-controlled email, if wanted | No |

Do not edit `.github/workflows/deploy.yml` merely to change accounts. Terraform
creates an OIDC trust for the supplied `github_owner`, `github_repository`, and
the `main` branch; the bootstrap script sets the matching GitHub variables.

## Values that normally remain unchanged

- `project_name = "cloud-vm-optimizer"`
- `environment = "demo"`
- `owner_tag = "college-demo"`
- port `8501`
- `t3.small` and 12-GB gp3 unless the team accepts a different cost
- `AWS_DEMO_ENABLED=false`
- branch `main`
- required project tags

Changing the repository name, owner, or deployment branch changes the GitHub
OIDC subject. Reapply Terraform after such a change. A different branch also
requires a deliberate edit to the trust condition in `infra/terraform/main.tf`
and the workflow trigger.

## Changing the region

Use one region consistently in all four places:

1. `aws_region` in `terraform.tfvars`;
2. `AWS_REGION_NAME` when bootstrapping;
3. the AWS CLI login command;
4. the EC2 console region selector during the viva.

The default VPC must exist in the selected region. If it was deleted, Terraform
cannot use `data.aws_vpc.default`; restore a default VPC or deliberately extend
the Terraform to create a VPC and subnets.

## Changing who can open the dashboard

`allowed_app_cidr = "0.0.0.0/0"` permits all IPv4 sources to reach port 8501.
For a single known network, use its public IP with `/32`, then apply:

```bash
eval "$(aws configure export-credentials \
  --profile cloud-vm-optimizer --format env)"
terraform -chdir=infra/terraform apply
```

Do not open port 22. Systems Manager handles administration without SSH keys.

## Changing budget or adding email

Set `monthly_budget_usd` and optional `budget_alert_email` only in the ignored
`terraform.tfvars`, then apply Terraform. AWS Budgets warns about threshold
crossing; it does not automatically stop resources. Email subscriptions may
require confirmation.

## Changing the dataset

For real or alternative data, retain these exact columns:

```text
timestamp,cpu_usage,ram_usage,job_count
```

Use hourly, increasing, unique timestamps; numeric CPU/RAM percentages; numeric
job counts; and at least 48 rows. Document the source and license, handle missing
values/outliers, rerun tests, and never present synthetic results as real data.

If VM assumptions change, edit `data/vm_catalog.csv` and explain the new source.
The application currently expects the small, medium, and large types represented
by that catalog.

## Files students should understand, not casually edit

- `src/.../forecasting/`: feature engineering, training, recursive prediction.
- `src/.../optimization/pso.py`: particle search, objective, penalty, seed.
- `src/.../services/optimization_service.py`: forecast-to-demand conversion.
- `infra/terraform/main.tf`: AWS resources and least-privilege roles.
- `.github/workflows/`: test and deployment automation.
- `deployment/setup_ec2.sh`: server installation and service restart.

## Pre-push safety check

```bash
git status --short
git diff --check
git grep -n "AKIA"
git check-ignore infra/terraform/terraform.tfvars infra/terraform/backend.hcl
terraform -chdir=infra/terraform fmt -check
terraform -chdir=infra/terraform validate
python -m pytest
```

`git grep -n "AKIA"` should produce no output. Review every staged file before
pushing. Do not add ignored files with `git add -f`.
