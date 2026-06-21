# -*- coding: utf-8 -*-
# ==============================================================================
#
#   DISSERTAÇÃO: O Impacto do Sentimento de Notícias Financeiras na Previsão
#                de Direção e Volatilidade do Ativo PETR4
#   Autor      : Vanderlei Barbosa da Silva
#   Orientador : Prof. Dr. Julio Cesar Nievola — PUCPR
#   Script     : 01 — Coleta de Dados Financeiros da PETR4
#
# ==============================================================================
#
#   O QUE ESTE SCRIPT FAZ
#   ─────────────────────
#   Coleta a série histórica diária da PETR4 (2018-2025) diretamente da B3
#   via biblioteca yFinance, calcula o Log-Retorno (variável dependente do
#   modelo) e salva o arquivo base no Google Drive para uso nos scripts
#   seguintes.
#
#   POR QUE CALCULAMOS O LOG-RETORNO?
#   ─────────────────────────────────
#   Conforme descrito na Seção 3.1.1 da dissertação (Equação 3.1):
#       Rt = ln(Pt / Pt-1)
#   O logaritmo natural garante aditividade temporal e aproxima a série da
#   estacionariedade — requisito obrigatório para os modelos GARCH e ML.
#
#   ARQUIVOS GERADOS
#   ────────────────
#   • base_financeira_petr4.csv  →  Série com preços + Log-Retorno (2018-2025)
#
#   COMO RODAR
#   ──────────
#   1. Abra este script no Google Colab
#   2. Clique em "Ambiente de execução" → "Executar tudo"
#   3. Autorize o acesso ao Google Drive quando solicitado
#
# ==============================================================================


# ==============================================================================
# BLOCO 1 — INSTALAÇÃO DAS BIBLIOTECAS NECESSÁRIAS
# ==============================================================================
# Instalamos apenas o que o Colab não tem por padrão.
# O "--quiet" evita que o terminal fique poluído com mensagens de instalação.

!pip install yfinance --quiet

print("✅ Bibliotecas verificadas e prontas.")


# ==============================================================================
# BLOCO 2 — IMPORTAÇÃO DAS FERRAMENTAS
# ==============================================================================

from google.colab import drive   # Para conectar ao seu Google Drive
import os                        # Para criar pastas
import pandas as pd              # Para manipular tabelas de dados
import numpy as np               # Para cálculos matemáticos (logaritmo)
import yfinance as yf            # Para baixar dados da bolsa (B3/NYSE)

print("✅ Todas as ferramentas importadas com sucesso.")


# ==============================================================================
# BLOCO 3 — CONEXÃO COM O GOOGLE DRIVE
# ==============================================================================
# Ao rodar esta célula, o Colab vai pedir autorização para acessar seu Drive.
# Clique no link que aparecer, escolha sua conta Google e cole o código.

drive.mount('/content/drive')

# Definimos a pasta onde TODOS os arquivos da dissertação serão salvos.
# Se a pasta não existir, o script a cria automaticamente.
caminho_base = '/content/drive/MyDrive/Mestrado_PETR4/'
os.makedirs(caminho_base, exist_ok=True)

print(f"✅ Google Drive conectado. Pasta da pesquisa: {caminho_base}")


# ==============================================================================
# BLOCO 4 — CONFIGURAÇÕES DA COLETA
# ==============================================================================
# Você pode alterar as datas aqui se precisar de um período diferente.

TICKER      = "PETR4.SA"    # Código da ação na B3 (sufixo .SA = São Paulo)
DATA_INICIO = "2018-01-01"  # Início do período de análise
DATA_FIM    = "2025-12-31"  # Fim do período de análise

print(f"\n📊 Iniciando coleta para: {TICKER}")
print(f"   Período: {DATA_INICIO} até {DATA_FIM}")


# ==============================================================================
# BLOCO 5 — DOWNLOAD DOS DADOS HISTÓRICOS
# ==============================================================================

try:
    ativo = yf.Ticker(TICKER)
    df_petr4 = ativo.history(start=DATA_INICIO, end=DATA_FIM)

    # Verificamos se os dados foram retornados corretamente
    if df_petr4.empty:
        raise ValueError("Nenhum dado foi retornado. Verifique o ticker e as datas.")

    print(f"✅ Dados baixados! Total de pregões coletados: {len(df_petr4)} dias")

