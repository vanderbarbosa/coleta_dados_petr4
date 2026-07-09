# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Pipeline REORDENADO com FILTRO DE RELEVÂNCIA (jul/2026)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Hipótese da banca/orientando: a acurácia é baixa porque o sentimento diário
#   mistura notícias irrelevantes. Testa a ordem: (1) coleta → (2) após 17h →
#   (3) FILTRO DE RELEVÂNCIA (só o que afeta o preço) → (4) encoders/predição.
#
#   Gera (só dados REAIS de noticias_com_sentimento.csv + base_master_petr4.csv):
#     • CSV das notícias após 17h (com índice único por notícia)
#     • CSV das notícias RELEVANTES ao contexto (menção direta à empresa/petróleo)
#     • CSV por período (Treino/Teste/Validação) com sentimento + risco + predição
#     • Re-treino/teste/validação da DIREÇÃO comparando SEM x COM filtro (datado)
#     • Re-teste da causalidade de Granger (sentimento → volatilidade) por variante
# ==============================================================================
import sys, unicodedata, json
from datetime import date
from pathlib import Path
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
MP = RAIZ / "Mestrado_PETR4"
OUT = RAIZ / "datasets_refino"
OUT.mkdir(exist_ok=True)
HOJE = "2026-07-05"
sys.path.insert(0, str(RAIZ / "src" / "comum"))
import taxonomia as tx

ENC = "FinBERT-PT-BR (lucas-leme/FinBERT-PT-BR); max_length=512; truncation=True"
M_RISCO = "GARCH(1,1) t-Student"
M_FUSION = "XGBoost; features=[Retorno_Ontem, Volatilidade_Ontem, Sentimento_Ontem]"


def sa(s):
    return "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c)).lower()

TER_REL = [sa(t) for t in tx.TERMOS_RELEVANCIA_ESTRITA]   # menção direta (empresa/petróleo)


# ── 1) Corpus por notícia (após 17h) com índice único ─────────────────────────
cols = ["Data_Coleta", "data_gmt", "Data_Ajustada", "categoria", "Fonte", "dominio",
        "Titulo", "Resumo", "URL", "Idioma", "Indice_Sentimento", "Label_Sentimento",
        "Score_Confianca"]
c = pd.read_csv(MP / "noticias_com_sentimento.csv", usecols=lambda x: x in cols)
c["dt_pub"] = pd.to_datetime(c["Data_Coleta"], errors="coerce")
ap = c[c["dt_pub"].dt.hour >= 17].copy()
ap = ap.sort_values(["data_gmt", "Titulo"]).reset_index(drop=True)
ap["indice"] = ["N%07d" % (i + 1) for i in range(len(ap))]

# pregão atribuído = próximo pregão real (>= Data_Ajustada), via calendário da base
bm = pd.read_csv(MP / "base_master_petr4.csv", parse_dates=["Date"]).sort_values("Date").reset_index(drop=True)
cal = bm[["Date"]].copy()
ap["_da"] = pd.to_datetime(ap["Data_Ajustada"], errors="coerce")
ap = ap[ap["_da"].notna()].sort_values("_da")
ap = pd.merge_asof(ap, cal.rename(columns={"Date": "Pregao"}), left_on="_da", right_on="Pregao", direction="forward")
ap["Data_Pregao_Atribuido"] = ap["Pregao"].dt.strftime("%Y-%m-%d")

txt = (ap["Titulo"].fillna("") + " " + ap["Resumo"].fillna("")).map(sa)
ap["rel_direta"] = txt.apply(lambda t: any(k in t for k in TER_REL))
ap["cat12"] = ap["categoria"].isin(["CAT1_Empresa", "CAT2_Mercado_Petroleo"])

ESQ = ["indice", "Data_Publicacao", "data_gmt", "Data_Pregao_Atribuido", "Categoria",
       "Portal", "Fonte", "Noticia", "Resumo", "URL", "Idioma"]
def esquema_noticias(d):
    return pd.DataFrame({
        "indice": d["indice"], "Data_Publicacao": d["Data_Coleta"], "data_gmt": d["data_gmt"],
        "Data_Pregao_Atribuido": d["Data_Pregao_Atribuido"], "Categoria": d["categoria"],
        "Portal": d["dominio"], "Fonte": d["Fonte"], "Noticia": d["Titulo"],
        "Resumo": d["Resumo"], "URL": d["URL"], "Idioma": d["Idioma"]})[ESQ]

