# -*- coding: utf-8 -*-
# ==============================================================================
#   QUANTO A NOTÍCIA MOVE? — a pergunta central, respondida em porcentagem
#
#   Os scripts 07 e 08 responderam isso para a CVM. Este responde para a
#   IMPRENSA, com o mesmo desenho, para que os dois números sejam comparáveis:
#
#     - mesma régua: o pregão dividido pela média dos 5 pregões anteriores
#       [-6,-2] daquele mesmo papel;
#     - mesmo piso de controle: as noites em que não houve NADA (nem notícia
#       acima do normal, nem comunicado à CVM). É contra esse piso que o
#       excesso é medido, e não contra 1,00.
#
#   ISTO NÃO É PREVISÃO. É MEDIÇÃO. Não se pergunta se dá para adivinhar o
#   amanhã; pergunta-se quanto o mercado se mexeu, em porcentagem, depois de
#   uma noite de notícia.
#
#   Saída: dados/quanto_a_noticia_move.json
# ==============================================================================
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
TICKER, JANELA = "PETR4", 5


def resumo(x: pd.Series) -> dict:
    x = x.dropna()
    return {"n": int(len(x)), "media": round(float(x.mean()), 4),
            "mediana": round(float(x.median()), 4)}


def excesso(grupo: pd.Series, piso: pd.Series) -> dict:
    """Excesso percentual do grupo sobre o piso de controle, com teste."""
    g, p = grupo.dropna(), piso.dropna()
    if len(g) < 30 or len(p) < 30:
        return {}
    t = stats.mannwhitneyu(g, p, alternative="two-sided")
    return {"n": int(len(g)), "media": round(float(g.mean()), 4),
            "mediana": round(float(g.median()), 4),
            "excesso_media_pct": round(float((g.mean() / p.mean() - 1) * 100), 1),
            "excesso_mediana_pct": round(float((g.median() / p.median() - 1) * 100), 1),
            "p": float(t.pvalue)}


