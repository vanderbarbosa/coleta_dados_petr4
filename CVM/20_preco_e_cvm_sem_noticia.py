# -*- coding: utf-8 -*-
# ==============================================================================
#   PREÇO, E PREÇO + CVM (COM E SEM FILTRO DE FATO RELEVANTE) — pedido do
#   Prof. Julio em 30/09/2026, itens 2, 4, 5 e 6.
#
#   POR QUE ESTE SCRIPT EXISTE, E NÃO O 18/19 DIRETO:
#   Mestrado_PETR4/base_master_petr4.csv (gitignored) não está nesta máquina —
#   ele é montado pelo Script 04 a partir do ISM diário de notícias
#   (indice_sentimento_petr4.csv), que por sua vez exige o corpus classificado
#   de notícias, também ausente aqui. Os braços que dependem de NOTÍCIA
#   (itens 3 e 7 do pedido) não podem ser reexecutados nesta máquina — ver
#   aviso impresso no fim. Os que dependem só de PREÇO e CVM podem, porque
#   ohlcv_b3.csv (preço) está presente e o GARCH(1,1) é recalculado aqui, com
#   os MESMOS parâmetros do Script 04 (vol='Garch', p=1, q=1, dist='t'),
#   conferidos linha a linha nessa fonte antes de escrever este script.
#
#   Protocolo idêntico ao Script 18 (Cap. 3): SVM-RBF e XGBoost (300 árvores,
#   depth 3, lr 0,05, subsample 0,9), split cronológico 60/15/25, McNemar.
#
#   Saída: dados/preco_e_cvm_sem_noticia.json
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
DADOS, RAIZ = AQUI / "dados", AQUI.parent
TICKER = "PETR4"

XGB = dict(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
           colsample_bytree=0.9, random_state=42, eval_metric="logloss", n_jobs=-1)


# ──────────────────────────────────────────────────────────────────────────────
#   Painel de preço (sem notícia) — Retorno_Ontem, Volatilidade_Ontem, Alvo
# ──────────────────────────────────────────────────────────────────────────────
def painel_preco() -> pd.DataFrame:
    px = pd.read_csv(DADOS / "ohlcv_b3.csv", parse_dates=["Data"])
    px = px[px["Ticker"] == TICKER].sort_values("Data").reset_index(drop=True)
    px = px[px["Retorno"].notna()].reset_index(drop=True)

    ret_pct = px["Retorno"].values * 100.0
    g = arch_model(ret_pct, vol="Garch", p=1, q=1, dist="t").fit(disp="off")
    px["Volatilidade_GARCH"] = g.conditional_volatility
    print(f"  GARCH(1,1) ajustado aqui — ω={g.params['omega']:.5f}  "
          f"α={g.params['alpha[1]']:.4f}  β={g.params['beta[1]']:.4f}  "
          f"(conferir com o Script 04: α+β deve ficar perto de 0,98)")

    d = pd.DataFrame({
        "Date": px["Data"],
        "Retorno_Ontem": px["Retorno"].shift(1) * 100.0,
        "Volatilidade_Ontem": px["Volatilidade_GARCH"].shift(1),
        "Alvo": np.where(px["Retorno"] > 0, 1, 0),
    })
    return d.dropna(subset=["Retorno_Ontem", "Volatilidade_Ontem"]).reset_index(drop=True)


def bloco_cvm(so_categoria: str | None) -> tuple[pd.DataFrame, list]:
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
            "ganho_pp_vs_majoritaria": round((accuracy_score(yt, pv) - maj) * 100, 2),
            "p_binomial_vs_majoritaria": float(
                stats.binomtest(int((yt == pv).sum()), len(yt), maj).pvalue),
            "_prev": pv,
        }
    return out


