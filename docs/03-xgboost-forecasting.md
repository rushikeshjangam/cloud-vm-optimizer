# 3. XGBoost Forecasting

XGBoost builds many small decision trees sequentially. Each new tree focuses on
reducing errors left by earlier trees. It works well for tabular, non-linear
patterns and does not require the much larger dataset or complexity of a neural
network.

Three regressors predict CPU, RAM, and job count. Their inputs are:

- hour and day of week;
- lags 1, 2, and 3 for each signal;
- rolling means of the previous 3 and 6 values for each signal.

All rolling windows are shifted by one row. Therefore a target value is never
used to predict itself. The first 80% of feature rows train the model and the
last 20% test it, preserving time order. This is more honest for forecasting
than randomly mixing past and future rows.

Future prediction is recursive. After hour one is predicted, its values become
lag history for hour two. CPU and RAM are clipped to 0–100%, and jobs to zero or
above. Longer recursive horizons can accumulate error, which is why the UI caps
the demonstration at 24 hours.

MAE is the mean absolute error. RMSE is the square root of mean squared error and
penalizes large mistakes more strongly. Both dashboard values are computed from
actual hold-out predictions; they are not fixed display numbers.

