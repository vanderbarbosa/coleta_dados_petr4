# -*- coding: utf-8 -*-
# ==============================================================================
#  gerar_datasets_refino.py — Datasets do REFINO pedido pela banca (jul/2026)
#  Dissertação PETR4 | Vanderlei Barbosa da Silva
#
#  Gera, SOMENTE a partir de dados reais da pesquisa (sem inventar):
#   01 · Notícias publicadas APÓS as 17h (Lead-Lag) — subconjunto do corpus.
#   02 · Dataset enriquecido: data, notícia, sentimento (FinBERT), volatilidade
#        (GARCH) do pregão e os parâmetros dos encoders usados.
#   03 · Resultados de VOLATILIDADE consolidados (Granger, quantílica, regime).
#
#  Cada arquivo é versionado (_vN) e NÃO sobrescreve os anteriores (comparação).
#  Fontes: Mestrado_PETR4/{noticias_com_sentimento.csv, base_master_petr4.csv,
#          resultados_granger/quantilica/regime, modelo_meta.json}.
# ==============================================================================
import json
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "Mestrado_PETR4"
OUT = RAIZ / "datasets_refino"
OUT.mkdir(exist_ok=True)
VER = "v1"


def versao(nome):
    """Nome versionado; se já existir, incrementa (mantém os anteriores)."""
    base, ext = nome.rsplit(".", 1)
    p = OUT / f"{base}_{VER}.{ext}"
    n = 1
    while p.exists():
        n += 1
        p = OUT / f"{base}_v{n}.{ext}"
    return p


# ── Parâmetros dos encoders (proveniência — fonte: app.py, modelo_meta.json) ──
meta = json.loads((DADOS / "modelo_meta.json").read_text(encoding="utf-8"))
PARAMS = {
    "Encoder_Sentimento": "FinBERT-PT-BR (lucas-leme/FinBERT-PT-BR); max_length=512; truncation=True; device=CPU",
    "Modelo_Risco": "GARCH(1,1) t-Student",
    "Modelo_DataFusion": "XGBoost; features=" + ", ".join(meta.get("features", [])),
    "Periodo_Treino": " a ".join(meta.get("periodo_treino", [])),
    "Periodo_Teste": " a ".join(meta.get("periodo_teste", [])),
}


def gerar_apos_17h():
    cols = ["Data_Coleta", "data_gmt", "Data", "Data_Ajustada", "categoria", "Fonte",
            "dominio", "Titulo", "Resumo", "URL", "Idioma", "conjunto",
            "Indice_Sentimento", "Label_Sentimento", "Score_Confianca"]
    df = pd.read_csv(DADOS / "noticias_com_sentimento.csv", usecols=lambda c: c in cols)
    df["dt_pub"] = pd.to_datetime(df["Data_Coleta"], errors="coerce")  # hora de Brasília
    total = len(df)
    apos = df[df["dt_pub"].dt.hour >= 17].copy()
    print(f"  Corpus total: {total:,} | após 17h: {len(apos):,} ({100*len(apos)/total:.1f}%)")

    saida = apos.rename(columns={
        "Data_Coleta": "Data_Publicacao", "Data_Ajustada": "Data_Pregao_Atribuido",
        "categoria": "Categoria", "dominio": "Portal", "Titulo": "Noticia",
        "Indice_Sentimento": "Sentimento_Indice", "Label_Sentimento": "Sentimento_Rotulo",
        "Score_Confianca": "Sentimento_Confianca",
    })[["Data_Publicacao", "data_gmt", "Data_Pregao_Atribuido", "Categoria", "Portal",
        "Fonte", "Noticia", "Resumo", "URL", "Idioma", "conjunto",
        "Sentimento_Indice", "Sentimento_Rotulo", "Sentimento_Confianca"]]
    p = versao("01_noticias_apos_17h.csv")
    saida.to_csv(p, index=False, encoding="utf-8-sig")
    print(f"  ✓ {p.name}  ({len(saida):,} linhas)")
    return saida