def main() -> None:
    print("=" * 100)
    print("  ITENS 2, 4, 5 e 6 DO PEDIDO (30/09/2026) — PREÇO, E PREÇO + CVM — PETR4")
    print("=" * 100)
    dp = painel_preco()
    f_fr, cols_fr = bloco_cvm("Fato Relevante")
    f_tot, cols_tot = bloco_cvm(None)
    d = dp.merge(f_fr, on="Date", how="left").merge(f_tot, on="Date", how="left")
    for c in cols_fr + cols_tot:
        d[c] = d[c].fillna(0.0)

    tr, va, te = corta(d)
    yte = d["Alvo"].astype(int).iloc[te].values
    maj = max(yte.mean(), 1 - yte.mean())
    print(f"\n  pregões: {len(d):,}  ({d['Date'].min():%d/%m/%Y} a {d['Date'].max():%d/%m/%Y})")
    print(f"  teste: {len(yte):,}   classe majoritária: {maj:.2%}")
    print(f"  pregões do teste com Fato Relevante na véspera: "
          f"{int(d['CVM_FR_Tem_Ontem'].iloc[te].sum()):,}")
    print(f"  pregões do teste com QUALQUER comunicado na véspera: "
          f"{int(d['CVM_TODOS_Tem_Ontem'].iloc[te].sum()):,}")

    BASE = ["Retorno_Ontem", "Volatilidade_Ontem"]
    BRACOS = [
        ("2. apenas preço histórico", BASE),
        ("4. preço + CVM (TODOS os comunicados)", BASE + cols_tot),
        ("5. preço + CVM (SÓ Fato Relevante)", BASE + cols_fr),
    ]

    print(f"\n  {'braço':<42} {'modelo':<9} {'acur':>7} {'ganho pp':>9} {'AUC':>7} {'p vs maj':>9}")
    print("  " + "-" * 88)
    res, guarda = {"n": {"total": int(len(d)), "teste": int(len(yte))},
                  "majoritaria_teste": round(float(maj), 4), "direcao": {}}, {}
    for nome, cols in BRACOS:
        o = treina(d, cols, maj)
        guarda[nome] = {k: v.pop("_prev") for k, v in o.items()}
        res["direcao"][nome] = o
        for mn, m in o.items():
            sinal = "  *" if m["p_binomial_vs_majoritaria"] < 0.05 else ""
            print(f"  {nome:<42} {mn:<9} {m['acuracia']:>6.2%} {m['ganho_pp_vs_majoritaria']:>+8.2f} "
                  f"{m['auc']:>7.3f} {m['p_binomial_vs_majoritaria']:>9.4f}{sinal}")

    print("\n" + "=" * 100)
    print("  McNEMAR — item 6 e os controles do item 5")
    print("=" * 100)
    PARES = [
        ("5 vs 2 — o Fato Relevante acrescenta sobre só preço?",
         "2. apenas preço histórico", "5. preço + CVM (SÓ Fato Relevante)"),
        ("4 vs 2 — TODOS os comunicados acrescentam sobre só preço?",
         "2. apenas preço histórico", "4. preço + CVM (TODOS os comunicados)"),
        ("6 — SÓ Fato Relevante é melhor/pior que TODOS os comunicados?",
         "4. preço + CVM (TODOS os comunicados)", "5. preço + CVM (SÓ Fato Relevante)"),
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

    print("\n  " + "!" * 96)
    print("  ITENS 3 e 7 (notícia de jornal, sozinha e combinada com Fato Relevante)")
    print("  NÃO foram reexecutados nesta máquina: dependem do corpus de notícias")
    print("  classificado (indice_sentimento_petr4.csv), que não está aqui. O item 3")
    print("  (preço + notícia) tem um número de execução anterior, registrado em")
    print("  pesquisa_com_cvm.json — mas não é execução de hoje, e por isso é citado")
    print("  à parte. O item 7 (notícia + SÓ Fato Relevante) nunca foi calculado.")
    print("  " + "!" * 96)

    (DADOS / "preco_e_cvm_sem_noticia.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print("\n  gravado: dados/preco_e_cvm_sem_noticia.json")


if __name__ == "__main__":
    main()
