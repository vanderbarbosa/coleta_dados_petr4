# -*- coding: utf-8 -*-
# ==============================================================================
#   PREVER A VOLATILIDADE DO PREGÃO SEGUINTE, combinando as duas fontes
#
#   Esta é a lacuna que faltava. O confronto anterior previu DIREÇÃO; aqui se
#   prevê MAGNITUDE — que é, aliás, o alvo em que toda a pesquisa mostra sinal
#   forte, enquanto a direção mal se distingue do acaso.
#
#   O DESENHO MUDA, e a razão é conceitual:
#
#     Para DIREÇÃO importa o LADO do sentimento — notícia ruim prevê queda.
#     Para VOLATILIDADE o lado é irrelevante. Um dia que sobe 5% e um que cai
#     5% têm a mesma volatilidade. O que importa é a INTENSIDADE:
#
#       - quão longe do normal está o sentimento da noite, em valor absoluto
#       - quantos textos foram publicados
#       - se houve comunicado à CVM, e se foi Fato Relevante
#
#   SEM OLHAR O FUTURO: todo limiar vem de mediana expansiva, calculada apenas
#   sobre os pregões anteriores. Nenhuma noite enxerga o próprio desfecho.
#
#   Saída: CVM/dados/prever_volatilidade.json
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
TICKER = "PETR4"
FECHA, ABRE = 17, 10
JANELA_BASE = 5          # pregões da linha de base, pulando os dois anteriores
MIN_HIST = 120           # mínimo de história antes de começar a prever


def avalia(real, prev, rot) -> dict | None:
    m = pd.notna(prev)
    real, prev = np.asarray(real)[m], np.asarray(prev)[m]
    if len(real) < 60:
        return None
    from sklearn.metrics import cohen_kappa_score, matthews_corrcoef
    acc = (real == prev).mean()
    maj = pd.Series(real).value_counts(normalize=True).iloc[0]
    p = stats.binomtest(int((real == prev).sum()), len(real), 0.5).pvalue
    return {"rotulo": rot, "n": int(len(real)), "acuracia": round(float(acc), 4),
            "majoritaria": round(float(maj), 4),
            "ganho_pp": round(float((acc - maj) * 100), 2),
            "p_vs_acaso": float(p),
            "kappa": round(float(cohen_kappa_score(real, prev)), 4),
            "mcc": round(float(matthews_corrcoef(real, prev)), 4),
            "prev_acima_pct": round(float((prev == "ACIMA").mean() * 100), 1)}


def imprime(m):
    if m is None:
        return
    ok = "  *" if m["p_vs_acaso"] < 0.05 else ""
    print(f"  {m['rotulo']:<34} {m['n']:>5,} {m['acuracia']:>8.1%} "
          f"{m['majoritaria']:>8.1%} {m['ganho_pp']:>+7.2f} {m['p_vs_acaso']:>9.4f}{ok}"
          f"   prevê ACIMA {m['prev_acima_pct']:>5.1f}%")


def limiar_expansivo(serie: pd.Series, minimo: int = MIN_HIST) -> pd.Series:
    """Mediana de tudo o que veio ANTES de cada ponto. Nunca olha o futuro."""
    return serie.shift(1).expanding(min_periods=minimo).median()


