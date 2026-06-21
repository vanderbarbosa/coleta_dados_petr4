# -*- coding: utf-8 -*-
# ==============================================================================
#
#   DISSERTAÇÃO: O Impacto do Sentimento de Notícias Financeiras na Previsão
#                de Direção e Volatilidade do Ativo PETR4
#   Autor      : Vanderlei Barbosa da Silva
#   Orientador : Prof. Dr. Julio Cesar Nievola — PUCPR
#   Script     : 04 — Modelagem Preditiva: GARCH + SVM + XGBoost
#
# ==============================================================================
#
#   O QUE ESTE SCRIPT FAZ
#   ─────────────────────
#   Este é o script central da dissertação. Ele:
#
#   1. Carrega os dados financeiros (Script 01) e o ISM (Script 03)
#   2. Executa os testes estatísticos de pré-requisito (Jarque-Bera, ADF, ARCH-LM)
#   3. Modela a volatilidade histórica com GARCH(1,1) (Seção 3.3)
#   4. Funde as variáveis em uma Matriz de Atributos (Data Fusion — Seção 3.4)
#   5. Treina SVM e XGBoost com split treino/validação/teste (60/15/25, Seção 3.5):
#      treino ajusta os modelos, validação seleciona hiperparâmetros, teste é
#      avaliado uma única vez (out-of-sample, sem data leakage)
#   6. Gera a Tabela 4.3 da dissertação: comparativo com e sem sentimento
#   7. Salva todos os resultados para inclusão no documento
#
#   ESTRUTURA DE MODELOS AVALIADOS
#   ──────────────────────────────
#   Modelo 1 — SVM   | Apenas preços históricos (baseline)
#   Modelo 2 — XGBoost | Apenas preços históricos (baseline)
#   Modelo 3 — SVM   | Data Fusion (preços + GARCH + Sentimento)
#   Modelo 4 — XGBoost | Data Fusion (preços + GARCH + Sentimento)
#
#   VARIÁVEL-ALVO
#   ─────────────
#   Alvo = 1 se o Log-Retorno do dia t+1 for positivo (Alta)
#   Alvo = 0 se o Log-Retorno do dia t+1 for negativo ou zero (Baixa)
#
#   ARQUIVOS GERADOS
#   ────────────────
#   • resultados_modelos_petr4.csv  →  Tabela de acurácia de todos os modelos
#   • grafico_volatilidade_garch.png  →  Figura 4.2 da dissertação
#   • grafico_dispersao_sentimento_volatilidade.png  →  Figura 4.4
#   • relatorio_testes_estatisticos.txt  →  Testes Jarque-Bera, ADF, ARCH-LM
#
# ==============================================================================


# ==============================================================================
# BLOCO 1 — DEPENDÊNCIAS
# ==============================================================================
# Execução LOCAL. Instale uma vez:  pip install -r requirements.txt
#   (arch, xgboost, scikit-learn, pandas, numpy, matplotlib, scipy, statsmodels)

print("✅ Bibliotecas verificadas.")


# ==============================================================================
# BLOCO 2 — IMPORTAÇÕES
# ==============================================================================

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")   # backend não interativo: evita travar em plt.show() (execução local/background)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings('ignore')

# Econometria
from arch import arch_model
from scipy import stats
from statsmodels.stats.diagnostic import het_arch
from statsmodels.tsa.stattools import adfuller

# Machine Learning
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from xgboost import XGBClassifier

# Configuração visual dos gráficos
plt.rcParams['figure.figsize']  = (14, 6)
plt.rcParams['font.size']       = 12
plt.rcParams['axes.titlesize']  = 14
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.spines.top']    = False
plt.rcParams['axes.spines.right']  = False

print("✅ Ferramentas importadas.")


# ==============================================================================
# BLOCO 3 — PASTA DE DADOS (LOCAL)
# ==============================================================================
# Este script vive em src/modelagem/, então a raiz do projeto está 2 níveis acima.

try:
    _RAIZ = Path(__file__).resolve().parents[2]
except NameError:
    _RAIZ = Path.cwd()
caminho_base = str(_RAIZ / "Mestrado_PETR4") + os.sep
os.makedirs(caminho_base, exist_ok=True)

print(f"✅ Drive conectado.")


# ==============================================================================
# BLOCO 4 — CARREGAMENTO DOS DADOS
# ==============================================================================

print("\n📂 Carregando bases de dados...")

# --- Base Financeira (Script 01) ---
caminho_financeiro = caminho_base + "base_financeira_petr4.csv"
try:
    df_financeiro = pd.read_csv(caminho_financeiro, index_col='Date', parse_dates=True)
    df_financeiro.index = pd.to_datetime(df_financeiro.index).tz_localize(None)
    print(f"   ✅ Base financeira: {len(df_financeiro)} pregões")
except FileNotFoundError:
    print(f"   ❌ Não encontrado: {caminho_financeiro}")
    print("      Execute o Script 01 primeiro.")
    raise