esquema_noticias(ap).to_csv(OUT / f"10_noticias_apos_17h_{HOJE}.csv", index=False, encoding="utf-8-sig")
rel = ap[ap["rel_direta"]].copy()
esquema_noticias(rel).to_csv(OUT / f"11_noticias_relevantes_{HOJE}.csv", index=False, encoding="utf-8-sig")
print(f"[1] após17h={len(ap):,} | relevantes(menção direta)={len(rel):,} ({100*len(rel)/len(ap):.1f}%)")


# ── 2) Split cronológico 60/15/25 sobre os pregões cobertos (2018–2025) ───────
bm18 = bm[(bm["Date"] >= "2018-01-01") & (bm["Date"] <= "2025-12-31")].sort_values("Date").reset_index(drop=True)
n = len(bm18); i_tr, i_va = int(n * 0.60), int(n * 0.75)
d_tr_fim, d_va_fim = bm18["Date"].iloc[i_tr - 1], bm18["Date"].iloc[i_va - 1]
def periodo(dt):
    dt = pd.to_datetime(dt)
    return "Treino" if dt <= d_tr_fim else ("Validacao" if dt <= d_va_fim else "Teste")
print(f"[2] pregões 2018-2025={n} | Treino<= {d_tr_fim.date()} | Val<= {d_va_fim.date()} | Teste> {d_va_fim.date()}")


# ── 3) Re-treino/teste da DIREÇÃO: SEM x COM filtro de relevância ─────────────
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score, matthews_corrcoef
from scipy.stats import binomtest
from statsmodels.tsa.stattools import grangercausalitytests
from xgboost import XGBClassifier

def ism_diario(sub):
    g = sub.groupby("Data_Pregao_Atribuido")["Indice_Sentimento"].mean()
    g.index = pd.to_datetime(g.index)
    return g

VARIANTES = {
    "todas_apos17h": ap,                       # todas as após-17h (só limpeza)
    "relevante_direta": ap[ap["rel_direta"]],  # + filtro de relevância (menção direta)
    "categoria_CAT1_CAT2": ap[ap["cat12"]],    # + filtro por categoria mais direta
}
bm18 = bm18.copy()
bm18["ret_ontem"] = bm18["Log_Retorno_Pct"].shift(1)
bm18["vol_ontem"] = bm18["Volatilidade_GARCH"].shift(1)

resultados = []
preds_por_variante = {}
for nome, sub in VARIANTES.items():
    ism = ism_diario(sub)
    d = bm18.copy()
    d["Sent"] = d["Date"].map(ism).astype(float)     # sentimento pré-mercado do pregão
    cobertura = d["Sent"].notna().mean()
    d["Sent"] = d["Sent"].fillna(0.0)
    d = d.dropna(subset=["ret_ontem", "vol_ontem"]).reset_index(drop=True)
    X = d[["ret_ontem", "vol_ontem", "Sent"]].values
    y = d["Alvo"].astype(int).values
    m = len(d); a, b = int(m * 0.60), int(m * 0.75)
    sc = StandardScaler().fit(X[:a])
    Xtr, Xva, Xte = sc.transform(X[:a]), sc.transform(X[a:b]), sc.transform(X[b:])
    mdl = XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
                        colsample_bytree=0.9, eval_metric="logloss", tree_method="hist",
                        random_state=42, n_jobs=4)
    mdl.fit(Xtr, y[:a])
    p_va, p_te = mdl.predict_proba(Xva)[:, 1], mdl.predict_proba(Xte)[:, 1]
    best_t, best_acc = 0.5, -1
    for t in np.arange(0.40, 0.601, 0.01):
        ac = accuracy_score(y[a:b], (p_va >= t).astype(int))
        if ac > best_acc:
            best_acc, best_t = ac, t
    pred_te = (p_te >= best_t).astype(int)
    acc = accuracy_score(y[b:], pred_te)
    base = max((y[b:] == 1).mean(), (y[b:] == 0).mean())
    # Granger sentimento -> volatilidade
    try:
        gg = grangercausalitytests(d[["Volatilidade_GARCH", "Sent"]].dropna(), maxlag=5, verbose=False)
        p_granger = round(min(gg[k][0]["ssr_ftest"][1] for k in gg), 4)
    except Exception:
        p_granger = None
    met = {"data": HOJE, "variante": nome, "cobertura_dias_com_noticia": round(float(cobertura), 3),
           "n_teste": int(len(y[b:])), "acuracia_teste": round(acc * 100, 2),
           "auc": round(roc_auc_score(y[b:], p_te), 4), "f1_macro": round(f1_score(y[b:], pred_te, average="macro") * 100, 2),
           "mcc": round(matthews_corrcoef(y[b:], pred_te), 4), "limiar": round(float(best_t), 2),
           "baseline_maj": round(base * 100, 2), "supera_baseline": bool(acc > base),
           "p_binomial_vs_50": round(binomtest(int((pred_te == y[b:]).sum()), len(y[b:]), 0.5, alternative="greater").pvalue, 4),
           "p_granger_sent_para_vol_min": p_granger}
    resultados.append(met)
    dprev = pd.DataFrame({"Data": d["Date"].dt.strftime("%Y-%m-%d"),
                          "prob_alta": np.round(mdl.predict_proba(sc.transform(X))[:, 1], 4)})
    dprev["previsto"] = (dprev["prob_alta"] >= best_t).astype(int)
    dprev["real"] = y
    preds_por_variante[nome] = dprev.set_index("Data")
    dprev.to_csv(OUT / f"exp_{HOJE}_XGBoost_{nome}.csv", index=False, encoding="utf-8-sig")
    print(f"  ✓ {nome:<20} cobertura={cobertura:.2f} acc_teste={met['acuracia_teste']}% "
          f"auc={met['auc']} granger_p={p_granger} {'>base' if met['supera_baseline'] else '<=base'}")

