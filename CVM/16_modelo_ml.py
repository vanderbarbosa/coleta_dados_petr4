# -*- coding: utf-8 -*-
# ==============================================================================
#   O MODELO DE APRENDIZADO DE MÁQUINA — como o escopo da pesquisa manda
#
#   Os scripts 07 a 15 usaram REGRAS FEITAS À MÃO: contar positivas e negativas,
#   subtrair, comparar com um limiar. Isso não é aprendizado de máquina, e não
#   era o escopo. O escopo é:
#
#       usar o encoder para classificar notícias e comunicados, e a partir
#       dessas representações TREINAR UM MODELO que projete direção e
#       volatilidade do pregão seguinte.
#
#   É o que este script faz. O que muda:
#
#   1. O ENCODER ENTRA INTEIRO, não como contagem. Entram as probabilidades
#      p_pos/p_neg/p_neu que a rede produz, a confiança, a dispersão da noite,
#      e — para os comunicados da CVM — o EMBEDDING de 768 dimensões, que é a
#      representação que o encoder constrói do texto antes de decidir o rótulo.
#      A contagem de positivas e negativas vira apenas mais uma coluna entre
#      dezenas; quem decide o peso de cada uma é o modelo, não eu.
#
#   2. O MODELO APRENDE, não obedece. Regressão logística, floresta aleatória e
#      gradient boosting, cada um livre para achar a relação que existir.
#
#   3. A VALIDAÇÃO É TEMPORAL. Treina no passado, testa no futuro, nunca
#      embaralha. A PCA dos embeddings é ajustada SÓ no treino de cada dobra.
#
#   4. O ADVERSÁRIO É HONESTO. Há um braço só com o histórico de preço, sem
#      texto nenhum. Se o texto não vencer esse braço, o texto não serve — e
#      isso precisa aparecer.
#
#   Saída: dados/modelo_ml.json
# ==============================================================================
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
RAIZ = AQUI.parent
TICKER = "PETR4"
N_PCA = 16          # componentes do embedding; ajustadas só no treino
TESTE = 250         # tamanho de cada bloco de teste, em pregões
MIN_TREINO = 500    # história mínima antes da primeira previsão


# ──────────────────────────────────────────────────────────────────────────────
#   1. O PREGÃO: alvos e o que dele já se sabia na véspera
# ──────────────────────────────────────────────────────────────────────────────
def painel_precos() -> pd.DataFrame:
    px = pd.read_csv(DADOS / "ohlcv_b3.csv", parse_dates=["Data"])
    px = px[px["Ticker"] == TICKER].sort_values("Data").reset_index(drop=True)

    px["vol_med5"] = px["Parkinson"].shift(1).rolling(5).mean()
    px["vol_med22"] = px["Parkinson"].shift(1).rolling(22).mean()
    px["razao_vol"] = px["Parkinson"] / px["vol_med5"]

    # ── os alvos ─────────────────────────────────────────────────────────────
    px["alvo_dir"] = (px["Retorno"] > 0).astype(int)
    px["alvo_vol"] = (px["razao_vol"] > 1.0).astype(int)
    lim = px["Parkinson"].shift(1).expanding(min_periods=250).quantile(0.90)
    px["alvo_ext"] = (px["Parkinson"] > lim).astype(int)
    px.loc[lim.isna(), "alvo_ext"] = np.nan

    # ── o que já se sabia ANTES do pregão abrir (tudo defasado) ──────────────
    for c in ["Parkinson", "Retorno", "Volume", "Gap", "Intradia"]:
        px[f"m_{c}_1"] = px[c].shift(1)
    px["m_absret_1"] = px["Retorno"].abs().shift(1)
    px["m_vol_med5"] = px["vol_med5"]
    px["m_vol_med22"] = px["vol_med22"]
    px["m_razao_vol_1"] = px["razao_vol"].shift(1)
    px["m_vol_ontem_sobre_med"] = px["Parkinson"].shift(1) / px["vol_med5"]
    px["m_giro_rel"] = px["Volume"].shift(1) / px["Volume"].shift(1).rolling(5).mean()
    px["m_absret_med5"] = px["Retorno"].abs().shift(1).rolling(5).mean()
    px["m_ret_med5"] = px["Retorno"].shift(1).rolling(5).mean()
    px["m_dp_ret5"] = px["Retorno"].shift(1).rolling(5).std()

    cols = ["Data", "alvo_dir", "alvo_vol", "alvo_ext", "Parkinson", "Retorno"]
    return px[cols + [c for c in px.columns if c.startswith("m_")]]


