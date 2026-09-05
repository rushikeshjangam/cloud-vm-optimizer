# Handover Guide for Ayush and Team

This page is the operational checklist. Replace bracketed placeholders only
after Milestone B deployment.

## Details to record after deployment

- Application URL: `http://[EC2-PUBLIC-IP]:8501`
- AWS region: `[for example, ap-south-1]`
- EC2 instance ID/name: `[record one tagged demo host]`
- Repository URL: `[GitHub URL]`

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

Connect using EC2 Instance Connect or SSH and run:

```bash
sudo systemctl status cloud-vm-optimizer
sudo systemctl restart cloud-vm-optimizer
sudo journalctl -u cloud-vm-optimizer -n 100 --no-pager
```

Confirm the instance security group permits inbound TCP 8501 only from the
required source range. Confirm the public IP has not changed after a stop/start.
Application logs are in the systemd journal shown above.

If AWS or the network is unavailable during the viva, run the same repository
on a prepared laptop and open `http://localhost:8501`; the core demo needs no AWS API.

## Avoiding charges

- Stop the host whenever it is not being demonstrated.
- Keep only one small, budget-approved host and its small root EBS volume.
- Review AWS Billing and Cost Explorer after deployment.
- Do not add NAT Gateway, load balancer, RDS, EKS, SageMaker, or extra instances.
- Set a billing budget/alarm in the console before the first long-running demo.

## Complete cleanup after grading

Only the account owner should do this after backing up the repository and results:

1. Verify the exact resource carries all three project tags.
2. Terminate the one demo EC2 instance in the AWS Console.
3. Delete its unattached project EBS volume only after verifying it is no longer needed.
4. Release a project Elastic IP, if one was deliberately allocated.
5. Remove project security groups and IAM role/policy after dependencies are gone.
6. Check Billing/Cost Explorer again the following day.

These cleanup steps are manual by design; the application contains no terminate action.

