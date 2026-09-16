# -*- coding: utf-8 -*-
# ==============================================================================
#   RODADA B — a NOSSA classificação acerta a direção do pregão seguinte?
#
#   A Rodada A mostrou que a publicação move o preço, mas o rótulo da CVM não
#   tem sinal: ele diz que algo aconteceu, não se foi bom ou ruim. Por isso a
#   direção deu nula lá, e tinha de dar.
#
#   Aqui entra a nossa classificação, que TEM sinal. É o único teste capaz de
#   responder "para que lado o preço vai" — e é onde a contribuição desta
#   dissertação se prova ou não.
#
#   A REGRA DE ACERTO, declarada antes de rodar:
#     classificamos POSITIVO  -> acerta se o preço SOBE
#     classificamos NEGATIVO  -> acerta se o preço CAI
#     classificamos NEUTRO    -> não faz previsão de direção; fica de fora do
#                                cálculo de acurácia, e é reportado à parte
#
#   A medida principal é o GAP DE ABERTURA, porque a notícia saiu depois que o
#   mercado fechou: é o primeiro instante em que ela pôde ser precificada.
#
#   Entrada: CVM/dados/cvm_classificado.csv (produzido no Colab)
#   Saída:   CVM/dados/rodada_B.json e rodada_B_casos.csv
# ==============================================================================
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"

CLASSIF = DADOS / "cvm_classificado.csv"
BASE_VOL = "razaoVol_1 semana (-6 a -2)"
BASE_QTD = "razaoVolume_1 semana (-6 a -2)"

GENERICOS = (r"^not[íi]cia divulgada na m[íi]dia$|^negocia[çc][õo]es at[íi]picas|"
             r"^esclarecimento sobre|^resposta a of[íi]cio|^comunicado ao mercado$|"
             r"^fato relevante$|^esclarecimentos$")


def metricas(verdade, previsto, rot="") -> dict:
    """Todos os índices de classificação, de uma vez."""
    from sklearn.metrics import (accuracy_score, precision_recall_fscore_support,
                                 cohen_kappa_score, matthews_corrcoef,
                                 confusion_matrix)
    acc = accuracy_score(verdade, previsto)
    pr, rc, f1, sup = precision_recall_fscore_support(
        verdade, previsto, labels=["ALTA", "BAIXA"], zero_division=0)
    prm, rcm, f1m, _ = precision_recall_fscore_support(
        verdade, previsto, average="macro", zero_division=0)
    n = len(verdade)
    acertos = int((np.array(verdade) == np.array(previsto)).sum())
    binom = stats.binomtest(acertos, n, 0.5).pvalue if n else np.nan
    # classe majoritária: acertar sempre o lado mais frequente
    maj = pd.Series(verdade).value_counts(normalize=True).iloc[0]
    return {"rotulo": rot, "n": int(n), "acertos": acertos,
            "acuracia": round(float(acc), 4),
            "classe_majoritaria": round(float(maj), 4),
            "ganho_sobre_majoritaria": round(float(acc - maj), 4),
            "p_binomial_vs_50": float(binom),
            "precisao_ALTA": round(float(pr[0]), 4), "recall_ALTA": round(float(rc[0]), 4),
            "f1_ALTA": round(float(f1[0]), 4), "n_ALTA": int(sup[0]),
            "precisao_BAIXA": round(float(pr[1]), 4), "recall_BAIXA": round(float(rc[1]), 4),
            "f1_BAIXA": round(float(f1[1]), 4), "n_BAIXA": int(sup[1]),
            "f1_macro": round(float(f1m), 4),
            "kappa": round(float(cohen_kappa_score(verdade, previsto)), 4),
            "mcc": round(float(matthews_corrcoef(verdade, previsto)), 4),
            "matriz": confusion_matrix(verdade, previsto,
                                       labels=["ALTA", "BAIXA"]).tolist()}


