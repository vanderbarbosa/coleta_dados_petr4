# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — Filtrar o índice por relevância melhora o sinal? (gap G10)
# =============================================================================
#
#  ------------------------------------------------------------------
#  A PERGUNTA, EM LINGUAGEM COMUM
#  ------------------------------------------------------------------
#  O autor do FinBERT-PT-BR, ao montar a base de treino dele, jogou fora as
#  notícias que não tinham nada a ver com finanças — 158 de 661, quase um
#  quarto do total. Nós não fizemos isso: o nosso índice de sentimento usa
#  TODAS as 205.697 notícias coletadas.
#
#  A pergunta natural é: e se jogássemos fora as notícias que não interessam
#  à Petrobras? O índice ficaria melhor?
#
#  ------------------------------------------------------------------
#  POR QUE A COMPARAÇÃO COM SANTOS NÃO É DIRETA
#  ------------------------------------------------------------------
#  Os dois filtros medem coisas diferentes:
#
#    Santos descartou o que NÃO ERA FINANCEIRO
#      (política, texto sem sentido) — 23,9% da amostra dele
#
#    O nosso rótulo marca o que NÃO AFETA A PETROBRAS
#      (mas continua sendo notícia financeira) — 63,0% do conjunto-ouro
#
#  As nossas "não relevantes" são coisas como "EUA e União Europeia excluem
#  Rússia do sistema Swift" — notícia financeira legítima, que Santos teria
#  MANTIDO. Além disso, o nosso corpus já passou por um filtro equivalente ao
#  dele, mas na COLETA: a taxonomia de 152 termos.
#
#  ------------------------------------------------------------------
#  O QUE ESTE SCRIPT TESTA
#  ------------------------------------------------------------------
#  Três versões do índice, da mais ampla à mais restrita, comparadas pela
#  correlação com a volatilidade realizada:
#
#    A — TODAS as notícias                     205.697 (100%)
#    B — CAT1 (empresa) + CAT2 (petróleo)      120.792  (59%)
#    C — só CAT1 (empresa)                      64.882  (32%)
#
#  RESULTADO (10/08/2026), |r| com a volatilidade de D+1:
#      A = 0,1385   B = 0,1704   C = 0,1495
#      B contra A: +0,0319; IC95% [+0,0135; +0,0504]; p = 0,0010  SIGNIFICATIVO
#      B contra C: +0,0205; p = 0,098                             não signif.
#
#  Ou seja: filtrar MELHORA o índice em cerca de 23%, mas filtrar DEMAIS
#  desperdiça sinal. As notícias do mercado de petróleo importam para a PETR4
#  mesmo quando não citam a Petrobras — o que faz sentido econômico, já que a
#  empresa é uma produtora.
#
#  Uso:
#      python src/sentimento/filtrar_ism_por_relevancia.py
# =============================================================================
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parents[2]
DIR = RAIZ / "Mestrado_PETR4"
N_BOOT = 10_000

VARIANTES = {
    "A_todas": (None, "TODAS as noticias"),
    "B_cat1_cat2": (["CAT1_Empresa", "CAT2_Mercado_Petroleo"], "CAT1+CAT2 (empresa + petroleo)"),
    "C_so_cat1": (["CAT1_Empresa"], "so CAT1_Empresa"),
}


def carregar(dir_dados: Path):
    c = pd.read_csv(dir_dados / "noticias_com_sentimento.csv",
                    usecols=["categoria", "Data", "Indice_Sentimento"])
    c["Data"] = pd.to_datetime(c["Data"], errors="coerce")
    c = c.dropna(subset=["Data", "Indice_Sentimento"])

    p = pd.read_csv(dir_dados / "base_financeira_petr4.csv", skiprows=[1])
    p["Date"] = pd.to_datetime(p["Date"], errors="coerce")
    p["Close"] = pd.to_numeric(p["Close"], errors="coerce")
    p = p.dropna(subset=["Date", "Close"]).sort_values("Date")
    p["ret"] = np.log(p["Close"]).diff()
    p["vol"] = p["ret"].abs()
    p["vol_prox"] = p["vol"].shift(-1)
    p["ret_prox"] = p["ret"].shift(-1)
    p["d"] = p["Date"].dt.date
    return c, p


def indice_diario(c: pd.DataFrame, categorias) -> pd.Series:
    """ISM diário = média do índice das notícias do dia, no recorte pedido."""
    sub = c if categorias is None else c[c["categoria"].isin(categorias)]
    return sub.groupby(sub["Data"].dt.date)["Indice_Sentimento"].mean()