# --- Índice de Sentimento (Script 03) ---
caminho_ism = caminho_base + "indice_sentimento_petr4.csv"
try:
    df_ism = pd.read_csv(caminho_ism, parse_dates=['Data'])
    df_ism['Data'] = pd.to_datetime(df_ism['Data'])
    df_ism.set_index('Data', inplace=True)
    print(f"   ✅ Índice de Sentimento: {len(df_ism)} dias")
except FileNotFoundError:
    print(f"   ❌ Não encontrado: {caminho_ism}")
    print("      Execute o Script 03 primeiro.")
    raise

# --- ISM por categoria (Script 03 — OPCIONAL, habilita a análise de ablação) ---
# Se o corpus foi coletado com a taxonomia (Script 02b), o Script 03 gera um
# ISM separado por categoria. Quando presente, o Bloco 21 executa a ablação.
caminho_ism_cat = caminho_base + "indice_sentimento_categorias_petr4.csv"
try:
    df_ism_cat = pd.read_csv(caminho_ism_cat, parse_dates=['Data'])
    df_ism_cat['Data'] = pd.to_datetime(df_ism_cat['Data'])
    df_ism_cat.set_index('Data', inplace=True)
    COLUNAS_CATEGORIA = [c for c in df_ism_cat.columns if c.startswith('ISM_')]
    print(f"   ✅ ISM por categoria: {len(df_ism_cat)} dias, {len(COLUNAS_CATEGORIA)} categorias")
except FileNotFoundError:
    df_ism_cat = None
    COLUNAS_CATEGORIA = []
    print(f"   ℹ️  ISM por categoria não encontrado — análise de ablação será pulada.")
    print(f"      (Para habilitá-la, colete com o Script 02b e rode o Script 03.)")


# ==============================================================================
# BLOCO 5 — PRÉ-PROCESSAMENTO: ESCALA DO LOG-RETORNO
# ==============================================================================
# O GARCH requer que os retornos sejam em percentual (×100), não em decimal.
# Ex: 0.02 → 2.0 (o ativo subiu 2%)

df_financeiro['Log_Retorno_Pct'] = df_financeiro['Log_Retorno'] * 100

print(f"\n📐 Log-Retorno convertido para percentual.")
print(f"   Mín: {df_financeiro['Log_Retorno_Pct'].min():.2f}%")
print(f"   Máx: {df_financeiro['Log_Retorno_Pct'].max():.2f}%")


# ==============================================================================
# BLOCO 6 — TESTES ESTATÍSTICOS DE PRÉ-REQUISITO (SEÇÃO 3.3.1)
# ==============================================================================
# Antes de aplicar o GARCH, precisamos provar estatisticamente que:
# 1. A série NÃO é normal (fat tails) — Teste Jarque-Bera
# 2. A série É estacionária (sem raiz unitária) — Teste ADF
# 3. A série TEM efeito ARCH (heterocedasticidade) — Teste ARCH-LM

print("\n" + "="*60)
print("TESTES ESTATÍSTICOS (SEÇÃO 3.3.1 DA DISSERTAÇÃO)")
print("="*60)

retornos = df_financeiro['Log_Retorno_Pct'].dropna()

# --- TESTE 1: Jarque-Bera (Normalidade) ---
jb_stat, jb_pvalue = stats.jarque_bera(retornos)
print(f"\n📊 TESTE DE NORMALIDADE — JARQUE-BERA")
print(f"   Estatística JB : {jb_stat:.4f}")
print(f"   p-valor        : {jb_pvalue:.6f}")
if jb_pvalue < 0.05:
    print(f"   ✅ Resultado: Rejeita H0 (p < 0.05) → A série NÃO é normal.")
    print(f"      Interpretação: A série tem caudas pesadas (fat tails), confirmando")
    print(f"      a necessidade de distribuição Student-t no GARCH.")
else:
    print(f"   ⚠️  Resultado: Não rejeita H0 → A série pode ser aproximadamente normal.")

# --- TESTE 2: Dickey-Fuller Aumentado (Estacionariedade) ---
adf_resultado = adfuller(retornos, autolag='AIC')
adf_stat    = adf_resultado[0]
adf_pvalue  = adf_resultado[1]
print(f"\n📊 TESTE DE ESTACIONARIEDADE — DICKEY-FULLER AUMENTADO (ADF)")
print(f"   Estatística ADF: {adf_stat:.4f}")
print(f"   p-valor        : {adf_pvalue:.6f}")
if adf_pvalue < 0.05:
    print(f"   ✅ Resultado: Rejeita H0 (p < 0.05) → A série É estacionária.")
    print(f"      Interpretação: Os log-retornos não possuem raiz unitária.")
    print(f"      O uso de GARCH e ML é apropriado.")
else:
    print(f"   ⚠️  Resultado: Não rejeita H0 → A série pode ter raiz unitária.")

