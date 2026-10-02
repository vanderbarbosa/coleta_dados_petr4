# -*- coding: utf-8 -*-
# ==============================================================================
#   COMPARATIVO — TOP 10 AÇÕES DO IBOVESPA, pedido do Prof. Julio na mentoria
#   de 30/09/2026: repetir individualmente, para cada uma das 10 principais
#   ações da bolsa, a mesma comparação feita para a PETR4 (Script 20).
#
#   OS 10 PAPÉIS: as 10 ações de maior peso na carteira teórica OFICIAL do
#   Ibovespa (fonte: B3, endpoint GetPortfolioDay, consultado em 02/10/2026),
#   restritas às que JÁ fazem parte da pesquisa — isto é, que já têm
#   comunicados da CVM coletados e classificados pelo FinBERT-PT-BR
#   (CVM/dados/rodada_A_casos.csv + cvm_classificado.csv) e preço coletado
#   (CVM/dados/ohlcv_b3.csv). Isso DEIXA DE FORA nomes grandes do índice que
#   não estão na nossa base — WEGE3, AXIA3 (ex-Eletrobras), EMBJ3, CPLE3,
#   ENEV3 — porque incluí-los exigiria coletar e classificar comunicados da
#   CVM do zero para eles, o que não foi feito.
#
#   MESMO PROTOCOLO do Script 20, por papel: GARCH(1,1) próprio (vol='Garch',
#   p=1, q=1, dist='t'), SVM-RBF e XGBoost (300 árvores, depth 3, lr 0,05,
#   subsample 0,9), divisão cronológica 60/15/25, McNemar. NÃO inclui notícia
#   de jornal — bloqueado para os 10 papéis pela mesma razão do Script 20
#   (falta o corpus de notícias classificado nesta máquina).
#
#   Saída: dados/comparativo_top10_acoes.json
# ==============================================================================
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from arch import arch_model
from scipy import stats
from sklearn.metrics import accuracy_score, f1_score, precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"

TOP10 = ["VALE3", "ITUB4", "PETR4", "SBSP3", "BBDC4", "B3SA3", "ITSA4",
         "BPAC11", "BBAS3", "ABEV3"]

XGB = dict(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
           colsample_bytree=0.9, random_state=42, eval_metric="logloss", n_jobs=-1)

_OHLCV = pd.read_csv(DADOS / "ohlcv_b3.csv", parse_dates=["Data"])
_CVM_CASOS = pd.read_csv(DADOS / "rodada_A_casos.csv", low_memory=False,
                          usecols=["Protocolo_Entrega", "Ticker", "Categoria",
                                   "Entrega", "Pregao_reacao"])
_CVM_CASOS["Entrega"] = pd.to_datetime(_CVM_CASOS["Entrega"], errors="coerce")
_CVM_CASOS["Date"] = pd.to_datetime(_CVM_CASOS["Pregao_reacao"], errors="coerce")
_CVM_CLASS = pd.read_csv(DADOS / "cvm_classificado.csv", low_memory=False)
_DIST_CAP = pd.read_csv(DADOS / "distribuicao_capital_papeis.csv")
_IBOV = pd.read_csv(DADOS / "ibovespa_carteira_teorica.csv")


def painel_preco(ticker: str) -> pd.DataFrame:
    px = _OHLCV[_OHLCV["Ticker"] == ticker].sort_values("Data").reset_index(drop=True)
    px = px[px["Retorno"].notna()].reset_index(drop=True)
    ret_pct = px["Retorno"].values * 100.0
    g = arch_model(ret_pct, vol="Garch", p=1, q=1, dist="t").fit(disp="off")
    px["Volatilidade_GARCH"] = g.conditional_volatility
    d = pd.DataFrame({
        "Date": px["Data"],
        "Retorno_Ontem": px["Retorno"].shift(1) * 100.0,
        "Volatilidade_Ontem": px["Volatilidade_GARCH"].shift(1),
        "Alvo": np.where(px["Retorno"] > 0, 1, 0),
    })
    d = d.dropna(subset=["Retorno_Ontem", "Volatilidade_Ontem"]).reset_index(drop=True)
    garch_params = {"omega": round(float(g.params["omega"]), 5),
                    "alpha": round(float(g.params["alpha[1]"]), 4),
                    "beta": round(float(g.params["beta[1]"]), 4)}
    return d, garch_params, float(px["Fechamento"].iloc[-1]), str(px["Data"].iloc[-1].date())