except Exception as e:
    print(f"❌ Erro na coleta: {e}")
    print("   Dica: verifique sua conexão com a internet e tente novamente.")
    raise


# ==============================================================================
# BLOCO 6 — CÁLCULO DO LOG-RETORNO (EQUAÇÃO 3.1 DA DISSERTAÇÃO)
# ==============================================================================
# Rt = ln(Pt / Pt-1)
# np.log() = logaritmo natural
# .shift(1) = valor do dia anterior (Pt-1)

df_petr4['Log_Retorno'] = np.log(df_petr4['Close'] / df_petr4['Close'].shift(1))

# O primeiro dia não tem "dia anterior", então o Log_Retorno seria NaN.
# Removemos essa linha para não poluir a base.
df_petr4.dropna(inplace=True)

print(f"\n📐 Log-Retorno calculado.")
print(f"   Mínimo: {df_petr4['Log_Retorno'].min():.4f}")
print(f"   Máximo: {df_petr4['Log_Retorno'].max():.4f}")
print(f"   Média:  {df_petr4['Log_Retorno'].mean():.4f}")


# ==============================================================================
# BLOCO 7 — SELEÇÃO DAS COLUNAS RELEVANTES PARA A PESQUISA
# ==============================================================================
# Mantemos apenas as colunas que serão usadas na modelagem.
# Removemos colunas geradas pelo yFinance que não são necessárias
# (Dividends, Stock Splits, Capital Gains).

colunas_relevantes = ['Open', 'High', 'Low', 'Close', 'Volume', 'Log_Retorno']

# Verificamos quais dessas colunas existem (o yFinance pode variar)
colunas_existentes = [col for col in colunas_relevantes if col in df_petr4.columns]
df_petr4 = df_petr4[colunas_existentes]

# Padronizamos o índice de data para um formato limpo (sem fuso horário)
# Isso evita erros na junção com os dados de notícias no Script 04
df_petr4.index = pd.to_datetime(df_petr4.index).tz_localize(None)
df_petr4.index.name = 'Date'

print(f"\n📋 Colunas mantidas na base: {list(df_petr4.columns)}")


# ==============================================================================
# BLOCO 8 — ESTATÍSTICAS DESCRITIVAS (VERIFICAÇÃO DE QUALIDADE)
# ==============================================================================
# Este bloco permite verificar se os dados fazem sentido antes de salvar.
# Um preço de fechamento negativo, por exemplo, indicaria erro nos dados.

print("\n" + "="*60)
print("ESTATÍSTICAS DESCRITIVAS DA SÉRIE FINANCEIRA")
print("="*60)
print(df_petr4.describe().round(4))

print(f"\n📅 Primeiro registro: {df_petr4.index[0].date()}")
print(f"📅 Último registro:   {df_petr4.index[-1].date()}")


# ==============================================================================
# BLOCO 9 — SALVAMENTO NO GOOGLE DRIVE
# ==============================================================================

caminho_arquivo = caminho_base + "base_financeira_petr4.csv"

df_petr4.to_csv(caminho_arquivo)

print("\n" + "="*60)
print("✅ COLETA CONCLUÍDA COM SUCESSO!")
print("="*60)
print(f"   Arquivo salvo em: {caminho_arquivo}")
print(f"   Total de dias de pregão: {len(df_petr4)}")
print(f"   Período coberto: {df_petr4.index[0].date()} até {df_petr4.index[-1].date()}")
print("\n▶️  Próximo passo: execute o Script 02 para coletar as notícias.")


# ==============================================================================
# BLOCO 10 — PRÉVIA DOS DADOS (PRIMEIRAS E ÚLTIMAS LINHAS)
# ==============================================================================
# Exibe uma amostra dos dados para confirmar que tudo está correto.

print("\n📊 PRIMEIRAS 5 LINHAS DA BASE:")
print(df_petr4.head())

print("\n📊 ÚLTIMAS 5 LINHAS DA BASE:")
print(df_petr4.tail())
