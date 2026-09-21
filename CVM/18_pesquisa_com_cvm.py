# -*- coding: utf-8 -*-
# ==============================================================================
#   O PROTOCOLO DA PESQUISA, AGORA COM AS PUBLICAÇÕES DA CVM
#
#   Este script não inventa desenho. Ele segue o Capítulo 3 da dissertação e
#   acrescenta UM bloco novo de atributos — os comunicados da CVM — para
#   responder à pergunta que o orientador fez: o que muda em relação ao que
#   tínhamos ANTES de usar a CVM?
#
#   O QUE VEM DA PESQUISA, sem alteração:
#
#     · fusão precoce com os atributos defasados em t-1: retorno de ontem,
#       volatilidade condicional do GARCH(1,1) de ontem, índice de sentimento
#       do FinBERT-PT-BR de ontem  (Cap. 3, eq. da fusão);
#     · classificadores SVM com núcleo RBF e XGBoost, este com 300 árvores,
#       profundidade 3, taxa 0,05 e subamostragem de 90% (Cap. 3, §parâmetros);
#     · divisão estritamente cronológica 60 / 15 / 25 — treino, validação,
#       teste — sem embaralhar (Cap. 3, §protocolo de avaliação);
#     · linhas de base da classe majoritária E do modelo apenas-preços;
#     · testes binomial e de McNemar (Cap. 3, §métricas);
#     · volatilidade pelo HAR de Corsi com médias de 1, 5 e 22 dias, e a
#       combinação quantílica de pesos variáveis, medidas por MAE e R²-OS.
#
#   O QUE É NOVO: o bloco da CVM em t-1 — índice de sentimento dos comunicados
#   entregues com o pregão fechado, contagem, presença de Fato Relevante e as
#   componentes principais do embedding de 768 dimensões do FinBERT.
#
#   Saída: dados/pesquisa_com_cvm.json
# ==============================================================================
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, QuantileRegressor
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             roc_auc_score)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS, RAIZ = AQUI / "dados", AQUI.parent
TICKER = "PETR4"
N_PCA = 8
QUANTIS = [0.10, 0.25, 0.50, 0.75, 0.90]

# hiperparâmetros exatamente como registrados no Capítulo 3
XGB = dict(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
           colsample_bytree=0.9, random_state=42, eval_metric="logloss",
           n_jobs=-1)


# ──────────────────────────────────────────────────────────────────────────────
#   A matriz da pesquisa, e o bloco novo da CVM
# ──────────────────────────────────────────────────────────────────────────────
def bloco_cvm() -> pd.DataFrame:
    """Comunicados entregues com o pregão fechado, atribuídos ao pregão que
    podia reagir a eles. A atribuição é a validada no Capítulo do relógio da
    CVM, de modo que o valor da linha t é informação anterior à abertura de t."""
    a = pd.read_csv(DADOS / "rodada_A_casos.csv", low_memory=False,
                    usecols=["Protocolo_Entrega", "Ticker", "Categoria",
                             "Entrega", "Pregao_reacao"])
    a = a[a["Ticker"] == TICKER].copy()
    a["Entrega"] = pd.to_datetime(a["Entrega"], errors="coerce")
    a["Date"] = pd.to_datetime(a["Pregao_reacao"], errors="coerce")
    a = a[a["Entrega"].notna() & a["Date"].notna()]
    a = a[a["Entrega"].dt.hour >= 17]

    c = pd.read_csv(DADOS / "cvm_classificado.csv", low_memory=False)
    c = a.merge(c[["Protocolo_Entrega", "p_pos", "p_neg", "p_neu", "Confianca"]],
                on="Protocolo_Entrega", how="inner")
    # o índice de sentimento dos comunicados, na mesma forma do ISM da pesquisa
    c["ism"] = c["p_pos"] - c["p_neg"]

    g = c.groupby("Date")
    f = pd.DataFrame({
        "CVM_Sentimento_Ontem": g["ism"].mean(),
        "CVM_Sentimento_Max_Ontem": g["ism"].max(),
        "CVM_Sentimento_Min_Ontem": g["ism"].min(),
        "CVM_Confianca_Ontem": g["Confianca"].mean(),
        "CVM_Qtd_Ontem": g.size(),
        "CVM_FatoRelevante_Ontem": c.assign(
            x=c["Categoria"].eq("Fato Relevante")).groupby("Date")["x"].sum(),
    }).reset_index()
    f["CVM_Tem_Ontem"] = 1.0

    z = np.load(DADOS / "cvm_embeddings.npz", allow_pickle=True)
    emb = pd.DataFrame(z["emb"])
    emb.columns = [f"CVM_emb{i}" for i in range(emb.shape[1])]
    emb["Protocolo_Entrega"] = z["protocolo"]
    dims = [x for x in emb.columns if x.startswith("CVM_emb")]
    e = (c[["Protocolo_Entrega", "Date"]]
         .merge(emb, on="Protocolo_Entrega", how="inner")
         .groupby("Date")[dims].mean().reset_index())
    return f.merge(e, on="Date", how="left")


