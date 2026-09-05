# Handover Guide for Ayush and Team

This page is the operational checklist for the deployed demo environment.

## Details to record after deployment

- Application URL: `http://13.201.225.52:8501`
- AWS region: `ap-south-1`
- EC2 instance ID: `i-08ac723fd5f598d75`
- Repository URL: `https://github.com/rushikeshjangam/cloud-vm-optimizer`
- AWS account: `363434190963`

Never put an AWS password, access key, secret key, or token in this file.

## Start and stop the host in the AWS Console

1. Sign in to the AWS Console and open **EC2 → Instances** in the recorded region.
2. Find the single host tagged `Project=cloud-vm-optimizer`.
3. To present, select it and choose **Instance state → Start instance**.
4. Wait until the state is `Running` and both status checks pass.
5. Copy its current public IPv4 address into the URL above and open it.
6. After the presentation, choose **Instance state → Stop instance**.

Stopping avoids compute charges, but EBS storage can still incur a small charge.
Do not choose **Terminate** during ordinary operation.

## Five-minute college demo

1. Open the application URL and point out safe AWS demo mode.
2. Show seven days of historical CPU, RAM, and job patterns.
3. Select a six-hour horizon and click **Run Forecast**.
4. Explain lag features and the real hold-out MAE/RMSE table.
5. Leave cost/energy at 0.50/0.50 and click **Optimize VM Allocation**.
6. Compare baseline and PSO counts, cost, and estimated energy.
7. Explain the final scaling recommendation and its simulation boundary.

## If the application is down

Use AWS Systems Manager Run Command or Session Manager and run:

```bash
sudo systemctl status cloud-vm-optimizer
sudo systemctl restart cloud-vm-optimizer
sudo journalctl -u cloud-vm-optimizer -n 100 --no-pager
```

The Terraform security group permits inbound TCP 8501 and deliberately does not
open SSH. Confirm the public IP has not changed after a stop/start.
Application logs are in the systemd journal shown above.

## Redeploying

Pushes to `main` are configured to deploy through GitHub Actions using OIDC,
S3, and Systems Manager. If GitHub reports `startup_failure` before creating any
job, resolve the repository/account Actions restriction first. Until then, an
account owner with an active AWS CLI login can run `scripts/deploy_aws.sh` with
the instance ID and artifact bucket environment variables.

If AWS or the network is unavailable during the viva, run the same repository
on a prepared laptop and open `http://localhost:8501`; the core demo needs no AWS API.

## Avoiding charges

- Stop the host whenever it is not being demonstrated.
- Keep only one small, budget-approved host and its small root EBS volume.
- Review AWS Billing and Cost Explorer after deployment.
- Do not add NAT Gateway, load balancer, RDS, EKS, SageMaker, or extra instances.
- A USD 15 monthly AWS Budget is configured. Email notification is intentionally
  omitted for now and should be added during team handover.

## Complete cleanup after grading

Only the account owner should do this after backing up the repository and results:

1. Verify the exact resource carries all three project tags.
2. Terminate the one demo EC2 instance in the AWS Console.
3. Delete its unattached project EBS volume only after verifying it is no longer needed.
4. Release a project Elastic IP, if one was deliberately allocated.
5. Remove project security groups and IAM role/policy after dependencies are gone.
6. Check Billing/Cost Explorer again the following day.

These cleanup steps are manual by design; the application contains no terminate action.
