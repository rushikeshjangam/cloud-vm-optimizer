# 11. Automated AWS Handover

This is the repeatable path for a fresh AWS account. It does not require Docker,
SSH keys, or permanent AWS keys in GitHub.

## What automation creates

- one Ubuntu 24.04 `t3.small` EC2 instance with an encrypted 12-GB gp3 disk;
- one security group exposing only Streamlit port 8501;
- an EC2 IAM role for Systems Manager and the private artifact bucket;
- one private S3 artifact bucket with 14-day cleanup;
- GitHub's OIDC provider and a repository/branch-restricted deployment role;
- a monthly USD 15 budget, with optional 80% email alerts;
- a separate versioned and encrypted S3 bucket for Terraform state.

Administration and deployment use AWS Systems Manager, so port 22 is not open.

## One-time setup on a new account

1. Install AWS CLI 2.32+ and Terraform 1.9+.
2. Authenticate using temporary browser credentials:

   ```bash
   aws login --profile cloud-vm-optimizer --region ap-south-1
   ```

3. Create or fork the GitHub repository and authenticate `gh`.
4. Run from the repository:

   ```bash
   AWS_PROFILE_NAME=cloud-vm-optimizer bash scripts/bootstrap_aws.sh
   ```

The script creates the state bucket, applies Terraform, and sets non-secret
GitHub repository variables. It does not store AWS access keys in GitHub.

## Normal student workflow

Students edit code in GitHub and merge or push to `main`. The Test workflow runs
pytest. The Deploy workflow obtains short-lived AWS credentials through OIDC,
uploads a ZIP to private S3, and tells the tagged instance to install/restart the
application through Systems Manager. The browser URL is a Terraform output.

## Budget alert

Copy `terraform.tfvars.example` to the ignored `terraform.tfvars`, replace the
email placeholder, and apply Terraform. AWS sends a confirmation email for the
budget subscription. Do not commit a student's email address.

## Cleanup after grading

Run `terraform destroy` from `infra/terraform`. After confirming that state is no
longer needed, manually empty and remove the state bucket printed by the
bootstrap script. Destruction is intentionally not available in GitHub Actions.