def painel() -> pd.DataFrame:
    b = pd.read_csv(RAIZ / "Mestrado_PETR4" / "base_master_petr4.csv",
                    parse_dates=["Date"])
    d = b.merge(bloco_cvm(), on="Date", how="left")
    for c in ["CVM_Qtd_Ontem", "CVM_FatoRelevante_Ontem", "CVM_Tem_Ontem"]:
        d[c] = d[c].fillna(0.0)
    for c in ["CVM_Sentimento_Ontem", "CVM_Sentimento_Max_Ontem",
              "CVM_Sentimento_Min_Ontem", "CVM_Confianca_Ontem"]:
        d[c] = d[c].fillna(0.0)
    return d.dropna(subset=["Retorno_Ontem", "Volatilidade_Ontem",
                            "Sentimento_Ontem", "Alvo"]).reset_index(drop=True)


def corta(d: pd.DataFrame) -> tuple[slice, slice, slice]:
    """Divisão estritamente cronológica 60 / 15 / 25, como no Capítulo 3."""
    n = len(d)
    a, b = int(n * 0.60), int(n * 0.75)
    return slice(0, a), slice(a, b), slice(b, n)


# ──────────────────────────────────────────────────────────────────────────────
#   Direção
# ──────────────────────────────────────────────────────────────────────────────
def mcnemar(y, a, b) -> dict:
    """Teste pareado: isola os pregões em que os dois modelos discordam."""
    ca, cb = (a == y), (b == y)
    n01, n10 = int((~ca & cb).sum()), int((ca & ~cb).sum())
    if n01 + n10 == 0:
        return {"acertos_so_do_novo": 0, "acertos_so_do_antigo": 0, "p": 1.0}
    p = stats.binomtest(n01, n01 + n10, 0.5).pvalue
    return {"acertos_so_do_novo": n01, "acertos_so_do_antigo": n10, "p": float(p)}


def treina_direcao(d, cols, emb, nome) -> dict:
    tr, va, te = corta(d)
    X = d[cols].copy()
    if emb:
        p = PCA(n_components=min(N_PCA, len(emb)), random_state=42)
        p.fit(d[emb].iloc[tr].fillna(0.0).values)      # ajustada só no treino
        for i, v in enumerate(p.transform(d[emb].fillna(0.0).values).T):
            X[f"CVM_pc{i}"] = v
    X = X.fillna(X.iloc[tr].median())
    y = d["Alvo"].astype(int)
    # treino + validação juntos para o ajuste final, teste intocado
    fit = slice(0, te.start)
    out = {}
    for mod_nome, mod in [
        ("SVM-RBF", make_pipeline(StandardScaler(), SVC(kernel="rbf",
                                                        probability=True,
                                                        random_state=42))),
        ("XGBoost", XGBClassifier(**XGB)),
    ]:
        m = mod.fit(X.iloc[fit], y.iloc[fit])
        pv = m.predict(X.iloc[te])
        pp = m.predict_proba(X.iloc[te])[:, 1]
        yt = y.iloc[te].values
        out[mod_nome] = {
            "n_teste": int(len(yt)),
            "acuracia": round(float(accuracy_score(yt, pv)), 4),
            "precisao": round(float(precision_score(yt, pv, zero_division=0)), 4),
            "f1": round(float(f1_score(yt, pv, zero_division=0)), 4),
            "auc": round(float(roc_auc_score(yt, pp)), 4),
            "p_binomial": float(stats.binomtest(int((yt == pv).sum()),
                                                len(yt), 0.5).pvalue),
            "_prev": pv,
        }
    return out