# --- TESTE 3: ARCH-LM (Heterocedasticidade Condicional) ---
arch_test = het_arch(retornos, nlags=5)
arch_stat   = arch_test[0]
arch_pvalue = arch_test[1]
print(f"\n📊 TESTE DE HETEROCEDASTICIDADE — ARCH-LM (Engle)")
print(f"   Estatística LM : {arch_stat:.4f}")
print(f"   p-valor        : {arch_pvalue:.6f}")
if arch_pvalue < 0.05:
    print(f"   ✅ Resultado: Rejeita H0 (p < 0.05) → Efeito ARCH detectado.")
    print(f"      Interpretação: A variância NÃO é constante ao longo do tempo.")
    print(f"      Isso JUSTIFICA matematicamente o uso do GARCH(1,1).")
else:
    print(f"   ⚠️  Resultado: Não rejeita H0 → Efeito ARCH não significativo.")

# Salva o relatório dos testes em arquivo de texto
relatorio_testes = f"""RELATÓRIO DE TESTES ESTATÍSTICOS — PETR4 (2018-2025)
======================================================

TESTE DE NORMALIDADE — JARQUE-BERA
  Estatística JB : {jb_stat:.4f}
  p-valor        : {jb_pvalue:.6f}
  Conclusão      : {'Rejeita H0 — série NÃO é normal (fat tails confirmadas)' if jb_pvalue < 0.05 else 'Não rejeita H0'}

TESTE DE ESTACIONARIEDADE — DICKEY-FULLER AUMENTADO (ADF)
  Estatística ADF: {adf_stat:.4f}
  p-valor        : {adf_pvalue:.6f}
  Conclusão      : {'Rejeita H0 — série É estacionária (sem raiz unitária)' if adf_pvalue < 0.05 else 'Não rejeita H0'}

TESTE DE HETEROCEDASTICIDADE — ARCH-LM (Engle)
  Estatística LM : {arch_stat:.4f}
  p-valor        : {arch_pvalue:.6f}
  Conclusão      : {'Rejeita H0 — efeito ARCH detectado (GARCH justificado)' if arch_pvalue < 0.05 else 'Não rejeita H0'}
"""

with open(caminho_base + "relatorio_testes_estatisticos.txt", 'w', encoding='utf-8') as f:
    f.write(relatorio_testes)

print(f"\n💾 Relatório salvo: {caminho_base}relatorio_testes_estatisticos.txt")


# ==============================================================================
# BLOCO 7 — MODELAGEM GARCH(1,1) (EQUAÇÃO 3.2 DA DISSERTAÇÃO)
# ==============================================================================
# GARCH(1,1): σ²t = ω + α·ε²(t-1) + β·σ²(t-1)
#
# Onde:
# • σ²t       = variância condicional (volatilidade prevista no dia t)
# • ω         = variância de longo prazo (constante)
# • α·ε²(t-1) = termo ARCH: impacto do choque do dia anterior
# • β·σ²(t-1) = termo GARCH: persistência da volatilidade histórica
#
# Distribuição t-Student: adequada para séries financeiras com fat tails

print("\n" + "="*60)
print("MODELAGEM GARCH(1,1) — SEÇÃO 3.3 DA DISSERTAÇÃO")
print("="*60)

modelo_garch = arch_model(
    retornos,
    vol  = 'Garch',  # Modelo de volatilidade: GARCH
    p    = 1,         # Número de termos ARCH (lags do choque)
    q    = 1,         # Número de termos GARCH (lags da volatilidade)
    dist = 't'        # Distribuição t-Student (caudas pesadas)
)

print("Estimando parâmetros do GARCH(1,1)...")
resultado_garch = modelo_garch.fit(disp='off')  # disp='off' = sem output verboso

print(resultado_garch.summary())

# Extrai a volatilidade condicional estimada
df_financeiro['Volatilidade_GARCH'] = resultado_garch.conditional_volatility

# Verifica os parâmetros chave
params = resultado_garch.params
print(f"\n📊 PARÂMETROS DO GARCH(1,1):")
print(f"   ω (omega) = {params.get('omega', params.iloc[0]):.6f}  — variância de longo prazo")
print(f"   α (alpha) = {params.get('alpha[1]', params.iloc[1]):.6f}  — impacto de choques")
print(f"   β (beta)  = {params.get('beta[1]', params.iloc[2]):.6f}  — persistência da volatilidade")

alpha_val = params.get('alpha[1]', 0)
beta_val  = params.get('beta[1]', 0)
persistencia = alpha_val + beta_val
print(f"\n   α + β = {persistencia:.4f}  (próximo a 1 = alta persistência de volatilidade)")

if persistencia > 0.95:
    print("   ✅ Alta persistência: choques de volatilidade demoram a dissipar na PETR4.")


# ==============================================================================
# BLOCO 8 — GRÁFICO DA VOLATILIDADE CONDICIONAL (FIGURA 4.2 DA DISSERTAÇÃO)
# ==============================================================================

print("\n📊 Gerando gráfico da Volatilidade Condicional (Figura 4.2)...")

fig, axes = plt.subplots(2, 1, figsize=(16, 10))

# --- Painel superior: Log-Retorno ---
axes[0].plot(df_financeiro.index, df_financeiro['Log_Retorno_Pct'],
             color='#2c7bb6', linewidth=0.6, alpha=0.8)
