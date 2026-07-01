# -*- coding: utf-8 -*-
# ==============================================================================
#   exportar_estatico.py — Gera um SNAPSHOT ESTÁTICO (JSON) dos dados da pesquisa
#   Dissertação PETR4 | Vanderlei Barbosa da Silva
#
#   O site é hospedado no GitHub Pages (conteúdo estático). Como o backend
#   FastAPI não roda no Pages, este script pré-exporta os mesmos dados que a API
#   serviria, em arquivos JSON dentro de `site/frontend/public/dados/`. O
#   frontend consome esses arquivos quando não há backend ao vivo configurado.
#
#   Reexecute sempre que os dados da pesquisa mudarem:
#       python site/exportar_estatico.py
# ==============================================================================

import json
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]        # coleta_dados_petr4/
DADOS = RAIZ / "Mestrado_PETR4"
SAIDA = RAIZ / "site" / "frontend" / "public" / "dados"
SAIDA.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(RAIZ / "src" / "comum"))
try:
    import taxonomia as tx
    ROTULOS = tx.ROTULOS_CATEGORIA
except Exception:
    ROTULOS = {}

# Notícias exportadas (amostra) — mantém o JSON leve para o Pages, cobrindo
# todo o período (amostragem aleatória estratificada implícita pelo sample).
MAX_NOTICIAS = 5000


def _grava(nome, obj):
    caminho = SAIDA / nome
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    kb = caminho.stat().st_size / 1024
    print(f"  ✓ {nome:<32} {kb:8.1f} KB")


def carregar_noticias():
    cols = ["data_publicacao", "categoria", "fonte_coleta", "termo_busca",
            "titulo", "resumo", "url", "dominio", "conjunto"]
    df = pd.read_csv(DADOS / "base_textual_petr4_tratada.csv",
                     usecols=lambda c: c in cols)
    df["dt"] = pd.to_datetime(df["data_publicacao"], errors="coerce")
    return df[df["dt"].notna()].copy()


def carregar_precos():
    df = pd.read_csv(DADOS / "base_financeira_petr4.csv", parse_dates=["Date"])
    return df[df["Date"].notna()].copy()


def item_noticia(r):
    return {
        "data": str(r["data_publicacao"]),
        "categoria": r["categoria"],
        "rotulo_categoria": ROTULOS.get(r["categoria"], r["categoria"]),
        "titulo": r["titulo"],
        "resumo": r.get("resumo", "") if not pd.isna(r.get("resumo", "")) else "",
        "fonte": r.get("dominio", "") if not pd.isna(r.get("dominio", "")) else "",
        "url": r.get("url", "") if not pd.isna(r.get("url", "")) else "",
        "conjunto": r.get("conjunto", "") if not pd.isna(r.get("conjunto", "")) else "",
    }


