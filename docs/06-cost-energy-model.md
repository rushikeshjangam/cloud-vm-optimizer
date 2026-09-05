# 6. Cost and Energy Model

## Cost

For every selected VM type:

```text
cost = VM count × demo hourly price × execution hours
total cost = sum of costs for all VM types
```

Execution hours default to the forecast horizon. Prices are explicitly labeled
**Demo pricing assumptions**. They are not queried from AWS and must not be
presented as current AWS prices.

## Estimated energy

First calculate the fraction used for CPU, RAM, and jobs. The busiest-resource
fraction becomes the utilization factor, bounded between 20% (idle-power
assumption) and 100%.

```text
energy kWh = total catalog watts × utilization factor × hours / 1000
```

This makes the model simple, repeatable, and explainable. It is not a measurement
of a physical AWS server. Real facilities have shared hosts, cooling overhead,
power-supply loss, CPU power curves, and changing carbon intensity that are not
represented here.

Improvement uses:

```text
(baseline value - optimized value) / baseline value × 100
```

A negative improvement honestly means the weighted PSO choice made that metric
worse to improve the other objective.

