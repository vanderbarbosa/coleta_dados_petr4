# -*- coding: utf-8 -*-
# ==============================================================================
#   PETR4 — API da Pesquisa (backend FastAPI)
#   Dissertação: O Impacto do Sentimento de Notícias Financeiras na Previsão
#   de Direção e Volatilidade do Ativo PETR4 | Vanderlei Barbosa da Silva
#
#   Serve, a partir dos DADOS REAIS da pesquisa, endpoints para o site:
#     • /api/noticias   — consulta de notícias com filtro por categoria/data/texto
#     • /api/categorias — categorias temáticas e contagens
#     • /api/precos     — série de preços da PETR4 com filtro por data/ano/mês
#     • /api/estatisticas — agregados (por ano, categoria, portal, Lead-Lag)
#
#   Execução (ambiente 'base', que tem pandas):
#     uvicorn app:app --reload --port 8000     (a partir de site/backend/)
# ==============================================================================

import sys
from pathlib import Path
from functools import lru_cache

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "Mestrado_PETR4"
sys.path.insert(0, str(RAIZ / "src" / "comum"))
try:
    import taxonomia as tx
    ROTULOS = tx.ROTULOS_CATEGORIA
except Exception:
    ROTULOS = {}

app = FastAPI(title="PETR4 — API da Pesquisa", version="0.1.0",
              description="API que serve os dados reais da dissertação sobre sentimento e PETR4.")

# CORS liberado para o frontend de desenvolvimento (Vite/React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_methods=["*"], allow_headers=["*"],
)


# ── Carga preguiçosa e cacheada dos dados ─────────────────────────────────────
@lru_cache(maxsize=1)
def carregar_noticias() -> pd.DataFrame:
    cols = ["data_publicacao", "categoria", "fonte_coleta", "termo_busca",
            "titulo", "resumo", "url", "dominio", "conjunto"]
    arq = DADOS / "base_textual_petr4_tratada.csv"
    df = pd.read_csv(arq, usecols=lambda c: c in cols)
    df["dt"] = pd.to_datetime(df["data_publicacao"], errors="coerce")
    df = df[df["dt"].notna()].copy()
    return df


@lru_cache(maxsize=1)
def carregar_precos() -> pd.DataFrame:
    df = pd.read_csv(DADOS / "base_financeira_petr4.csv", parse_dates=["Date"])
    return df


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/api/saude")
def saude():
    return {"status": "ok", "servico": "PETR4 API da Pesquisa"}


@app.get("/api/categorias")
def categorias():
    df = carregar_noticias()
    vc = df["categoria"].value_counts()
    return [{"id": c, "rotulo": ROTULOS.get(c, c), "total": int(n)} for c, n in vc.items()]


@app.get("/api/noticias")
def noticias(
    categoria: str | None = None,
    inicio: str | None = None,   # data inicial YYYY-MM-DD
    fim: str | None = None,      # data final YYYY-MM-DD
    q: str | None = None,        # busca textual no título
    pagina: int = 1,
    por_pagina: int = 20,
):
    por_pagina = max(1, min(int(por_pagina), 100))
    df = carregar_noticias()
    if categoria:
        df = df[df["categoria"] == categoria]
    if inicio:
        df = df[df["dt"] >= pd.to_datetime(inicio)]
    if fim:
        df = df[df["dt"] < pd.to_datetime(fim) + pd.Timedelta(days=1)]
    if q:
        df = df[df["titulo"].str.contains(q, case=False, na=False)]

    total = len(df)
    df = df.sort_values("dt", ascending=False)
    ini = max(0, (pagina - 1) * por_pagina)
    page = df.iloc[ini:ini + por_pagina]
    itens = [{
        "data": str(r["data_publicacao"]),
        "categoria": r["categoria"],
        "rotulo_categoria": ROTULOS.get(r["categoria"], r["categoria"]),
        "titulo": r["titulo"],
        "resumo": r.get("resumo", ""),
        "fonte": r.get("dominio", ""),
        "url": r.get("url", ""),
        "conjunto": r.get("conjunto", ""),
    } for _, r in page.iterrows()]
    return {"total": total, "pagina": pagina, "por_pagina": por_pagina, "itens": itens}


@app.get("/api/precos")
def precos(
    inicio: str | None = None,
    fim: str | None = None,
    ano: int | None = None,
    mes: int | None = None,
):
    df = carregar_precos()
    if ano:
        df = df[df["Date"].dt.year == ano]
    if mes:
        df = df[df["Date"].dt.month == mes]
    if inicio:
        df = df[df["Date"] >= pd.to_datetime(inicio)]
    if fim:
        df = df[df["Date"] <= pd.to_datetime(fim)]
    return [{
        "data": d.strftime("%Y-%m-%d"),
        "abertura": round(float(o), 2),
        "fechamento": round(float(c), 2),
        "maxima": round(float(h), 2),
        "minima": round(float(l), 2),
        "volume": int(v),
        "log_retorno": round(float(lr), 4),
    } for d, o, c, h, l, v, lr in zip(
        df["Date"], df["Open"], df["Close"], df["High"], df["Low"],
        df["Volume"], df["Log_Retorno"])]


