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
#     1. BASE TRATADA (FILTRAGEM LEVE) — aplica apenas uma LIMPEZA DE QUALIDADE,
#        removendo ruído degenerado: títulos vazios, muito curtos (sem conteúdo
#        semântico útil para análise de sentimento) e marcadores de remoção
#        (ex.: "[Removed]"). NÃO aplica filtro temático — preserva a amplitude
#        das 7 categorias (incl. geopolítica e macro), pois o termo da taxonomia
#        já é o sinal de relevância usado na captura (Script 02b). Isso mantém
#        intacta a base para a ANÁLISE DE ABLAÇÃO por categoria.
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
#   • base_textual_petr4_tratada.csv       — corpus com limpeza leve + coluna 'conjunto'
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
ARQ_TRATADA  = PASTA_BASE / "base_textual_petr4_tratada.csv"
ARQ_SPLITDEF = PASTA_BASE / "definicao_split_temporal.csv"
ARQ_DOC      = Path("DOCUMENTACAO_BASES.md")   # na raiz do projeto (versionável)

# ── Filtragem LEVE (limpeza de qualidade — NÃO é filtro temático) ─────────────
# Remove apenas notícias degeneradas, preservando toda a amplitude temática
# (as 7 categorias permanecem). O termo da taxonomia já garante a relevância.
APLICAR_LIMPEZA   = True
MIN_TITULO_CHARS  = 15     # títulos mais curtos não têm conteúdo semântico útil
MARCADORES_INVALIDOS = ["[removed]", "[removida]", "(sem título)", "sem titulo"]

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
# BLOCO 3 — FILTRAGEM LEVE: LIMPEZA DE QUALIDADE (gera base derivada)
# ==============================================================================
# Remove apenas linhas degeneradas. NÃO há filtro temático — todas as 7
# categorias são preservadas (importante para a análise de ablação).

if APLICAR_LIMPEZA:
    titulo = df['titulo'].fillna('').astype(str).str.strip()
    titulo_low = titulo.str.lower()

    cond_vazio   = titulo == ''
    cond_curto   = titulo.str.len() < MIN_TITULO_CHARS
    cond_marcado = titulo_low.isin([m.lower() for m in MARCADORES_INVALIDOS])

    remover = cond_vazio | cond_curto | cond_marcado
    df_filt = df[~remover].copy()

    print(f"\n🧹 Filtragem LEVE (limpeza de qualidade) aplicada:")
    print(f"   Mantidas : {len(df_filt)} ({len(df_filt)/n_original*100:.1f}%)")
    print(f"   Removidas: {int(remover.sum())} ({remover.mean()*100:.1f}%)")
    print(f"      • título vazio        : {int(cond_vazio.sum())}")
    print(f"      • título < {MIN_TITULO_CHARS} chars   : {int((cond_curto & ~cond_vazio).sum())}")
    print(f"      • marcador inválido   : {int(cond_marcado.sum())}")
else:
    df_filt = df.copy()
    print("\n🧹 Limpeza DESATIVADA — base tratada = base original.")


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
print("\n📊 Distribuição do split (base tratada):")
for nome in ['treino', 'validacao', 'teste']:
    n = int(dist.get(nome, 0))
    print(f"   {nome:10s}: {n:6d} ({n/len(df_filt)*100:4.1f}%)")

# Tabela ano × conjunto (confirma que todos os anos estão nos 3 conjuntos)
tab_ano = pd.crosstab(df_filt['ano'], df_filt['conjunto'])
tab_ano = tab_ano.reindex(columns=['treino', 'validacao', 'teste'], fill_value=0)
print("\n📊 Notícias por ano × conjunto:")
print(tab_ano.to_string())

# Salva a base tratada (com a coluna 'conjunto')
colunas_saida = [c for c in df_filt.columns if c not in ('ano', 'data')]
df_filt[colunas_saida].to_csv(ARQ_TRATADA, index=False, encoding='utf-8')
print(f"\n💾 Base tratada salva: {ARQ_TRATADA}")

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

## 2. Base TRATADA (derivada — filtragem LEVE)

- **Arquivo:** `Mestrado_PETR4/base_textual_petr4_tratada.csv`
- **Filtragem leve (limpeza de qualidade):** remove apenas notícias degeneradas —
  título vazio, com menos de {MIN_TITULO_CHARS} caracteres, ou marcadores de remoção.
  **Não** há filtro temático: todas as 7 categorias são preservadas.
- **Total após limpeza:** {len(df_filt)} ({len(df_filt)/n_original*100:.1f}% da base original)
- **Coluna adicional:** `conjunto` (treino / validacao / teste).

### Notícias por categoria (original → tratada)
| Categoria | Original | Tratada |
|-----------|----------|---------|
{linhas_cat}

> ✅ A filtragem leve preserva a amplitude temática (incl. geopolítica e macro),
> mantendo a base adequada para a análise de ablação por categoria. O sinal de
> relevância vem do termo da taxonomia usado na captura (Script 02b).

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
