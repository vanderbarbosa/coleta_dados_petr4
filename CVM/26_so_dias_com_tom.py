# -*- coding: utf-8 -*-
# ==============================================================================
#   SÓ OS DIAS COM TOM DEFINIDO — pedido da mentoria de 29/10/2026
#
#   A proposta: descartar os pregões sem comunicado E os pregões cujos
#   comunicados são todos neutros, treinando e avaliando apenas onde há tom
#   declarado (positivo ou negativo). Começar pela PETR4.
#
#   ─── EXPECTATIVA REGISTRADA ANTES DE RODAR ───────────────────────────────
#   O filtro reduz o teste da PETR4 de 165 para 56 pregões, e o IC95% da taxa
#   de acerto sobe de ±7,6 para ±13,1 pontos. Só um efeito acima de treze
#   pontos seria detectável — magnitude que nada nesta pesquisa sugere. A
#   expectativa, portanto, é de resultado INCONCLUSIVO na PETR4 isolada, e a
#   resposta útil deve vir do agrupamento dos dez papéis. Registra-se isto
#   ANTES para que o resultado não seja lido como se tivesse sido previsto
#   depois.
#
#   ─── DUAS RESSALVAS QUE O RESULTADO CARREGA ──────────────────────────────
#   (1) O filtro usa o RÓTULO do FinBERT, e a validação contra o conjunto-ouro
#       humano desta pesquisa aferiu 58% de acurácia nesse rótulo. Filtrar por
#       "não-neutro" é, portanto, filtrar com instrumento ruidoso: descarta-se
#       dia que não era neutro e mantém-se dia que era.
#   (2) Esta é a quarta fatia testada (todos os dias; dias com evento;
#       especialista treinado em eventos; agora tom definido). Cada tentativa
#       nova eleva a chance de um falso positivo por sorte. O limiar de
#       Bonferroni para a família acumulada é reportado ao fim.
#
#   Saída: dados/so_dias_com_tom.json
# ==============================================================================
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from arch import arch_model
from scipy import stats
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
TOP10 = ["VALE3", "ITUB4", "PETR4", "SBSP3", "BBDC4", "B3SA3", "ITSA4",
         "BPAC11", "BBAS3", "ABEV3"]
MIN_TREINO, MIN_TESTE = 100, 30
XGB = dict(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
           colsample_bytree=0.9, random_state=42, eval_metric="logloss", n_jobs=-1)

_OHLCV = pd.read_csv(DADOS / "ohlcv_b3.csv", parse_dates=["Data"])
_CASOS = pd.read_csv(DADOS / "rodada_A_casos.csv", low_memory=False,
                      usecols=["Protocolo_Entrega", "Ticker", "Entrega", "Pregao_reacao"])
_CASOS["Entrega"] = pd.to_datetime(_CASOS["Entrega"], errors="coerce")
_CASOS["Data"] = pd.to_datetime(_CASOS["Pregao_reacao"], errors="coerce")
_CLASS = pd.read_csv(DADOS / "cvm_classificado.csv", low_memory=False)


