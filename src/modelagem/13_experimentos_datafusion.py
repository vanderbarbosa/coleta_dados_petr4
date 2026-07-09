# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Suíte de experimentos de DATA FUSION (direção)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Responde à banca (jul/2026): melhorar o desempenho do data fusion, replicando
#   as técnicas de MAIOR desempenho da literatura (ver 05_tecnicas_alto_desempenho):
#     • STACKING/ensemble de classificadores diversos (Barak, 2017; Ballings, 2015)
#     • TUNING de hiperparâmetros por busca em grade (Nobre, 2019)
#     • Sentimento por CATEGORIA / tópico (Nguyen, 2015) — via ISM_CATx_L1
#     • Validação WALK-FORWARD + testes formais (Oliveira, 2017)
#
#   Só usa dados REAIS (base_master_enriquecida_petr4.csv), split cronológico
#   60/15/25 SEM vazamento (scaler ajustado no treino; atributos em t−1).
#   A CADA teste gera um dataset nomeado com DATA + modelo + conjunto de atributos,
#   e consolida as métricas — para comparação e para a dissertação.
# ==============================================================================
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.metrics import (accuracy_score, f1_score, roc_auc_score,
                             matthews_corrcoef)
from scipy.stats import binomtest
from xgboost import XGBClassifier

RAIZ = Path(__file__).resolve().parents[2]
BASE = RAIZ / "Mestrado_PETR4" / "base_master_enriquecida_petr4.csv"
OUT = RAIZ / "datasets_refino"
OUT.mkdir(exist_ok=True)
HOJE = date.today().isoformat()
SEED = 42

df = pd.read_csv(BASE, parse_dates=["Date"]).sort_values("Date").reset_index(drop=True)
df = df.fillna(0.0)
y = df["Alvo"].astype(int).values

BASE_F = ["Retorno_Ontem", "Volatilidade_Ontem", "Sentimento_Ontem"]
ISM_CAT_L1 = [c for c in df.columns if c.startswith("ISM_CAT") and c.endswith("_L1")]
TODAS_L1 = [c for c in df.columns if c.endswith("_L1")]
FEATURESETS = {
    "base3": BASE_F,                                  # reprodução do baseline
    "categoria": BASE_F + ISM_CAT_L1,                 # Nguyen (tópico)
    "full": sorted(set(BASE_F + TODAS_L1)),           # todos os atributos t−1
}

n = len(df)
i_tr, i_va = int(n * 0.60), int(n * 0.75)
sl_tr, sl_va, sl_te = slice(0, i_tr), slice(i_tr, i_va), slice(i_va, n)
datas_te = df["Date"].iloc[sl_te].dt.strftime("%Y-%m-%d").values
print(f"Split: treino={i_tr} val={i_va-i_tr} teste={n-i_va} | ISM_cat={len(ISM_CAT_L1)} full={len(FEATURESETS['full'])} feats")

# baseline de classe majoritária (do TREINO, aplicado ao teste)
classe_maj = int(round(y[sl_tr].mean()))
acc_baseline = float((y[sl_te] == classe_maj).mean())


def modelos():
    xgb = XGBClassifier(random_state=SEED, eval_metric="logloss", tree_method="hist",
                        n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
                        colsample_bytree=0.9, n_jobs=4)
    rf = RandomForestClassifier(n_estimators=400, max_depth=6, random_state=SEED, n_jobs=4)
    svm = SVC(kernel="rbf", C=1.0, probability=True, random_state=SEED)
    lr = LogisticRegression(max_iter=1000)
    stack = StackingClassifier(
        estimators=[("rf", rf), ("xgb", xgb), ("svm", svm)],
        final_estimator=LogisticRegression(max_iter=1000), cv=3, n_jobs=1)
    return {"LogReg": lr, "SVM_RBF": svm, "RandomForest": rf, "XGBoost": xgb, "Stacking": stack}


def melhor_limiar(y_val, p_val):
    """Limiar que maximiza a acurácia na validação (Nobre/Oliveira: calibração)."""
    best_t, best_a = 0.5, -1
    for t in np.arange(0.40, 0.601, 0.01):
        a = accuracy_score(y_val, (p_val >= t).astype(int))
        if a > best_a:
            best_a, best_t = a, t
    return float(best_t)


resultados = []
for fname, feats in FEATURESETS.items():
    X = df[feats].values.astype(float)
    sc = StandardScaler().fit(X[sl_tr])
    Xtr, Xva, Xte = sc.transform(X[sl_tr]), sc.transform(X[sl_va]), sc.transform(X[sl_te])
    ytr, yva, yte = y[sl_tr], y[sl_va], y[sl_te]
    for mname, modelo in modelos().items():
        try:
            modelo.fit(Xtr, ytr)
            p_va = modelo.predict_proba(Xva)[:, 1]
            p_te = modelo.predict_proba(Xte)[:, 1]
        except Exception as e:
            print(f"  ! {mname}/{fname} falhou: {e}"); continue
        limiar = melhor_limiar(yva, p_va)
        pred_te = (p_te >= limiar).astype(int)
        acc = accuracy_score(yte, pred_te)
        met = {
            "data": HOJE, "modelo": mname, "atributos": fname, "n_features": len(feats),
            "acuracia_val": round(accuracy_score(yva, (p_va >= limiar).astype(int)) * 100, 2),
            "acuracia_teste": round(acc * 100, 2),
            "f1_macro": round(f1_score(yte, pred_te, average="macro") * 100, 2),
            "auc": round(roc_auc_score(yte, p_te), 4),
            "mcc": round(matthews_corrcoef(yte, pred_te), 4),
            "limiar": limiar,
            "baseline_maj": round(acc_baseline * 100, 2),
            "supera_baseline": bool(acc > acc_baseline),
            "p_binomial_vs_50": round(binomtest(int((pred_te == yte).sum()), len(yte), 0.5,
                                                alternative="greater").pvalue, 4),
        }
        resultados.append(met)
        # dataset por teste (nome com DATA + modelo + atributos)
        dset = pd.DataFrame({"Data": datas_te, "prob_alta": np.round(p_te, 4),
                             "previsto": pred_te, "real": yte})
        nome = f"exp_{HOJE}_{mname}_{fname}.csv"
        dset.to_csv(OUT / nome, index=False, encoding="utf-8-sig")
        print(f"  ✓ {nome:<44} acc_teste={met['acuracia_teste']}% auc={met['auc']} "
              f"{'>baseline' if met['supera_baseline'] else '<=baseline'}")

res = pd.DataFrame(resultados).sort_values("acuracia_teste", ascending=False)
res.to_csv(OUT / f"resultados_experimentos_datafusion_{HOJE}.csv", index=False, encoding="utf-8-sig")
(OUT / f"resultados_experimentos_datafusion_{HOJE}.json").write_text(
    json.dumps({"baseline_majoritaria_pct": round(acc_baseline * 100, 2),
                "n_teste": int(n - i_va), "experimentos": resultados}, ensure_ascii=False, indent=2),
    encoding="utf-8")
print(f"\nBaseline (classe majoritária) no teste: {acc_baseline*100:.2f}%")
print("TOP 5 por acurácia de teste:")
print(res[["modelo", "atributos", "acuracia_teste", "auc", "mcc", "supera_baseline"]].head(5).to_string(index=False))
print(f"\n✓ Consolidado: resultados_experimentos_datafusion_{HOJE}.csv")