axes[0].axhline(y=0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)
axes[0].set_title('Log-Retorno Diário da PETR4 (%)', fontweight='bold')
axes[0].set_ylabel('Log-Retorno (%)')
axes[0].set_xlabel('')

# --- Painel inferior: Volatilidade Condicional GARCH ---
axes[1].fill_between(df_financeiro.index,
                     df_financeiro['Volatilidade_GARCH'],
                     color='#d7191c', alpha=0.4, label='Volatilidade Condicional')
axes[1].plot(df_financeiro.index, df_financeiro['Volatilidade_GARCH'],
             color='#d7191c', linewidth=0.8)
axes[1].set_title('Volatilidade Condicional da PETR4 — Modelo GARCH(1,1)\n(Agrupamentos de Volatilidade — Volatility Clusters)',
                  fontweight='bold')
axes[1].set_ylabel('Volatilidade Condicional (σ)')
axes[1].set_xlabel('Data')

# Formata o eixo X para mostrar apenas os anos
for ax in axes:
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.grid(True, alpha=0.3)

plt.tight_layout()

caminho_grafico_garch = caminho_base + "grafico_volatilidade_garch.png"
plt.savefig(caminho_grafico_garch, dpi=150, bbox_inches='tight')
plt.show()

print(f"   💾 Gráfico salvo: {caminho_grafico_garch}")


# ==============================================================================
# BLOCO 9 — DATA FUSION: CONSTRUÇÃO DA MATRIZ DE ATRIBUTOS (SEÇÃO 3.4)
# ==============================================================================
# Conforme a Figura 3.2 da dissertação, a Matriz de Atributos combina:
# (1) Retorno do dia anterior     (Rt-1)
# (2) Volatilidade GARCH          (σ²t-1)
# (3) Sentimento da mídia         (ISM t-1)
#
# DESLOCAMENTO TEMPORAL (LAG):
# O modelo prevê D0 (hoje) usando apenas informações de D-1 (ontem).
# Isso evita data leakage (uso de informação do futuro).

print("\n" + "="*60)
print("DATA FUSION — CONSTRUÇÃO DA MATRIZ DE ATRIBUTOS (SEÇÃO 3.4)")
print("="*60)

# Junta os dados financeiros com o ISM diário
df_master = df_financeiro.join(df_ism[['Indice_Sentimento_Transformer']], how='left')

# Junta também o ISM por categoria, quando disponível (habilita ablação)
COLUNAS_CATEGORIA_LAG = []
if df_ism_cat is not None and COLUNAS_CATEGORIA:
    df_master = df_master.join(df_ism_cat[COLUNAS_CATEGORIA], how='left')

# Aplica o deslocamento de 1 dia (lag) em todas as variáveis preditoras
df_master['Retorno_Ontem']      = df_master['Log_Retorno_Pct'].shift(1)
df_master['Volatilidade_Ontem'] = df_master['Volatilidade_GARCH'].shift(1)
df_master['Sentimento_Ontem']   = df_master['Indice_Sentimento_Transformer'].shift(1)

# Lag de 1 dia para cada categoria (mesma lógica anti-data-leakage)
for col in COLUNAS_CATEGORIA:
    col_lag = col + "_Ontem"
    df_master[col_lag] = df_master[col].shift(1)
    COLUNAS_CATEGORIA_LAG.append(col_lag)

# Variável-Alvo: 1 = Alta (retorno positivo), 0 = Baixa (retorno negativo ou zero)
df_master['Alvo'] = np.where(df_master['Log_Retorno_Pct'] > 0, 1, 0)

# Remove linhas com valores ausentes (primeiro dia e dias sem cobertura de notícias)
df_master.dropna(subset=['Retorno_Ontem', 'Volatilidade_Ontem', 'Alvo'], inplace=True)

# Para os dias sem ISM (sem notícias coletadas), preenchemos com zero (sentimento neutro)
# Atribuição explícita (compatível com Copy-on-Write do pandas >= 3.0).
df_master['Sentimento_Ontem'] = df_master['Sentimento_Ontem'].fillna(0)
for col_lag in COLUNAS_CATEGORIA_LAG:
    df_master[col_lag] = df_master[col_lag].fillna(0)

print(f"✅ Matriz de atributos construída:")
print(f"   Total de pregões no modelo : {len(df_master)}")
print(f"   Pregões com ISM real        : {df_master['Sentimento_Ontem'].ne(0).sum()}")
print(f"   Pregões sem notícias (zero) : {df_master['Sentimento_Ontem'].eq(0).sum()}")
print(f"\n   Distribuição da Variável-Alvo:")
print(f"   Alta  (1): {df_master['Alvo'].sum():5d} dias ({df_master['Alvo'].mean()*100:.1f}%)")
print(f"   Baixa (0): {(df_master['Alvo']==0).sum():5d} dias ({(1-df_master['Alvo'].mean())*100:.1f}%)")


# ==============================================================================
# BLOCO 10 — GRÁFICO DE DISPERSÃO: SENTIMENTO vs. VOLATILIDADE (FIGURA 4.4)
# ==============================================================================

# Filtra apenas os dias com ISM real (sentimento diferente de zero)
df_plot = df_master[df_master['Sentimento_Ontem'] != 0].copy()

