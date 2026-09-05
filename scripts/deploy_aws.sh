#!/usr/bin/env bash
# Local fallback for the same S3 + SSM deployment performed by GitHub Actions.
set -euo pipefail

AWS_PROFILE_NAME="${AWS_PROFILE_NAME:-cloud-vm-optimizer}"
AWS_REGION_NAME="${AWS_REGION_NAME:-ap-south-1}"
AWS_CLI_PATH="${AWS_CLI_PATH:-aws}"
INSTANCE_ID="${INSTANCE_ID:?Set INSTANCE_ID to the Terraform output.}"
ARTIFACT_BUCKET="${ARTIFACT_BUCKET:?Set ARTIFACT_BUCKET to the Terraform output.}"

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REVISION="$(git -C "$REPOSITORY_ROOT" rev-parse --short HEAD)"
ARCHIVE_PATH="/tmp/cloud-vm-optimizer-${REVISION}.tar.gz"
OBJECT_KEY="deployments/${REVISION}.tar.gz"
PARAMETERS_PATH="/tmp/cloud-vm-optimizer-ssm-parameters.json"

tar \
  --exclude=.git \
  --exclude=.venv \
  --exclude=.terraform \
  --exclude=.pytest_cache \
  --exclude=__pycache__ \
  -czf "$ARCHIVE_PATH" -C "$REPOSITORY_ROOT" .

$AWS_CLI_PATH s3 cp "$ARCHIVE_PATH" "s3://${ARTIFACT_BUCKET}/${OBJECT_KEY}" \
  --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME"
PRESIGNED_URL="$($AWS_CLI_PATH s3 presign "s3://${ARTIFACT_BUCKET}/${OBJECT_KEY}" \
  --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" --expires-in 1800)"

jq -n --arg url "$PRESIGNED_URL" '{commands: [
  "set -eu",
  "cloud-init status --wait",
  "curl -fsSL --retry 5 --retry-delay 5 -o /tmp/cloud-vm-optimizer.tar.gz \"" + $url + "\"",
  "sudo mkdir -p /opt/cloud-vm-optimizer",
  "sudo tar -xzf /tmp/cloud-vm-optimizer.tar.gz -C /opt/cloud-vm-optimizer",
  "sudo chown -R ubuntu:ubuntu /opt/cloud-vm-optimizer",
  "sudo -u ubuntu bash /opt/cloud-vm-optimizer/deployment/setup_ec2.sh"
]}' > "$PARAMETERS_PATH"

COMMAND_ID="$($AWS_CLI_PATH ssm send-command \
  --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" \
  --instance-ids "$INSTANCE_ID" \
  --document-name AWS-RunShellScript \
  --comment "Deploy ${REVISION}" \
  --parameters "file://${PARAMETERS_PATH}" \
  --query Command.CommandId --output text)"

echo "SSM command: ${COMMAND_ID}"
set +e
$AWS_CLI_PATH ssm wait command-executed \
  --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" \
  --command-id "$COMMAND_ID" --instance-id "$INSTANCE_ID"
WAIT_STATUS=$?
set -e

$AWS_CLI_PATH ssm get-command-invocation \
  --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" \
  --command-id "$COMMAND_ID" --instance-id "$INSTANCE_ID" \
  --query '{Status:Status,Output:StandardOutputContent,Error:StandardErrorContent}' \
  --output json
exit "$WAIT_STATUS"
