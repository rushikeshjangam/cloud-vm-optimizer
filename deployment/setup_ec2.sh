#!/usr/bin/env bash
# Run on an Ubuntu 24.04 EC2 host after cloning the repository to /opt/cloud-vm-optimizer.
set -euo pipefail

APP_DIR="/opt/cloud-vm-optimizer"
if [[ ! -f "$APP_DIR/pyproject.toml" ]]; then
  echo "Expected the repository at $APP_DIR" >&2
  exit 1
fi

sudo apt-get update
sudo apt-get install -y python3 python3-venv
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/python" -m pip install --upgrade pip
"$APP_DIR/.venv/bin/python" -m pip install "$APP_DIR"

sudo install -m 0644 "$APP_DIR/deployment/cloud-vm-optimizer.service" \
  /etc/systemd/system/cloud-vm-optimizer.service
sudo systemctl daemon-reload
sudo systemctl enable --now cloud-vm-optimizer
sudo systemctl status cloud-vm-optimizer --no-pager

