#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3 python3-venv unzip curl awscli
mkdir -p /opt/cloud-vm-optimizer
chown ubuntu:ubuntu /opt/cloud-vm-optimizer

# Ubuntu AWS images normally include the SSM agent as a snap. Keep this
# idempotent so a GitHub deployment can begin as soon as the instance registers.
if command -v snap >/dev/null 2>&1; then
  snap start amazon-ssm-agent || snap install amazon-ssm-agent --classic
fi
