# -*- coding: utf-8 -*-
"""Agrega o ISM 2016-2026: sentimento existente (2018-2025) + novas (2016-17, 2026).
Replica a logica do Script 03 (media diaria com Lead-Lag 17h; categorias por pivot)."""
import shutil
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent / "Mestrado_PETR4"

# 1) existente (ja tem Data_Ajustada, Indice_Sentimento, Label_Sentimento, categoria)
ex = pd.read_csv(BASE / "noticias_com_sentimento.csv",
                 usecols=["Data_Ajustada", "Indice_Sentimento", "Label_Sentimento", "categoria"])
ex["Data_Ajustada"] = pd.to_datetime(ex["Data_Ajustada"], errors="coerce").dt.date
print(f"[..] existente: {len(ex)}")

# 2) novas: calcula Data_Ajustada (Lead-Lag 17h a partir de data_publicacao)
nv = pd.read_csv(BASE / "noticias_novas_sentimento.csv")
dt = pd.to_datetime(nv["data_publicacao"], errors="coerce", utc=True).dt.tz_convert("America/Sao_Paulo")
nv["Data_Ajustada"] = [(d + pd.Timedelta(days=1)).date() if (pd.notna(d) and d.hour >= 17) else (d.date() if pd.notna(d) else None) for d in dt]
nv = nv[["Data_Ajustada", "Indice_Sentimento", "Label_Sentimento", "categoria"]]
print(f"[..] novas: {len(nv)}")

full = pd.concat([ex, nv], ignore_index=True).dropna(subset=["Data_Ajustada"])
print(f"[..] total: {len(full)} | {full['Data_Ajustada'].min()} a {full['Data_Ajustada'].max()}")

# 3) ISM agregado
ism = (full.groupby("Data_Ajustada").agg(
        Indice_Sentimento_Transformer=("Indice_Sentimento", "mean"),
        Qtd_Noticias_do_Dia=("Indice_Sentimento", "count"),
        Qtd_Positivas=("Label_Sentimento", lambda x: (x == "Positive").sum()),
        Qtd_Negativas=("Label_Sentimento", lambda x: (x == "Negative").sum()),
        Qtd_Neutras=("Label_Sentimento", lambda x: (x == "Neutral").sum()),
      ).reset_index().rename(columns={"Data_Ajustada": "Data"}))

# 4) ISM por categoria (pivot)
cat = (full.pivot_table(index="Data_Ajustada", columns="categoria", values="Indice_Sentimento", aggfunc="mean")
       .reset_index().rename(columns={"Data_Ajustada": "Data"}))
cat.columns = [c if c == "Data" else f"ISM_{c}" for c in cat.columns]

# 5) backup e salva
for nome, novo in [("indice_sentimento_petr4.csv", ism), ("indice_sentimento_categorias_petr4.csv", cat)]:
    orig = BASE / nome
    if orig.exists():
        shutil.copyfile(orig, BASE / (nome.replace(".csv", "_2018_2025_bkp.csv")))
    novo.to_csv(orig, index=False)
    print(f"[OK] {nome}: {len(novo)} pregões")
print("ISM 2016-2026:", ism["Data"].min(), "a", ism["Data"].max(),
      "| media", round(ism["Indice_Sentimento_Transformer"].mean(), 4))