def main() -> None:
    px = pd.read_csv(DADOS / "ohlcv_b3.csv", parse_dates=["Data"])
    px = px[px["Ticker"] == TICKER].sort_values("Data").reset_index(drop=True)
    for col, novo in [("Parkinson", "vol"), ("Volume", "giro")]:
        base = px[col].shift(2).rolling(JANELA).mean()
        px[f"razao_{novo}"] = px[col] / base
    px["mov_abs"] = px["Retorno"].abs()
    px["razao_mov"] = px["mov_abs"] / px["mov_abs"].shift(2).rolling(JANELA).mean()

    d = pd.read_csv(DADOS / "confronto_fontes_dias.csv", parse_dates=["data"])
    d = d.merge(px[["Data", "razao_vol", "razao_giro", "razao_mov", "Retorno",
                    "Parkinson", "Volume"]],
                left_on="data", right_on="Data", how="left")
    d = d[d["razao_vol"].notna()].sort_values("data").reset_index(drop=True)

    # ── a noite: quanto texto, e de que tom ──────────────────────────────────
    d["qtd"] = d["n_tot"].fillna(0)
    corte = d["qtd"].median()
    d["saldo"] = (d["n_pos"] - d["n_neg"]) / d["n_tot"].replace(0, np.nan)
    d["desvio_tom"] = d["saldo"] - d["saldo"].expanding(min_periods=60).mean().shift(1)
    d["tem_cvm"] = d["c_tot"].fillna(0) > 0
    d["tem_fr"] = d["c_fr"].fillna(0) > 0

    # ── o piso de controle: noites em que NÃO houve nada ─────────────────────
    calma = (d["qtd"] <= corte) & ~d["tem_cvm"]
    piso = {m: d.loc[calma, f"razao_{m}"] for m in ["vol", "giro", "mov"]}

    print("=" * 88)
    print(f"  QUANTO A NOTÍCIA MOVE O PREGÃO SEGUINTE — {TICKER}")
    print("=" * 88)
    print(f"\n  pregões analisados: {len(d):,}")
    print(f"  corte de 'noite agitada': mais de {corte:.0f} textos publicados")
    print(f"\n  O PISO DE CONTROLE — {int(calma.sum()):,} noites em que não houve nada")
    print("  (nem notícia acima do normal, nem comunicado à CVM)")
    for m, rot in [("vol", "volatilidade"), ("giro", "volume negociado"),
                   ("mov", "tamanho da variação")]:
        r = resumo(piso[m])
        print(f"    {rot:<22} média {r['media']:.3f}   mediana {r['mediana']:.3f}")
    print("\n  Repare: o piso NAO e 1,00. Um dia pode ser cinco vezes mais agitado")
    print("  que a media, mas nunca cinco vezes menos -- o minimo e zero.")

    res = {"ticker": TICKER, "n": int(len(d)), "corte_texto": float(corte),
           "n_piso": int(calma.sum()),
           "piso": {m: resumo(piso[m]) for m in piso}, "grupos": {}}

    grupos = {
        "noite de MUITA notícia (sem CVM)": (d["qtd"] > corte) & ~d["tem_cvm"],
        "houve Comunicado ao Mercado": d["tem_cvm"] & ~d["tem_fr"],
        "houve FATO RELEVANTE": d["tem_fr"],
        "FATO RELEVANTE + muita notícia": d["tem_fr"] & (d["qtd"] > corte),
    }

    for m, rot in [("vol", "VOLATILIDADE"), ("giro", "VOLUME NEGOCIADO"),
                   ("mov", "TAMANHO DA VARIAÇÃO DO PREÇO")]:
        print("\n" + "=" * 88)
        print(f"  {rot} — excesso sobre a noite em que não houve nada")
        print("=" * 88)
        print(f"\n  {'tipo de noite':<36} {'noites':>7} {'excesso':>10} "
              f"{'pelo típico':>12} {'p':>10}")
        print("  " + "-" * 82)
        for nome, cond in grupos.items():
            e = excesso(d.loc[cond, f"razao_{m}"], piso[m])
            if not e:
                continue
            res["grupos"].setdefault(nome, {})[m] = e
            ok = "  *" if e["p"] < 0.05 else ""
            print(f"  {nome:<36} {e['n']:>7,} {e['excesso_media_pct']:>+9.1f}% "
                  f"{e['excesso_mediana_pct']:>+11.1f}% {e['p']:>10.2e}{ok}")

    # ── a direção: o tom da notícia prevê o LADO? ────────────────────────────
    print("\n" + "=" * 88)
    print("  E A DIREÇÃO? o tom da notícia diz para que lado o preço vai?")
    print("=" * 88)
    q = d["desvio_tom"].quantile([0.2, 0.8])
    faixas = {
        "noite de tom MUITO NEGATIVO": d["desvio_tom"] <= q[0.2],
        "noite de tom comum": (d["desvio_tom"] > q[0.2]) & (d["desvio_tom"] < q[0.8]),
        "noite de tom MUITO POSITIVO": d["desvio_tom"] >= q[0.8],
    }
    print(f"\n  {'faixa de tom':<36} {'noites':>7} {'retorno médio':>15} {'% de alta':>11}")
    print("  " + "-" * 74)
    res["direcao"] = {}
    for nome, cond in faixas.items():
        r = d.loc[cond, "Retorno"].dropna()
        if len(r) < 30:
            continue
        res["direcao"][nome] = {"n": int(len(r)),
                                "retorno_medio_pct": round(float(r.mean() * 100), 3),
                                "pct_alta": round(float((r > 0).mean() * 100), 1)}
        print(f"  {nome:<36} {len(r):>7,} {r.mean()*100:>+14.3f}% "
              f"{(r > 0).mean()*100:>10.1f}%")

    neg = d.loc[faixas["noite de tom MUITO NEGATIVO"], "Retorno"].dropna()
    pos = d.loc[faixas["noite de tom MUITO POSITIVO"], "Retorno"].dropna()
    t = stats.mannwhitneyu(neg, pos, alternative="two-sided")
    res["direcao"]["p_neg_vs_pos"] = float(t.pvalue)
    print(f"\n  diferença entre o tom muito negativo e o muito positivo: "
          f"p = {t.pvalue:.3f}" + ("  *" if t.pvalue < 0.05 else "   (nao passa)"))

    # ── em números do dia a dia ──────────────────────────────────────────────
    print("\n" + "=" * 88)
    print("  O QUE ISSO É EM NÚMEROS CONCRETOS")
    print("=" * 88)
    res["concreto"] = {}
    for nome, cond in [
        ("noite em que não houve nada", calma),
        ("noite de muita notícia (sem CVM)", grupos["noite de MUITA notícia (sem CVM)"]),
        ("noite de FATO RELEVANTE", grupos["houve FATO RELEVANTE"]),
        ("FATO RELEVANTE + muita notícia", grupos["FATO RELEVANTE + muita notícia"]),
    ]:
        osc = d.loc[cond, "Parkinson"].median() * 100
        gir = d.loc[cond, "Volume"].median() / 1e6
        res["concreto"][nome] = {"oscilacao_pct": round(float(osc), 2),
                                 "giro_milhoes": round(float(gir), 1)}
        print(f"  {nome:<36} oscila {osc:>5.2f}%   gira {gir:>6.1f} milhões de ações")

    (DADOS / "quanto_a_noticia_move.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n  gravado: dados/quanto_a_noticia_move.json")


if __name__ == "__main__":
    main()
