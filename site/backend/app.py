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

_modelo_cache = {}

# Categorias de OFERTA (choques que tendem a mover o preço do petróleo).
_CATS_OFERTA = {"CAT2_Mercado_Petroleo", "CAT3_Geopolitica",
                "CAT4_Infraestrutura", "CAT5_Sancoes_Navegacao"}


def _detectar_categoria(texto_low: str):
    """Detecta a categoria temática pela taxonomia completa (152 termos).
    Retorna (categoria_id, rotulo, qtd_termos_casados) ou (None, None, 0)."""
    melhor, melhor_qtd = None, 0
    try:
        for cat, termos in tx.TERMOS_POR_CATEGORIA.items():
            qtd = sum(1 for t in termos if t.lower() in texto_low)
            if qtd > melhor_qtd:
                melhor, melhor_qtd = cat, qtd
    except Exception:
        pass
    if melhor is None:
        return None, None, 0
    return melhor, ROTULOS.get(melhor, melhor), melhor_qtd


def _leitura_setorial(cat, polaridade):
    """Interpretação econômica QUALITATIVA por categoria, fundamentada na
    literatura (Kilian, 2009; Hamilton, 1983). Distingue o efeito sobre o
    MERCADO do efeito sobre a PETR4 (produtora de petróleo) — exatamente a
    distinção apontada pela banca."""
    if cat == "CAT1_Empresa":
        if polaridade > 0:
            return "alta", "Notícia corporativa de tom positivo tende a favorecer a PETR4."
        if polaridade < 0:
            return "baixa", "Notícia corporativa de tom negativo tende a pressionar a PETR4."
        return "neutra", "Notícia corporativa de tom neutro, sem direção clara."
    if cat in _CATS_OFERTA:
        if polaridade < 0:
            return "alta", ("Choque de OFERTA com teor de disrupção (conflito, bloqueio, sanção, "
                            "interrupção) tende a ELEVAR o preço do petróleo; como a Petrobras é "
                            "produtora da commodity, o efeito sobre a PETR4 costuma ser FAVORÁVEL — "
                            "ainda que o tom da notícia seja negativo para o mercado em geral "
                            "(Kilian, 2009; Hamilton, 1983).")
        if polaridade > 0:
            return "baixa", ("Distensão ou aumento de oferta tende a REDUZIR o preço do petróleo, "
                             "o que costuma ser DESFAVORÁVEL para a Petrobras.")
        return "neutra", "Evento de oferta de tom neutro, sem direção clara."
    if cat == "CAT6_Governanca":
        if polaridade < 0:
            return "baixa", "Risco de governança/intervenção estatal tende a pressionar a PETR4."
        if polaridade > 0:
            return "alta", "Sinal de governança favorável tende a beneficiar a PETR4."
        return "neutra", "Notícia de governança de tom neutro."
    # CAT7 — Macro/Energia: efeito ambíguo
    return "contextual", ("Fator macroeconômico (câmbio, juros, demanda, transição energética) de "
                          "efeito ambíguo, dependente do contexto.")


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

    # 2) Relevância + categoria (taxonomia COMPLETA — 152 termos)
    alvo = texto.lower()
    cat_id, cat_rotulo, qtd_termos = _detectar_categoria(alvo)
    relevante = cat_id is not None
    nivel_relevancia = ("alta" if qtd_termos >= 2 else "media") if relevante else "baixa"

    # 3) Leitura ESTATÍSTICA: direção do próximo pregão (XGBoost Data Fusion)
    import numpy as np
    X = np.array([[meta["retorno_recente"], meta["volatilidade_recente"], indice]])
    prob_alta = float(modelo.predict_proba(X)[0, 1])
    if prob_alta >= 0.55:
        dir_modelo = "alta"
    elif prob_alta <= 0.45:
        dir_modelo = "baixa"
    else:
        dir_modelo = "indefinida"

    # 4) Leitura ECONÔMICA SETORIAL (qualitativa, fundamentada na literatura)
    if relevante:
        dir_setorial, just_setorial = _leitura_setorial(cat_id, polaridade)
    else:
        dir_setorial, just_setorial = "sem_influencia", \
            "A notícia não casa com nenhum termo da taxonomia (Petrobras, mercado de petróleo, " \
            "geopolítica, infraestrutura, sanções, governança ou macroeconomia)."

    # 5) Veredito-síntese: prioriza a leitura econômica quando relevante (mais
    #    interpretável); o número estatístico do modelo é exibido em paralelo.
    if not relevante:
        direcao, explica = "sem_influencia", "Notícia sem relevância aparente para a PETR4."
    elif dir_setorial in ("alta", "baixa"):
        seta = "ALTA" if dir_setorial == "alta" else "BAIXA"
        direcao, explica = dir_setorial, f"Tendência de {seta}. {just_setorial}"
    else:
        direcao, explica = "indefinida", just_setorial

    return {
        "sentimento": {"rotulo": rotulo_sent, "indice": round(indice, 4),
                       "confianca": round(float(r["score"]), 4)},
        "relevante": relevante,
        "nivel_relevancia": nivel_relevancia,
        "categoria": {"id": cat_id, "rotulo": cat_rotulo, "termos_casados": qtd_termos},
        "direcao": direcao,
        "explicacao": explica,
        "leitura_setorial": {"direcao": dir_setorial, "justificativa": just_setorial},
        "leitura_modelo": {
            "direcao": dir_modelo, "prob_alta": round(prob_alta, 4),
            "nota": "Modelo estatístico baseado em sentimento agregado; sua acurácia (~53%) e o uso "
                    "de polaridade genérica limitam a captura da distinção mercado × ativo.",
        },
        "contexto": {
            "data_referencia": meta["data_referencia"],
            "retorno_recente_pct": round(meta["retorno_recente"], 3),
            "volatilidade_recente": round(meta["volatilidade_recente"], 3),
            "modelo": "XGBoost Data Fusion (preços + GARCH + sentimento)",
            "acuracia_teste": meta["acuracia_teste_fusion"],
            "auc_teste": meta["auc_teste_fusion"],
        },
        "aviso": "Análise acadêmica/experimental — não é recomendação de investimento.",
    }


@app.get("/")
def raiz():
    return {"api": "PETR4 — Pesquisa", "docs": "/docs",
            "endpoints": ["/api/saude", "/api/categorias", "/api/noticias", "/api/precos", "/api/estatisticas"]}