@app.get("/api/estatisticas")
def estatisticas():
    n = carregar_noticias()
    p = carregar_precos()
    por_ano = n["dt"].dt.year.value_counts().sort_index()
    por_cat = n["categoria"].value_counts()
    por_portal = n["dominio"].value_counts()
    lead_lag = float((n["dt"].dt.hour >= 17).mean() * 100)
    return {
        "noticias_total": int(len(n)),
        "pregoes_total": int(len(p)),
        "periodo_noticias": [str(n["dt"].min().date()), str(n["dt"].max().date())],
        "periodo_precos": [str(p["Date"].min().date()), str(p["Date"].max().date())],
        "lead_lag_pct": round(lead_lag, 1),
        "por_ano": {str(k): int(v) for k, v in por_ano.items()},
        "por_categoria": [{"id": c, "rotulo": ROTULOS.get(c, c), "total": int(v)} for c, v in por_cat.items()],
        "por_portal": {str(k): int(v) for k, v in por_portal.items()},
    }


# ── Previsão de direção a partir de uma notícia ───────────────────────────────
# Requer o ambiente 'petr4' (torch + transformers + xgboost). Os imports são
# preguiçosos (lazy) para que os endpoints de dados funcionem mesmo no 'base'.

TERMOS_RELEVANCIA = getattr(tx, "TERMOS_RELEVANCIA_ESTRITA", ["petrobras", "petr4", "petróleo"])
_modelo_cache = {}


def _carregar_preditor():
    """Carrega (uma vez) o modelo XGBoost, os metadados e o pipeline FinBERT-PT-BR."""
    if _modelo_cache:
        return _modelo_cache
    import json
    # SSL relaxado para o Hugging Face (proxy); o modelo já está em cache local.
    try:
        import huggingface_hub, requests, urllib3
        urllib3.disable_warnings()
        huggingface_hub.configure_http_backend(
            backend_factory=lambda: (lambda s: (s.__setattr__("verify", False) or s))(requests.Session()))
    except Exception:
        pass
    from transformers import pipeline
    from xgboost import XGBClassifier

    with open(DADOS / "modelo_meta.json", encoding="utf-8") as f:
        meta = json.load(f)
    modelo = XGBClassifier()
    modelo.load_model(str(DADOS / "modelo_xgb_fusion.json"))
    nlp = pipeline("sentiment-analysis", model="lucas-leme/FinBERT-PT-BR",
                   truncation=True, max_length=512, device=-1)
    _modelo_cache.update(meta=meta, modelo=modelo, nlp=nlp)
    return _modelo_cache


class EntradaPrevisao(BaseModel):
    texto: str


@app.post("/api/prever")
def prever(entrada: EntradaPrevisao):
    texto = (entrada.texto or "").strip()
    if len(texto) < 10:
        return {"erro": "Informe um texto de notícia com pelo menos 10 caracteres."}

    p = _carregar_preditor()
    meta, modelo, nlp = p["meta"], p["modelo"], p["nlp"]

    # 1) Sentimento (FinBERT-PT-BR) → índice em [-1, +1]
    r = nlp(texto)[0]
    L = str(r["label"]).upper()
    polaridade = 1 if "POS" in L else (-1 if "NEG" in L else 0)
    indice = polaridade * float(r["score"])
    rotulo_sent = "Positivo" if polaridade > 0 else ("Negativo" if polaridade < 0 else "Neutro")

    # 2) Relevância temática (relacionada ao ativo/commodity)
    alvo = texto.lower()
    relevante = any(t in alvo for t in TERMOS_RELEVANCIA)

    # 3) Previsão de direção do próximo pregão (XGBoost Data Fusion)
    import numpy as np
    X = np.array([[meta["retorno_recente"], meta["volatilidade_recente"], indice]])
    prob_alta = float(modelo.predict_proba(X)[0, 1])

    # 4) Veredito (honesto: só afirma direção com confiança mínima)
    if not relevante:
        direcao, explica = "sem_influencia", "A notícia não aparenta relação direta com a Petrobras/PETR4 ou com o mercado de petróleo."
    elif prob_alta >= 0.55:
        direcao, explica = "alta", "O modelo indica tendência de ALTA no próximo pregão."
    elif prob_alta <= 0.45:
        direcao, explica = "baixa", "O modelo indica tendência de BAIXA no próximo pregão."
    else:
        direcao, explica = "indefinida", "O modelo não identifica direção clara (provável baixa influência)."

    return {
        "sentimento": {"rotulo": rotulo_sent, "indice": round(indice, 4), "confianca": round(float(r["score"]), 4)},
        "relevante": relevante,
        "prob_alta": round(prob_alta, 4),
        "direcao": direcao,
        "explicacao": explica,
        "contexto": {
            "data_referencia": meta["data_referencia"],
            "retorno_recente_pct": round(meta["retorno_recente"], 3),
            "volatilidade_recente": round(meta["volatilidade_recente"], 3),
            "modelo": "XGBoost Data Fusion (preços + GARCH + sentimento)",
            "acuracia_teste": meta["acuracia_teste_fusion"],
            "auc_teste": meta["auc_teste_fusion"],
        },
        "aviso": "Previsão de natureza acadêmica/experimental — não é recomendação de investimento.",
    }


@app.get("/")
def raiz():
    return {"api": "PETR4 — Pesquisa", "docs": "/docs",
            "endpoints": ["/api/saude", "/api/categorias", "/api/noticias", "/api/precos", "/api/estatisticas"]}
