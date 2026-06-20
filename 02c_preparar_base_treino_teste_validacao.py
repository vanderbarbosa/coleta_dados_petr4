# -*- coding: utf-8 -*-
# ==============================================================================
#
#   DISSERTAÇÃO : O Impacto do Sentimento de Notícias Financeiras na Previsão
#                 de Direção e Volatilidade do Ativo PETR4
#   Autor       : Vanderlei Barbosa da Silva
#   Orientador  : Prof. Dr. Julio Cesar Nievola — PUCPR
#   Script      : 02c — Preparação da Base: Filtragem + Split Treino/Validação/Teste
#   Versão      : 1.0
#
# ==============================================================================
#
#   O QUE ESTE SCRIPT FAZ
#   ──────────────────────
#   A coleta (Script 02b) gera a BASE ORIGINAL com 205.716 notícias. Este script
#   NÃO a modifica — apenas a LÊ e gera bases DERIVADAS para a modelagem:
#
#     1. BASE FILTRADA — aplica um filtro de relevância (notícias cujo título ou
#        resumo mencionam Petrobras/PETR4/petróleo/Brent/OPEP etc.). Reduz ruído
#        de termos exógenos amplos, focando o corpus no ativo.
#
#     2. SPLIT TEMPORAL Treino/Validação/Teste — separa os dados em três conjuntos
#        na proporção 60/15/25, ESTRATIFICADO POR ANO: dentro de cada ano, os
#        primeiros 60% dos dias (cronologicamente) vão para TREINO, os 15%
#        seguintes para VALIDAÇÃO e os 25% finais (mais recentes) para TESTE.
#        Isso garante que TODOS os anos estejam representados nos três conjuntos
#        (o modelo vê todos os regimes de mercado) SEM embaralhar o tempo dentro
#        do ano (evita data leakage / lookahead) e SEM partir um dia entre
#        conjuntos (um dia inteiro pertence sempre a um único conjunto).
#
#   POR QUE MANTER A BASE ORIGINAL INTACTA
#   ───────────────────────────────────────
#   A coleta levou horas e não deve ser repetida. A base bruta é o registro
#   primário auditável (apresentável na defesa). Todas as transformações são
#   feitas em CÓPIAS derivadas — a rastreabilidade fica preservada.
#
#   ARQUIVOS GERADOS (todos derivados; a base original permanece intacta)
#   ─────────────────────────────────────────────────────────────────────
#   • base_textual_petr4_filtrada.csv      — corpus filtrado + coluna 'conjunto'
#   • definicao_split_temporal.csv         — mapa Data → conjunto (para o Script 04)
#   • DOCUMENTACAO_BASES.md                — relatório completo das bases e do split
#
# ==============================================================================

import pandas as pd
from pathlib import Path

# ==============================================================================
# BLOCO 1 — CONFIGURAÇÕES
# ==============================================================================

_NO_COLAB  = Path("/content/drive/MyDrive").exists()
PASTA_BASE = Path("/content/drive/MyDrive/Mestrado_PETR4") if _NO_COLAB \
             else Path("./Mestrado_PETR4")

ARQ_ORIGINAL = PASTA_BASE / "base_textual_petr4_wordpress_2018_2025.csv"   # INTACTA
ARQ_FILTRADA = PASTA_BASE / "base_textual_petr4_filtrada.csv"
ARQ_SPLITDEF = PASTA_BASE / "definicao_split_temporal.csv"
ARQ_DOC      = Path("DOCUMENTACAO_BASES.md")   # na raiz do projeto (versionável)

# ── Filtro de relevância ──────────────────────────────────────────────────────
# Mantém a notícia se o TÍTULO ou o RESUMO contiver algum destes termos.
APLICAR_FILTRO = True
TERMOS_RELEVANCIA = [
    "petrobras", "petr4", "petr3", "petroleira", "petróleo", "petroleo",
    "brent", "wti", "opep", "barril", "combustível", "combustivel",
    "gasolina", "diesel", "refinaria", "pré-sal", "pre-sal",
]

# ── Proporções do split (cronológico, estratificado por ano) ──────────────────
# Mapeamento: dentro de cada ano, em ordem de data —
#   primeiros PROP_TREINO   → treino
#   seguintes PROP_VALIDACAO → validação
#   últimos   PROP_TESTE     → teste (parte mais recente do ano)
# Se o Prof. Emerson quiser teste=15% e validação=25%, basta trocar os dois valores.
PROP_TREINO    = 0.60
PROP_VALIDACAO = 0.15
PROP_TESTE     = 0.25   # = 1 - TREINO - VALIDACAO


# ==============================================================================
# BLOCO 2 — LEITURA DA BASE ORIGINAL (somente leitura — nunca modificada)
# ==============================================================================

