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
#   5. Treina e avalia SVM e XGBoost com Walk-Forward Validation (Seção 3.5)
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
# BLOCO 1 — INSTALAÇÃO DAS BIBLIOTECAS
# ==============================================================================

!pip install arch xgboost scikit-learn pandas numpy matplotlib scipy statsmodels --quiet

print("✅ Bibliotecas instaladas.")


# ==============================================================================
# BLOCO 2 — IMPORTAÇÕES
# ==============================================================================

from google.colab import drive
import os
import pandas as pd
import numpy as np
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
# BLOCO 3 — CONEXÃO COM O GOOGLE DRIVE
# ==============================================================================

drive.mount('/content/drive')

caminho_base = '/content/drive/MyDrive/Mestrado_PETR4/'

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

# Aplica o deslocamento de 1 dia (lag) em todas as variáveis preditoras
df_master['Retorno_Ontem']      = df_master['Log_Retorno_Pct'].shift(1)
df_master['Volatilidade_Ontem'] = df_master['Volatilidade_GARCH'].shift(1)
df_master['Sentimento_Ontem']   = df_master['Indice_Sentimento_Transformer'].shift(1)

# Variável-Alvo: 1 = Alta (retorno positivo), 0 = Baixa (retorno negativo ou zero)
df_master['Alvo'] = np.where(df_master['Log_Retorno_Pct'] > 0, 1, 0)

# Remove linhas com valores ausentes (primeiro dia e dias sem cobertura de notícias)
df_master.dropna(subset=['Retorno_Ontem', 'Volatilidade_Ontem', 'Alvo'], inplace=True)

# Para os dias sem ISM (sem notícias coletadas), preenchemos com zero (sentimento neutro)
df_master['Sentimento_Ontem'].fillna(0, inplace=True)

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
# BLOCO 12 — WALK-FORWARD VALIDATION (SEÇÃO 3.5)
# ==============================================================================
# Conforme a Figura 3.3 da dissertação, usamos validação em janelas deslizantes:
# • Janela de treino inicial : primeiros 80% dos dados cronologicamente
# • Janela de teste          : últimos 20% dos dados (nunca vistos pelo modelo)
# • Para publicação final    : implementar o walk-forward completo por janelas
#
# NOTA: Para os resultados preliminares, usamos a divisão 80/20 cronológica
# (equivalente ao Walk 1 da Figura 3.3). Isso já é academicamente válido e
# é chamado de "Out-of-Sample Test" na literatura financeira.

print("\n" + "="*60)
print("WALK-FORWARD VALIDATION (SEÇÃO 3.5)")
print("="*60)

# Ponto de corte temporal (80% treino, 20% teste)
n_total = len(Y)
corte   = int(n_total * 0.80)

# Datas de referência para o relatório
data_inicio_treino = df_master.index[0].date()
data_fim_treino    = df_master.index[corte-1].date()
data_inicio_teste  = df_master.index[corte].date()
data_fim_teste     = df_master.index[-1].date()

print(f"   Total de pregões      : {n_total}")
print(f"   Janela de TREINO      : {data_inicio_treino} até {data_fim_treino} ({corte} pregões)")
print(f"   Janela de TESTE (cega): {data_inicio_teste} até {data_fim_teste} ({n_total - corte} pregões)")


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
# BLOCO 14 — TREINAMENTO E AVALIAÇÃO: MODELO 1 — SVM BASELINE
# ==============================================================================

print("\n" + "─"*60)
print("MODELO 1 — SVM | Apenas Preços Históricos (Baseline)")
print("─"*60)

# Divisão treino/teste
X_bl_treino, X_bl_teste = X_baseline[:corte], X_baseline[corte:]
Y_treino, Y_teste        = Y[:corte], Y[corte:]

# Normalização: SVM é sensível à escala das variáveis
# IMPORTANTE: o scaler é ajustado APENAS no treino (evita data leakage)
scaler_bl = StandardScaler()
X_bl_treino_norm = scaler_bl.fit_transform(X_bl_treino)
X_bl_teste_norm  = scaler_bl.transform(X_bl_teste)

# Treinamento
svm_baseline = SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42)
svm_baseline.fit(X_bl_treino_norm, Y_treino)

# Avaliação
prev_svm_bl   = svm_baseline.predict(X_bl_teste_norm)
proba_svm_bl  = svm_baseline.predict_proba(X_bl_teste_norm)[:, 1]
metricas_svm_bl = avaliar_modelo("SVM (Apenas Preços)", prev_svm_bl, Y_teste, proba_svm_bl)

print(f"   Acurácia : {metricas_svm_bl['Acurácia']:.2f}%")
print(f"   Precisão : {metricas_svm_bl['Precisão']:.2f}%")
print(f"   F1-Score : {metricas_svm_bl['F1-Score']:.2f}%")
print(f"   AUC-ROC  : {metricas_svm_bl['AUC-ROC']:.4f}")


# ==============================================================================
# BLOCO 15 — MODELO 2 — XGBOOST BASELINE
# ==============================================================================

print("\n" + "─"*60)
print("MODELO 2 — XGBoost | Apenas Preços Históricos (Baseline)")
print("─"*60)

