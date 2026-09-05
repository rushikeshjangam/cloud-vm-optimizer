"""Stable Streamlit entry point that also works before editable installation."""

from __future__ import annotations

import sys
from pathlib import Path

SOURCE_DIRECTORY = Path(__file__).resolve().parent / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from cloud_vm_optimizer.ui.app import main


main()

