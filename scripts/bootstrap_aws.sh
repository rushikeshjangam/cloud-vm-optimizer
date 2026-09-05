#!/usr/bin/env bash
# One-time account bootstrap. After this, pushes to main deploy through GitHub OIDC.
set -euo pipefail

AWS_PROFILE_NAME="${AWS_PROFILE_NAME:-cloud-vm-optimizer}"
AWS_REGION_NAME="${AWS_REGION_NAME:-ap-south-1}"
GITHUB_OWNER_NAME="${GITHUB_OWNER_NAME:-rushikeshjangam}"
GITHUB_REPOSITORY_NAME="${GITHUB_REPOSITORY_NAME:-cloud-vm-optimizer}"
AWS_CLI_PATH="${AWS_CLI_PATH:-aws}"
TERRAFORM_PATH="${TERRAFORM_PATH:-terraform}"

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TERRAFORM_DIRECTORY="$REPOSITORY_ROOT/infra/terraform"

ACCOUNT_ID="$($AWS_CLI_PATH sts get-caller-identity \
  --profile "$AWS_PROFILE_NAME" --query Account --output text)"
STATE_BUCKET="cloud-vm-optimizer-${ACCOUNT_ID}-${AWS_REGION_NAME}-tfstate"

echo "Using AWS account ${ACCOUNT_ID}, region ${AWS_REGION_NAME}."

if ! $AWS_CLI_PATH s3api head-bucket \
  --profile "$AWS_PROFILE_NAME" --bucket "$STATE_BUCKET" 2>/dev/null; then
  $AWS_CLI_PATH s3api create-bucket \
    --profile "$AWS_PROFILE_NAME" \
    --region "$AWS_REGION_NAME" \
    --bucket "$STATE_BUCKET" \
    --create-bucket-configuration "LocationConstraint=${AWS_REGION_NAME}"
fi

$AWS_CLI_PATH s3api put-public-access-block \
  --profile "$AWS_PROFILE_NAME" \
  --bucket "$STATE_BUCKET" \
  --public-access-block-configuration \
  'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'
$AWS_CLI_PATH s3api put-bucket-versioning \
  --profile "$AWS_PROFILE_NAME" \
  --bucket "$STATE_BUCKET" \
  --versioning-configuration Status=Enabled
$AWS_CLI_PATH s3api put-bucket-encryption \
  --profile "$AWS_PROFILE_NAME" \
  --bucket "$STATE_BUCKET" \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
$AWS_CLI_PATH s3api put-bucket-tagging \
  --profile "$AWS_PROFILE_NAME" \
  --bucket "$STATE_BUCKET" \
  --tagging 'TagSet=[{Key=Project,Value=cloud-vm-optimizer},{Key=Owner,Value=college-demo},{Key=Environment,Value=demo},{Key=ManagedBy,Value=bootstrap-script}]'

printf 'bucket = "%s"\nkey = "demo/terraform.tfstate"\nregion = "%s"\nencrypt = true\n' \
  "$STATE_BUCKET" "$AWS_REGION_NAME" > "$TERRAFORM_DIRECTORY/backend.hcl"

export AWS_PROFILE="$AWS_PROFILE_NAME"
$TERRAFORM_PATH -chdir="$TERRAFORM_DIRECTORY" init \
  -reconfigure -backend-config=backend.hcl
$TERRAFORM_PATH -chdir="$TERRAFORM_DIRECTORY" apply \
  -auto-approve \
  -var="aws_region=${AWS_REGION_NAME}" \
  -var="github_owner=${GITHUB_OWNER_NAME}" \
  -var="github_repository=${GITHUB_REPOSITORY_NAME}"

ROLE_ARN="$($TERRAFORM_PATH -chdir="$TERRAFORM_DIRECTORY" output -raw github_deploy_role_arn)"
ARTIFACT_BUCKET="$($TERRAFORM_PATH -chdir="$TERRAFORM_DIRECTORY" output -raw artifact_bucket)"
INSTANCE_ID="$($TERRAFORM_PATH -chdir="$TERRAFORM_DIRECTORY" output -raw instance_id)"
APPLICATION_URL="$($TERRAFORM_PATH -chdir="$TERRAFORM_DIRECTORY" output -raw application_url)"
REPOSITORY_SLUG="${GITHUB_OWNER_NAME}/${GITHUB_REPOSITORY_NAME}"

gh variable set AWS_DEPLOY_ROLE_ARN --repo "$REPOSITORY_SLUG" --body "$ROLE_ARN"
gh variable set AWS_ARTIFACT_BUCKET --repo "$REPOSITORY_SLUG" --body "$ARTIFACT_BUCKET"
gh variable set AWS_INSTANCE_ID --repo "$REPOSITORY_SLUG" --body "$INSTANCE_ID"
gh variable set AWS_REGION --repo "$REPOSITORY_SLUG" --body "$AWS_REGION_NAME"

echo "Infrastructure ready: ${APPLICATION_URL}"
echo "Push to main or run the Deploy to AWS workflow to deploy the application."

