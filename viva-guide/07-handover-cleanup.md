# 7. Team Handover, Cost Control, and Cleanup

## Handover checklist

- [ ] Team controls the GitHub repository; old personal remote is not `origin`.
- [ ] At least two trusted team members have appropriate repository access.
- [ ] AWS root MFA is enabled and root access keys do not exist.
- [ ] Daily administration uses a team-controlled non-root identity where possible.
- [ ] `aws sts get-caller-identity` shows the intended new AWS account.
- [ ] Root `HANDOVER.md` contains the current account, region, instance, URL, and repo.
- [ ] `terraform.tfvars` and `backend.hcl` are ignored and absent from GitHub.
- [ ] GitHub variables point to the new account’s role, bucket, instance, and region.
- [ ] CI and deploy workflows have been demonstrated, or the Actions blocker and
      local fallback have been documented.
- [ ] AWS Budget exists; optional alert email is owned by the team.
- [ ] One student has rehearsed recovery with Systems Manager.
- [ ] Offline demo and screenshots are available.

## Evidence for the report

Capture sanitized screenshots or outputs showing:

1. architecture/data-flow diagram;
2. historical workload and forecast graph;
3. chronological MAE/RMSE table;
4. baseline and PSO VM allocations;
5. cost and estimated-energy comparison;
6. scaling recommendation;
7. Terraform output/resource summary;
8. successful test and deployment workflow;
9. EC2 tags, security group port 8501/no port 22, and SSM online;
10. AWS Budget configuration.

Hide account email, billing address, payment data, tokens, role-session details,
presigned URLs, and any credential material.

## Cost-control routine

- Start the EC2 host only for setup, rehearsal, and presentation.
- Stop it from the EC2 console when finished.
- Review Billing/Cost Explorer and Budgets regularly.
- Keep one small host and its small EBS root volume.
- Do not add NAT Gateway, load balancer, RDS, EKS, SageMaker, OpenSearch, or
  Elastic IP without a documented need and cost review.
- A stopped instance avoids instance compute charges, but attached storage and
  some networking resources can still cost money.
- A normal public IP can change after stop/start; update the demo URL.

## Temporary stop versus permanent cleanup

Use **Stop** between rehearsals. Use Terraform destruction only after final
grading, report evidence, and repository backup are complete. Termination deletes
the EC2 root volume because Terraform sets `delete_on_termination = true`.

## Permanent cleanup after grading

First verify the identity and inspect Terraform’s plan:

```bash
aws sts get-caller-identity --profile cloud-vm-optimizer
eval "$(aws configure export-credentials \
  --profile cloud-vm-optimizer --format env)"
terraform -chdir=infra/terraform state list
terraform -chdir=infra/terraform plan -destroy
```

The artifact bucket uses `force_destroy = false`, so empty only the exact bucket
reported by Terraform before destruction. Bucket versioning means current and
noncurrent versions may need removal through the S3 console. Then run:

```bash
terraform -chdir=infra/terraform destroy
```

Do not approve until the plan contains only this project’s tagged resources.
The bootstrap-created Terraform state bucket is intentionally outside Terraform.
After destroy succeeds and the team no longer needs recovery/history, empty and
delete that exact account-specific state bucket through S3. This final deletion
is irreversible and must be performed by the account owner after checking the
bucket name and account ID twice.

Finally verify:

- no running or stopped project EC2 instance remains;
- no project EBS volume or Elastic IP remains;
- artifact and state buckets are removed when no longer required;
- project IAM roles, instance profile, security group, OIDC provider, and budget
  are removed by Terraform;
- Billing is checked again the following day.

Do not delete unrelated resources belonging to the account.
