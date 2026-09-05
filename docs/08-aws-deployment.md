# 8. AWS Deployment

## Cheap target architecture

Use one small Ubuntu 24.04 EC2 instance with a small root EBS volume. Do not add
RDS, NAT Gateway, load balancer, EKS, SageMaker, or OpenSearch. Confirm the chosen
instance and storage price in AWS before launch because pricing changes.

Required tags:

```text
Project=cloud-vm-optimizer
Owner=college-demo
Environment=demo
```

## Deployment outline

1. Create one budget-approved small instance in the chosen region.
2. Restrict SSH to the administrator's IP. Permit TCP 8501 only from the audience
   range needed for the demo; avoid `0.0.0.0/0` when practical.
3. Clone the repository to `/opt/cloud-vm-optimizer` and make it owned by `ubuntu`.
4. Run `sudo -u ubuntu bash deployment/setup_ec2.sh` from the repository.
5. Verify `sudo systemctl status cloud-vm-optimizer`.
6. Open `http://PUBLIC-IP:8501` and follow `docs/07-streamlit-demo.md`.

The setup creates a virtual environment, installs the Python package, registers
the included systemd service, and starts Streamlit on `0.0.0.0:8501`. It does
not create any AWS resource.

## Optional read-only EC2 inspection

Leave `AWS_DEMO_ENABLED=false` for Milestone A. A later least-privilege IAM role
can allow `ec2:DescribeInstances`; boto3 then discovers role credentials
automatically. Set the service environment to `true` only after role and tag
checks are reviewed. The code filters by all required tags and rechecks returned
tags. There are no start, stop, create, or terminate API calls.

Record the final URL and recovery details in `HANDOVER.md`. Configure an AWS
Budget before leaving the host running. Stop it outside rehearsals and demos.