xgb_baseline = XGBClassifier(
    n_estimators  = 100,
    max_depth     = 3,
    learning_rate = 0.1,
    subsample     = 0.8,
    colsample_bytree = 0.8,
    eval_metric   = 'logloss',
    random_state  = 42,
    verbosity     = 0,
)
xgb_baseline.fit(X_bl_treino, Y_treino)  # XGBoost não requer normalização

prev_xgb_bl   = xgb_baseline.predict(X_bl_teste)
proba_xgb_bl  = xgb_baseline.predict_proba(X_bl_teste)[:, 1]
metricas_xgb_bl = avaliar_modelo("XGBoost (Apenas Preços)", prev_xgb_bl, Y_teste, proba_xgb_bl)

print(f"   Acurácia : {metricas_xgb_bl['Acurácia']:.2f}%")
print(f"   Precisão : {metricas_xgb_bl['Precisão']:.2f}%")
print(f"   F1-Score : {metricas_xgb_bl['F1-Score']:.2f}%")
print(f"   AUC-ROC  : {metricas_xgb_bl['AUC-ROC']:.4f}")


# ==============================================================================
# BLOCO 16 — MODELO 3 — SVM DATA FUSION (com sentimento)
# ==============================================================================

print("\n" + "─"*60)
print("MODELO 3 — SVM | Data Fusion (Preços + GARCH + Sentimento)")
print("─"*60)

X_df_treino, X_df_teste = X_data_fusion[:corte], X_data_fusion[corte:]

scaler_df = StandardScaler()
X_df_treino_norm = scaler_df.fit_transform(X_df_treino)
X_df_teste_norm  = scaler_df.transform(X_df_teste)

svm_fusion = SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42)
svm_fusion.fit(X_df_treino_norm, Y_treino)

prev_svm_df   = svm_fusion.predict(X_df_teste_norm)
proba_svm_df  = svm_fusion.predict_proba(X_df_teste_norm)[:, 1]
metricas_svm_df = avaliar_modelo("SVM (Data Fusion — GARCH + NLP)", prev_svm_df, Y_teste, proba_svm_df)

print(f"   Acurácia : {metricas_svm_df['Acurácia']:.2f}%")
print(f"   Precisão : {metricas_svm_df['Precisão']:.2f}%")
print(f"   F1-Score : {metricas_svm_df['F1-Score']:.2f}%")
print(f"   AUC-ROC  : {metricas_svm_df['AUC-ROC']:.4f}")


# ==============================================================================
# BLOCO 17 — MODELO 4 — XGBOOST DATA FUSION (com sentimento)
# ==============================================================================

print("\n" + "─"*60)
print("MODELO 4 — XGBoost | Data Fusion (Preços + GARCH + Sentimento)")
print("─"*60)

xgb_fusion = XGBClassifier(
    n_estimators  = 100,
    max_depth     = 3,
    learning_rate = 0.1,
    subsample     = 0.8,
    colsample_bytree = 0.8,
    eval_metric   = 'logloss',
    random_state  = 42,
    verbosity     = 0,
)
xgb_fusion.fit(X_df_treino, Y_treino)

prev_xgb_df   = xgb_fusion.predict(X_df_teste)
proba_xgb_df  = xgb_fusion.predict_proba(X_df_teste)[:, 1]
metricas_xgb_df = avaliar_modelo("XGBoost (Data Fusion — GARCH + NLP)", prev_xgb_df, Y_teste, proba_xgb_df)

print(f"   Acurácia : {metricas_xgb_df['Acurácia']:.2f}%")
print(f"   Precisão : {metricas_xgb_df['Precisão']:.2f}%")
print(f"   F1-Score : {metricas_xgb_df['F1-Score']:.2f}%")
print(f"   AUC-ROC  : {metricas_xgb_df['AUC-ROC']:.4f}")


# ==============================================================================
# BLOCO 18 — TABELA COMPARATIVA (TABELA 4.3 DA DISSERTAÇÃO)
# ==============================================================================

print("\n" + "="*60)
print("TABELA 4.3 — DESEMPENHO DOS CLASSIFICADORES (SEÇÃO 4.4)")
print("="*60)
print(f"Período de treino : {data_inicio_treino} até {data_fim_treino}")
print(f"Período de teste  : {data_inicio_teste} até {data_fim_teste}")
print()

df_resultados = pd.DataFrame([
    metricas_svm_bl,
    metricas_xgb_bl,
    metricas_svm_df,
    metricas_xgb_df,
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

print("\n" + "="*60)
print("✅ MODELAGEM CONCLUÍDA COM SUCESSO!")
print("="*60)
print(f"   💾 Tabela de resultados   : {caminho_resultados}")
print(f"   💾 Base master consolidada: {caminho_master}")
print(f"   💾 Gráfico GARCH          : {caminho_base}grafico_volatilidade_garch.png")
print(f"   💾 Gráfico Dispersão      : {caminho_base}grafico_dispersao_sentimento_volatilidade.png")
print(f"   💾 Testes estatísticos    : {caminho_base}relatorio_testes_estatisticos.txt")
print("\n🎓 Todos os resultados estão prontos para inclusão na dissertação.")