print("📖 Lendo a base ORIGINAL (intacta):", ARQ_ORIGINAL)
df = pd.read_csv(ARQ_ORIGINAL)
df['data_publicacao'] = pd.to_datetime(df['data_publicacao'], errors='coerce')
df = df[df['data_publicacao'].notna()].copy()
n_original = len(df)
df['ano'] = df['data_publicacao'].dt.year
df['data'] = df['data_publicacao'].dt.date
print(f"   Base original: {n_original} notícias | {df['ano'].min()}–{df['ano'].max()}")


# ==============================================================================
# BLOCO 3 — FILTRAGEM DE RELEVÂNCIA (gera base derivada)
# ==============================================================================

if APLICAR_FILTRO:
    alvo = (df['titulo'].fillna('') + ' ' + df['resumo'].fillna('')).str.lower()
    mask = alvo.apply(lambda t: any(termo in t for termo in TERMOS_RELEVANCIA))
    df_filt = df[mask].copy()
    print(f"\n🔎 Filtro de relevância aplicado:")
    print(f"   Mantidas : {len(df_filt)} ({len(df_filt)/n_original*100:.1f}%)")
    print(f"   Removidas: {n_original-len(df_filt)} ({(n_original-len(df_filt))/n_original*100:.1f}%)")
else:
    df_filt = df.copy()
    print("\n🔎 Filtro DESATIVADO — base filtrada = base original.")


# ==============================================================================
# BLOCO 4 — SPLIT TEMPORAL 60/15/25 ESTRATIFICADO POR ANO (por dias inteiros)
# ==============================================================================
# Dentro de cada ano, ordenamos os DIAS cronologicamente e atribuímos cada dia
# (inteiro) a um conjunto conforme a fração ACUMULADA de notícias do ano:
#   fração acumulada ≤ 0.60          → treino
#   fração acumulada ≤ 0.75          → validação
#   caso contrário                   → teste
# Assim a proporção por linhas fica próxima de 60/15/25 SEM partir nenhum dia.

print("\n📅 Construindo o split temporal (60/15/25, estratificado por ano)...")

CORTE_TREINO = PROP_TREINO                  # 0.60
CORTE_VALID  = PROP_TREINO + PROP_VALIDACAO  # 0.75

def classificar_ano(grupo: pd.DataFrame) -> pd.Series:
    """Atribui 'conjunto' a cada linha de um ano, por dias inteiros e cronológico."""
    # Contagem de notícias por dia, em ordem de data
    contagem_dia = grupo.groupby('data').size().sort_index()
    total_ano = contagem_dia.sum()
    frac_acum = contagem_dia.cumsum() / total_ano

    # Mapa dia → conjunto
    dia_conjunto = {}
    for dia, f in frac_acum.items():
        if f <= CORTE_TREINO:
            dia_conjunto[dia] = 'treino'
        elif f <= CORTE_VALID:
            dia_conjunto[dia] = 'validacao'
        else:
            dia_conjunto[dia] = 'teste'
    return grupo['data'].map(dia_conjunto)

df_filt['conjunto'] = (
    df_filt.groupby('ano', group_keys=False).apply(classificar_ano)
)

# Garante que não sobrou nenhum dia sem classificação
df_filt['conjunto'] = df_filt['conjunto'].fillna('treino')


# ==============================================================================
# BLOCO 5 — ESTATÍSTICAS E SALVAMENTO
# ==============================================================================

# Distribuição global do split
dist = df_filt['conjunto'].value_counts()
print("\n📊 Distribuição do split (base filtrada):")
for nome in ['treino', 'validacao', 'teste']:
    n = int(dist.get(nome, 0))
    print(f"   {nome:10s}: {n:6d} ({n/len(df_filt)*100:4.1f}%)")

# Tabela ano × conjunto (confirma que todos os anos estão nos 3 conjuntos)
tab_ano = pd.crosstab(df_filt['ano'], df_filt['conjunto'])
tab_ano = tab_ano.reindex(columns=['treino', 'validacao', 'teste'], fill_value=0)
print("\n📊 Notícias por ano × conjunto:")
print(tab_ano.to_string())

# Salva a base filtrada (com a coluna 'conjunto')
colunas_saida = [c for c in df_filt.columns if c not in ('ano', 'data')]
df_filt[colunas_saida].to_csv(ARQ_FILTRADA, index=False, encoding='utf-8')
print(f"\n💾 Base filtrada salva: {ARQ_FILTRADA}")

# Salva o mapa Data → conjunto (para o Script 04 aplicar aos dias de pregão)
mapa = (df_filt[['data', 'conjunto']]
        .drop_duplicates('data')
        .sort_values('data')
        .rename(columns={'data': 'Data'}))
mapa.to_csv(ARQ_SPLITDEF, index=False, encoding='utf-8')
print(f"💾 Definição do split salva: {ARQ_SPLITDEF} ({len(mapa)} dias)")


# ==============================================================================
# BLOCO 6 — GERAÇÃO DA DOCUMENTAÇÃO (números reais — reprodutível)
# ==============================================================================