# ──────────────────────────────────────────────────────────────────────────────
#   2. A NOTÍCIA, pela saída do encoder — não pela contagem
# ──────────────────────────────────────────────────────────────────────────────
def painel_noticia() -> pd.DataFrame:
    n = pd.read_csv(RAIZ / "datasets_refino" / "01_noticias_apos_17h_v1.csv",
                    low_memory=False)
    n["pregao"] = pd.to_datetime(n["Data_Pregao_Atribuido"], errors="coerce")
    n = n[n["pregao"].notna()].copy()
    n["idx"] = pd.to_numeric(n["Sentimento_Indice"], errors="coerce")
    n["conf"] = pd.to_numeric(n["Sentimento_Confianca"], errors="coerce")
    rot = n["Sentimento_Rotulo"].astype(str).str.capitalize()

    g = n.groupby("pregao")
    f = pd.DataFrame({
        # volume de texto
        "nt_n": g.size(),
        # a distribuição do índice do encoder naquela noite
        "nt_idx_med": g["idx"].mean(),
        "nt_idx_dp": g["idx"].std(),
        "nt_idx_min": g["idx"].min(),
        "nt_idx_max": g["idx"].max(),
        "nt_idx_q10": g["idx"].quantile(0.10),
        "nt_idx_q90": g["idx"].quantile(0.90),
        "nt_idx_absmed": g["idx"].apply(lambda s: s.abs().mean()),
        # a confiança da rede
        "nt_conf_med": g["conf"].mean(),
        "nt_conf_max": g["conf"].max(),
    })
    # as proporções de rótulo entram como UMA coluna entre dezenas,
    # e quem decide o peso delas é o modelo
    for r in ["Positive", "Negative", "Neutral"]:
        f[f"nt_p_{r[:3].lower()}"] = n.assign(x=(rot == r)).groupby("pregao")["x"].mean()
    # as sete categorias temáticas
    if "Categoria" in n:
        cat = n.pivot_table(index="pregao", columns="Categoria", values="idx",
                            aggfunc="mean")
        cat.columns = [f"nt_cat_{c}" for c in cat.columns]
        f = f.join(cat)
    f["nt_log_n"] = np.log1p(f["nt_n"])
    return f.reset_index().rename(columns={"pregao": "Data"})