def imprime(m: dict) -> None:
    print(f"\n  ----- {m['rotulo']} -----")
    print(f"    casos ...................... {m['n']:,}")
    print(f"    ACURÁCIA ................... {m['acuracia']:.1%}  "
          f"({m['acertos']:,} acertos)")
    print(f"    classe majoritária ......... {m['classe_majoritaria']:.1%}")
    print(f"    GANHO sobre a majoritária .. {m['ganho_sobre_majoritaria']*100:+.2f} p.p.")
    print(f"    valor-p contra o acaso ..... {m['p_binomial_vs_50']:.4f}"
          f"{'  *' if m['p_binomial_vs_50'] < 0.05 else '   (não significativo)'}")
    print(f"    F1 macro ................... {m['f1_macro']:.4f}")
    print(f"    kappa ...................... {m['kappa']:+.4f}")
    print(f"    MCC ........................ {m['mcc']:+.4f}")
    print(f"    ALTA : precisão {m['precisao_ALTA']:.3f} | recall {m['recall_ALTA']:.3f} "
          f"| F1 {m['f1_ALTA']:.3f} | n={m['n_ALTA']}")
    print(f"    BAIXA: precisão {m['precisao_BAIXA']:.3f} | recall {m['recall_BAIXA']:.3f} "
          f"| F1 {m['f1_BAIXA']:.3f} | n={m['n_BAIXA']}")


