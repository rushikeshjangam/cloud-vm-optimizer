# 7. Streamlit Demo

## Presentation script

1. Open the browser URL and read the project overview.
2. Show daily/weekly patterns in historical CPU, RAM, and jobs.
3. Keep the six-hour horizon and four current VMs.
4. Click **Run Forecast** and wait for XGBoost training.
5. Explain peak predictions, then open the MAE/RMSE explanation.
6. Keep cost and energy weights at 0.50 each.
7. Click **Optimize VM Allocation**.
8. Compare baseline and PSO allocation tables and charts.
9. Explain the scale action compares current count with recommended count.
10. Finish at AWS Demonstration and emphasize that disabled mode makes the
    academic demo independent of AWS availability.

Changing the cost slider demonstrates a tradeoff: energy automatically receives
the remaining weight. If an improvement is negative, explain that optimizing two
objectives can trade one metric for the other.

## Browser behavior

Forecast and optimization results remain in Streamlit session state while the
page reruns. Running a new forecast clears the prior optimization so mismatched
results are not displayed.

