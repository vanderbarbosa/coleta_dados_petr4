import re, hashlib, pandas as pd
from pathlib import Path

RAW = Path("data/raw/news_prio3_2015_2024.csv")
OUT = Path("data/intermediate/news_clean.parquet")

df = pd.read_csv(RAW)

# Standardise date column
df = (df
      .rename(columns={"published date": "published_date"})
      .assign(published_date=lambda d: pd.to_datetime(
          d["published_date"], utc=True, errors="coerce"))
      .dropna(subset=["published_date"]))

# Strip trailing “- Publisher” or “| Publisher” from titles 
df["title"] = df["title"].str.replace(
    r"\s*[-|]\s*[A-Za-zÀ-ÿ0-9&.\- ]+$",  # ← generic publisher slug
    "",
    regex=True,
    flags=re.I
)

# Keyword filter (Brazilian oil E&P context)
PRIO_WORDS = [
    "petro ?rio", "prior3", "prio3", "produção", "barris", "campo",
    "licen[çc]a", "fpsos?", "manati", "polo", r"\banp\b",
    "reservas?", "lifting cost", "regula[çc][aã]o", "combustível",
    "petr[oó]leo", "gasolina", "leil[aã]o", "investimento"
]
pattern = re.compile("|".join(PRIO_WORDS), flags=re.I)

df = df[df["title"].str.contains(pattern) |
        df["description"].str.contains(pattern, na=False)]

# Deduplicate exact-same URLs
df["url_hash"] = df["url"].apply(lambda u: hashlib.md5(
    str(u).encode("utf-8")).hexdigest())
df = df.drop_duplicates(subset="url_hash").drop(columns="url_hash")

# Finalise & save
df = df.set_index("published_date").sort_index()
df.to_parquet(OUT)
print(f"✅ Clean news written to {OUT} — {len(df):,} rows.")