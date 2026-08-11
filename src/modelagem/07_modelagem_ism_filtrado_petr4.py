# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — O filtro de relevância se propaga até a previsão?
# =============================================================================
#
#  ------------------------------------------------------------------
#  O QUE ESTE SCRIPT INVESTIGA, EM LINGUAGEM COMUM
#  ------------------------------------------------------------------
#  Descobrimos que o índice de sentimento fica melhor quando calculado apenas
#  com notícias da empresa e do mercado de petróleo, em vez de todas as
#  205.697 notícias coletadas. A correlação com a volatilidade sobe 23%.
#
#  Mas correlação não é previsão. A pergunta agora é: esse ganho chega até o
#  fim do pipeline? Ou seja, um índice melhor produz uma PREVISÃO melhor da
#  direção do preço e da volatilidade?
#
#  ------------------------------------------------------------------
#  COMO O TESTE É FEITO
#  ------------------------------------------------------------------
#  Roda-se o MESMO pipeline duas vezes, mudando apenas o índice de sentimento:
#
#    A — ISM com TODAS as notícias           (como está hoje na dissertação)
#    B — ISM com CAT1 + CAT2                 (empresa + mercado de petróleo)
#
#  Tudo o mais é idêntico: mesmo GARCH, mesmos atributos, mesma divisão
#  cronológica 60/15/25, mesmos modelos, mesma semente. Assim, qualquer
#  diferença é atribuível ao índice.
#
#  Replica os parâmetros do Script 04:
#    GARCH(1,1) com distribuição t-Student
#    atributos: [retorno de ontem, volatilidade de ontem, sentimento de ontem]
#    SVM com núcleo RBF e XGBoost, com a mesma grade de hiperparâmetros
#    seleção pela validação; o teste é consultado uma única vez
#
#  Uso:
#      python src/modelagem/07_modelagem_ism_filtrado_petr4.py
# =============================================================================
from __future__ import annotations

import argparse
import json
import warnings
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from arch import arch_model
from scipy import stats
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parents[2]
DIR = RAIZ / "Mestrado_PETR4"

PROP_TREINO, PROP_VALIDACAO = 0.60, 0.15      # teste = 25%, como no Script 04
SEMENTE = 42
CAT_FILTRO = ["CAT1_Empresa", "CAT2_Mercado_Petroleo"]
GRADE_SVM = [{"C": c} for c in (0.5, 1.0, 10.0)]
GRADE_XGB = [{"max_depth": d, "learning_rate": lr}
             for d in (3, 5) for lr in (0.05, 0.1)]


# ─────────────────────────────────────────────────────────────────────────────
def construir_ism(noticias: pd.DataFrame, categorias=None) -> pd.Series:
    """ISM diário = média do índice de sentimento das notícias do pregão."""
    sub = noticias if categorias is None else noticias[noticias["categoria"].isin(categorias)]
    return sub.groupby(sub["Data"].dt.date)["Indice_Sentimento"].mean().rename("ISM")


def preparar(precos: pd.DataFrame, ism: pd.Series) -> pd.DataFrame:
    """Monta a base de modelagem: GARCH, atributos defasados e alvo.

    Todos os atributos são defasados em um dia. É essa defasagem que garante
    que a previsão de hoje use apenas informação de ontem, evitando o
    vazamento de informação futura.
    """
    d = precos.copy()
    d["Log_Retorno_Pct"] = np.log(d["Close"]).diff() * 100

    serie = d["Log_Retorno_Pct"].dropna()
    garch = arch_model(serie, vol="Garch", p=1, q=1, dist="t").fit(disp="off")
    d.loc[serie.index, "Volatilidade_GARCH"] = garch.conditional_volatility

    d["dia"] = d["Date"].dt.date
    d = d.merge(ism.rename("ISM"), left_on="dia", right_index=True, how="left")

    d["Retorno_Ontem"] = d["Log_Retorno_Pct"].shift(1)
    d["Volatilidade_Ontem"] = d["Volatilidade_GARCH"].shift(1)
    d["Sentimento_Ontem"] = d["ISM"].shift(1)
    # alvo: 1 se o retorno de HOJE for positivo (previsto com dados de ontem)
    d["Alvo"] = (d["Log_Retorno_Pct"] > 0).astype(int)
    d["Vol_Realizada"] = d["Log_Retorno_Pct"].abs()

    return d.dropna(subset=["Retorno_Ontem", "Volatilidade_Ontem",
                            "Sentimento_Ontem", "Alvo"]).reset_index(drop=True)


