import pandas as pd
import numpy as np
from pathlib import Path

NEWS   = Path("data/intermediate/news_with_sentiment.parquet")
PRICES = Path("data/intermediate/prio3_prices_clean.parquet")
OUT    = Path("data/processed/sentiment_price.parquet")

LOCAL_TZ = "America/Sao_Paulo"

def to_local_midnight(idx):
    local = idx.tz_convert(LOCAL_TZ)
    return pd.to_datetime(local.date)

news   = pd.read_parquet(NEWS)
prices = pd.read_parquet(PRICES)

def max_magnitude(series):
    """
    Return the sentiment value (±) with the largest absolute magnitude.
    Safe for empty / all-NaN groups.
    """
    s = series.dropna()
    if s.empty:
        return np.nan
    arr = s.to_numpy(dtype=float)
    return arr[np.abs(arr).argmax()]

daily_sent = (
    news.groupby(pd.Grouper(freq="D"))
        .agg(compound_mean=("compound", "mean"),
             compound_mag =("compound", max_magnitude),
             art_count    =("compound", "size"))
)

daily_sent["compound_mean"] = daily_sent["compound_mean"].astype(float)
daily_sent["compound_mag"]  = daily_sent["compound_mag"].astype(float)

daily_sent.index = to_local_midnight(daily_sent.index)
prices.index     = to_local_midnight(prices.index)

prices = prices.assign(
    pct_change = prices["price_close"].pct_change(),
    price_up   = prices["price_close"].diff().gt(0)
)

merged = prices.join(daily_sent, how="inner").sort_index()
merged = merged[merged["art_count"] > 0]

def pct_forward(series, days):
    return (series.shift(-days) - series) / series

merged["pct_d0"] = (merged["price_close"] - merged["price_open"]) / merged["price_open"]
for d in (1, 3, 5, 7, 15, 30, 60, 80, 90):
    merged[f"pct_d{d}"] = pct_forward(merged["price_close"], d)

cols = ["price_close", "art_count", "compound_mean", "compound_mag",
        "pct_d0", "pct_d1", "pct_d3", "pct_d5", "pct_d7", "pct_d15",
        "pct_d30", "pct_d60", "pct_d80", "pct_d90"]

merged = merged[cols].reset_index().rename(columns={"index": "date"})
merged.to_parquet(OUT)
print(f"Saved {len(merged):,} rows to {OUT}")