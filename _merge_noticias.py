# -*- coding: utf-8 -*-
"""Mescla o corpus 2018-2025 existente com os gaps 2016-2017 e 2026.
Nao recoleta nada; apenas une, remove duplicatas e reporta os totais reais."""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent / "Mestrado_PETR4"
existente = "base_textual_petr4_wordpress_2018_2025.csv"
gaps = ["base_textual_petr4_wordpress_2016_2017.csv", "base_textual_petr4_wordpress_2026.csv"]
SAIDA = BASE / "base_textual_petr4_wordpress_2016_2026.csv"

partes = []
for nome in [existente] + gaps:
    p = BASE / nome
    if p.exists():
        d = pd.read_csv(p)
        print(f"  {nome}: {len(d)} linhas")
        partes.append(d)
    else:
        print(f"  {nome}: AUSENTE (coleta ainda em andamento?)")

df = pd.concat(partes, ignore_index=True)
antes = len(df)
# limpeza leve (mesmo criterio da dissertacao) + dedup por hash do titulo
df["titulo"] = df["titulo"].astype(str)
df = df[df["titulo"].str.len() >= 15]
if "hash_titulo" in df.columns:
    df = df.drop_duplicates(subset=["hash_titulo"])
else:
    df = df.drop_duplicates(subset=["titulo"])
df["data_publicacao"] = pd.to_datetime(df["data_publicacao"], errors="coerce", utc=True)
df = df.dropna(subset=["data_publicacao"]).sort_values("data_publicacao")
df.to_csv(SAIDA, index=False)

print(f"\n[OK] {SAIDA.name}")
print(f"   bruto {antes} -> {len(df)} apos limpeza/dedup")
print(f"   periodo: {df['data_publicacao'].min().date()} a {df['data_publicacao'].max().date()}")
df["ano"] = df["data_publicacao"].dt.year
print("   por ano:", df["ano"].value_counts().sort_index().to_dict())
if "fonte_coleta" in df.columns:
    print("   por fonte:", df["fonte_coleta"].value_counts().to_dict())
