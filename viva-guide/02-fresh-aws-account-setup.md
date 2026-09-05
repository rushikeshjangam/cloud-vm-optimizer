# 2. Deploy from a Fresh AWS Account

This procedure creates a separate copy under the team's GitHub owner and a new
AWS stack. Commands assume Ubuntu or WSL and are run from the repository root.
Replace every value written in `UPPER_CASE`.

## Phase A — secure and prepare the accounts

1. Create/activate the AWS account and verify its payment method and phone.
2. Enable MFA on the AWS root user. Do not create root access keys.
3. Prefer an administrative IAM Identity Center user for normal work. For a
   short college setup, AWS CLI browser login also supports an authorized root,
   IAM, or federated console session and provides temporary credentials.
4. Create the team's GitHub repository. Keep it private if the project must not
   be public, and add every student who needs access as a collaborator.
5. Ensure GitHub Actions is enabled at account and repository level.

Official references: [AWS CLI browser login](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html),
[root-user best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html),
and [Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html).

## Phase B — install local tools

Required:

- Git;
- GitHub CLI (`gh`);
- AWS CLI v2.32 or newer (`aws login` requires this);
- Terraform 1.9 or newer;
- `jq`, `zip`, `curl`, and a browser.

On Ubuntu/WSL, install common helper packages:

```bash
sudo apt-get update
sudo apt-get install -y git jq zip unzip curl
```

Install AWS CLI, Terraform, and GitHub CLI from their official instructions,
then verify:

```bash
aws --version
terraform version
gh --version
git --version
jq --version
```

## Phase C — make the team's repository copy

If the team has access to the current repository, clone it, detach the old
remote, create a new private repository, and push the complete history:

```bash
git clone https://github.com/rushikeshjangam/cloud-vm-optimizer.git
cd cloud-vm-optimizer
git remote rename origin upstream
gh auth login
gh auth status
gh repo create NEW_GITHUB_OWNER/cloud-vm-optimizer --private --source=. --remote=origin --push
```

If the repository has already been transferred or forked to the team, clone its
new URL instead and do not create another repository. Confirm:

```bash
git remote -v
gh repo view NEW_GITHUB_OWNER/cloud-vm-optimizer
```

The value `NEW_GITHUB_OWNER` is case-sensitive for the Terraform OIDC trust.
Use the exact owner shown in the repository URL.

## Phase D — create local Terraform settings

The real `terraform.tfvars` is ignored by Git and must stay local:

```bash
cp infra/terraform/terraform.tfvars.example infra/terraform/terraform.tfvars
```

Edit it to contain the new team's values:

```hcl
github_owner       = "NEW_GITHUB_OWNER"
github_repository  = "cloud-vm-optimizer"
aws_region         = "ap-south-1"
instance_type      = "t3.small"
root_volume_gb     = 12
allowed_app_cidr   = "0.0.0.0/0"
monthly_budget_usd = 15
budget_alert_email = ""
```

For a classroom network with a stable public IP, replace `0.0.0.0/0` with
`CLASSROOM_PUBLIC_IP/32`. Public access is easier for a viva but exposes the
dashboard to the internet; stop the host after the session. Add an alert email
later by placing it only in the ignored file and confirming the AWS email.

Check that secrets and local Terraform data are ignored:

```bash
git check-ignore infra/terraform/terraform.tfvars
git check-ignore infra/terraform/backend.hcl
```

Both commands should print the paths.

## Phase E — authenticate without permanent AWS keys

Use a dedicated profile so any old default credentials remain separate:

```bash
aws login --profile cloud-vm-optimizer --region ap-south-1
aws sts get-caller-identity --profile cloud-vm-optimizer
```

If WSL cannot open the Windows browser, use:

```bash
aws login --remote --profile cloud-vm-optimizer --region ap-south-1
```

Before continuing, read the returned `Account` value aloud and confirm it is the
new account. Stop immediately if it is the old or suspended account. Never paste
the returned credentials or authentication URL into Git or documentation.

For direct Terraform commands in the current shell, export the profile's
short-lived credentials. Repeat this after opening a new shell or logging in
again; do not save the output in a file:

```bash
eval "$(aws configure export-credentials \
  --profile cloud-vm-optimizer --format env)"
export AWS_PROFILE=cloud-vm-optimizer
```

Authenticate GitHub too:

```bash
gh auth login
gh auth status
```

## Phase F — bootstrap infrastructure

Run the repository automation with the new owner and repository explicitly set:

```bash
AWS_PROFILE_NAME=cloud-vm-optimizer \
AWS_REGION_NAME=ap-south-1 \
GITHUB_OWNER_NAME=NEW_GITHUB_OWNER \
GITHUB_REPOSITORY_NAME=cloud-vm-optimizer \
bash scripts/bootstrap_aws.sh
```

The script:

1. reads the active AWS account ID;
2. creates a unique encrypted/versioned S3 Terraform-state bucket;
3. generates ignored `infra/terraform/backend.hcl`;
4. initializes and applies Terraform;
5. creates one Ubuntu `t3.small`, 12-GB encrypted gp3 disk, security group,
   instance IAM role, artifact bucket, GitHub OIDC role, and monthly budget;
6. writes `AWS_DEPLOY_ROLE_ARN`, `AWS_ARTIFACT_BUCKET`, `AWS_INSTANCE_ID`, and
   `AWS_REGION` as non-secret GitHub repository variables.

Expect several minutes. Do not interrupt during `terraform apply`. At completion,
save the printed application URL and run:

```bash
terraform -chdir=infra/terraform output
gh variable list --repo NEW_GITHUB_OWNER/cloud-vm-optimizer
```

## Phase G — deploy the application

First try the normal automated path:

```bash
git commit --allow-empty -m "Trigger first deployment"
git push origin main
gh run list --repo NEW_GITHUB_OWNER/cloud-vm-optimizer --limit 5
```

The Test workflow installs the project and runs pytest. The Deploy workflow
uses OIDC, uploads a private bundle to S3, and uses Systems Manager to install
and restart Streamlit. No AWS access key is stored in GitHub.

If GitHub shows `startup_failure` with zero jobs, inspect the Actions page for
an account billing/Actions restriction. This occurs before repository code runs.
Use the verified local fallback while resolving GitHub:

```bash
INSTANCE_ID=$(terraform -chdir=infra/terraform output -raw instance_id)
ARTIFACT_BUCKET=$(terraform -chdir=infra/terraform output -raw artifact_bucket)

AWS_PROFILE_NAME=cloud-vm-optimizer \
AWS_REGION_NAME=ap-south-1 \
INSTANCE_ID="$INSTANCE_ID" \
ARTIFACT_BUCKET="$ARTIFACT_BUCKET" \
bash scripts/deploy_aws.sh
```

## Phase H — verify and record

```bash
APP_URL=$(terraform -chdir=infra/terraform output -raw application_url)
curl --fail --show-error "$APP_URL/_stcore/health"
```

Expected output: `ok`. Open the application URL in a browser and complete one
forecast and optimization. Replace the old account, instance, region, repository,
and URL in root `HANDOVER.md`, then commit and push that documentation.

The public IPv4 address normally changes after an EC2 stop/start. After starting
the host again, obtain the new URL with `terraform output -raw application_url`
or the EC2 console and update the handover record.