res = pd.DataFrame(resultados).sort_values("acuracia_teste", ascending=False)
res.to_csv(OUT / f"resultados_relevancia_{HOJE}.csv", index=False, encoding="utf-8-sig")
(OUT / f"resultados_relevancia_{HOJE}.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")


# ── 4) CSVs por período (Treino/Teste/Validação) com sentimento + risco + predição ─
prev_rel = preds_por_variante["relevante_direta"]   # predição da variante relevante
bm_key = bm.set_index(bm["Date"].dt.strftime("%Y-%m-%d"))
rel = rel.copy()
rel["Periodo"] = rel["Data_Pregao_Atribuido"].map(periodo)
rel = rel[rel["Data_Pregao_Atribuido"].isin(bm_key.index)]
per = pd.DataFrame({
    "indice": rel["indice"], "Data_Publicacao": rel["Data_Coleta"],
    "Data_Pregao_Atribuido": rel["Data_Pregao_Atribuido"], "Noticia": rel["Titulo"], "Resumo": rel["Resumo"],
    "Encoder_Sentimento": ENC, "Sentimento_Indice": rel["Indice_Sentimento"],
    "Sentimento_Rotulo": rel["Label_Sentimento"], "Sentimento_Confianca": rel["Score_Confianca"],
    "Volatilidade_GARCH_pregao": rel["Data_Pregao_Atribuido"].map(bm_key["Volatilidade_GARCH"]),
    "Log_Retorno_Pct_pregao": rel["Data_Pregao_Atribuido"].map(bm_key["Log_Retorno_Pct"]),
    "Direcao_Real_pregao": rel["Data_Pregao_Atribuido"].map(bm_key["Alvo"]).map({1: "alta", 0: "baixa"}),
    "Prob_Alta_prevista": rel["Data_Pregao_Atribuido"].map(prev_rel["prob_alta"]),
    "Direcao_Prevista_pregao": rel["Data_Pregao_Atribuido"].map(prev_rel["previsto"]).map({1: "alta", 0: "baixa"}),
    "Modelo_Risco": M_RISCO, "Modelo_DataFusion": M_FUSION, "Data_Execucao": HOJE, "Periodo": rel["Periodo"],
})
for p in ["Treino", "Validacao", "Teste"]:
    sub = per[per["Periodo"] == p]
    sub.to_csv(OUT / f"12_relevantes_{p}_{HOJE}.csv", index=False, encoding="utf-8-sig")
    print(f"  ✓ 12_relevantes_{p}_{HOJE}.csv  ({len(sub):,} notícias relevantes)")

print("\n=== COMPARAÇÃO (acurácia de teste) ===")
print(res[["variante", "cobertura_dias_com_noticia", "acuracia_teste", "auc", "p_granger_sent_para_vol_min", "supera_baseline"]].to_string(index=False))
