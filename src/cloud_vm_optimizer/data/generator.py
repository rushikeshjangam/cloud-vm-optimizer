"""Generate a repeatable workload with daily and weekly patterns."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def generate_demo_workload(
    periods: int = 24 * 30,
    seed: int = 42,
    start: str = "2025-01-01",
) -> pd.DataFrame:
    """Return realistic-looking hourly demo data; no values are fabricated later."""

    if periods < 48:
        raise ValueError("At least 48 hourly observations are required.")

    rng = np.random.default_rng(seed)
    timestamps = pd.date_range(start=start, periods=periods, freq="h")
    hour = timestamps.hour.to_numpy()
    day_of_week = timestamps.dayofweek.to_numpy()

    # Business-hours and weekly terms make the forecasting problem meaningful.
    daily = (np.sin(2 * np.pi * (hour - 7) / 24) + 1) / 2
    business_hours = ((hour >= 9) & (hour <= 18)).astype(float)
    weekday = (day_of_week < 5).astype(float)
    slow_trend = np.linspace(0, 5, periods)

    jobs = 35 + 72 * daily + 30 * business_hours * weekday + slow_trend
    jobs += rng.normal(0, 7, periods)
    jobs = np.clip(np.rint(jobs), 10, 190).astype(int)

    cpu = 18 + 0.39 * jobs + 6 * daily + rng.normal(0, 4, periods)
    ram = 25 + 0.29 * jobs + 4 * weekday + rng.normal(0, 3, periods)

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "cpu_usage": np.clip(cpu, 5, 96).round(2),
            "ram_usage": np.clip(ram, 8, 94).round(2),
            "job_count": jobs,
        }
    )


def save_demo_workload(path: Path, periods: int = 24 * 30) -> Path:
    """Create the checked-in style CSV used by the dashboard."""

    path.parent.mkdir(parents=True, exist_ok=True)
    generate_demo_workload(periods=periods).to_csv(path, index=False)
    return path


if __name__ == "__main__":
    repository_root = Path(__file__).resolve().parents[3]
    created = save_demo_workload(repository_root / "data" / "demo_workload.csv")
    print(f"Created {created}")

