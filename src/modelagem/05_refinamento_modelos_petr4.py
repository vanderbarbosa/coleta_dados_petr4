# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Etapa 4b: Refinamento e melhoria do desempenho preditivo
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Objetivo: aprofundar a modelagem de DIREÇÃO da PETR4 além do baseline de
#   53% do Data Fusion. Parte das mesmas três fontes (preços, GARCH, sentimento)
#   e investiga, de forma controlada e honesta, se enriquecimento de atributos,
#   seleção de variáveis, modelos alternativos e ajuste de limiar elevam o
#   desempenho FORA da amostra (conjunto de teste), sob divisão cronológica.
#
#   Protocolo: divisão cronológica tripla 60/15/25 (treino/validação/teste).
#   Cada experimento é TREINADO no treino, SELECIONADO/AJUSTADO na validação e
#   AVALIADO UMA ÚNICA VEZ no teste — evitando vazamento e ajuste ao teste.
#
#   Saídas (em Mestrado_PETR4/):
#     - resultados_refinamento_petr4.csv     (uma linha por experimento)
#     - base_master_enriquecida_petr4.csv    (matriz de atributos usada)
# ==============================================================================

import sys, json, warnings
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "Mestrado_PETR4"

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from xgboost import XGBClassifier

try:
    from lightgbm import LGBMClassifier
    TEM_LGBM = True
except Exception:
    TEM_LGBM = False

RNG = 42
np.random.seed(RNG)

# ──────────────────────────────────────────────────────────────────────────────
# 1) Carga e construção da matriz de atributos enriquecida
#    Todos os atributos preditivos referem-se a t-1 (defasagem), pois a previsão
#    do pregão t só pode usar informação disponível até o fechamento de t-1.
# ──────────────────────────────────────────────────────────────────────────────
def carregar():
    master = pd.read_csv(PASTA / "base_master_petr4.csv", parse_dates=["Date"])
    cats = pd.read_csv(PASTA / "indice_sentimento_categorias_petr4.csv", parse_dates=["Data"])
    agg = pd.read_csv(PASTA / "indice_sentimento_petr4.csv", parse_dates=["Data"])
    cats = cats.rename(columns={"Data": "Date"})
    agg = agg.rename(columns={"Data": "Date"})
    # do agregado, apenas as contagens diárias (o índice já está em base_master)
    agg = agg[["Date", "Qtd_Noticias_do_Dia", "Qtd_Positivas", "Qtd_Negativas", "Qtd_Neutras"]]
    df = master.merge(cats, on="Date", how="left").merge(agg, on="Date", how="left")
    return df.sort_values("Date").reset_index(drop=True)


def construir_features(df):
    cat_cols = [c for c in df.columns if c.startswith("ISM_CAT")]
    # sentimento por categoria: ausência de notícia na categoria = 0 (neutro)
    df[cat_cols] = df[cat_cols].fillna(0.0)
    df["Qtd_Noticias_do_Dia"] = df["Qtd_Noticias_do_Dia"].fillna(0)
    df["Qtd_Positivas"] = df["Qtd_Positivas"].fillna(0)
    df["Qtd_Negativas"] = df["Qtd_Negativas"].fillna(0)

    # intensidade e dispersão do noticiário
    qtd = df["Qtd_Noticias_do_Dia"].replace(0, np.nan)
    df["Sent_Liquido"] = ((df["Qtd_Positivas"] - df["Qtd_Negativas"]) / qtd).fillna(0)
    df["Sent_Abs"] = df["Indice_Sentimento_Transformer"].abs()
    df["Log_Volume_Noticias"] = np.log1p(df["Qtd_Noticias_do_Dia"])

    # dinâmica do sentimento (médias móveis sobre o índice agregado)
    s = df["Indice_Sentimento_Transformer"].fillna(0)
    df["Sent_MM3"] = s.rolling(3, min_periods=1).mean()
    df["Sent_MM5"] = s.rolling(5, min_periods=1).mean()
    df["Sent_DP5"] = s.rolling(5, min_periods=1).std().fillna(0)
    df["Vol_MM5"] = df["Volatilidade_GARCH"].rolling(5, min_periods=1).mean()

    # TODOS os atributos derivados defasados em 1 dia (informação de t-1)
    derivados = cat_cols + ["Sent_Liquido", "Sent_Abs", "Log_Volume_Noticias",
                            "Sent_MM3", "Sent_MM5", "Sent_DP5", "Vol_MM5"]
    for c in derivados:
        df[c + "_L1"] = df[c].shift(1)

    df = df.dropna(subset=["Retorno_Ontem", "Volatilidade_Ontem", "Sentimento_Ontem"]).copy()
    df = df.fillna(0.0)
    return df, cat_cols


# ──────────────────────────────────────────────────────────────────────────────
# 2) Divisão cronológica tripla 60/15/25
# ──────────────────────────────────────────────────────────────────────────────
def split_cronologico(df):
    n = len(df)
    i_tr, i_va = int(n * 0.60), int(n * 0.75)
    return df.iloc[:i_tr], df.iloc[i_tr:i_va], df.iloc[i_va:]


