# Soybean Price Forecasting via Hybrid LSTM-LLM Architecture

Code accompanying **“Soybean Price Forecasting via Hybrid LSTM-LLM
Architecture: Statistical and Economic Evaluation of Brazilian Agribusiness
News Sentiment.”** The study forecasts the next trading day's SJCc1 soybean
price from historical closes and sentiment extracted from Brazilian
agribusiness news.

The experiments compare a naive benchmark, a pure LSTM, two LSTMs with frozen
sentiment extractors, and two exploratory end-to-end hybrids. The strongest
hybrid reduced MSE, but did not statistically dominate the naive forecast in
the 90% Model Confidence Set. Full execution instructions are in
[Reproduction](docs/reproduction.md).

## Associated publication

Marco Antonio França Benjamim, Samuel Bellido Rodrigues, Lucas da Silva
Ribeiro, Levi Lopes Teixeira, Tasia Hickmann, and Jairo Marlon Correa (2026).
*Revista RGE Interdisciplinar*, 17(6), 1–21.
[https://doi.org/10.56238/revgeov17n6-094](https://doi.org/10.56238/revgeov17n6-094)

This work was supported by UTFPR through the Institutional Scientific Initiation Scholarship 
Program (PIBIC).

## Research question and data

The target is the next available trading-day close. The price dataset contains
3,261 observations from 12 June 2012 to 19 July 2025, split chronologically:
2,281 training records (through 1 September 2021), 490 validation records
(2 September 2021–18 August 2023), and 490 hold-out test records
(21 August 2023–19 July 2025). No random time-series split is used.

The news corpus contains 27,024 articles from Canal Rural (11,182), Notícias
Agrícolas (13,521), and Globo Rural (2,321). Sentiment fine-tuning used 1,000
articles sampled without replacement only from the training period, labeled
bearish (-1), neutral (0), or bullish (1) with Gemini 2.5 Pro. Manual validation
on a stratified sample of 99 articles (33 per class) produced weighted Cohen's
kappa 0.92 and accuracy 89.5%.

## Main results

| Model | MSE | MAE | MAPE | MCS p-value |
| --- | ---: | ---: | ---: | ---: |
| LSTM+LLM_Prob | 0.0664 | 0.1948 | 0.86% | 1.000 |
| Naive | 0.0667 | 0.1922 | 0.85% | 0.793 |
| Pure LSTM | 0.0737 | 0.2097 | 0.92% | 0.080 |
| LSTM+LLM_Tanh (E2E) | 0.0773 | 0.2093 | 0.92% | 0.080 |
| LSTM+LLM_Tanh | 0.0778 | 0.2142 | 0.95% | 0.068 |
| LSTM+LLM_Prob (E2E) | 0.0858 | 0.2262 | 1.00% | 0.000 |

LSTM+LLM_Prob achieved the lowest MSE; the naive benchmark had slightly lower
MAE and MAPE. Only these two remained in the 90% Model Confidence Set, so the
supported conclusion is statistical equivalence in predictive ability, not
hybrid superiority over naive.

## Key Economic Result

During the 490-day hold-out test period, the frozen LSTM+LLM architecture with
probabilistic sentiment output achieved a cumulative return of 58.27%. It was
the only evaluated model to generate statistically significant cumulative
excess return relative to the buy-and-hold benchmark (paired block bootstrap,
p ≈ 0.003).

The Pure LSTM achieved a cumulative return of 28.53%, but its excess return was
not statistically significant (p ≈ 0.141). The probabilistic hybrid model also
recorded an approximate Sharpe ratio of 1.74 and a maximum drawdown of -11.68%.

![Cumulative returns during the hold-out test period](assets/cumulativeReturns.png)

*Figure: Cumulative returns during the hold-out test period from August 2023
to July 2025. Returns exclude transaction costs and should not be interpreted
as the performance of a production-ready trading strategy.*

## Evaluated architectures

| Architecture | Sentiment representation | Optimization status |
| --- | --- | --- |
| Naive | None; previous close | Computed during evaluation |
| Pure LSTM | None | 500 TPE iterations |
| LSTM+LLM_Tanh | Frozen scalar extractor | 300 LLM trials + 500 LSTM iterations |
| LSTM+LLM_Prob | Frozen three-class vector | 300 LLM trials + 500 LSTM iterations |
| LSTM+LLM_Tanh end-to-end | Scalar, jointly trained | One exploratory run; inherited hyperparameters |
| LSTM+LLM_Prob end-to-end | Three-class vector, jointly trained | One exploratory run; inherited hyperparameters |

Evaluation therefore requires five trained checkpoints plus the naive benchmark
calculated directly from prices.

## Repository structure

```text
configs/                 canonical datasets, training, optimization, and evaluation settings
docs/                    acquisition, reproduction, evaluation, and troubleshooting guides
src/acquisition/         source-specific news scrapers
src/preprocessing/       price, news, and causal alignment logic
src/sentiment/           sentiment models, training, inference, and shared article selection
src/forecasting/         LSTM and end-to-end forecasting
src/evaluation/          predictive and economic evaluation
src/statistics/          MCS and paired block bootstrap
tests/                   scientific-contract regression tests
requirements-paper.txt   versions recorded for the publication environment
```

## Data availability

Price files, raw or processed news text, the 1,000 labeled articles, and derived
text/label splits are **not distributed** because of copyright and
redistribution restrictions. `.gitignore` excludes these materials while
allowing `.gitkeep` placeholders. The repository supplies preparation and
collection code, not the study data.

Users must obtain the [international soybean
series](https://br.investing.com/commodities/us-soybeans) and [Brazilian soybean
series](https://br.investing.com/commodities/us-soybeans-opinion/23?cid=964523)
manually. Exact expected paths and formats are in [Data
acquisition](docs/data-acquisition.md).

Scrapers are provided for the three news sources, but site HTML, pagination,
selectors, blocking, and policies may have changed. Scripts may need updates and
cannot guarantee exact reconstruction or continued availability of historical
articles. Respect terms of use, `robots.txt`, rate limits, and copyright.

## Installation

The recorded paper environment was Google Colab with an NVIDIA Tesla T4 (15 GB
VRAM), 12.7 GB RAM, sessions limited to five hours, and Python 3.12.12. The exact
reported library versions are pinned in `requirements-paper.txt`; extra project
and test tooling remains in `requirements.txt`.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-paper.txt
python -m pip install -r requirements.txt
```

Linux/macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-paper.txt
python -m pip install -r requirements.txt
```

The paper versions were pandas 2.2.2, NumPy 2.0.2, PyTorch 2.10.0, matplotlib
3.10.0, arch 8.0.0, Optuna 4.7.0, SciPy 1.16.3, transformers 5.0.0,
scikit-learn 1.6.1, BeautifulSoup 4.14.3, and requests 2.32.4. CUDA-compatible
PyTorch installation may depend on the target platform.

## Exact paper reproduction

Full reproduction requires the protected author-held inputs, external price
exports, the original corpus (where still obtainable), substantial GPU time,
and five trained checkpoints. Follow the [complete workflow](docs/reproduction.md)
and [evaluation guide](docs/evaluation.md). Canonical settings are 300 TPE
trials per LLM variant, 500 TPE iterations per optimized LSTM, at most 20 epochs
per optimization trial, and early-stopping patience 3.

Daily Tanh and Probability inference uses exactly the same deterministic set of
at most 20 articles before averaging. With no news, the neutral values are 0.0
and [0.33, 0.34, 0.33]. Weekend and holiday news is assigned to the preceding
trading day. Price z-score parameters are fitted exclusively on training data.

## Statistical and economic evaluation

The six architectures are evaluated by test MSE/MAE/MAPE, a 90% Model
Confidence Set, and a paired stationary block bootstrap of compounded return
against buy-and-hold (10,000 replications, block length 10, seed 42). Signals are
unleveraged: long if the forecast next close exceeds the current close, short
otherwise. See [Evaluation](docs/evaluation.md).

## Reproducibility notes and limitations

- The published price imputation used 1,265 CBOT-regression fills plus 24 linear
  interpolations (1,289 total), correlation 0.9948, and imputation test R²
  0.9924. Only one imputation occurred in the hold-out test set.
- Historical repository artifacts disagree on which articles were retained on
  days exceeding 20 items. The publication does not resolve that order. The
  canonical code now applies one shared, stable-prefix policy to both sentiment
  representations; exact equivalence to the unavailable historical selection
  cannot be established.
- The local labeled file found during this audit contains 966 rows and no usable
  dates, not the published 1,000-row training-period sample. The canonical
  pipeline rejects it for paper reproduction.
- The local processed price file duplicates 2025-04-04 and includes Saturday
  2025-07-19. Removing these rows would conflict with the supplied 3,261-record
  contract and split endpoints, so corrected author-held source data or an
  authoritative calendar/imputation artifact is required.
- Scraping cannot guarantee recovery of the original corpus. Hardware and
  library differences can also prevent bitwise reproduction.
- End-to-end results are exploratory, and transaction costs were not modeled.

## Citation

Benjamim, M. A. F., Rodrigues, S. B., Ribeiro, L. S., Teixeira, L. L.,
Hickmann, T., & Correa, J. M. (2026). Soybean Price Forecasting via Hybrid
LSTM-LLM Architecture: Statistical and Economic Evaluation of Brazilian
Agribusiness News Sentiment. *Revista RGE Interdisciplinar, 17*(6), 1–21.
https://doi.org/10.56238/revgeov17n6-094

```bibtex
@article{benjamim2026soybean,
  author  = {Marco Antonio Fran\c{c}a Benjamim and Samuel Bellido Rodrigues and Lucas da Silva Ribeiro and Levi Lopes Teixeira and Tasia Hickmann and Jairo Marlon Correa},
  title   = {Soybean Price Forecasting via Hybrid {LSTM}-{LLM} Architecture: Statistical and Economic Evaluation of Brazilian Agribusiness News Sentiment},
  journal = {Revista RGE Interdisciplinar},
  year    = {2026},
  volume  = {17},
  number  = {6},
  pages   = {1--21},
  doi     = {10.56238/revgeov17n6-094}
}
```

## Copyright

Copyright (c) 2026 Marco Antonio França Benjamim and contributors.
All rights reserved.

No license is granted to use, copy, modify, or redistribute this code or the
associated materials without prior permission from the copyright holders.
Third-party prices, news, base models, and other materials remain subject to
their respective owners' rights and terms.