def painel(ticker: str) -> pd.DataFrame:
    px = _OHLCV[_OHLCV["Ticker"] == ticker].sort_values("Data").reset_index(drop=True)
    px = px[px["Retorno"].notna()].reset_index(drop=True)
    g = arch_model(px["Retorno"].values * 100.0, vol="Garch", p=1, q=1, dist="t").fit(disp="off")
    px["Volatilidade_GARCH"] = g.conditional_volatility

    a = _CASOS[(_CASOS["Ticker"] == ticker) & _CASOS["Entrega"].notna() & _CASOS["Data"].notna()]
    a = a[a["Entrega"].dt.hour >= 17]
    c = a.merge(_CLASS[["Protocolo_Entrega", "p_pos", "p_neg", "Rotulo", "Confianca"]],
                on="Protocolo_Entrega", how="inner")
    c["ism"] = c["p_pos"] - c["p_neg"]
    # agregado de TODOS os comunicados do pregão
    todos = c.groupby("Data").agg(Sent=("ism", "mean"), Qtd=("ism", "size")).reset_index()
    # agregado SÓ dos comunicados com tom declarado (descarta os neutros)
    nn = c[c["Rotulo"] != "NEUTRAL"]
    tom = nn.groupby("Data").agg(Sent_tom=("ism", "mean"), Qtd_tom=("ism", "size")).reset_index()

    d = px.merge(todos, on="Data", how="left").merge(tom, on="Data", how="left")
    d["TEM_TOM"] = d["Qtd_tom"].notna()
    for col in ["Sent", "Qtd", "Sent_tom", "Qtd_tom"]:
        d[col] = d[col].fillna(0.0)
    d["Retorno_Ontem"] = d["Retorno"].shift(1) * 100.0
    d["Volatilidade_Ontem"] = d["Volatilidade_GARCH"].shift(1)
    d["Alvo"] = np.where(d["Retorno"] > 0, 1, 0)
    return d.dropna(subset=["Retorno_Ontem", "Volatilidade_Ontem"]).reset_index(drop=True)


def avalia(y, pred, prob=None) -> dict:
    n = len(y)
    if n < MIN_TESTE:
        return {"n": int(n), "aviso": f"menos de {MIN_TESTE} pregões — não avaliável"}
    maj = float(max(y.mean(), 1 - y.mean()))
    acc = float(accuracy_score(y, pred))
    out = {"n": int(n), "majoritaria": round(maj, 4), "acuracia": round(acc, 4),
           "ganho_pp": round((acc - maj) * 100, 2),
           "ic95_meia_largura_pp": round(float(1.96 * np.sqrt(0.25 / n) * 100), 2),
           "p_vs_majoritaria": float(stats.binomtest(int((y == pred).sum()), n, maj).pvalue)}
    if prob is not None and len(np.unique(y)) > 1:
        out["auc"] = round(float(roc_auc_score(y, prob)), 4)
    return out


def processa(ticker: str) -> dict:
    d = painel(ticker)
    n = len(d)
    i_tr, i_te = np.arange(0, int(n * 0.75)), np.arange(int(n * 0.75), n)
    tom = d["TEM_TOM"].values
    tr_tom, te_tom = i_tr[tom[i_tr]], i_te[tom[i_te]]
    y = d["Alvo"].astype(int)

    r = {"n_treino_com_tom": int(len(tr_tom)), "n_teste_com_tom": int(len(te_tom)),
         "n_teste_total": int(len(i_te)), "arms": {}, "_cru": {}}
    if len(tr_tom) < MIN_TREINO or len(te_tom) < MIN_TESTE:
        r["aviso"] = (f"treino com tom = {len(tr_tom)} (mín. {MIN_TREINO}), "
                      f"teste com tom = {len(te_tom)} (mín. {MIN_TESTE})")
        if len(te_tom) < MIN_TESTE:
            return r

    COLS = ["Retorno_Ontem", "Volatilidade_Ontem", "Sent_tom", "Qtd_tom"]
    COLS_PRECO = ["Retorno_Ontem", "Volatilidade_Ontem"]
    for nome, cols, treino in [
            ("só preço, treinado em tudo", COLS_PRECO, i_tr),
            ("preço + tom, treinado em tudo", COLS, i_tr),
            ("só preço, treinado só nos dias com tom", COLS_PRECO, tr_tom),
            ("preço + tom, treinado só nos dias com tom", COLS, tr_tom)]:
        if len(treino) < MIN_TREINO or len(np.unique(y.values[treino])) < 2:
            r["arms"][nome] = {"aviso": f"treino insuficiente ({len(treino)})"}
            continue
        X = d[cols].fillna(0.0)
        for mn in ["SVM", "XGBoost"]:
            mod = (make_pipeline(StandardScaler(), SVC(kernel="rbf", probability=True, random_state=42))
                   if mn == "SVM" else XGBClassifier(**XGB))
            mod.fit(X.iloc[treino], y.iloc[treino])
            pv = mod.predict(X.iloc[te_tom]); pp = mod.predict_proba(X.iloc[te_tom])[:, 1]
            r["arms"][f"{mn} — {nome}"] = avalia(y.values[te_tom], pv, pp)
            r["_cru"][f"{mn} — {nome}"] = {"y": y.values[te_tom].tolist(), "pred": pv.tolist()}
    return r