def main():
    print(f"Exportando snapshot estático → {SAIDA}")
    n = carregar_noticias()
    p = carregar_precos().sort_values("Date").reset_index(drop=True)

    # ── categorias.json ───────────────────────────────────────────────────────
    vc = n["categoria"].value_counts()
    categorias = [{"id": c, "rotulo": ROTULOS.get(c, c), "total": int(q)}
                  for c, q in vc.items()]
    _grava("categorias.json", categorias)

    # ── estatisticas.json ─────────────────────────────────────────────────────
    por_ano = n["dt"].dt.year.value_counts().sort_index()
    por_portal = n["dominio"].value_counts()
    lead_lag = float((n["dt"].dt.hour >= 17).mean() * 100)
    _grava("estatisticas.json", {
        "noticias_total": int(len(n)),
        "pregoes_total": int(len(p)),
        "periodo_noticias": [str(n["dt"].min().date()), str(n["dt"].max().date())],
        "periodo_precos": [str(p["Date"].min().date()), str(p["Date"].max().date())],
        "lead_lag_pct": round(lead_lag, 1),
        "por_ano": {str(k): int(v) for k, v in por_ano.items()},
        "por_categoria": categorias,
        "por_portal": {str(k): int(v) for k, v in por_portal.items()},
    })

    # ── precos.json (série completa) ──────────────────────────────────────────
    precos = [{
        "data": d.strftime("%Y-%m-%d"),
        "abertura": round(float(o), 2), "fechamento": round(float(c), 2),
        "maxima": round(float(h), 2), "minima": round(float(l), 2),
        "volume": int(v), "log_retorno": round(float(lr), 4),
    } for d, o, c, h, l, v, lr in zip(
        p["Date"], p["Open"], p["Close"], p["High"], p["Low"],
        p["Volume"], p["Log_Retorno"])]
    _grava("precos.json", precos)

    # ── noticias.json (amostra, cobrindo todo o período) ──────────────────────
    amostra = n.sample(min(MAX_NOTICIAS, len(n)), random_state=42) if len(n) > MAX_NOTICIAS else n
    amostra = amostra.sort_values("dt", ascending=False)
    itens = [item_noticia(r) for _, r in amostra.iterrows()]
    _grava("noticias.json", {"total_corpus": int(len(n)), "amostra": len(itens), "itens": itens})

    # ── eventos.json + demonstracao/<id>.json ─────────────────────────────────
    EVENTOS = [
        {"id": "ceo2021", "data": "2021-02-22", "titulo": "Troca do comando da Petrobras (fev/2021)",
         "contexto": "O anúncio da substituição do presidente da Petrobras pelo governo provocou forte queda da ação."},
        {"id": "covid2020", "data": "2020-03-18", "titulo": "COVID-19 e guerra de preços do petróleo (mar/2020)",
         "contexto": "A pandemia somada ao colapso do preço do petróleo levou a PETR4 a mínimas históricas."},
        {"id": "ceo2022", "data": "2022-06-20", "titulo": "Demissão do CEO e pressão do governo (jun/2022)",
         "contexto": "Troca de comando em meio ao conflito sobre a política de preços de combustíveis."},
        {"id": "ucrania2022", "data": "2022-02-24", "titulo": "Rússia invade a Ucrânia (fev/2022)",
         "contexto": "O conflito elevou o preço do petróleo no mundo, com efeito sobre as produtoras."},
    ]
    _grava("eventos.json", EVENTOS)

    try:
        ism_df = pd.read_csv(DADOS / "indice_sentimento_petr4.csv", parse_dates=["Data"])
        ISM = {d.date(): float(v) for d, v in
               zip(ism_df["Data"], ism_df["Indice_Sentimento_Transformer"])}
    except Exception:
        ISM = {}

    # Arquivos de demonstração nomeados pela DATA do evento (o frontend consulta
    # `demonstracao/<AAAA-MM-DD>.json`, espelhando o parâmetro `data` da API).
    for ev in EVENTOS:
        _grava(f"demonstracao/{ev['data']}.json", demonstracao(p, n, ISM, ev, janela=18))

    # ── resultados.json ───────────────────────────────────────────────────────
    out = {"modelos": [], "ablacao": [], "meta": None}
    try:
        out["modelos"] = pd.read_csv(DADOS / "resultados_modelos_petr4.csv").to_dict(orient="records")
    except Exception:
        pass
    try:
        out["ablacao"] = pd.read_csv(DADOS / "resultados_ablacao_categorias_petr4.csv").to_dict(orient="records")
    except Exception:
        pass
    try:
        with open(DADOS / "modelo_meta.json", encoding="utf-8") as f:
            out["meta"] = json.load(f)
    except Exception:
        pass
    _grava("resultados.json", out)

    print("Concluído.")


def demonstracao(p, n, ISM, ev, janela=18):
    d0 = pd.to_datetime(ev["data"])
    pos = int(p["Date"].searchsorted(d0))
    pos = min(max(pos, 0), len(p) - 1)
    ini, fim = max(0, pos - janela), min(len(p), pos + janela + 1)
    jan = p.iloc[ini:fim]
    data_evento = p.iloc[pos]["Date"]
    preco_evento = float(p.iloc[pos]["Close"])

    def varN(k):
        j = pos + k
        if 0 <= j < len(p):
            return round((float(p.iloc[j]["Close"]) / preco_evento - 1) * 100, 2)
        return None

    var_dia = None
    if pos - 1 >= 0:
        var_dia = round((preco_evento / float(p.iloc[pos - 1]["Close"]) - 1) * 100, 2)

    serie = [{"data": dt.strftime("%Y-%m-%d"), "fechamento": round(float(c), 2),
              "evento": dt.date() == data_evento.date()}
             for dt, c in zip(jan["Date"], jan["Close"])]

    dia = n[n["dt"].dt.date == data_evento.date()]
    if len(dia) < 3:
        dia = n[(n["dt"].dt.date >= (data_evento - pd.Timedelta(days=1)).date()) &
                (n["dt"].dt.date <= data_evento.date())]
    noticias = [{"titulo": r["titulo"], "categoria": ROTULOS.get(r["categoria"], r["categoria"]),
                 "fonte": r.get("dominio", "") if not pd.isna(r.get("dominio", "")) else ""}
                for _, r in dia.head(6).iterrows()]

    ism = ISM.get(data_evento.date())
    return {
        "data_evento": data_evento.strftime("%Y-%m-%d"),
        "preco_evento": round(preco_evento, 2),
        "serie": serie,
        "variacoes": {"dia": var_dia, "d1": varN(1), "d5": varN(5), "d10": varN(10)},
        "ism_dia": round(ism, 3) if ism is not None else None,
        "noticias": noticias,
    }


if __name__ == "__main__":
    main()
