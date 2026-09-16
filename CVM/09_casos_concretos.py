# -*- coding: utf-8 -*-
# ==============================================================================
#   Casos concretos — a engenharia reversa, um evento por vez
#
#   Os orientadores pediram exatamente isto: "no dia x foi publicada uma
#   notícia que, segundo a classificação, é fato relevante; verificar se de
#   fato causou mudança no preço, e qual foi a volatilidade e a direção".
#
#   Este script produz a tabela caso a caso, auditável na mão.
#
#   Saída: CVM/dados/casos_concretos.csv e casos_concretos_top.csv
# ==============================================================================
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"

BASE_VOL = "razaoVol_1 semana (-6 a -2)"
BASE_QTD = "razaoVolume_1 semana (-6 a -2)"

# assuntos genéricos: o campo existe mas não informa nada sobre o fato
GENERICOS = (r"^not[íi]cia divulgada na m[íi]dia$|^negocia[çc][õo]es at[íi]picas|"
             r"^esclarecimento sobre|^resposta a of[íi]cio|^comunicado ao mercado$|"
             r"^fato relevante$|^esclarecimentos$")


def main() -> None:
    print("=" * 78)
    print("CASOS CONCRETOS — a engenharia reversa, evento por evento")
    print("=" * 78)

    d = pd.read_csv(DADOS / "rodada_A_casos.csv", parse_dates=["Entrega", "Pregao_reacao"])
    print(f"\n  eventos após o fechamento: {len(d):,}")

    d["Generico"] = d["Assunto"].fillna("").str.strip().str.lower().str.match(GENERICOS)
    print(f"  assunto genérico (não informa nada): {d['Generico'].sum():,} "
          f"({d['Generico'].mean():.1%})")

    # ── a leitura de cada caso, em linguagem comum ───────────────────────────
    d["Volatilidade_vs_semana"] = d[BASE_VOL]
    d["Volume_vs_semana"] = d[BASE_QTD]
    d["Direcao"] = np.where(d["Retorno_d1"] > 0, "SUBIU", "CAIU")
    d["Variacao_pct"] = d["Retorno_d1"] * 100
    d["Gap_pct"] = d["Gap_d1"] * 100
    d["Intradia_pct"] = d["Intradia_d1"] * 100

    # um veredicto legível: a notícia mexeu?
    def veredicto(r):
        v, q = r["Volatilidade_vs_semana"], r["Volume_vs_semana"]
        if pd.isna(v) or pd.isna(q):
            return "sem base de comparação"
        if v >= 2.0 or q >= 2.0:
            return "MEXEU MUITO"
        if v >= 1.3 or q >= 1.3:
            return "mexeu"
        if v <= 0.8 and q <= 0.8:
            return "dia mais parado que o normal"
        return "dentro do normal"

    d["Veredicto"] = d.apply(veredicto, axis=1)

    # ── eventos agrupados ────────────────────────────────────────────────────
    # Quando a mesma empresa publica mais de um documento na mesma noite, todos
    # apontam para o mesmo pregão. O movimento observado NÃO pode ser atribuído
    # a um documento específico. Marca-se para que a leitura seja honesta.
    grupo = d.groupby(["Ticker", "Pregao_reacao"])["Assunto"].transform("size")
    d["Docs_na_mesma_noite"] = grupo
    d["Atribuivel"] = grupo == 1
    print("")
    print("  eventos isolados (atribuiveis a UM documento): "
          + f"{d['Atribuivel'].sum():,} ({d['Atribuivel'].mean():.1%})")
    print(f"  eventos agrupados (2+ documentos na mesma noite): "
          f"{(~d['Atribuivel']).sum():,}")

    print("\n  DISTRIBUIÇÃO DOS VEREDICTOS:")
    for k, v in d["Veredicto"].value_counts().items():
        print(f"    {k:32s} {v:>5,}  ({v/len(d):>5.1%})")

    cols = ["Entrega", "Pregao_reacao", "Ticker", "Empresa", "Categoria", "Assunto",
            "Generico", "Docs_na_mesma_noite", "Atribuivel", "Veredicto",
            "Volatilidade_vs_semana", "Volume_vs_semana",
            "Direcao", "Variacao_pct", "Gap_pct", "Intradia_pct"]
    saida = d[cols].sort_values("Entrega")
    saida.to_csv(DADOS / "casos_concretos.csv", index=False, encoding="utf-8-sig")

    # ── os 20 maiores, para a apresentação ───────────────────────────────────
    top = (d[(~d["Generico"]) & d["Atribuivel"]]
           .dropna(subset=["Volatilidade_vs_semana"])
           .nlargest(20, "Volatilidade_vs_semana"))
    top[cols].to_csv(DADOS / "casos_concretos_top.csv", index=False,
                     encoding="utf-8-sig")

    print("\n" + "=" * 78)
    print("  OS 20 MAIORES — notícia divulgada após o fechamento e o pregão seguinte")
    print("=" * 78)
    for _, r in top.iterrows():
        print(f"\n  {r['Ticker']}  —  publicado {r['Entrega']:%d/%m/%Y às %H:%M}")
        print(f"    \"{str(r['Assunto'])[:92]}\"")
        print(f"    pregão de {r['Pregao_reacao']:%d/%m/%Y}: "
              f"volatilidade {r['Volatilidade_vs_semana']:.1f}x a da semana anterior, "
              f"volume {r['Volume_vs_semana']:.1f}x")
        print(f"    o preço {r['Direcao']} {abs(r['Variacao_pct']):.1f}%  "
              f"(abertura {r['Gap_pct']:+.1f}%, depois {r['Intradia_pct']:+.1f}%)")

    # ── recorte da PETR4 ─────────────────────────────────────────────────────
    p = d[(d["Ticker"] == "PETR4") & (~d["Generico"]) & d["Atribuivel"]].dropna(
        subset=["Volatilidade_vs_semana"])
    print("\n" + "=" * 78)
    print(f"  PETR4 — os 8 maiores de {len(p)} casos")
    print("=" * 78)
    for _, r in p.nlargest(8, "Volatilidade_vs_semana").iterrows():
        print(f"\n  {r['Entrega']:%d/%m/%Y %H:%M}  \"{str(r['Assunto'])[:78]}\"")
        print(f"    volatilidade {r['Volatilidade_vs_semana']:.1f}x | "
              f"volume {r['Volume_vs_semana']:.1f}x | "
              f"{r['Direcao']} {abs(r['Variacao_pct']):.1f}%")

    print(f"\n  gravados: casos_concretos.csv ({len(saida):,}) e casos_concretos_top.csv")


if __name__ == "__main__":
    main()