def main() -> None:
    print("=" * 92)
    print(f"  PREVER A VOLATILIDADE DO PREGÃO SEGUINTE — {TICKER}")
    print("=" * 92)

    # ── preços e o alvo ──────────────────────────────────────────────────────
    px = pd.read_csv(DADOS / "ohlcv_b3.csv", parse_dates=["Data"])
    px = px[px["Ticker"] == TICKER].sort_values("Data").reset_index(drop=True)
    # linha de base: média dos pregões [-6,-2], pulando os dois anteriores
    px["base_vol"] = px["Parkinson"].shift(2).rolling(JANELA_BASE).mean()
    px["razao_vol"] = px["Parkinson"] / px["base_vol"]
    px["alvo"] = np.where(px["razao_vol"] > 1.0, "ACIMA", "ABAIXO")
    pregoes = px["Data"].tolist()

    # ── os sinais da noite ───────────────────────────────────────────────────
    d = pd.read_csv(DADOS / "confronto_fontes_dias.csv", parse_dates=["data"])
    d = d.merge(px[["Data", "razao_vol", "alvo", "base_vol"]],
                left_on="data", right_on="Data", how="left")
    d = d[d["alvo"].notna() & d["razao_vol"].notna()].sort_values("data").reset_index(drop=True)
    print(f"\n  pregões com alvo e sinais: {len(d):,}")
    print(f"  o alvo é equilibrado? ACIMA em {(d['alvo']=='ACIMA').mean():.1%} dos casos")

    # ── construção dos sinais, todos sem olhar o futuro ──────────────────────
    # 1) INTENSIDADE do sentimento: o quanto a noite se afasta do seu normal
    saldo_n = (d["n_pos"] - d["n_neg"]) / d["n_tot"].replace(0, np.nan)
    d["int_news"] = (saldo_n - saldo_n.shift(1).rolling(60, min_periods=30).mean()).abs()
    saldo_c = (d["c_pos"] - d["c_neg"]) / d["c_tot"].replace(0, np.nan)
    d["int_cvm"] = (saldo_c - saldo_c.shift(1).rolling(60, min_periods=30).mean()).abs()

    # 2) QUANTIDADE de texto na noite
    d["qtd_news"] = d["n_tot"].astype(float)

    # 3) PRESENÇA de comunicado oficial
    d["tem_cvm"] = (d["c_tot"] > 0).astype(float)
    d["tem_fr"] = (d["c_fr"] > 0).astype(float)

    # limiares expansivos — só com o passado
    for c in ["int_news", "qtd_news", "int_cvm"]:
        d[f"lim_{c}"] = limiar_expansivo(d[c])

    res = {"ticker": TICKER, "n": int(len(d)),
           "alvo_acima_pct": round(float((d["alvo"] == "ACIMA").mean() * 100), 1),
           "arms": {}}

    cab = (f"\n  {'sinal usado':<34} {'dias':>5} {'acertou':>8} {'palpite':>8} "
           f"{'ganho':>7} {'p':>9}")

    # ── ARM 1: só notícia ────────────────────────────────────────────────────
    print("\n" + "=" * 92)
    print("  QUAL SINAL PREVÊ MELHOR QUE O PREÇO VAI SACUDIR MAIS QUE O NORMAL?")
    print("=" * 92)
    print(cab)
    print("  " + "-" * 88)

    testes = [
        ("notícia: quantidade de textos",
         np.where(d["qtd_news"] > d["lim_qtd_news"], "ACIMA", "ABAIXO"),
         d["lim_qtd_news"].notna()),
        ("notícia: intensidade do tom",
         np.where(d["int_news"] > d["lim_int_news"], "ACIMA", "ABAIXO"),
         d["lim_int_news"].notna() & d["int_news"].notna()),
        ("CVM: houve comunicado?",
         np.where(d["tem_cvm"] > 0, "ACIMA", "ABAIXO"),
         pd.Series(True, index=d.index)),
        ("CVM: houve Fato Relevante?",
         np.where(d["tem_fr"] > 0, "ACIMA", "ABAIXO"),
         pd.Series(True, index=d.index)),
        ("CVM: intensidade do tom",
         np.where(d["int_cvm"] > d["lim_int_cvm"], "ACIMA", "ABAIXO"),
         d["lim_int_cvm"].notna() & d["int_cvm"].notna()),
    ]
    for rot, prev, valido in testes:
        p = pd.Series(prev, index=d.index).where(valido)
        m = avalia(d["alvo"], p, rot)
        imprime(m)
        if m:
            res["arms"][rot] = m

    # ── ARM 2: as duas fontes juntas ─────────────────────────────────────────
    print("\n" + "=" * 92)
    print("  E JUNTANDO AS DUAS FONTES?")
    print("=" * 92)
    print("  Regra: prevê ACIMA se a noite teve muito texto OU tom fora do normal")
    print("         OU houve comunicado à CVM.")
    print(cab)
    print("  " + "-" * 88)

    muito_texto = d["qtd_news"] > d["lim_qtd_news"]
    tom_fora = d["int_news"] > d["lim_int_news"]
    combin = [
        ("notícia: texto OU tom", muito_texto | tom_fora, d["lim_qtd_news"].notna()),
        ("notícia (texto OU tom) + CVM",
         muito_texto | tom_fora | (d["tem_cvm"] > 0), d["lim_qtd_news"].notna()),
        ("notícia (texto OU tom) + Fato Relevante",
         muito_texto | tom_fora | (d["tem_fr"] > 0), d["lim_qtd_news"].notna()),
    ]
    for rot, cond, valido in combin:
        p = pd.Series(np.where(cond, "ACIMA", "ABAIXO"), index=d.index).where(valido)
        m = avalia(d["alvo"], p, rot)
        imprime(m)
        if m:
            res["arms"][rot] = m

    # ── ARM 3: só nas noites de Fato Relevante ───────────────────────────────
    fr = d[d["tem_fr"] > 0]
    if len(fr) >= 60:
        print("\n" + "=" * 92)
        print(f"  E SE OLHARMOS SÓ AS {len(fr):,} NOITES DE FATO RELEVANTE?")
        print("=" * 92)
        print(f"  nessas noites, o alvo já é ACIMA em {(fr['alvo']=='ACIMA').mean():.1%} "
              "dos casos")
        print(cab)
        print("  " + "-" * 88)
        for rot, cond in [
            ("FR: quantidade de texto", fr["qtd_news"] > fr["lim_qtd_news"]),
            ("FR: intensidade do tom", fr["int_news"] > fr["lim_int_news"]),
            ("FR: texto OU tom", (fr["qtd_news"] > fr["lim_qtd_news"]) |
                                 (fr["int_news"] > fr["lim_int_news"])),
        ]:
            p = pd.Series(np.where(cond, "ACIMA", "ABAIXO"), index=fr.index)
            p = p.where(fr["lim_qtd_news"].notna())
            m = avalia(fr["alvo"], p, rot)
            imprime(m)
            if m:
                res["arms"][rot] = m

    # ── comparação com a direção ─────────────────────────────────────────────
    print("\n" + "=" * 92)
    print("  PARA COMPARAR — o melhor resultado de DIREÇÃO desta pesquisa")
    print("=" * 92)
    try:
        cf = json.loads((DADOS / "confronto_corrigido.json").read_text(encoding="utf-8"))
        o = cf["fatorel_dev_ambos"]
        print(f"  {'direção, as duas fontes em noite de FR':<34} {o['n']:>5,} "
              f"{o['acuracia']:>8.1%} {o['maj']:>8.1%} {o['ganho_pp']:>+7.2f} "
              f"{o['p']:>9.4f}  *")
        res["referencia_direcao"] = o
    except Exception:                                             # noqa: BLE001
        pass

    d.to_csv(DADOS / "prever_volatilidade_dias.csv", index=False, encoding="utf-8-sig")
    (DADOS / "prever_volatilidade.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  gravados: prever_volatilidade.json e prever_volatilidade_dias.csv")


if __name__ == "__main__":
    main()