BASE = ["Retorno_Ontem", "Volatilidade_Ontem", "Sentimento_Ontem"]
CAT_L1 = lambda cat_cols: [c + "_L1" for c in cat_cols]
VOL_L1 = ["Sent_Liquido_L1", "Log_Volume_Noticias_L1", "Sent_Abs_L1"]
DIN_L1 = ["Sent_MM3_L1", "Sent_MM5_L1", "Sent_DP5_L1", "Vol_MM5_L1"]


def xy(d, feats):
    return d[feats].values, d["Alvo"].values


def avaliar(modelo, Xtr, ytr, Xte, yte, escalar=False):
    if escalar:
        sc = StandardScaler().fit(Xtr)
        Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
    modelo.fit(Xtr, ytr)
    if hasattr(modelo, "predict_proba"):
        p = modelo.predict_proba(Xte)[:, 1]
    else:
        p = modelo.decision_function(Xte)
    pred = (p >= 0.5).astype(int)
    return accuracy_score(yte, pred) * 100, roc_auc_score(yte, p), p


def xgb(**kw):
    par = dict(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
               colsample_bytree=0.9, eval_metric="logloss", random_state=RNG,
               n_jobs=4)
    par.update(kw)
    return XGBClassifier(**par)


# ──────────────────────────────────────────────────────────────────────────────
# 3) Execução dos experimentos
# ──────────────────────────────────────────────────────────────────────────────
def main():
    df = carregar()
    df, cat_cols = construir_features(df)
    df.to_csv(PASTA / "base_master_enriquecida_petr4.csv", index=False)
    tr, va, te = split_cronologico(df)

    print(f"Bases  ->  treino={len(tr)}  validação={len(va)}  teste={len(te)}  (total={len(df)})")
    for nome, d in [("treino", tr), ("validação", va), ("teste", te)]:
        bal = d["Alvo"].mean() * 100
        print(f"  {nome:10s}: {d['Date'].min().date()} a {d['Date'].max().date()} "
              f"| altas={bal:.1f}%")

    res = []

    def registra(exp, descricao, feats, modelo, escalar=False, limiar=0.5):
        Xtr, ytr = xy(tr, feats)
        Xva, yva = xy(va, feats)
        Xte, yte = xy(te, feats)
        # treina e mede em validação e teste
        if escalar:
            sc = StandardScaler().fit(Xtr)
            Xtr_, Xva_, Xte_ = sc.transform(Xtr), sc.transform(Xva), sc.transform(Xte)
        else:
            Xtr_, Xva_, Xte_ = Xtr, Xva, Xte
        modelo.fit(Xtr_, ytr)
        prob = lambda X: (modelo.predict_proba(X)[:, 1] if hasattr(modelo, "predict_proba")
                          else modelo.decision_function(X))
        pva, pte = prob(Xva_), prob(Xte_)
        acc_va = accuracy_score(yva, (pva >= limiar).astype(int)) * 100
        acc_te = accuracy_score(yte, (pte >= limiar).astype(int)) * 100
        auc_te = roc_auc_score(yte, pte)
        res.append({"Experimento": exp, "Descrição": descricao, "Nº_features": len(feats),
                    "Acc_validação": round(acc_va, 2), "Acc_teste": round(acc_te, 2),
                    "AUC_teste": round(auc_te, 4)})
        print(f"  [{exp}] {descricao:42s} val={acc_va:5.2f}%  teste={acc_te:5.2f}%  AUC={auc_te:.3f}")
        return pva, pte, yva, yte

    print("\n=== Experimentos ===")
    # E0 — baseline reprodutível (3 atributos, XGBoost Data Fusion)
    registra("E0", "Baseline Data Fusion (3 atributos)", BASE, xgb())

    # E1 — + sentimento por categoria (7 séries defasadas)
    f1 = BASE + CAT_L1(cat_cols)
    registra("E1", "+ sentimento por categoria (7)", f1, xgb())

    # E2 — + volume/intensidade do noticiário
    f2 = f1 + VOL_L1
    registra("E2", "+ volume e sentimento líquido", f2, xgb())

    # E3 — + dinâmica (médias móveis de sentimento e volatilidade)
    f3 = f2 + DIN_L1
    registra("E3", "+ dinâmica (médias móveis)", f3, xgb())

    # E4 — seleção de atributos por importância (ganho) na validação
    base_xgb = xgb().fit(tr[f3].values, tr["Alvo"].values)
    imp = pd.Series(base_xgb.feature_importances_, index=f3).sort_values(ascending=False)
    melhor_k, melhor_acc, melhor_feats = None, -1, f3
    for k in [3, 5, 8, 10, 12, len(f3)]:
        fk = list(imp.index[:k])
        Xtr, ytr = xy(tr, fk); Xva, yva = xy(va, fk)
        m = xgb().fit(Xtr, ytr)
        a = accuracy_score(yva, m.predict(Xva)) * 100
        if a > melhor_acc:
            melhor_acc, melhor_k, melhor_feats = a, k, fk
    registra("E4", f"seleção top-{melhor_k} por importância", melhor_feats, xgb())

    # E5 — modelos alternativos sobre o melhor conjunto (seleção na validação)
    candidatos = [
        ("Regressão Logística", LogisticRegression(max_iter=1000, C=0.5), True),
        ("SVM (RBF)", SVC(probability=True, C=1.0, gamma="scale", random_state=RNG), True),
        ("Random Forest", RandomForestClassifier(n_estimators=400, max_depth=5,
                                                  min_samples_leaf=20, random_state=RNG), False),
        ("Gradient Boosting", GradientBoostingClassifier(max_depth=3, learning_rate=0.05,
                                                         n_estimators=300, random_state=RNG), False),
        ("XGBoost", xgb(), False),
    ]
    if TEM_LGBM:
        candidatos.append(("LightGBM", LGBMClassifier(n_estimators=300, max_depth=3,
                          learning_rate=0.05, verbose=-1, random_state=RNG), False))
    melhor = None
    for nome, modelo, esc in candidatos:
        acc_va, _, _ = avaliar(modelo, *xy(tr, melhor_feats), *xy(va, melhor_feats), escalar=esc)
        if melhor is None or acc_va > melhor[1]:
            melhor = (nome, acc_va, modelo, esc)
    print(f"     melhor na validação: {melhor[0]} ({melhor[1]:.2f}%)")
    registra("E5", f"melhor modelo: {melhor[0]}", melhor_feats, melhor[2], escalar=melhor[3])

    # E6 — busca de hiperparâmetros do XGBoost na validação
    melhor_hp, melhor_hp_acc = None, -1
    for md in [2, 3, 4]:
        for lr in [0.02, 0.05, 0.1]:
            for ne in [200, 400]:
                m = xgb(max_depth=md, learning_rate=lr, n_estimators=ne)
                acc_va, _, _ = avaliar(m, *xy(tr, melhor_feats), *xy(va, melhor_feats))
                if acc_va > melhor_hp_acc:
                    melhor_hp_acc, melhor_hp = acc_va, dict(max_depth=md, learning_rate=lr, n_estimators=ne)
    print(f"     melhores hiperparâmetros: {melhor_hp} (val={melhor_hp_acc:.2f}%)")
    pva, pte, yva, yte = registra("E6", "XGBoost com tuning", melhor_feats, xgb(**melhor_hp))

    # E7 — ajuste de limiar de decisão na validação (maximiza acurácia)
    limiares = np.linspace(0.40, 0.60, 41)
    melhor_lim = max(limiares, key=lambda t: accuracy_score(yva, (pva >= t).astype(int)))
    acc_te_lim = accuracy_score(yte, (pte >= melhor_lim).astype(int)) * 100
    auc_te = roc_auc_score(yte, pte)
    acc_va_lim = accuracy_score(yva, (pva >= melhor_lim).astype(int)) * 100
    res.append({"Experimento": "E7", "Descrição": f"+ ajuste de limiar ({melhor_lim:.3f})",
                "Nº_features": len(melhor_feats), "Acc_validação": round(acc_va_lim, 2),
                "Acc_teste": round(acc_te_lim, 2), "AUC_teste": round(auc_te, 4)})
    print(f"  [E7] ajuste de limiar ({melhor_lim:.3f}) val={acc_va_lim:5.2f}%  teste={acc_te_lim:5.2f}%")

    # E8 — validação walk-forward (janela expansível) p/ robustez do melhor modelo
    dfx = df.reset_index(drop=True)
    n = len(dfx); ini = int(n * 0.60); passo = max(20, int(n * 0.05))
    accs = []
    i = ini
    while i < n:
        tr_wf = dfx.iloc[:i]; te_wf = dfx.iloc[i:i + passo]
        if len(te_wf) < 5:
            break
        m = xgb(**melhor_hp).fit(tr_wf[melhor_feats].values, tr_wf["Alvo"].values)
        a = accuracy_score(te_wf["Alvo"].values, m.predict(te_wf[melhor_feats].values)) * 100
        accs.append(a); i += passo
    wf_media = float(np.mean(accs))
    res.append({"Experimento": "E8", "Descrição": f"walk-forward ({len(accs)} janelas)",
                "Nº_features": len(melhor_feats), "Acc_validação": "—",
                "Acc_teste": round(wf_media, 2), "AUC_teste": "—"})
    print(f"  [E8] walk-forward: média={wf_media:.2f}%  (min={min(accs):.1f}, max={max(accs):.1f})")

    # ── persistência ──
    out = pd.DataFrame(res)
    out.to_csv(PASTA / "resultados_refinamento_petr4.csv", index=False)
    meta = {"baseline_teste": res[0]["Acc_teste"], "melhor_feats": melhor_feats,
            "melhor_modelo_E5": melhor[0], "melhor_hp": melhor_hp,
            "limiar_E7": float(melhor_lim), "walkforward_media": wf_media,
            "n_treino": len(tr), "n_validacao": len(va), "n_teste": len(te)}
    with open(PASTA / "meta_refinamento_petr4.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("\n[OK] Refinamento concluido.")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