def main() -> None:
    print("=" * 78)
    print("RODADA B — A NOSSA CLASSIFICAÇÃO ACERTA A DIREÇÃO?")
    print("=" * 78)

    if not CLASSIF.exists():
        print(f"\n  FALTA o arquivo {CLASSIF.name}.")
        print("  Rode o caderno CVM/colab/CVM_classificar_FinBERT.ipynb no Colab,")
        print("  baixe o cvm_classificado.csv e coloque em CVM/dados/.")
        sys.exit(1)

    casos = pd.read_csv(DADOS / "rodada_A_casos.csv",
                        parse_dates=["Entrega", "Pregao_reacao"])
    cls = pd.read_csv(CLASSIF, dtype=str)

    # junção pelo protocolo, que é único por documento
    chave = "Protocolo_Entrega"
    if chave not in cls.columns:
        sys.exit(f"o arquivo classificado precisa da coluna {chave}")

    base = pd.read_csv(DADOS / "cvm_para_classificar.csv", dtype=str)
    base = base[["Protocolo_Entrega", "Assunto", "Ticker"]].rename(
        columns={"Assunto": "Assunto_base"})
    cls = cls.merge(base, on=chave, how="left", suffixes=("", "_b"))

    d = casos.merge(cls[[chave, "Rotulo", "Indice", "Confianca", "Assunto"]]
                    .rename(columns={"Assunto": "Assunto_cls"}),
                    left_on="Assunto", right_on="Assunto_cls", how="left") \
        if chave not in casos.columns else casos.merge(cls, on=chave, how="left")

    d = d[d["Rotulo"].notna()].copy()
    d["Indice"] = pd.to_numeric(d["Indice"], errors="coerce")
    print(f"\n  eventos com classificação: {len(d):,}")
    print("  distribuição:", d["Rotulo"].value_counts().to_dict())

    d["Generico"] = d["Assunto"].fillna("").str.strip().str.lower().str.match(GENERICOS)
    grupo = d.groupby(["Ticker", "Pregao_reacao"])["Assunto"].transform("size")
    d["Atribuivel"] = grupo == 1

    res = {"n": int(len(d)), "dist": d["Rotulo"].value_counts().to_dict(), "testes": {}}

    # ── B.1 acurácia direcional ──────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("  B.1  ACURÁCIA DIRECIONAL")
    print("  Positivo prevê ALTA; Negativo prevê BAIXA; Neutro não prevê nada.")
    print("=" * 78)

    for alvo_rot, alvo_col in (("GAP DE ABERTURA", "Gap_d1"),
                               ("PREGÃO INTEIRO", "Retorno_d1")):
        for filtro_rot, sub in (("todos os eventos", d),
                                ("só os atribuíveis a 1 documento",
                                 d[d["Atribuivel"] & ~d["Generico"]])):
            s = sub[sub["Rotulo"].isin(["Positive", "Negative"])].dropna(subset=[alvo_col])
            if len(s) < 30:
                continue
            prev = np.where(s["Rotulo"] == "Positive", "ALTA", "BAIXA")
            real = np.where(s[alvo_col] > 0, "ALTA", "BAIXA")
            m = metricas(real, prev, f"{alvo_rot} — {filtro_rot}")
            imprime(m)
            res["testes"][m["rotulo"]] = m

    # ── B.2 o índice contínuo correlaciona com o retorno? ────────────────────
    print("\n" + "=" * 78)
    print("  B.2  O ÍNDICE CONTÍNUO acompanha o retorno?")
    print("=" * 78)
    for rot, col in (("gap de abertura", "Gap_d1"), ("pregão inteiro", "Retorno_d1")):
        s = d.dropna(subset=["Indice", col])
        rp, pp = stats.pearsonr(s["Indice"], s[col])
        rs, ps = stats.spearmanr(s["Indice"], s[col])
        print(f"  {rot:<18} Pearson {rp:+.4f} (p={pp:.4f})   "
              f"Spearman {rs:+.4f} (p={ps:.4f})")
        res.setdefault("correlacao", {})[rot] = {
            "pearson": round(float(rp), 4), "p_pearson": float(pp),
            "spearman": round(float(rs), 4), "p_spearman": float(ps), "n": int(len(s))}
    print("\n  Sinal POSITIVO esperado: quanto melhor a notícia, maior o retorno.")

    # ── B.3 magnitude por classe ─────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("  B.3  VOLATILIDADE E VOLUME POR CLASSE DE SENTIMENTO")
    print("=" * 78)
    print(f"  {'classe':<12} {'n':>6} {'volatilidade':>14} {'volume':>10} "
          f"{'retorno médio':>15}")
    print("  " + "-" * 62)
    for cls_ in ["Positive", "Neutral", "Negative"]:
        s = d[d["Rotulo"] == cls_]
        if len(s) < 30:
            continue
        print(f"  {cls_:<12} {len(s):>6,} {s[BASE_VOL].mean():>14.3f} "
              f"{s[BASE_QTD].mean():>10.3f} {s['Retorno_d1'].mean()*100:>14.4f}%")
        res.setdefault("por_classe", {})[cls_] = {
            "n": int(len(s)), "volatilidade": round(float(s[BASE_VOL].mean()), 4),
            "volume": round(float(s[BASE_QTD].mean()), 4),
            "retorno_pct": round(float(s["Retorno_d1"].mean() * 100), 4)}

    # ── B.4 o sentimento acrescenta algo além da categoria? ──────────────────
    print("\n" + "=" * 78)
    print("  B.4  O SENTIMENTO ACRESCENTA ALGO ALÉM DA CATEGORIA DA CVM?")
    print("=" * 78)
    try:
        import statsmodels.api as sm
        s = d.dropna(subset=["Indice", BASE_VOL, "Gap_d1"]).copy()
        s["eh_FR"] = (s["Categoria"] == "Fato Relevante").astype(float)
        s["abs_gap"] = s["Gap_d1"].abs()
        for alvo, rot in ((BASE_VOL, "volatilidade"), ("abs_gap", "tamanho do gap")):
            X = sm.add_constant(s[["eh_FR", "Indice"]])
            mod = sm.OLS(s[alvo], X).fit()
            print(f"\n  alvo: {rot}   (n={len(s):,}, R² = {mod.rsquared:.4f})")
            for nome in ("eh_FR", "Indice"):
                print(f"    {nome:<10} coef {mod.params[nome]:+.5f}   "
                      f"p = {mod.pvalues[nome]:.4f}"
                      f"{'  *' if mod.pvalues[nome] < 0.05 else ''}")
            res.setdefault("regressao", {})[rot] = {
                "r2": round(float(mod.rsquared), 5),
                **{k: {"coef": round(float(mod.params[k]), 6),
                       "p": float(mod.pvalues[k])} for k in ("eh_FR", "Indice")}}
    except Exception as e:                                        # noqa: BLE001
        print(f"  (regressão não executada: {e})")

    d.to_csv(DADOS / "rodada_B_casos.csv", index=False, encoding="utf-8-sig")
    (DADOS / "rodada_B.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  gravados: rodada_B_casos.csv ({len(d):,}) e rodada_B.json")


if __name__ == "__main__":
    main()