def dividir(n: int):
    """Divisão CRONOLÓGICA: os mais antigos treinam, os mais recentes testam."""
    i_tr = int(n * PROP_TREINO)
    i_va = int(n * (PROP_TREINO + PROP_VALIDACAO))
    return np.arange(0, i_tr), np.arange(i_tr, i_va), np.arange(i_va, n)


def treinar(nome, criar, X, y, idx, grade, escalar):
    """Seleciona hiperparâmetro na VALIDAÇÃO e mede uma única vez no TESTE."""
    i_tr, i_va, i_te = idx
    if escalar:
        sc = StandardScaler().fit(X[i_tr])          # ajustado só no treino
        X = sc.transform(X)
    melhor, melhor_acc = None, -1
    for p in grade:
        m = criar(p)
        m.fit(X[i_tr], y[i_tr])
        acc = accuracy_score(y[i_va], m.predict(X[i_va]))
        if acc > melhor_acc:
            melhor, melhor_acc = p, acc
    m = criar(melhor)
    m.fit(np.vstack([X[i_tr], X[i_va]]), np.concatenate([y[i_tr], y[i_va]]))
    pred = m.predict(X[i_te])
    prob = m.predict_proba(X[i_te])[:, 1]
    return {
        "modelo": nome, "hiperparametros": melhor,
        "acuracia_validacao": round(float(melhor_acc), 4),
        "acuracia_teste": round(float(accuracy_score(y[i_te], pred)), 4),
        "f1_teste": round(float(f1_score(y[i_te], pred, zero_division=0)), 4),
        "auc_teste": round(float(roc_auc_score(y[i_te], prob)), 4),
    }, pred