# ──────────────────────────────────────────────────────────────────────────────
#   Volatilidade — HAR de Corsi e a combinação quantílica de pesos variáveis
# ──────────────────────────────────────────────────────────────────────────────
def har(d: pd.DataFrame) -> pd.DataFrame:
    v = d["Volatilidade_GARCH"]
    h = pd.DataFrame({"Date": d["Date"], "alvo": v})
    h["har1"] = v.shift(1)
    h["har5"] = v.shift(1).rolling(5).mean()
    h["har22"] = v.shift(1).rolling(22).mean()
    for c in ["Sentimento_Ontem", "CVM_Sentimento_Ontem",
              "CVM_FatoRelevante_Ontem", "CVM_Qtd_Ontem"]:
        h[c] = d[c]
    h["Sent_Abs_Ontem"] = d["Sentimento_Ontem"].abs()
    return h.dropna().reset_index(drop=True)


def r2os(erro, ref) -> float:
    return float(1 - (erro ** 2).sum() / (ref ** 2).sum())


def avalia_vol(h, cols, nome, ref_erro=None) -> dict:
    tr, va, te = corta(h)
    Xtr, ytr = h[cols].iloc[tr], h["alvo"].iloc[tr]
    Xva, yva = h[cols].iloc[va], h["alvo"].iloc[va]
    Xte, yte = h[cols].iloc[te], h["alvo"].iloc[te]

    lin = LinearRegression().fit(pd.concat([Xtr, Xva]), pd.concat([ytr, yva]))
    e_lin = yte.values - lin.predict(Xte)

    # combinação quantílica: pesos inversamente proporcionais ao erro na validação
    preds, pesos = [], []
    for q in QUANTIS:
        m = QuantileRegressor(quantile=q, alpha=0.001, solver="highs").fit(Xtr, ytr)
        mae_va = np.abs(yva.values - m.predict(Xva)).mean()
        preds.append(m.predict(Xte))
        pesos.append(1.0 / max(mae_va, 1e-9))
    w = np.array(pesos) / np.sum(pesos)
    e_q = yte.values - np.average(np.vstack(preds), axis=0, weights=w)

    r = {"nome": nome, "n_teste": int(len(yte)),
         "mae_linear": round(float(np.abs(e_lin).mean()), 4),
         "rmse_linear": round(float(np.sqrt((e_lin ** 2).mean())), 4),
         "mae_quantilico": round(float(np.abs(e_q).mean()), 4),
         "rmse_quantilico": round(float(np.sqrt((e_q ** 2).mean())), 4)}
    if ref_erro is not None:
        r["r2os_linear_vs_HAR"] = round(r2os(e_lin, ref_erro) * 100, 2)
        r["r2os_quantilico_vs_HAR"] = round(r2os(e_q, ref_erro) * 100, 2)
    return r, e_lin


# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    d = painel()
    EMB = [c for c in d.columns if c.startswith("CVM_emb")]
    tr, va, te = corta(d)

    print("=" * 100)
    print("  O PROTOCOLO DA PESQUISA, COM E SEM AS PUBLICAÇÕES DA CVM — PETR4")
    print("=" * 100)
    print(f"\n  pregões: {len(d):,}  ({d['Date'].min():%d/%m/%Y} a {d['Date'].max():%d/%m/%Y})")
    print(f"  treino {tr.stop:,} | validação {va.stop-va.start:,} | "
          f"teste {te.stop-te.start:,}   (60/15/25, cronológico)")
    print(f"  pregões do teste com comunicado da CVM na véspera: "
          f"{int(d['CVM_Tem_Ontem'].iloc[te].sum()):,} "
          f"({d['CVM_Tem_Ontem'].iloc[te].mean():.1%})")

    BASE = ["Retorno_Ontem", "Volatilidade_Ontem"]
    FUSAO = BASE + ["Sentimento_Ontem"]
    CVM = ["CVM_Sentimento_Ontem", "CVM_Sentimento_Max_Ontem",
           "CVM_Sentimento_Min_Ontem", "CVM_Confianca_Ontem",
           "CVM_Qtd_Ontem", "CVM_FatoRelevante_Ontem", "CVM_Tem_Ontem"]

    BRACOS = [
        ("apenas preços  [linha de base da pesquisa]", BASE, []),
        ("Data Fusion: preços + notícia  [O QUE TÍNHAMOS ANTES]", FUSAO, []),
        ("Data Fusion + CVM  [NOVO]", FUSAO + CVM, []),
        ("Data Fusion + CVM + embedding  [NOVO]", FUSAO + CVM, EMB),
        ("preços + CVM, sem notícia  [controle]", BASE + CVM, []),
    ]

    yte = d["Alvo"].astype(int).iloc[te].values
    maj = max(yte.mean(), 1 - yte.mean())
    print("\n" + "=" * 100)
    print("  DIREÇÃO — o pregão seguinte fecha em alta?")
    print("=" * 100)
    print(f"\n  classe majoritária no teste: {maj:.2%}")
    print(f"\n  {'braço':<52} {'modelo':<9} {'acur':>7} {'prec':>7} "
          f"{'F1':>7} {'AUC':>7} {'p-binom':>9}")
    print("  " + "-" * 96)

    res, guarda = {"direcao": {}, "volatilidade": {}}, {}
    for nome, cols, emb in BRACOS:
        o = treina_direcao(d, cols, emb, nome)
        guarda[nome] = {k: v.pop("_prev") for k, v in o.items()}
        res["direcao"][nome] = o
        for mn, m in o.items():
            print(f"  {nome:<52} {mn:<9} {m['acuracia']:>6.2%} {m['precisao']:>6.2%} "
                  f"{m['f1']:>6.2%} {m['auc']:>7.3f} {m['p_binomial']:>9.4f}")

    print("\n" + "=" * 100)
    print("  TESTE DE McNEMAR — a fonte nova acrescenta sobre a anterior?")
    print("=" * 100)
    ANTES = "Data Fusion: preços + notícia  [O QUE TÍNHAMOS ANTES]"
    PRECO = "apenas preços  [linha de base da pesquisa]"
    res["mcnemar"] = {}
    for mn in ["SVM-RBF", "XGBoost"]:
        for rot, a, b in [
            ("a notícia acrescenta sobre o preço?", PRECO, ANTES),
            ("a CVM acrescenta sobre a notícia?", ANTES,
             "Data Fusion + CVM  [NOVO]"),
            ("o embedding acrescenta sobre os rótulos?", "Data Fusion + CVM  [NOVO]",
             "Data Fusion + CVM + embedding  [NOVO]"),
        ]:
            m = mcnemar(yte, guarda[a][mn], guarda[b][mn])
            res["mcnemar"][f"{mn} — {rot}"] = m
            sinal = "  *" if m["p"] < 0.05 else ""
            print(f"  {mn:<9} {rot:<42} ganhou {m['acertos_so_do_novo']:>3} × "
                  f"perdeu {m['acertos_so_do_antigo']:>3}   p = {m['p']:.4f}{sinal}")

    # ── volatilidade ─────────────────────────────────────────────────────────
    h = har(d)
    print("\n" + "=" * 100)
    print("  VOLATILIDADE — HAR de Corsi e a combinação quantílica de pesos variáveis")
    print("=" * 100)
    ref, e_ref = avalia_vol(h, ["har1", "har5", "har22"], "HAR (referência)")
    print(f"\n  {'modelo':<52} {'MAE lin':>9} {'MAE quant':>11} "
          f"{'R2-OS lin':>11} {'R2-OS quant':>13}")
    print("  " + "-" * 96)
    VB = [
        ("HAR (referência da pesquisa)", ["har1", "har5", "har22"]),
        ("HAR + sentimento  [O QUE TÍNHAMOS ANTES]",
         ["har1", "har5", "har22", "Sentimento_Ontem", "Sent_Abs_Ontem"]),
        ("HAR + sentimento + CVM  [NOVO]",
         ["har1", "har5", "har22", "Sentimento_Ontem", "Sent_Abs_Ontem",
          "CVM_Sentimento_Ontem", "CVM_FatoRelevante_Ontem", "CVM_Qtd_Ontem"]),
        ("HAR + CVM, sem notícia  [controle]",
         ["har1", "har5", "har22", "CVM_Sentimento_Ontem",
          "CVM_FatoRelevante_Ontem", "CVM_Qtd_Ontem"]),
    ]
    for nome, cols in VB:
        r, _ = avalia_vol(h, cols, nome, ref_erro=e_ref)
        res["volatilidade"][nome] = r
        print(f"  {nome:<52} {r['mae_linear']:>9.4f} {r['mae_quantilico']:>11.4f} "
              f"{r.get('r2os_linear_vs_HAR', 0):>+10.2f}% "
              f"{r.get('r2os_quantilico_vs_HAR', 0):>+12.2f}%")

    res["majoritaria_teste"] = round(float(maj), 4)
    res["n"] = {"total": int(len(d)), "teste": int(te.stop - te.start)}
    (DADOS / "pesquisa_com_cvm.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print("\n  gravado: dados/pesquisa_com_cvm.json")


if __name__ == "__main__":
    main()
