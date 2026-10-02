# -*- coding: utf-8 -*-
# ==============================================================================
#   SÓ FATO RELEVANTE × TODOS OS COMUNICADOS — pedido do Prof. Julio (30/09/2026)
#
#   Reaproveita EXATAMENTE o protocolo do script 18 (Cap. 3: fusão precoce em
#   t-1, SVM-RBF e XGBoost com os mesmos hiperparâmetros, divisão cronológica
#   60/15/25, McNemar). O que muda é o bloco de atributos da CVM: aqui ele é
#   calculado duas vezes — uma só com Fato Relevante, outra com todos os
#   comunicados — para a pergunta do orientador: "o Fato Relevante sozinho
#   projeta melhor, pior ou igual a usar todos os comunicados?"
#
#   NÃO inclui o embedding de 768 dimensões (não entra em nenhuma das BRACOS
#   do script 18 que este reaproveita como baseline) para que as comparações
#   fiquem limpas: cada braço novo difere do seu baseline só pelo filtro de
#   categoria.
#
#   Saída: dados/fr_vs_todos_comunicados.json
# ==============================================================================
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import accuracy_score, f1_score, precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS, RAIZ = AQUI / "dados", AQUI.parent
TICKER = "PETR4"

XGB = dict(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
           colsample_bytree=0.9, random_state=42, eval_metric="logloss", n_jobs=-1)


# ──────────────────────────────────────────────────────────────────────────────
def bloco_cvm(so_categoria: str | None) -> pd.DataFrame:
    """Atributos da CVM em t-1, na mesma forma do script 18. so_categoria=None
    usa TODOS os comunicados; 'Fato Relevante' filtra só essa categoria."""
    a = pd.read_csv(DADOS / "rodada_A_casos.csv", low_memory=False,
                    usecols=["Protocolo_Entrega", "Ticker", "Categoria",
                             "Entrega", "Pregao_reacao"])
    a = a[a["Ticker"] == TICKER].copy()
    a["Entrega"] = pd.to_datetime(a["Entrega"], errors="coerce")
    a["Date"] = pd.to_datetime(a["Pregao_reacao"], errors="coerce")
    a = a[a["Entrega"].notna() & a["Date"].notna()]
    a = a[a["Entrega"].dt.hour >= 17]
    if so_categoria is not None:
        a = a[a["Categoria"] == so_categoria]

    c = pd.read_csv(DADOS / "cvm_classificado.csv", low_memory=False)
    c = a.merge(c[["Protocolo_Entrega", "p_pos", "p_neg", "p_neu", "Confianca"]],
                on="Protocolo_Entrega", how="inner")
    c["ism"] = c["p_pos"] - c["p_neg"]

    pref = "CVM_FR_" if so_categoria else "CVM_TODOS_"
    g = c.groupby("Date")
    f = pd.DataFrame({
        f"{pref}Sentimento_Ontem": g["ism"].mean(),
        f"{pref}Sentimento_Max_Ontem": g["ism"].max(),
        f"{pref}Sentimento_Min_Ontem": g["ism"].min(),
        f"{pref}Confianca_Ontem": g["Confianca"].mean(),
        f"{pref}Qtd_Ontem": g.size(),
    }).reset_index()
    f[f"{pref}Tem_Ontem"] = 1.0
    return f, [c for c in f.columns if c != "Date"]


def painel() -> tuple[pd.DataFrame, list, list]:
    b = pd.read_csv(RAIZ / "Mestrado_PETR4" / "base_master_petr4.csv", parse_dates=["Date"])
    f_fr, cols_fr = bloco_cvm("Fato Relevante")
    f_tot, cols_tot = bloco_cvm(None)
    d = b.merge(f_fr, on="Date", how="left").merge(f_tot, on="Date", how="left")
    for c in cols_fr + cols_tot:
        d[c] = d[c].fillna(0.0)
    d = d.dropna(subset=["Retorno_Ontem", "Volatilidade_Ontem", "Sentimento_Ontem",
                         "Alvo"]).reset_index(drop=True)
    return d, cols_fr, cols_tot


def corta(d: pd.DataFrame) -> tuple[slice, slice, slice]:
    n = len(d)
    a, b = int(n * 0.60), int(n * 0.75)
    return slice(0, a), slice(a, b), slice(b, n)


def mcnemar(y, a, b) -> dict:
    ca, cb = (a == y), (b == y)
    n01, n10 = int((~ca & cb).sum()), int((ca & ~cb).sum())
    if n01 + n10 == 0:
        return {"acertos_so_do_novo": 0, "acertos_so_do_antigo": 0, "p": 1.0}
    p = stats.binomtest(n01, n01 + n10, 0.5).pvalue
    return {"acertos_so_do_novo": n01, "acertos_so_do_antigo": n10, "p": float(p)}


