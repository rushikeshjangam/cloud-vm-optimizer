# 2. Dataset

`data/demo_workload.csv` contains 720 hourly observations (30 days):

| Column | Meaning | Unit |
|---|---|---|
| `timestamp` | Observation time | hourly timestamp |
| `cpu_usage` | Aggregate CPU use | percent |
| `ram_usage` | Aggregate RAM use | percent |
| `job_count` | Jobs/requests in the hour | count |

The deterministic generator in `data/generator.py` combines a daily wave,
business-hour peak, weekday effect, small growth trend, and seeded random noise.
CPU and RAM partly depend on job count. This produces learnable patterns without
pretending the data came from a real company.

The loader checks required columns, parses numeric values and timestamps, rejects
duplicate timestamps, sorts time order, and requires at least 48 rows. Run
`python -m cloud_vm_optimizer.data.generator` to recreate a 30-day dataset.

For a future real dataset, retain the four column names, use a consistent hourly
interval, describe its source/license, and inspect missing values and outliers
before training.

