# Statistical and economic evaluation

Five trained checkpoints are loaded and evaluated together with the naive
benchmark computed directly from prices, giving six architectures in total.

```shell
python -m src.scripts.run_statistical_evaluation --config configs/evaluation/statistical_tests.yaml
python -m src.scripts.run_economic_evaluation --config configs/evaluation/economic_returns.yaml
python -m src.scripts.run_reporting --config configs/reports/forecasting_report.yaml
```

Predictive accuracy uses hold-out test MSE, MAE, and MAPE. Statistical
robustness uses a 90% Model Confidence Set. The naive forecast is the previous
price. Economic evaluation takes a long position when the next-close forecast
exceeds the current close and a short position otherwise. The naive directional
signal is long when the preceding close exceeds the close two periods earlier,
and short otherwise.

The paired stationary block bootstrap compares compounded cumulative model
return with buy-and-hold using 10,000 replications, block length 10, and seed 42.
Positions are unleveraged. Transaction costs are not included; these results do
not describe a deployment-ready trading strategy.