def bloco_cvm(ticker: str, so_categoria: str | None) -> tuple[pd.DataFrame, list]:
    a = _CVM_CASOS[_CVM_CASOS["Ticker"] == ticker].copy()
    a = a[a["Entrega"].notna() & a["Date"].notna()]
    a = a[a["Entrega"].dt.hour >= 17]
    if so_categoria is not None:
        a = a[a["Categoria"] == so_categoria]
    c = a.merge(_CVM_CLASS[["Protocolo_Entrega", "p_pos", "p_neg", "p_neu", "Confianca"]],
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
    return f, [col for col in f.columns if col != "Date"], int(len(c))


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
            "p_binomial_vs_majoritaria": float(
                stats.binomtest(int((yt == pv).sum()), len(yt), maj).pvalue),
            "_prev": pv,
        }
    return out


def processa_papel(ticker: str) -> dict:
    print(f"\n{'='*90}\n  {ticker}\n{'='*90}")
    dp, garch_params, preco_atual, data_preco = painel_preco(ticker)
    f_fr, cols_fr, n_fr = bloco_cvm(ticker, "Fato Relevante")
    f_tot, cols_tot, n_tot = bloco_cvm(ticker, None)
    d = dp.merge(f_fr, on="Date", how="left").merge(f_tot, on="Date", how="left")
    for c in cols_fr + cols_tot:
        d[c] = d[c].fillna(0.0)

    tr, va, te = corta(d)
    yte = d["Alvo"].astype(int).iloc[te].values
    maj = max(yte.mean(), 1 - yte.mean())
    print(f"  pregões: {len(d):,}  teste: {len(yte):,}  majoritária: {maj:.2%}  "
          f"eventos FR: {n_fr}  eventos totais: {n_tot}  preço atual: {preco_atual:.2f} ({data_preco})")

    BASE = ["Retorno_Ontem", "Volatilidade_Ontem"]
    BRACOS = [
        ("apenas preço", BASE),
        ("preço + CVM (todos)", BASE + cols_tot),
        ("preço + CVM (só FR)", BASE + cols_fr),
    ]
    direcao, guarda = {}, {}
    for nome, cols in BRACOS:
        o = treina(d, cols, maj)
        guarda[nome] = {k: v.pop("_prev") for k, v in o.items()}
        direcao[nome] = o
        for mn, m in o.items():
            print(f"    {nome:<22} {mn:<9} acc={m['acuracia']:.2%}  auc={m['auc']:.3f}  "
                  f"p={m['p_binomial_vs_majoritaria']:.3f}")

    pares = [
        ("FR acrescenta sobre só preço?", "apenas preço", "preço + CVM (só FR)"),
        ("TODOS acrescentam sobre só preço?", "apenas preço", "preço + CVM (todos)"),
        ("SÓ FR x TODOS os comunicados", "preço + CVM (todos)", "preço + CVM (só FR)"),
    ]
    mcn = {}
    for rot, a, b in pares:
        for mn in ["SVM-RBF", "XGBoost"]:
            mcn[f"{mn} — {rot}"] = mcnemar(yte, guarda[a][mn], guarda[b][mn])

    ibov_row = _IBOV[_IBOV["cod"] == ticker]
    peso_ibov = float(str(ibov_row["part"].iloc[0]).replace(",", ".")) if len(ibov_row) else None
    nome_empresa = ibov_row["asset"].iloc[0] if len(ibov_row) else None

    inv_row = (_DIST_CAP[_DIST_CAP["Ticker"] == ticker]
               .sort_values("Data_Referencia").iloc[-1])

    return {
        "ticker": ticker, "empresa": nome_empresa, "peso_ibovespa_pct": peso_ibov,
        "preco_atual": round(preco_atual, 2), "data_preco": data_preco,
        "garch": garch_params,
        "n": {"total": int(len(d)), "teste": int(len(yte))},
        "majoritaria_teste": round(float(maj), 4),
        "n_eventos_cvm": {"fato_relevante": n_fr, "todos": n_tot},
        "investidores": {
            "data_referencia": inv_row["Data_Referencia"],
            "total": int(inv_row["Qtd_Acionistas_Total"]),
            "pessoa_fisica": int(inv_row["Quantidade_Acionistas_PF"]),
            "pessoa_juridica": int(inv_row["Quantidade_Acionistas_PJ"]),
            "institucionais": int(inv_row["Quantidade_Acionistas_Investidores_Institucionais"]),
            "acoes_em_circulacao": int(inv_row["Quantidade_Total_Acoes_Circulacao"]),
            "acoes_por_investidor": round(float(inv_row["Media_Acoes_Por_Acionista"]), 1),
        },
        "direcao": direcao,
        "mcnemar": mcn,
    }


def main() -> None:
    resultado = {"gerado_em": "2026-10-02", "protocolo": "Cap. 3 — GARCH+SVM/XGBoost, 60/15/25, McNemar",
                "fonte_ibovespa": "B3, carteira teórica, consultada em 02/10/2026",
                "papeis": {}}
    for tk in TOP10:
        resultado["papeis"][tk] = processa_papel(tk)
    (DADOS / "comparativo_top10_acoes.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\n  gravado: dados/comparativo_top10_acoes.json")


if __name__ == "__main__":
    main()