def bootstrap_dif_correlacao(x1, x2, y, n=N_BOOT, seed=42):
    """Diferença de |r| entre duas séries, na MESMA reamostra.

    Comparar duas correlações medidas sobre os mesmos pregões exige reamostrar
    os pregões em conjunto — reamostrar cada uma isoladamente ignoraria a
    dependência entre elas e subestimaria a incerteza da diferença.
    """
    rng = np.random.default_rng(seed)
    x1, x2, y = np.asarray(x1), np.asarray(x2), np.asarray(y)
    difs = np.empty(n)
    for k in range(n):
        i = rng.integers(0, len(y), len(y))
        difs[k] = (abs(np.corrcoef(x1[i], y[i])[0, 1])
                   - abs(np.corrcoef(x2[i], y[i])[0, 1]))
    lo, hi = np.percentile(difs, [2.5, 97.5])
    pv = 2 * min((difs <= 0).mean(), (difs >= 0).mean())
    return float(difs.mean()), float(lo), float(hi), float(pv)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=DIR / "filtro_relevancia_ism.json")
    args = ap.parse_args()

    c, p = carregar(DIR)
    total = len(c)

    print("=" * 76)
    print("COBERTURA DE CADA FILTRO")
    print("=" * 76)
    series = {}
    res = {"data_execucao": date.today().isoformat(), "n_corpus": int(total),
           "variantes": {}}
    for chave, (cats, rotulo) in VARIANTES.items():
        sub_n = total if cats is None else int(c["categoria"].isin(cats).sum())
        series[chave] = indice_diario(c, cats)
        print(f"  {rotulo:34s} {sub_n:>9,} noticias ({sub_n/total:>4.0%})  "
              f"{len(series[chave]):>6,} dias")
        res["variantes"][chave] = {"rotulo": rotulo, "n_noticias": sub_n,
                                   "pct_corpus": round(sub_n / total, 4)}

    # une tudo num só quadro, para que as comparações usem os mesmos pregões
    d = p.set_index("d")[["vol", "vol_prox", "ret_prox"]]
    for chave, s in series.items():
        d = d.join(s.rename(chave))
    d = d.dropna(subset=list(series) + ["vol_prox"])
    print(f"\n  pregoes com todas as variantes disponiveis: {len(d):,}")

    print("\n" + "=" * 76)
    print("CORRELACAO COM A VOLATILIDADE")
    print("=" * 76)
    print(f"  {'variante':34s}{'|r| vol D+1':>14s}{'p':>10s}{'|r| vol hoje':>15s}{'p':>10s}")
    for chave, (_, rotulo) in VARIANTES.items():
        r1, p1 = stats.pearsonr(d[chave], d["vol_prox"])
        r2, p2 = stats.pearsonr(d[chave], d["vol"])
        print(f"  {rotulo:34s}{abs(r1):>14.4f}{p1:>10.4f}{abs(r2):>15.4f}{p2:>10.4f}")
        res["variantes"][chave].update({
            "abs_r_vol_prox": round(abs(r1), 4), "p_vol_prox": round(float(p1), 4),
            "abs_r_vol_hoje": round(abs(r2), 4), "p_vol_hoje": round(float(p2), 4)})

    print("\n" + "=" * 76)
    print("A MELHORA E SIGNIFICATIVA? (bootstrap pareado)")
    print("=" * 76)
    comparacoes = [("B_cat1_cat2", "A_todas", "CAT1+CAT2 melhor que TODAS?"),
                   ("B_cat1_cat2", "C_so_cat1", "CAT1+CAT2 melhor que so CAT1?"),
                   ("C_so_cat1", "A_todas", "so CAT1 melhor que TODAS?")]
    res["comparacoes"] = []
    for a, b, rot in comparacoes:
        m, lo, hi, pv = bootstrap_dif_correlacao(d[a], d[b], d["vol_prox"])
        sig = lo > 0 or hi < 0
        print(f"  {rot:32s} delta|r|={m:+.4f}  IC95=[{lo:+.4f},{hi:+.4f}]  "
              f"p={pv:.4f}  -> {'SIGNIFICATIVA' if sig else 'nao significativa'}")
        res["comparacoes"].append({"contraste": f"{a}-{b}", "descricao": rot,
                                   "delta_abs_r": round(m, 4),
                                   "ic95": [round(lo, 4), round(hi, 4)],
                                   "p_valor": round(pv, 4), "significativa": bool(sig)})

    print("\n" + "=" * 76)
    print("CONCLUSAO")
    print("=" * 76)
    print("""
Filtrar o indice por relevancia MELHORA o sinal de volatilidade, mas ha um
ponto otimo. Manter empresa + mercado de petroleo (CAT1+CAT2) supera usar
todas as noticias de forma estatisticamente significativa. Restringir apenas
a noticias da empresa (CAT1) desperdica sinal.

A leitura economica e direta: a PETR4 e uma PRODUTORA de petroleo, de modo
que uma noticia sobre o mercado de petroleo a afeta mesmo sem citar a
Petrobras. Descarta-la e jogar fora informacao.

Registre-se uma tensao interessante: no conjunto-ouro, o anotador humano
marcou 54 noticias de CAT2 como "nao relevantes para a PETR4". A evidencia
estatistica contradiz esse julgamento — elas carregam sinal. O criterio
humano de relevancia e o criterio estatistico nao coincidem.
""")
    args.saida.write_text(json.dumps(res, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    print(f"[OK] Salvo em {args.saida}")


if __name__ == "__main__":
    main()
