"""Validated loaders for the two small built-in CSV files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from cloud_vm_optimizer.data.generator import generate_demo_workload
from cloud_vm_optimizer.domain.models import VMType

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_WORKLOAD_PATH = PROJECT_ROOT / "data" / "demo_workload.csv"
DEFAULT_CATALOG_PATH = PROJECT_ROOT / "data" / "vm_catalog.csv"
WORKLOAD_COLUMNS = ["timestamp", "cpu_usage", "ram_usage", "job_count"]


def load_workload(path: Path = DEFAULT_WORKLOAD_PATH) -> pd.DataFrame:
    """Load and validate workload history, falling back to deterministic demo data."""

    frame = pd.read_csv(path) if path.exists() else generate_demo_workload()
    missing = set(WORKLOAD_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Workload dataset is missing columns: {sorted(missing)}")

    frame = frame[WORKLOAD_COLUMNS].copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="raise")
    for column in WORKLOAD_COLUMNS[1:]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    if frame["timestamp"].duplicated().any():
        raise ValueError("Workload timestamps must be unique.")
    if len(frame) < 48:
        raise ValueError("Workload dataset must contain at least 48 rows.")
    return frame.sort_values("timestamp").reset_index(drop=True)


def load_vm_catalog(path: Path = DEFAULT_CATALOG_PATH) -> list[VMType]:
    """Load the documented fictional VM catalog."""

    frame = pd.read_csv(path)
    required = {
        "name",
        "vcpus",
        "memory_gb",
        "hourly_cost",
        "power_watts",
        "job_capacity",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"VM catalog is missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("VM catalog cannot be empty.")

    catalog = [VMType(**row) for row in frame[list(required)].to_dict("records")]
    for vm in catalog:
        values = (vm.vcpus, vm.memory_gb, vm.hourly_cost, vm.power_watts, vm.job_capacity)
        if any(value <= 0 for value in values):
            raise ValueError(f"All capacities and prices must be positive for {vm.name}.")
    return catalog