def treina(d, cols, maj) -> dict:
    tr, va, te = corta(d)
    X = d[cols].fillna(0.0)
    y = d["Alvo"].astype(int)
    fit = slice(0, te.start)
    out = {}
    for mn, mod in [
        ("SVM-RBF", make_pipeline(StandardScaler(), SVC(kernel="rbf", probability=True, random_state=42))),
        ("XGBoost", XGBClassifier(**XGB)),
    ]:
        m = mod.fit(X.iloc[fit], y.iloc[fit])
        pv = m.predict(X.iloc[te])
        pp = m.predict_proba(X.iloc[te])[:, 1]
        yt = y.iloc[te].values
        out[mn] = {
            "n_teste": int(len(yt)),
            "acuracia": round(float(accuracy_score(yt, pv)), 4),
            "precisao": round(float(precision_score(yt, pv, zero_division=0)), 4),
            "f1": round(float(f1_score(yt, pv, zero_division=0)), 4),
            "auc": round(float(roc_auc_score(yt, pp)), 4),
            "ganho_pp_vs_majoritaria": round(float(accuracy_score(yt, pv) - maj) * 100, 2),
            "p_binomial_vs_majoritaria": float(
                stats.binomtest(int((yt == pv).sum()), len(yt), maj).pvalue),
            "_prev": pv,
        }
    return out


def main() -> None:
    d, cols_fr, cols_tot = painel()
    tr, va, te = corta(d)
    yte = d["Alvo"].astype(int).iloc[te].values
    maj = max(yte.mean(), 1 - yte.mean())

    print("=" * 100)
    print("  SÓ FATO RELEVANTE × TODOS OS COMUNICADOS DA CVM — PETR4")
    print("=" * 100)
    print(f"\n  pregões: {len(d):,}  teste: {len(yte):,}   classe majoritária: {maj:.2%}")
    print(f"  pregões do teste com Fato Relevante na véspera: "
          f"{int(d['CVM_FR_Tem_Ontem'].iloc[te].sum()):,}")
    print(f"  pregões do teste com QUALQUER comunicado na véspera: "
          f"{int(d['CVM_TODOS_Tem_Ontem'].iloc[te].sum()):,}")

    BASE = ["Retorno_Ontem", "Volatilidade_Ontem"]
    FUSAO = BASE + ["Sentimento_Ontem"]

    BRACOS = [
        ("1. apenas preços", BASE),
        ("2. Data Fusion: preços + notícia", FUSAO),
        ("3. preços + CVM (SÓ Fato Relevante)", BASE + cols_fr),
        ("4. preços + CVM (TODOS os comunicados)", BASE + cols_tot),
        ("5. Data Fusion + CVM (SÓ Fato Relevante)", FUSAO + cols_fr),
        ("6. Data Fusion + CVM (TODOS os comunicados)", FUSAO + cols_tot),
    ]

    print(f"\n  {'braço':<46} {'modelo':<9} {'acur':>7} {'ganho pp':>9} {'AUC':>7} {'p vs maj':>9}")
    print("  " + "-" * 92)
    res, guarda = {"n": {"total": int(len(d)), "teste": int(len(yte))},
                  "majoritaria_teste": round(float(maj), 4), "direcao": {}}, {}
    for nome, cols in BRACOS:
        o = treina(d, cols, maj)
        guarda[nome] = {k: v.pop("_prev") for k, v in o.items()}
        res["direcao"][nome] = o
        for mn, m in o.items():
            sinal = "  *" if m["p_binomial_vs_majoritaria"] < 0.05 else ""
            print(f"  {nome:<46} {mn:<9} {m['acuracia']:>6.2%} {m['ganho_pp_vs_majoritaria']:>+8.2f} "
                  f"{m['auc']:>7.3f} {m['p_binomial_vs_majoritaria']:>9.4f}{sinal}")

    print("\n" + "=" * 100)
    print("  McNEMAR — pares que respondem diretamente ao pedido")
    print("=" * 100)
    PARES = [
        ("o Fato Relevante sozinho acrescenta sobre só preços?", "1. apenas preços",
         "3. preços + CVM (SÓ Fato Relevante)"),
        ("usar SÓ Fato Relevante é melhor/pior que usar TODOS os comunicados? (sem notícia)",
         "4. preços + CVM (TODOS os comunicados)", "3. preços + CVM (SÓ Fato Relevante)"),
        ("Fato Relevante acrescenta sobre a notícia de jornal?", "2. Data Fusion: preços + notícia",
         "5. Data Fusion + CVM (SÓ Fato Relevante)"),
        ("usar SÓ Fato Relevante + notícia é melhor/pior que TODOS os comunicados + notícia?",
         "6. Data Fusion + CVM (TODOS os comunicados)", "5. Data Fusion + CVM (SÓ Fato Relevante)"),
    ]
    res["mcnemar"] = {}
    for rot, a, b in PARES:
        for mn in ["SVM-RBF", "XGBoost"]:
            m = mcnemar(yte, guarda[a][mn], guarda[b][mn])
            res["mcnemar"][f"{mn} — {rot}"] = m
            sinal = "  *" if m["p"] < 0.05 else ""
            print(f"  {mn:<9} {rot}")
            print(f"            ganhou {m['acertos_so_do_novo']:>3} × perdeu "
                  f"{m['acertos_so_do_antigo']:>3}   p = {m['p']:.4f}{sinal}")

    (DADOS / "fr_vs_todos_comunicados.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print("\n  gravado: dados/fr_vs_todos_comunicados.json")


if __name__ == "__main__":
    main()