def main() -> None:
    res = {"expectativa_registrada_antes": (
               "o filtro reduz o teste da PETR4 de 165 para 56 pregões e alarga o IC95% de ±7,6 "
               "para ±13,1 pontos; espera-se resultado INCONCLUSIVO no papel isolado, com a "
               "resposta útil vindo do agrupamento"),
           "ressalvas": [
               "o filtro usa o rótulo do FinBERT, aferido em 58% de acurácia contra o conjunto-ouro humano",
               "esta é a quarta fatia testada; o limiar de Bonferroni acumulado é reportado ao fim"],
           "papeis": {}}
    for tk in TOP10:
        r = processa(tk)
        res["papeis"][tk] = r
        ok = [v for v in r["arms"].values() if "ganho_pp" in v]
        if ok:
            print(f"{tk}: treino c/ tom {r['n_treino_com_tom']:4} | teste c/ tom {r['n_teste_com_tom']:3} "
                  f"(de {r['n_teste_total']}) | ganho médio {np.mean([v['ganho_pp'] for v in ok]):+6.2f}pp "
                  f"(IC ±{ok[0]['ic95_meia_largura_pp']:.1f}) | significativos: "
                  f"{sum(v['p_vs_majoritaria'] < 0.05 and v['ganho_pp'] > 0 for v in ok)}/{len(ok)}", flush=True)
        else:
            print(f"{tk}: teste c/ tom {r['n_teste_com_tom']} — NÃO AVALIÁVEL", flush=True)

    # ── agrupado ────────────────────────────────────────────────────────────
    print("\n" + "=" * 92)
    print("  OS 10 PAPÉIS AGRUPADOS — onde a pergunta de fato cabe")
    print("=" * 92)
    bracos = sorted({b for tk in TOP10 for b in res["papeis"][tk].get("_cru", {})})
    res["agrupado"] = {}
    n_testes = 0
    for b in bracos:
        Y, P = [], []
        for tk in TOP10:
            cru = res["papeis"][tk].get("_cru", {}).get(b)
            if cru:
                Y += cru["y"]; P += cru["pred"]
        if len(Y) < MIN_TESTE:
            continue
        res["agrupado"][b] = avalia(np.array(Y), np.array(P))
        v = res["agrupado"][b]; n_testes += 1
        print(f"  {b:52} n={v['n']:4}  {v['ganho_pp']:+6.2f}pp  (IC ±{v['ic95_meia_largura_pp']:.1f}, "
              f"p={v['p_vs_majoritaria']:.3f})")
    # família acumulada: 60 (script 23) + 48 (script 25) + os desta rodada
    acumulado = 60 + 48 + n_testes + sum(len([v for v in res["papeis"][tk]["arms"].values()
                                              if "ganho_pp" in v]) for tk in TOP10)
    res["bonferroni"] = {"testes_acumulados_no_estudo": int(acumulado),
                         "limiar": round(0.05 / acumulado, 6)}
    print(f"\n  Família acumulada do estudo: {acumulado} testes → limiar de Bonferroni = "
          f"{0.05/acumulado:.6f}")
    for tk in TOP10:
        res["papeis"][tk].pop("_cru", None)
    (DADOS / "so_dias_com_tom.json").write_text(json.dumps(res, indent=2, ensure_ascii=False),
                                                 encoding="utf-8")
    print("\ngravado: dados/so_dias_com_tom.json")


if __name__ == "__main__":
    main()
