# -*- coding: utf-8 -*-
# ==============================================================================
#   Prepara os dados dos casos para o painel interativo
#
#   Escolhe casos REAIS que cobrem o espectro inteiro, e não só os bonitos:
#     - choques enormes
#     - casos da PETR4
#     - casos em que NADA aconteceu (que são a maioria)
#     - casos em que o nosso modelo ACERTOU
#     - casos em que o nosso modelo ERROU
#
#   Saída: CVM/dados/painel_casos.json
# ==============================================================================
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"

V = "razaoVol_1 semana (-6 a -2)"
Q = "razaoVolume_1 semana (-6 a -2)"


def serie_base(px: pd.DataFrame, tk: str, dia_reacao) -> dict | None:
    """Os pregões da semana anterior mais o dia da reação, para o gráfico."""
    p = px[px["Ticker"] == tk].reset_index(drop=True)
    i = p.index[p["Data"] == dia_reacao]
    if not len(i):
        return None
    i = int(i[0])
    if i < 8:
        return None
    jan = p.iloc[i - 6:i - 1]          # a linha de base: -6 a -2
    if jan["Parkinson"].isna().any() or (jan["Volume"] <= 0).any():
        return None
    return {
        "semana": [{"data": d.strftime("%d/%m"),
                    "vol": round(float(v) * 100, 3),
                    "qtd": round(float(q) / 1e6, 2)}
                   for d, v, q in zip(jan["Data"], jan["Parkinson"], jan["Volume"])],
        "dia": {"data": p["Data"].iloc[i].strftime("%d/%m"),
                "vol": round(float(p["Parkinson"].iloc[i]) * 100, 3),
                "qtd": round(float(p["Volume"].iloc[i]) / 1e6, 2)},
        "media_vol": round(float(jan["Parkinson"].mean()) * 100, 3),
        "media_qtd": round(float(jan["Volume"].mean()) / 1e6, 2),
        "abertura": round(float(p["Abertura"].iloc[i]), 2),
        "fechamento": round(float(p["Fechamento"].iloc[i]), 2),
        "fech_anterior": round(float(p["Fech_ant"].iloc[i]), 2),
        "maxima": round(float(p["Maxima"].iloc[i]), 2),
        "minima": round(float(p["Minima"].iloc[i]), 2),
    }


def monta(r, px, rotulo_grupo) -> dict | None:
    s = serie_base(px, r["Ticker"], r["Pregao_reacao"])
    if s is None:
        return None
    subiu = r["Retorno_d1"] > 0
    prev = {"Positive": "ALTA", "Negative": "BAIXA"}.get(r.get("Rotulo"), None)
    return {
        "grupo": rotulo_grupo,
        "ticker": r["Ticker"],
        "empresa": str(r["Empresa"]).title(),
        "categoria": r["Categoria"],
        "assunto": str(r["Assunto"]),
        "entrega": pd.Timestamp(r["Entrega"]).strftime("%d/%m/%Y %H:%M"),
        "entrega_hora": pd.Timestamp(r["Entrega"]).strftime("%H:%M"),
        "reacao": pd.Timestamp(r["Pregao_reacao"]).strftime("%d/%m/%Y"),
        "razao_vol": round(float(r[V]), 2),
        "razao_qtd": round(float(r[Q]), 2),
        "gap_pct": round(float(r["Gap_d1"]) * 100, 2),
        "intra_pct": round(float(r["Intradia_d1"]) * 100, 2),
        "ret_pct": round(float(r["Retorno_d1"]) * 100, 2),
        "direcao": "SUBIU" if subiu else "CAIU",
        "modelo": r.get("Rotulo") or "sem classificação",
        "modelo_previu": prev,
        "modelo_acertou": (None if prev is None
                           else (prev == ("ALTA" if subiu else "BAIXA"))),
        **s,
    }


def main() -> None:
    px = pd.read_csv(DADOS / "ohlcv_b3.csv", parse_dates=["Data"])
    d = pd.read_csv(DADOS / "rodada_B_casos.csv",
                    parse_dates=["Entrega", "Pregao_reacao"])
    d = d.dropna(subset=[V, Q, "Gap_d1", "Retorno_d1"])
    d = d[d["Atribuivel"] & ~d["Generico"]]
    print(f"casos elegíveis: {len(d):,}")

    escolhidos, vistos = [], set()

    def pega(sub, grupo, n):
        for _, r in sub.iterrows():
            ch = (r["Ticker"], r["Pregao_reacao"])
            if ch in vistos:
                continue
            c = monta(r, px, grupo)
            if c is None:
                continue
            vistos.add(ch)
            escolhidos.append(c)
            if sum(1 for x in escolhidos if x["grupo"] == grupo) >= n:
                break

    fr = d[d["Categoria"] == "Fato Relevante"]

    # 1. os choques grandes — o que todo mundo espera ver
    pega(fr.nlargest(40, V), "choque grande", 6)

    # 2. PETR4, que é o ativo da dissertação
    pega(d[d["Ticker"] == "PETR4"].nlargest(30, V), "PETR4", 4)

    # 3. o caso comum: NADA aconteceu. São a maioria e quase nunca são mostrados.
    calmo = fr[(fr[V] < 0.75) & (fr[Q] < 0.9)]
    pega(calmo.sample(min(len(calmo), 40), random_state=11), "não aconteceu nada", 5)

    # 4. o modelo acertou
    ok = fr[(fr["Rotulo"].isin(["Positive", "Negative"]))
            & (((fr["Rotulo"] == "Negative") & (fr["Retorno_d1"] < -0.02))
               | ((fr["Rotulo"] == "Positive") & (fr["Retorno_d1"] > 0.02)))]
    pega(ok.nlargest(30, V), "o modelo acertou", 4)

    # 5. o modelo errou — precisa aparecer
    erro = fr[(fr["Rotulo"].isin(["Positive", "Negative"]))
              & (((fr["Rotulo"] == "Negative") & (fr["Retorno_d1"] > 0.03))
                 | ((fr["Rotulo"] == "Positive") & (fr["Retorno_d1"] < -0.03)))]
    pega(erro.nlargest(30, V), "o modelo errou", 4)

    # ── números do conjunto, para a parte agregada ───────────────────────────
    todos = pd.read_csv(DADOS / "casos_concretos.csv")
    ver = todos["Veredicto"].value_counts()
    A = json.loads((DADOS / "rodada_A.json").read_text(encoding="utf-8"))
    FC = json.loads((DADOS / "fr_vs_cm.json").read_text(encoding="utf-8"))
    BC = json.loads((DADOS / "rodada_B_por_categoria.json").read_text(encoding="utf-8"))

    saida = {
        "casos": escolhidos,
        "resumo": {
            "n_eventos": int(len(todos)),
            "n_fr": int((todos["Categoria"] == "Fato Relevante").sum()),
            "n_cm": int((todos["Categoria"] == "Comunicado ao Mercado").sum()),
            "n_papeis": int(todos["Ticker"].nunique()),
            "veredicto": {k: int(v) for k, v in ver.items()},
            "controle": A["controle"],
            "fr_vs_cm": FC,
            "rodada_B": BC,
        },
    }
    (DADOS / "painel_casos.json").write_text(
        json.dumps(saida, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"\ncasos escolhidos: {len(escolhidos)}")
    for g in ["choque grande", "PETR4", "não aconteceu nada",
              "o modelo acertou", "o modelo errou"]:
        n = sum(1 for x in escolhidos if x["grupo"] == g)
        print(f"  {g:22s} {n}")
    print(f"\ngravado: painel_casos.json "
          f"({(DADOS / 'painel_casos.json').stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