if len(df_plot) > 50:
    print("\n📊 Gerando gráfico de dispersão Sentimento vs. Volatilidade (Figura 4.4)...")

    fig, ax = plt.subplots(figsize=(10, 7))

    # Coloração: azul = Alta, vermelho = Baixa
    cores = df_plot['Alvo'].map({1: '#2c7bb6', 0: '#d7191c'})

    scatter = ax.scatter(
        df_plot['Sentimento_Ontem'],
        df_plot['Volatilidade_Ontem'],
        c=cores, alpha=0.5, s=20, edgecolors='none'
    )

    ax.axvline(x=0, color='black', linewidth=1, linestyle='--', alpha=0.5, label='Sentimento Neutro')
    ax.set_xlabel('Índice de Sentimento Textual (BERTimbau)\n← Pessimismo | Otimismo →')
    ax.set_ylabel('Volatilidade Condicional — GARCH(1,1) (σ)')
    ax.set_title('Gráfico de Dispersão: Sentimento Textual vs. Volatilidade Condicional da PETR4\n(Seção 4.3 — Validação da Hipótese H3: Viés de Negatividade)',
                 fontweight='bold')

    # Legenda manual
    from matplotlib.patches import Patch
    legenda = [
        Patch(color='#2c7bb6', label='Alta no dia seguinte'),
        Patch(color='#d7191c', label='Baixa no dia seguinte'),
    ]
    ax.legend(handles=legenda, loc='upper right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    caminho_grafico_dispersao = caminho_base + "grafico_dispersao_sentimento_volatilidade.png"
    plt.savefig(caminho_grafico_dispersao, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"   💾 Gráfico salvo: {caminho_grafico_dispersao}")


# ==============================================================================
# BLOCO 11 — SEPARAÇÃO DAS FEATURES (ATRIBUTOS) PARA OS MODELOS
# ==============================================================================

# Features BASELINE: apenas dados históricos de preços (sem sentimento)
features_baseline = ['Retorno_Ontem', 'Volatilidade_Ontem']

# Features DATA FUSION: preços + GARCH + Sentimento
features_data_fusion = ['Retorno_Ontem', 'Volatilidade_Ontem', 'Sentimento_Ontem']

X_baseline    = df_master[features_baseline].values
X_data_fusion = df_master[features_data_fusion].values
Y             = df_master['Alvo'].values

print(f"\n✅ Features preparadas.")
print(f"   Baseline (sem sentimento)  : {len(features_baseline)} variáveis")
print(f"   Data Fusion (com sentimento): {len(features_data_fusion)} variáveis")


# ==============================================================================
# BLOCO 12 — PARTICIONAMENTO TREINO / VALIDAÇÃO / TESTE (SEÇÃO 3.5)
# ==============================================================================
# Atende à exigência da banca quanto à validade temporal (sem data leakage).
# Dois protocolos estão disponíveis (configuráveis em PROTOCOLO_SPLIT):
#
#   • "cronologico" (PADRÃO): treino = 60% mais antigos, validação = 15%
#     seguintes, teste = 25% mais recentes. Corte estritamente temporal — o
#     teste nunca participa do treino nem da seleção. É o protocolo
#     cientificamente mais defensável para séries temporais financeiras e o
#     que elimina o lookahead criticado na qualificação.
#
#   • "estratificado": usa o mapa definicao_split_temporal.csv (Script 02c),
#     que distribui 60/15/25 dentro de CADA ano. Garante todos os anos (regimes
#     de mercado) nos três conjuntos, mas introduz leve lookahead entre anos —
#     recomendado apenas como ANÁLISE DE SENSIBILIDADE.
#
# Papel de cada conjunto: TREINO ajusta os modelos; VALIDAÇÃO seleciona os
# hiperparâmetros; TESTE é avaliado uma ÚNICA vez (out-of-sample).

PROTOCOLO_SPLIT = "cronologico"          # "cronologico" (padrão) ou "estratificado"
PROP_TREINO, PROP_VALIDACAO = 0.60, 0.15  # teste = 25% (1 - treino - validação)

print("\n" + "="*60)
print("PARTICIONAMENTO TREINO / VALIDAÇÃO / TESTE (SEÇÃO 3.5)")
print("="*60)

n_total = len(Y)
datas   = df_master.index

if PROTOCOLO_SPLIT == "estratificado":
    caminho_split = caminho_base + "definicao_split_temporal.csv"
    if os.path.exists(caminho_split):
        _mapa = pd.read_csv(caminho_split, parse_dates=['Data'])
        _d2c  = dict(zip(_mapa['Data'].dt.date, _mapa['conjunto']))
        _conj = np.array([_d2c.get(d.date(), 'treino') for d in datas])
        idx_tr = np.where(_conj == 'treino')[0]
        idx_va = np.where(_conj == 'validacao')[0]
        idx_te = np.where(_conj == 'teste')[0]
        print("   Protocolo: ESTRATIFICADO por ano (definicao_split_temporal.csv)")
    else:
        print(f"   ⚠️  {caminho_split} não encontrado — usando protocolo cronológico.")
        PROTOCOLO_SPLIT = "cronologico"

if PROTOCOLO_SPLIT == "cronologico":
    c1 = int(n_total * PROP_TREINO)
    c2 = int(n_total * (PROP_TREINO + PROP_VALIDACAO))
    idx_tr = np.arange(0, c1)
    idx_va = np.arange(c1, c2)
    idx_te = np.arange(c2, n_total)
    print("   Protocolo: CRONOLÓGICO (sem data leakage)")

Y_treino, Y_val, Y_teste = Y[idx_tr], Y[idx_va], Y[idx_te]

# Datas de referência para relatórios e salvamento
data_inicio_treino = datas[idx_tr[0]].date()
data_fim_treino    = datas[idx_tr[-1]].date()
data_inicio_teste  = datas[idx_te[0]].date()
data_fim_teste     = datas[idx_te[-1]].date()

print(f"   Total de pregões : {n_total}")
print(f"   TREINO    : {len(idx_tr):4d} pregões ({len(idx_tr)/n_total*100:4.1f}%)")
print(f"   VALIDAÇÃO : {len(idx_va):4d} pregões ({len(idx_va)/n_total*100:4.1f}%)")
print(f"   TESTE     : {len(idx_te):4d} pregões ({len(idx_te)/n_total*100:4.1f}%)")


# ==============================================================================
# BLOCO 13 — FUNÇÃO DE AVALIAÇÃO DOS MODELOS
# ==============================================================================

def avaliar_modelo(nome, previsoes, Y_teste, Y_proba=None):
    """
    Calcula e exibe todas as métricas de avaliação do classificador.

    Parâmetros:
    -----------
    nome      : str   — nome do modelo para exibição
    previsoes : array — previsões binárias (0 ou 1)
    Y_teste   : array — rótulos reais
    Y_proba   : array — probabilidades (para AUC-ROC), opcional

    Retorna:
    --------
    dict : dicionário com todas as métricas
    """
    acuracia  = accuracy_score(Y_teste, previsoes)
    precisao  = precision_score(Y_teste, previsoes, zero_division=0)
    f1        = f1_score(Y_teste, previsoes, zero_division=0)
    auc_roc   = roc_auc_score(Y_teste, Y_proba) if Y_proba is not None else 0.5

    return {
        'Modelo'    : nome,
        'Acurácia'  : round(acuracia * 100, 2),
        'Precisão'  : round(precisao * 100, 2),
        'F1-Score'  : round(f1 * 100, 2),
        'AUC-ROC'   : round(auc_roc, 4),
    }


# ==============================================================================
# BLOCO 13b — FUNÇÃO UNIFICADA: TREINO + SELEÇÃO NA VALIDAÇÃO + TESTE
# ==============================================================================
# Encapsula o protocolo correto: ajusta o modelo no TREINO, escolhe o melhor
# hiperparâmetro pela AUC-ROC na VALIDAÇÃO e avalia uma ÚNICA vez no TESTE.
# O scaler (quando usado) é ajustado apenas no treino — evita data leakage.

def treinar_e_avaliar(nome, criar_modelo, X, grade, normalizar):
    X_tr, X_va, X_te = X[idx_tr], X[idx_va], X[idx_te]
    if normalizar:
        sc = StandardScaler().fit(X_tr)
        X_tr, X_va, X_te = sc.transform(X_tr), sc.transform(X_va), sc.transform(X_te)

    melhor, melhor_auc, melhor_params = None, -1.0, None
    for params in grade:                       # seleção de hiperparâmetros
        modelo = criar_modelo(params)
        modelo.fit(X_tr, Y_treino)
        auc_va = roc_auc_score(Y_val, modelo.predict_proba(X_va)[:, 1])
        if auc_va > melhor_auc:
            melhor, melhor_auc, melhor_params = modelo, auc_va, params

    prev  = melhor.predict(X_te)
    proba = melhor.predict_proba(X_te)[:, 1]
    met = avaliar_modelo(nome, prev, Y_teste, proba)
    met['AUC_val'] = round(melhor_auc, 4)
    met['_modelo'] = melhor
    met['_params'] = melhor_params
    print(f"   {nome}")
    print(f"      melhor hiperparâmetro (validação): {melhor_params} | AUC_val = {melhor_auc:.4f}")
    print(f"      TESTE → Acc {met['Acurácia']:.2f}% | Prec {met['Precisão']:.2f}% | "
          f"F1 {met['F1-Score']:.2f}% | AUC {met['AUC-ROC']:.4f}")
    return met


# ==============================================================================
# BLOCO 14 — TREINAMENTO DOS 4 MODELOS (SVM/XGBoost × Baseline/Data Fusion)
# ==============================================================================

print("\n" + "="*60)
print("TREINAMENTO E SELEÇÃO DOS MODELOS")
print("="*60)

def _criar_svm(p):
    return SVC(kernel='rbf', C=p['C'], gamma='scale', probability=True, random_state=42)

def _criar_xgb(p):
    return XGBClassifier(
        n_estimators=100, max_depth=p['max_depth'], learning_rate=p['learning_rate'],
        subsample=0.8, colsample_bytree=0.8, eval_metric='logloss',
        random_state=42, verbosity=0)

# Grades de hiperparâmetros (justificadas: parcimônia + busca leve na validação)
GRADE_SVM = [{'C': c} for c in (0.5, 1.0, 10.0)]
GRADE_XGB = [{'max_depth': d, 'learning_rate': lr} for d in (3, 5) for lr in (0.05, 0.1)]

metricas_svm_bl = treinar_e_avaliar("SVM (Apenas Preços)",                _criar_svm, X_baseline,    GRADE_SVM, True)
metricas_xgb_bl = treinar_e_avaliar("XGBoost (Apenas Preços)",            _criar_xgb, X_baseline,    GRADE_XGB, False)
metricas_svm_df = treinar_e_avaliar("SVM (Data Fusion — GARCH + NLP)",    _criar_svm, X_data_fusion, GRADE_SVM, True)
metricas_xgb_df = treinar_e_avaliar("XGBoost (Data Fusion — GARCH + NLP)",_criar_xgb, X_data_fusion, GRADE_XGB, False)

# Modelo XGBoost Data Fusion selecionado (usado na importância das variáveis)
xgb_fusion = metricas_xgb_df['_modelo']


# ==============================================================================
# BLOCO 18 — TABELA COMPARATIVA (TABELA 4.3 DA DISSERTAÇÃO)
# ==============================================================================

print("\n" + "="*60)
print("TABELA 4.3 — DESEMPENHO DOS CLASSIFICADORES (SEÇÃO 4.4)")
print("="*60)
print(f"Período de treino : {data_inicio_treino} até {data_fim_treino}")
print(f"Período de teste  : {data_inicio_teste} até {data_fim_teste}")
print()

# Monta a tabela apenas com as colunas de exibição (exclui chaves internas)
_COLS = ['Modelo', 'Acurácia', 'Precisão', 'F1-Score', 'AUC-ROC', 'AUC_val']
df_resultados = pd.DataFrame([
    {k: m[k] for k in _COLS}
    for m in (metricas_svm_bl, metricas_xgb_bl, metricas_svm_df, metricas_xgb_df)
])

print(df_resultados.to_string(index=False))

# Calcula o ganho do Data Fusion sobre o Baseline
ganho_svm = metricas_svm_df['Acurácia'] - metricas_svm_bl['Acurácia']
ganho_xgb = metricas_xgb_df['Acurácia'] - metricas_xgb_bl['Acurácia']

print(f"\n📊 GANHO DE ACURÁCIA COM DATA FUSION (SENTIMENTO + GARCH):")
print(f"   SVM:     {'+'if ganho_svm>=0 else ''}{ganho_svm:.2f} pontos percentuais")
print(f"   XGBoost: {'+'if ganho_xgb>=0 else ''}{ganho_xgb:.2f} pontos percentuais")


# ==============================================================================
# BLOCO 19 — IMPORTÂNCIA DAS VARIÁVEIS (XGBOOST DATA FUSION)
# ==============================================================================

print("\n📊 IMPORTÂNCIA DAS VARIÁVEIS — XGBoost Data Fusion:")
importancias = pd.DataFrame({
    'Variável'   : features_data_fusion,
    'Importância': xgb_fusion.feature_importances_,
}).sort_values('Importância', ascending=False)

for _, row in importancias.iterrows():
    bar = '█' * int(row['Importância'] * 50)
    print(f"   {row['Variável']:30s}: {row['Importância']:.4f}  {bar}")


# ==============================================================================
# BLOCO 19b — ANÁLISE DE ABLAÇÃO POR CATEGORIA DE NOTÍCIA
# ==============================================================================
# Responde à pergunta de pesquisa: "Qual CATEGORIA de notícia é mais informativa
# para prever a direção do PETR4?". A técnica de ablação:
#   1. Treina o modelo COMPLETO: preços + GARCH + sentimento das 7 categorias.
#   2. Remove UMA categoria por vez, retreina e mede a acurácia.
#   3. A queda de acurácia ao remover a categoria X = importância de X.
#      Quanto MAIOR a queda, mais informativa é aquela categoria.
#
# Só executa se o ISM por categoria estiver disponível (Script 02b → 03).

df_ablacao = None
if COLUNAS_CATEGORIA_LAG:
    print("\n" + "="*60)
    print("ANÁLISE DE ABLAÇÃO POR CATEGORIA (CONTRIBUIÇÃO CIENTÍFICA)")
    print("="*60)

    features_full = ['Retorno_Ontem', 'Volatilidade_Ontem'] + COLUNAS_CATEGORIA_LAG

    def treinar_xgb_acuracia(lista_features):
        """Treina XGBoost com o conjunto de features dado e retorna a acurácia no teste."""
        X = df_master[lista_features].values
        modelo = XGBClassifier(
            n_estimators=100, max_depth=3, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8, eval_metric='logloss',
            random_state=42, verbosity=0,
        )
        modelo.fit(X[idx_tr], Y_treino)
        return accuracy_score(Y_teste, modelo.predict(X[idx_te])) * 100

    # Modelo completo (todas as categorias)
    acc_full = treinar_xgb_acuracia(features_full)
    print(f"\n   Modelo COMPLETO (todas as {len(COLUNAS_CATEGORIA_LAG)} categorias): "
          f"{acc_full:.2f}% de acurácia")
    print(f"\n   Impacto de remover cada categoria (queda = importância):")

    linhas_ablacao = []
    for col_lag in COLUNAS_CATEGORIA_LAG:
        features_sem = [f for f in features_full if f != col_lag]
        acc_sem = treinar_xgb_acuracia(features_sem)
        impacto = acc_full - acc_sem  # queda ao remover esta categoria
        nome_cat = col_lag.replace('ISM_', '').replace('_Ontem', '')
        linhas_ablacao.append({
            'Categoria'          : nome_cat,
            'Acuracia_sem_ela'   : round(acc_sem, 2),
            'Impacto_pp'         : round(impacto, 2),  # pontos percentuais
        })

    df_ablacao = (pd.DataFrame(linhas_ablacao)
                  .sort_values('Impacto_pp', ascending=False)
                  .reset_index(drop=True))
    df_ablacao.insert(0, 'Acuracia_completo', round(acc_full, 2))

    for _, r in df_ablacao.iterrows():
        seta = '↓' if r['Impacto_pp'] > 0 else ('↑' if r['Impacto_pp'] < 0 else '·')
        bar = '█' * int(abs(r['Impacto_pp']) * 2)
        print(f"   {r['Categoria']:24s}: {seta} {r['Impacto_pp']:+5.2f} pp  {bar}")

    print(f"\n   📌 Categoria mais informativa: {df_ablacao.iloc[0]['Categoria']} "
          f"(remover custa {df_ablacao.iloc[0]['Impacto_pp']:.2f} pp de acurácia)")

    # Gráfico de barras da ablação
    try:
        fig, ax = plt.subplots(figsize=(11, 6))
        cores = ['#d7191c' if v > 0 else '#2c7bb6' for v in df_ablacao['Impacto_pp']]
        ax.barh(df_ablacao['Categoria'], df_ablacao['Impacto_pp'], color=cores, alpha=0.8)
        ax.axvline(0, color='black', linewidth=0.8)
        ax.set_xlabel('Queda de acurácia ao remover a categoria (pontos percentuais)')
        ax.set_title('Análise de Ablação: Importância de Cada Categoria de Notícia\n'
                     'na Previsão de Direção do PETR4 (XGBoost Data Fusion)',
                     fontweight='bold')
        ax.invert_yaxis()
        ax.grid(True, axis='x', alpha=0.3)
        plt.tight_layout()
        caminho_graf_ablacao = caminho_base + "grafico_ablacao_categorias.png"
        plt.savefig(caminho_graf_ablacao, dpi=150, bbox_inches='tight')
        plt.show()
        print(f"   💾 Gráfico de ablação salvo: {caminho_graf_ablacao}")
    except Exception as e:
        print(f"   ⚠️  Não foi possível gerar o gráfico de ablação: {e}")
else:
    print("\nℹ️  Análise de ablação pulada (ISM por categoria indisponível).")
    print("   Para habilitá-la: colete com o Script 02b e rode o Script 03.")


# ==============================================================================
# BLOCO 20 — SALVAMENTO DOS RESULTADOS
# ==============================================================================

# Salva tabela de resultados
caminho_resultados = caminho_base + "resultados_modelos_petr4.csv"
df_resultados.to_csv(caminho_resultados, index=False, encoding='utf-8')

# Salva base master consolidada (para análises posteriores)
caminho_master = caminho_base + "base_master_petr4.csv"
df_master[['Log_Retorno_Pct', 'Volatilidade_GARCH', 'Indice_Sentimento_Transformer',
           'Retorno_Ontem', 'Volatilidade_Ontem', 'Sentimento_Ontem', 'Alvo']].to_csv(
    caminho_master, encoding='utf-8'
)

# Salva a tabela de ablação por categoria (quando disponível)
if df_ablacao is not None:
    caminho_ablacao = caminho_base + "resultados_ablacao_categorias_petr4.csv"
    df_ablacao.to_csv(caminho_ablacao, index=False, encoding='utf-8')
    print(f"\n   💾 Tabela de ablação por categoria: {caminho_ablacao}")

print("\n" + "="*60)
print("✅ MODELAGEM CONCLUÍDA COM SUCESSO!")
print("="*60)
print(f"   💾 Tabela de resultados   : {caminho_resultados}")
print(f"   💾 Base master consolidada: {caminho_master}")
print(f"   💾 Gráfico GARCH          : {caminho_base}grafico_volatilidade_garch.png")
print(f"   💾 Gráfico Dispersão      : {caminho_base}grafico_dispersao_sentimento_volatilidade.png")
print(f"   💾 Testes estatísticos    : {caminho_base}relatorio_testes_estatisticos.txt")
print("\n🎓 Todos os resultados estão prontos para inclusão na dissertação.")