dist_cat_orig = df['categoria'].value_counts()
dist_cat_filt = df_filt['categoria'].value_counts()
dist_ano_orig = df['ano'].value_counts().sort_index()
hora = df['data_publicacao'].dt.hour
lead_lag = (hora >= 17).mean() * 100

linhas_cat = "\n".join(
    f"| {c} | {int(dist_cat_orig.get(c,0))} | {int(dist_cat_filt.get(c,0))} |"
    for c in dist_cat_orig.index
)
linhas_ano = "\n".join(
    f"| {ano} | {int(dist_ano_orig[ano])} | "
    f"{int(tab_ano.loc[ano,'treino']) if ano in tab_ano.index else 0} | "
    f"{int(tab_ano.loc[ano,'validacao']) if ano in tab_ano.index else 0} | "
    f"{int(tab_ano.loc[ano,'teste']) if ano in tab_ano.index else 0} |"
    for ano in dist_ano_orig.index
)

doc = f"""# Documentação das Bases de Dados — Corpus PETR4

*Gerado automaticamente pelo `02c_preparar_base_treino_teste_validacao.py`.*

## 1. Base ORIGINAL (intacta)

- **Arquivo:** `Mestrado_PETR4/base_textual_petr4_wordpress_2018_2025.csv`
- **Total de notícias:** {n_original}
- **Período:** {df['ano'].min()}–{df['ano'].max()}
- **Timestamp:** 100% das notícias têm hora exata de publicação (horário de Brasília).
- **Lead-Lag:** {lead_lag:.1f}% das notícias foram publicadas após o fechamento da B3 (≥17h) e são realocadas ao pregão seguinte.
- **Coleta:** Script 02b (WordPress REST API) de 5 portais (InfoMoney, Exame, Money Times, Petronotícias, Poder360), taxonomia de 7 categorias.
- **Status:** NUNCA é modificada. Todas as bases abaixo são derivadas dela.

### Distribuição por ano (base original)
| Ano | Notícias |
|-----|----------|
""" + "\n".join(f"| {ano} | {int(dist_ano_orig[ano])} |" for ano in dist_ano_orig.index) + f"""

## 2. Base FILTRADA (derivada)

- **Arquivo:** `Mestrado_PETR4/base_textual_petr4_filtrada.csv`
- **Filtro:** mantém notícias cujo título ou resumo contém termos de relevância
  ({', '.join(TERMOS_RELEVANCIA[:8])}…).
- **Total após filtro:** {len(df_filt)} ({len(df_filt)/n_original*100:.1f}% da base original)
- **Coluna adicional:** `conjunto` (treino / validacao / teste).

### Impacto do filtro por categoria (original → filtrada)
| Categoria | Original | Filtrada |
|-----------|----------|----------|
{linhas_cat}

> ⚠️ O filtro reduz fortemente as categorias exógenas (geopolítica, macro), pois
> essas notícias raramente citam "petróleo/Petrobras" no título. Para a análise
> de ablação por categoria, considere usar também a base original (não filtrada).

## 3. Split Temporal Treino / Validação / Teste

- **Proporção:** {PROP_TREINO*100:.0f}% treino / {PROP_VALIDACAO*100:.0f}% validação / {PROP_TESTE*100:.0f}% teste.
- **Estratégia:** estratificado por ano e cronológico dentro do ano. Em cada ano,
  os primeiros {PROP_TREINO*100:.0f}% dos dias vão para treino, os {PROP_VALIDACAO*100:.0f}% seguintes para validação
  e os {PROP_TESTE*100:.0f}% finais (mais recentes) para teste. Um dia inteiro nunca é dividido
  entre conjuntos — garante ausência de *data leakage* e representação de todos
  os anos (regimes de mercado) nos três conjuntos.
- **Mapa de datas:** `Mestrado_PETR4/definicao_split_temporal.csv` (Data → conjunto),
  aplicável aos dias de pregão no Script 04 para manter consistência.

### Distribuição global
| Conjunto | Notícias | % |
|----------|----------|---|
| treino | {int(dist.get('treino',0))} | {dist.get('treino',0)/len(df_filt)*100:.1f}% |
| validacao | {int(dist.get('validacao',0))} | {dist.get('validacao',0)/len(df_filt)*100:.1f}% |
| teste | {int(dist.get('teste',0))} | {dist.get('teste',0)/len(df_filt)*100:.1f}% |

### Notícias por ano × conjunto (confirma todos os anos nos 3 conjuntos)
| Ano | Treino | Validação | Teste |
|-----|--------|-----------|-------|
{linhas_ano}
"""

ARQ_DOC.write_text(doc, encoding='utf-8')
print(f"📄 Documentação gerada: {ARQ_DOC.resolve()}")
print("\n✅ Preparação concluída. Base original preservada intacta.")