def gerar_enriquecido(apos):
    # Volatilidade GARCH e retorno do PRÓXIMO pregão real (merge_asof forward:
    # notícia de sexta/véspera após 17h é atribuída ao próximo dia de negociação).
    bm = pd.read_csv(DADOS / "base_master_petr4.csv",
                     usecols=["Date", "Volatilidade_GARCH", "Log_Retorno_Pct", "Alvo"])
    bm["Date"] = pd.to_datetime(bm["Date"])
    bm = bm.sort_values("Date")
    apos = apos.copy()
    apos["_dt"] = pd.to_datetime(apos["Data_Pregao_Atribuido"], errors="coerce")
    apos = apos[apos["_dt"].notna()].sort_values("_dt")
    enr = pd.merge_asof(apos, bm, left_on="_dt", right_on="Date", direction="forward")

    out = pd.DataFrame({
        "Data_Pregao": enr["Date"].dt.strftime("%Y-%m-%d"),
        "Data_Publicacao": enr["Data_Publicacao"],
        "Noticia": enr["Noticia"],
        "Categoria": enr["Categoria"],
        "Portal": enr["Portal"],
        "Sentimento_Indice": enr["Sentimento_Indice"],
        "Sentimento_Rotulo": enr["Sentimento_Rotulo"],
        "Sentimento_Confianca": enr["Sentimento_Confianca"],
        "Volatilidade_GARCH_pregao": enr["Volatilidade_GARCH"],
        "Log_Retorno_Pct_pregao": enr["Log_Retorno_Pct"],
        "Direcao_Real_pregao": enr["Alvo"].map({1: "alta", 0: "baixa"}),
    })
    for k, v in PARAMS.items():
        out[k] = v
    p = versao("02_noticias_apos17h_enriquecido.csv")
    out.to_csv(p, index=False, encoding="utf-8-sig")
    faltando = out["Volatilidade_GARCH_pregao"].isna().sum()
    print(f"  ✓ {p.name}  ({len(out):,} linhas; sem volatilidade casada: {faltando:,})")
    return out


def gerar_resultados_volatilidade():
    linhas = []
    # Granger: sentimento -> volatilidade (e -> retorno), por defasagem
    g = pd.read_csv(DADOS / "resultados_granger_petr4.csv")
    for _, r in g.iterrows():
        linhas.append(["Granger sentimento→VOLATILIDADE", f"defasagem {int(r['Defasagem_dias'])} dia(s)",
                       "p-valor", round(float(r["p_sent_para_volatilidade"]), 4),
                       "Sim" if r["p_sent_para_volatilidade"] < 0.05 else "Não",
                       "resultados_granger_petr4.csv"])
        linhas.append(["Granger sentimento→retorno (controle)", f"defasagem {int(r['Defasagem_dias'])} dia(s)",
                       "p-valor", round(float(r["p_sent_para_retorno"]), 4),
                       "Sim" if r["p_sent_para_retorno"] < 0.05 else "Não",
                       "resultados_granger_petr4.csv"])
    # Regressão quantílica: efeito do sentimento sobre o retorno por quantil (bps)
    q = pd.read_csv(DADOS / "resultados_quantilica_petr4.csv")
    for _, r in q.iterrows():
        linhas.append(["Regressão quantílica (efeito assimétrico)", f"quantil τ={r['quantil']}",
                       "coef (bps)", round(float(r["coef_bps"]), 1),
                       "Sim" if r["p_valor"] < 0.05 else "Não", "resultados_quantilica_petr4.csv"])
    # Regime de incerteza
    reg = json.loads((DADOS / "resultados_regime_incerteza_petr4.json").read_text(encoding="utf-8"))
    for nome, d in [("baixa incerteza", reg["baixa_incerteza"]), ("alta incerteza", reg["alta_incerteza"])]:
        linhas.append(["Efeito do sentimento por regime", nome, "coef (bps)", round(d["coef_sent_bps"], 1),
                       "Sim" if d["p_valor"] < 0.05 else "Não", "resultados_regime_incerteza_petr4.json"])

    df = pd.DataFrame(linhas, columns=["Analise", "Detalhe", "Estatistica", "Valor",
                                       "Significante_5pct", "Fonte"])
    p = versao("03_resultados_volatilidade.csv")
    df.to_csv(p, index=False, encoding="utf-8-sig")
    print(f"  ✓ {p.name}  ({len(df)} linhas)")
    return df


if __name__ == "__main__":
    print("== 01/02 · Notícias após 17h e dataset enriquecido ==")
    apos = gerar_apos_17h()
    gerar_enriquecido(apos)
    print("== 03 · Resultados de volatilidade ==")
    gerar_resultados_volatilidade()
    print("Concluído. Arquivos em:", OUT)
