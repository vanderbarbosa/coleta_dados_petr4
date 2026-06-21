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


@app.get("/")
def raiz():
    return {"api": "PETR4 — Pesquisa", "docs": "/docs",
            "endpoints": ["/api/saude", "/api/categorias", "/api/noticias", "/api/precos", "/api/estatisticas"]}
