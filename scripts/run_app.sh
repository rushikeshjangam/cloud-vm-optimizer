#!/usr/bin/env bash
set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$REPOSITORY_ROOT/.venv/bin/streamlit" run "$REPOSITORY_ROOT/streamlit_app.py" \
  --server.address 0.0.0.0 --server.port 8501