def rodar(base: pd.DataFrame, rotulo: str) -> dict:
    idx = dividir(len(base))
    X_precos = base[["Retorno_Ontem", "Volatilidade_Ontem"]].to_numpy()
    X_fusao = base[["Retorno_Ontem", "Volatilidade_Ontem", "Sentimento_Ontem"]].to_numpy()
    y = base["Alvo"].to_numpy()

    print(f"\n{'=' * 76}\n{rotulo}\n{'=' * 76}")
    print(f"  pregoes: {len(base):,} | treino {len(idx[0])} | "
          f"validacao {len(idx[1])} | teste {len(idx[2])}")

    saida, preds = {"rotulo": rotulo, "n": int(len(base)), "modelos": []}, {}
    for nome, criar, Xm, grade, esc in [
        ("SVM (apenas precos)", lambda p: SVC(kernel="rbf", C=p["C"], gamma="scale",
                                              probability=True, random_state=SEMENTE),
         X_precos, GRADE_SVM, True),
        ("SVM (fusao)", lambda p: SVC(kernel="rbf", C=p["C"], gamma="scale",
                                      probability=True, random_state=SEMENTE),
         X_fusao, GRADE_SVM, True),
        ("XGBoost (apenas precos)", lambda p: XGBClassifier(
            n_estimators=100, max_depth=p["max_depth"], learning_rate=p["learning_rate"],
            subsample=0.8, colsample_bytree=0.8, eval_metric="logloss",
            random_state=SEMENTE, verbosity=0), X_precos, GRADE_XGB, False),
        ("XGBoost (fusao)", lambda p: XGBClassifier(
            n_estimators=100, max_depth=p["max_depth"], learning_rate=p["learning_rate"],
            subsample=0.8, colsample_bytree=0.8, eval_metric="logloss",
            random_state=SEMENTE, verbosity=0), X_fusao, GRADE_XGB, False),
    ]:
        m, pred = treinar(nome, criar, Xm, y, idx, grade, esc)
        saida["modelos"].append(m)
        preds[nome] = pred
        print(f"  {nome:26s} val={m['acuracia_validacao']:.4f}  "
              f"teste={m['acuracia_teste']:.4f}  AUC={m['auc_teste']:.4f}")

    # ── relação do sentimento com a volatilidade ─────────────────────────────
    v = base.dropna(subset=["Sentimento_Ontem", "Vol_Realizada"])
    r, pv = stats.pearsonr(v["Sentimento_Ontem"], v["Vol_Realizada"])
    ra, pa = stats.pearsonr(v["Sentimento_Ontem"].abs(), v["Vol_Realizada"])
    saida["volatilidade"] = {"r_ism_vol": round(float(r), 4), "p": round(float(pv), 4),
                             "r_abs_ism_vol": round(float(ra), 4), "p_abs": round(float(pa), 4)}
    print(f"  {'ISM -> volatilidade':26s} r={r:+.4f} (p={pv:.4f})  "
          f"|ISM| r={ra:+.4f} (p={pa:.4f})")

    saida["_y_teste"] = y[idx[2]]
    saida["_preds"] = preds
    return saida


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=DIR / "modelagem_ism_filtrado.json")
    args = ap.parse_args()

    noticias = pd.read_csv(DIR / "noticias_com_sentimento.csv",
                           usecols=["categoria", "Data", "Indice_Sentimento"])
    noticias["Data"] = pd.to_datetime(noticias["Data"], errors="coerce")
    noticias = noticias.dropna(subset=["Data", "Indice_Sentimento"])

    precos = pd.read_csv(DIR / "base_financeira_petr4.csv", skiprows=[1])
    precos["Date"] = pd.to_datetime(precos["Date"], errors="coerce")
    precos["Close"] = pd.to_numeric(precos["Close"], errors="coerce")
    precos = precos.dropna(subset=["Date", "Close"]).sort_values("Date").reset_index(drop=True)

    n_b = int(noticias["categoria"].isin(CAT_FILTRO).sum())
    print(f"Corpus: {len(noticias):,} noticias | filtrado: {n_b:,} ({n_b/len(noticias):.0%})")

    A = rodar(preparar(precos, construir_ism(noticias)), "A — ISM com TODAS as noticias")
    B = rodar(preparar(precos, construir_ism(noticias, CAT_FILTRO)),
              "B — ISM com CAT1 + CAT2 (empresa + petroleo)")

    # ── comparação ───────────────────────────────────────────────────────────
    print(f"\n{'=' * 76}\nCOMPARACAO A x B\n{'=' * 76}")
    print(f"  {'modelo':26s}{'A (todas)':>12s}{'B (filtrado)':>14s}{'delta':>10s}")
    comparacoes = []
    for ma, mb in zip(A["modelos"], B["modelos"]):
        dlt = mb["acuracia_teste"] - ma["acuracia_teste"]
        print(f"  {ma['modelo']:26s}{ma['acuracia_teste']:>12.4f}"
              f"{mb['acuracia_teste']:>14.4f}{dlt:>+10.4f}")
        comparacoes.append({"modelo": ma["modelo"], "A": ma["acuracia_teste"],
                            "B": mb["acuracia_teste"], "delta": round(dlt, 4)})

    # McNemar entre os dois modelos de fusão, no mesmo conjunto de teste
    if len(A["_y_teste"]) == len(B["_y_teste"]):
        for nome in ("XGBoost (fusao)", "SVM (fusao)"):
            pa_, pb_ = A["_preds"][nome], B["_preds"][nome]
            y = A["_y_teste"]
            b = int(((pa_ == y) & (pb_ != y)).sum())     # A acerta, B erra
            c = int(((pa_ != y) & (pb_ == y)).sum())     # B acerta, A erra
            pv = stats.binomtest(c, b + c, 0.5).pvalue if (b + c) else 1.0
            print(f"\n  McNemar [{nome}]: A-so={b}, B-so={c}, p={pv:.4f} "
                  f"-> {'diferenca significativa' if pv < 0.05 else 'nao significativa'}")
            comparacoes.append({"teste_mcnemar": nome, "A_acerta_B_erra": b,
                                "B_acerta_A_erra": c, "p_valor": round(float(pv), 4)})

    print(f"\n  {'ISM -> volatilidade':26s}"
          f"{A['volatilidade']['r_ism_vol']:>12.4f}"
          f"{B['volatilidade']['r_ism_vol']:>14.4f}"
          f"{B['volatilidade']['r_ism_vol'] - A['volatilidade']['r_ism_vol']:>+10.4f}")

    for r in (A, B):
        r.pop("_y_teste", None)
        r.pop("_preds", None)
    args.saida.write_text(json.dumps(
        {"data_execucao": date.today().isoformat(), "semente": SEMENTE,
         "filtro": CAT_FILTRO, "A_todas": A, "B_filtrado": B,
         "comparacoes": comparacoes}, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8")
    print(f"\n[OK] Salvo em {args.saida}")


if __name__ == "__main__":
    main()
