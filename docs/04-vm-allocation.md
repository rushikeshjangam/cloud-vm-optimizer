# 4. VM Allocation

The catalog has three generic VM types. Its prices and watts are demonstration
assumptions rather than live AWS specifications.

| VM | vCPU | RAM GB | USD/hour | Watts | Jobs/hour |
|---|---:|---:|---:|---:|---:|
| small | 2 | 4 | 0.06 | 50 | 25 |
| medium | 4 | 8 | 0.13 | 80 | 60 |
| large | 8 | 16 | 0.25 | 130 | 140 |

The forecast dataset describes a reference cluster of 16 vCPU and 32 GB:

```text
required vCPU = peak CPU percent / 100 × 16
required RAM  = peak RAM percent / 100 × 32
required jobs = peak predicted jobs
```

Using the peak of the selected horizon is conservative: the recommendation can
cover every predicted hour, even if different signals peak at different times.

The baseline uses only medium VMs. It calculates the count separately for CPU,
RAM, and jobs, rounds each upward, and uses the largest result. PSO may mix all
catalog types but is evaluated against the same three feasibility constraints.

