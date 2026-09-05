# Viva and Fresh-Account Deployment Guide

This folder is the complete student handover for deploying and presenting the
Cloud VM Optimizer. Start here instead of reading the repository in file order.

## Recommended reading order

1. [Project understanding](01-project-understanding.md) — problem, solution,
   data flow, algorithms, formulas, scope, and limitations.
2. [Fresh AWS account setup](02-fresh-aws-account-setup.md) — exact one-time
   setup using a new AWS account and a new GitHub owner.
3. [What to change](03-what-to-change.md) — every account-specific value and
   repository file students may need to update.
4. [Viva-day runbook](04-viva-day-runbook.md) — preparation, a 7-minute demo
   script, offline fallback, and shutdown.
5. [Questions and answers](05-viva-questions.md) — technical questions students
   should be able to answer in their own words.
6. [Troubleshooting and recovery](06-troubleshooting.md) — exact checks for AWS,
   Terraform, GitHub Actions, SSM, Streamlit, and changing public IPs.
7. [Handover and cleanup](07-handover-cleanup.md) — ownership transfer, cost
   controls, evidence to retain, and safe destruction after grading.

## What students must not do

- Never commit AWS passwords, access keys, secret keys, session tokens, email
  addresses, `.env`, `terraform.tfvars`, `backend.hcl`, or Terraform state.
- Never claim the demo VM prices are current AWS prices.
- Never claim the energy result is measured physical AWS energy.
- Never say the optimizer automatically creates, terminates, or resizes EC2.
- Never run `terraform destroy` before verifying the active AWS account and
  backing up the required evidence.

The existing deployment values in the root `HANDOVER.md` belong to the current
demo account. A new team must replace them after deploying its own stack.

