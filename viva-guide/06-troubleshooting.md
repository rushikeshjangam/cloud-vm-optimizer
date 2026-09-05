# 6. Troubleshooting and Recovery

Work from the top of each section and stop when the failed layer is identified.

## Confirm the active identities first

```bash
aws sts get-caller-identity --profile cloud-vm-optimizer
gh auth status
git remote -v
```

If the AWS account or GitHub owner is wrong, do not apply or deploy. Log in to
the correct account/profile and pass the correct bootstrap environment values.

## `aws login` is unknown

AWS CLI is older than v2.32 or a system copy appears earlier in `PATH`.

```bash
type -a aws
aws --version
```

Install/update the official AWS CLI v2, then open a new shell. With WSL browser
issues, use `aws login --remote`.

## Terraform cannot find the default VPC

The selected region has no default VPC. In the EC2/VPC console, confirm the
region. Restore a default VPC, choose a region with one, or extend Terraform to
create a dedicated VPC. Do not randomly paste subnet IDs into committed code.

## Terraform backend/profile authentication errors

Rerun `aws login`, verify `sts get-caller-identity`, and use
`scripts/bootstrap_aws.sh`. It exports short-lived login credentials into the
Terraform process because older Terraform/AWS provider combinations may not
directly understand the CLI login cache.

## GitHub OIDC `Not authorized to perform sts:AssumeRoleWithWebIdentity`

Compare all of these exactly:

- GitHub repository owner and name;
- branch `main`;
- Terraform `github_owner` and `github_repository`;
- repository variable `AWS_DEPLOY_ROLE_ARN`;
- AWS account containing that role.

Correct `terraform.tfvars`, reapply Terraform, and rerun bootstrap so GitHub
variables are refreshed. OIDC matching is case-sensitive.

## GitHub Actions `startup_failure` with zero jobs

This happens before workflow commands execute. Open the repository **Actions**
page and the GitHub account billing/settings pages. Check whether Actions is
disabled, spending/payment is restricted, or the account has an unresolved
restriction. Use `scripts/deploy_aws.sh` as the temporary verified fallback.

## SSM command cannot find the instance or remains pending

Confirm region, instance ID, state, and managed-node status:

```bash
aws ec2 describe-instances --profile cloud-vm-optimizer --region ap-south-1 \
  --instance-ids INSTANCE_ID \
  --query 'Reservations[0].Instances[0].[State.Name,PublicIpAddress,IamInstanceProfile.Arn]'

aws ssm describe-instance-information --profile cloud-vm-optimizer \
  --region ap-south-1 \
  --filters Key=InstanceIds,Values=INSTANCE_ID
```

Wait a few minutes after creation/start. Verify the instance profile includes
`AmazonSSMManagedInstanceCore` and outbound HTTPS is allowed.

## Application URL times out

1. Confirm instance is `running` and status checks passed.
2. Obtain its current public IP; do not reuse a pre-stop address.
3. Confirm the security group allows TCP 8501 from the viewer’s public IP.
4. Confirm the service through Systems Manager:

```bash
sudo systemctl status cloud-vm-optimizer --no-pager
sudo journalctl -u cloud-vm-optimizer -n 100 --no-pager
sudo systemctl restart cloud-vm-optimizer
```

Then test `http://CURRENT_PUBLIC_IP:8501/_stcore/health`.

## Service fails after deployment

Look at the journal first. Common causes are incomplete downloads, full disk,
Python package errors, or a bundle extracted into the wrong path.

```bash
df -h
ls -la /opt/cloud-vm-optimizer
/opt/cloud-vm-optimizer/.venv/bin/python --version
sudo journalctl -u cloud-vm-optimizer -n 200 --no-pager
```

Redeploy using the workflow or local fallback. Do not manually change random
files on the server without committing the same fix to Git, or the next deploy
will overwrite the repair.

## Forecast or optimization button appears stale

Streamlit keeps results in session state. Changing horizon invalidates the old
forecast; changing VM count/weights invalidates the comparison. Click the
corresponding button again. Refresh the page if the session itself is confused.

## Local tests fail because a virtual environment moved machines

Virtual environments are not portable. Delete only the repository-local `.venv`
after confirming its exact path, then recreate it on the current computer:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
python -m pytest
```

On Windows use `py -3.12 -m venv .venv` and `.venv\Scripts\Activate.ps1`.

## Escalation evidence to capture

When asking for help, provide the command, sanitized error, UTC time, Git commit,
AWS region, instance ID, and workflow URL. Never include a password, token,
credential file, presigned S3 URL, or complete authentication URL.

