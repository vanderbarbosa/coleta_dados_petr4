"""
Apply Portuguese preprocessing (optional) + FinBERT-PT-BR sentiment
to cleaned news and save the enriched dataframe.

Run from repo root with:
    python -m src.nlp.apply_sentiment
"""
from pathlib import Path
import pandas as pd

# Local imports
from .text_preprocess import preprocess  
from .sentiment import score                 # FinBERT-PT-BR scorer

INFILE  = Path("data/intermediate/news_clean.parquet")
OUTFILE = Path("data/intermediate/news_with_sentiment.parquet")

def main() -> None:
    news = pd.read_parquet(INFILE)

    # 1) (Optional) keep a lemmatised version for future NLP experiments
    news["clean_text"] = news["title"].apply(preprocess)

    # 2) Sentiment scores on the *raw* headline
    scores_df = news["title"].apply(score).apply(pd.Series)
    news = pd.concat([news, scores_df], axis=1)

    # 3) Save
    news.to_parquet(OUTFILE)
    print(f"Saved sentiment-enriched news to {OUTFILE}  ({len(news):,} rows).")

if __name__ == "__main__":
    main()