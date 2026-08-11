# Reproduction workflow

All commands run from the repository root. Complete reproduction requires the
protected inputs described in [data acquisition](data-acquisition.md).

## Canonical order

```shell
python -m src.scripts.run_price_pipeline --config configs/datasets/prices/soybean_prices.yaml
python -m src.scripts.run_price_correlation --config configs/datasets/prices/soybean_prices.yaml
python -m src.scripts.run_news_pipeline --config configs/datasets/news/soybean_news.yaml
python -m src.scripts.run_sentiment_dataset --config configs/datasets/sentiment/soybean_sentiment.yaml
python -m src.scripts.run_llm_optimization --config configs/optimization/llm_sentiment.yaml --profile tanh
python -m src.scripts.run_llm_optimization --config configs/optimization/llm_sentiment.yaml --profile probability
python -m src.scripts.run_sentiment_training --config configs/llm/sentiment_training.yaml --profile tanh
python -m src.scripts.run_sentiment_training --config configs/llm/sentiment_training.yaml --profile probability
python -m src.scripts.run_sentiment_inference --config configs/datasets/sentiment/soybean_daily_sentiment.yaml --mode tanh
python -m src.scripts.run_sentiment_inference --config configs/datasets/sentiment/soybean_daily_sentiment.yaml --mode probability
python -m src.scripts.run_forecasting_dataset --config configs/datasets/forecasting/soybean_forecasting.yaml
python -m src.scripts.run_lstm_optimization --config configs/optimization/lstm_bayesian.yaml --profile price
python -m src.scripts.run_lstm_optimization --config configs/optimization/lstm_bayesian.yaml --profile tanh
python -m src.scripts.run_lstm_optimization --config configs/optimization/lstm_bayesian.yaml --profile probability
python -m src.scripts.run_forecasting_training --config configs/lstm/lstm_baseline.yaml
python -m src.scripts.run_forecasting_training --config configs/lstm/lstm_llm_tanh.yaml
python -m src.scripts.run_forecasting_training --config configs/lstm/lstm_llm_prob.yaml
python -m src.scripts.run_joint_forecasting_training --config configs/lstm/lstm_llm_tanh_e2e.yaml
python -m src.scripts.run_joint_forecasting_training --config configs/lstm/lstm_llm_prob_e2e.yaml
python -m src.scripts.run_statistical_evaluation --config configs/evaluation/statistical_tests.yaml
python -m src.scripts.run_economic_evaluation --config configs/evaluation/economic_returns.yaml
python -m src.scripts.run_reporting --config configs/reports/forecasting_report.yaml
```

Each LLM representation uses 300 TPE trials, at most 20 epochs per trial, and
early stopping patience 3. Tanh minimizes MSE and Probability uses
cross-entropy. The selected base models were
`neuralmind/bert-base-portuguese-cased` (Tanh) and
`lucas-leme/FinBERT-PT-BR` (Probability).

Pure LSTM, LSTM+LLM_Tanh, and LSTM+LLM_Prob each use 500 TPE iterations,
validation MSE, at most 20 epochs, and patience 3. End-to-end models run once,
inherit their frozen-LLM counterparts' hyperparameters, and are exploratory.

Daily sentiment is the arithmetic mean of at most 20 articles. Both
representations receive the same selected articles. With no article, defaults
are 0.0 for Tanh and [0.33, 0.34, 0.33] for Probability. Non-trading-day news is
assigned to the preceding trading day. Normalization is fitted on training
prices only.

## Orchestrator checks

```shell
python -m src.scripts.run_experiment --config configs/experiments/canonical_research_pipeline.yaml
python -m src.scripts.run_experiment --config configs/experiments/canonical_research_pipeline.yaml --verify-inputs --verify-outputs
```

The first command is a dry run. Do not use `--execute-all-commands` until all
protected inputs, checkpoints, compute resources, and output locations have
been reviewed.