# ──────────────────────────────────────────────────────────────────────────────
#   3. A CVM — probabilidades da rede E o embedding de 768 dimensões
# ──────────────────────────────────────────────────────────────────────────────
def painel_cvm(_) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Usa a atribuição de pregão já validada no script 07, e restringe às
    entregas feitas com o pregão fechado (>= 17h), que é o desenho da pesquisa:
    a informação chega, ninguém pode negociar, e a primeira oportunidade é a
    abertura do pregão seguinte."""
    a = pd.read_csv(DADOS / "rodada_A_casos.csv", low_memory=False,
                    usecols=["Protocolo_Entrega", "Ticker", "Categoria",
                             "Entrega", "Pregao_reacao"])
    a = a[a["Ticker"] == TICKER].copy()
    a["Entrega"] = pd.to_datetime(a["Entrega"], errors="coerce")
    a["pregao"] = pd.to_datetime(a["Pregao_reacao"], errors="coerce")
    a = a[a["Entrega"].notna() & a["pregao"].notna()]
    a = a[a["Entrega"].dt.hour >= 17]                      # só após o fechamento

    c = pd.read_csv(DADOS / "cvm_classificado.csv", low_memory=False)
    c = a.merge(c[["Protocolo_Entrega", "p_pos", "p_neg", "p_neu", "Confianca"]],
                on="Protocolo_Entrega", how="inner")

    g = c.groupby("pregao")
    f = pd.DataFrame({
        "cv_n": g.size(),
        "cv_fr": c.assign(x=c["Categoria"].eq("Fato Relevante"))
                  .groupby("pregao")["x"].sum(),
        "cv_ppos_med": g["p_pos"].mean(), "cv_ppos_max": g["p_pos"].max(),
        "cv_pneg_med": g["p_neg"].mean(), "cv_pneg_max": g["p_neg"].max(),
        "cv_pneu_med": g["p_neu"].mean(), "cv_pneu_min": g["p_neu"].min(),
        "cv_conf_med": g["Confianca"].mean(), "cv_conf_max": g["Confianca"].max(),
    })
    f["cv_tem"] = 1.0
    f["cv_tem_fr"] = (f["cv_fr"] > 0).astype(float)
    f = f.reset_index().rename(columns={"pregao": "Data"})

    # ── o embedding: a representação que o encoder faz do texto ──────────────
    z = np.load(DADOS / "cvm_embeddings.npz", allow_pickle=True)
    emb = pd.DataFrame(z["emb"])
    emb.columns = [f"emb{i}" for i in range(emb.shape[1])]
    emb["Protocolo_Entrega"] = z["protocolo"]
    dims = [x for x in emb.columns if x.startswith("emb")]
    e = (c[["Protocolo_Entrega", "pregao"]]
         .merge(emb, on="Protocolo_Entrega", how="inner")
         .groupby("pregao")[dims].mean().reset_index()
         .rename(columns={"pregao": "Data"}))
    print(f"\n  comunicados da CVM apos o fechamento: {len(c):,} "
          f"em {c['pregao'].nunique():,} pregões")
    print(f"  com embedding recuperado            : {len(e):,} pregões")
    return f, e


# ──────────────────────────────────────────────────────────────────────────────
#   4. Treinar no passado, testar no futuro — nunca embaralhar
# ──────────────────────────────────────────────────────────────────────────────
def modelos() -> dict:
    return {
        "Regressão logística": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=2000, C=0.3)),
        "Floresta aleatória": RandomForestClassifier(
            n_estimators=400, min_samples_leaf=20, max_features="sqrt",
            random_state=42, n_jobs=-1),
        "Gradient boosting": HistGradientBoostingClassifier(
            max_iter=300, learning_rate=0.05, max_leaf_nodes=15,
            min_samples_leaf=30, l2_regularization=1.0, random_state=42),
    }


def caminha(d: pd.DataFrame, cols: list[str], alvo: str,
            cols_emb: list[str]) -> dict:
    """Janela expansiva: cada bloco de teste é previsto por um modelo que só
    viu o que veio antes dele. A PCA do embedding é ajustada só no treino."""
    d = d[d[alvo].notna()].reset_index(drop=True)
    usa = [c for c in cols if c in d.columns]
    if not usa or len(d) < MIN_TREINO + TESTE:
        return {}

    out = {nome: {"real": [], "prev": [], "prob": []} for nome in modelos()}
    inicio = MIN_TREINO
    while inicio + 1 <= len(d):
        fim = min(inicio + TESTE, len(d))
        tr, te = d.iloc[:inicio], d.iloc[inicio:fim]
        if te.empty or tr[alvo].nunique() < 2:
            inicio = fim
            continue

        Xtr, Xte = tr[usa].copy(), te[usa].copy()
        if cols_emb:
            ptr = tr[cols_emb].fillna(0.0).values
            pca = PCA(n_components=min(N_PCA, ptr.shape[1], len(tr) - 1),
                      random_state=42).fit(ptr)
            for i, v in enumerate(pca.transform(ptr).T):
                Xtr[f"pc{i}"] = v
            for i, v in enumerate(pca.transform(te[cols_emb].fillna(0.0).values).T):
                Xte[f"pc{i}"] = v

        med = Xtr.median(numeric_only=True)
        Xtr, Xte = Xtr.fillna(med).fillna(0.0), Xte.fillna(med).fillna(0.0)
        ytr, yte = tr[alvo].astype(int), te[alvo].astype(int)

        for nome, mod in modelos().items():
            m = mod.fit(Xtr, ytr)
            out[nome]["real"] += list(yte)
            out[nome]["prev"] += list(m.predict(Xte))
            out[nome]["prob"] += list(m.predict_proba(Xte)[:, 1])
        inicio = fim

    res = {}
    for nome, o in out.items():
        if len(o["real"]) < 100:
            continue
        r, p = np.array(o["real"]), np.array(o["prev"])
        maj = max(r.mean(), 1 - r.mean())
        acc = accuracy_score(r, p)
        res[nome] = {
            "n": int(len(r)), "acuracia": round(float(acc), 4),
            "majoritaria": round(float(maj), 4),
            "ganho_pp": round(float((acc - maj) * 100), 2),
            "f1_macro": round(float(f1_score(r, p, average="macro")), 4),
            "mcc": round(float(matthews_corrcoef(r, p)), 4),
            "auc": round(float(roc_auc_score(r, o["prob"])), 4),
            "p_vs_acaso": float(stats.binomtest(int((r == p).sum()), len(r), 0.5).pvalue),
            "prev_classe1_pct": round(float(p.mean() * 100), 1),
        }
    return res


def main() -> None:
    px = painel_precos()
    nt = painel_noticia()
    cv, emb = painel_cvm(px["Data"])

    d = (px.merge(nt, on="Data", how="left")
           .merge(cv, on="Data", how="left")
           .merge(emb, on="Data", how="left")
           .sort_values("Data").reset_index(drop=True))
    for c in ["cv_n", "cv_fr", "cv_tem", "cv_tem_fr", "nt_n", "nt_log_n"]:
        d[c] = d[c].fillna(0.0)

    C_MERC = [c for c in d.columns if c.startswith("m_")]
    C_NOT = [c for c in d.columns if c.startswith("nt_")]
    C_CVM = [c for c in d.columns if c.startswith("cv_")]
    C_EMB = [c for c in d.columns if c.startswith("emb")]

    print("=" * 96)
    print(f"  MODELO DE APRENDIZADO DE MÁQUINA — {TICKER}")
    print("=" * 96)
    print(f"\n  pregões no painel      : {len(d):,}")
    print(f"  período                : {d['Data'].min():%d/%m/%Y} a {d['Data'].max():%d/%m/%Y}")
    print(f"  colunas de mercado     : {len(C_MERC)}")
    print(f"  colunas de notícia     : {len(C_NOT)}")
    print(f"  colunas de CVM         : {len(C_CVM)}")
    print(f"  dimensões do embedding : {len(C_EMB)}  (viram {N_PCA} componentes)")
    print(f"\n  validação: treina no passado, testa nos {TESTE} pregões seguintes,")
    print(f"             repete. Mínimo de {MIN_TREINO} pregões de história.")

    BRACOS = {
        "só mercado (sem texto)": (C_MERC, []),
        "só notícia": (C_NOT, []),
        "só CVM (rótulos)": (C_CVM, []),
        "só CVM (rótulos + embedding)": (C_CVM, C_EMB),
        "notícia + CVM": (C_NOT + C_CVM, []),
        "notícia + CVM + embedding": (C_NOT + C_CVM, C_EMB),
        "mercado + notícia + CVM": (C_MERC + C_NOT + C_CVM, []),
        "TUDO (mercado + texto + embedding)": (C_MERC + C_NOT + C_CVM, C_EMB),
    }
    ALVOS = {
        "alvo_dir": "DIREÇÃO — o pregão seguinte fecha em alta?",
        "alvo_vol": "VOLATILIDADE — o pregão seguinte sacode mais que a média de 5 dias?",
        "alvo_ext": "DIA EXCEPCIONAL — o pregão seguinte entra nos 10% mais agitados?",
    }

    res = {"ticker": TICKER, "n": int(len(d)),
           "periodo": [str(d["Data"].min().date()), str(d["Data"].max().date())],
           "alvos": {}}

    for alvo, titulo in ALVOS.items():
        print("\n" + "=" * 96)
        print(f"  {titulo}")
        print("=" * 96)
        print(f"\n  {'braço':<36} {'modelo':<22} {'acertou':>8} {'palpite':>8} "
              f"{'ganho':>7} {'AUC':>7} {'p':>9}")
        print("  " + "-" * 92)
        res["alvos"][alvo] = {}
        for braco, (cols, ce) in BRACOS.items():
            r = caminha(d, cols, alvo, ce)
            if not r:
                continue
            res["alvos"][alvo][braco] = r
            for nome, m in r.items():
                ok = "  *" if m["p_vs_acaso"] < 0.05 and m["ganho_pp"] > 0 else ""
                print(f"  {braco:<36} {nome:<22} {m['acuracia']:>7.1%} "
                      f"{m['majoritaria']:>7.1%} {m['ganho_pp']:>+6.2f} "
                      f"{m['auc']:>7.3f} {m['p_vs_acaso']:>9.4f}{ok}")

    (DADOS / "modelo_ml.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    d.to_csv(DADOS / "painel_ml.csv", index=False, encoding="utf-8-sig")
    print("\n  gravados: dados/modelo_ml.json e dados/painel_ml.csv")


if __name__ == "__main__":
    main()
