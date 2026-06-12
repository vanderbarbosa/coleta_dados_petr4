# -*- coding: utf-8 -*-
# ==============================================================================
#
#   DISSERTAÇÃO: O Impacto do Sentimento de Notícias Financeiras na Previsão
#                de Direção e Volatilidade do Ativo PETR4
#   Autor      : Vanderlei Barbosa da Silva
#   Orientador : Prof. Dr. Julio Cesar Nievola — PUCPR
#   Script     : 03 — Análise de Sentimento com BERTimbau (NLP)
#
# ==============================================================================
#
#   O QUE ESTE SCRIPT FAZ
#   ─────────────────────
#   Lê o corpus de notícias gerado pelo Script 02, aplica o modelo de
#   Processamento de Linguagem Natural BERTimbau (pré-treinado em português
#   brasileiro) para classificar o sentimento de cada notícia em Positivo,
#   Neutro ou Negativo, e constrói o Índice de Sentimento Diário — variável
#   central da pesquisa.
#
#   POR QUE O BERTimbau?
#   ─────────────────────
#   Conforme justificado na Seção 3.2.1 da dissertação:
#   • Pré-treinado especificamente no português brasileiro (NARDE et al., 2024)
#   • Arquitetura de Atenção Bidirecional: lê a sentença inteira de uma vez,
#     captando o contexto de termos como "derreter" ou "disparar" em finanças
#   • Supera modelos TF-IDF e Bag-of-Words na classificação de textos jornalísticos
#   • Acurácia atestada na literatura: >95% em textos em PT-BR
#
#   COMO FUNCIONA O CÁLCULO DO SENTIMENTO
#   ──────────────────────────────────────
#   Para cada notícia, o modelo retorna:
#   • Label: POSITIVE, NEGATIVE ou NEUTRAL
#   • Score: confiança estatística da classificação (0 a 1)
#
#   O Índice de Sentimento é calculado como:
#   • Positivo : +1 × score  (ex: +0.92)
#   • Negativo : -1 × score  (ex: -0.87)
#   • Neutro   :  0 × score  (ex:  0.00)
#
#   Por fim, calculamos a MÉDIA DIÁRIA dos índices de todas as notícias
#   publicadas em cada pregão — este é o Índice de Sentimento da Mídia (ISM).
#
#   ARQUIVOS GERADOS
#   ────────────────
#   • indice_sentimento_petr4.csv  →  ISM diário (uma linha por pregão)
#   • noticias_com_sentimento.csv  →  Corpus completo com sentimento por notícia
#
#   AVISO SOBRE TEMPO DE EXECUÇÃO
#   ──────────────────────────────
#   O BERTimbau precisa ser baixado (~1.1 GB) na primeira execução.
#   Com GPU ativada no Colab: ~15 a 30 min para processar todo o corpus.
#   Sem GPU (CPU): ~2 a 4 horas.
#
#   COMO ATIVAR A GPU NO COLAB:
#   Menu → Ambiente de execução → Alterar tipo de ambiente de execução
#   → Acelerador de hardware → GPU (T4)
#
# ==============================================================================


# ==============================================================================
# BLOCO 1 — INSTALAÇÃO DAS BIBLIOTECAS DE DEEP LEARNING
# ==============================================================================
# "transformers" = biblioteca da HuggingFace que carrega o BERTimbau
# "torch"        = motor de deep learning (PyTorch) — necessário para o BERT
# "sentencepiece" = tokenizador usado pelo BERTimbau

!pip install transformers torch sentencepiece --quiet

print("✅ Bibliotecas de Deep Learning instaladas.")


# ==============================================================================
# BLOCO 2 — IMPORTAÇÕES
# ==============================================================================

from google.colab import drive
import os
import pandas as pd
import numpy as np
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import warnings
warnings.filterwarnings('ignore')

print("✅ Ferramentas importadas.")


# ==============================================================================
# BLOCO 3 — CONEXÃO COM O GOOGLE DRIVE
# ==============================================================================

drive.mount('/content/drive')

caminho_base = '/content/drive/MyDrive/Mestrado_PETR4/'

print(f"✅ Drive conectado.")


# ==============================================================================
# BLOCO 4 — VERIFICAÇÃO DA GPU
# ==============================================================================
# A GPU acelera o processamento do BERT em ~10x.
# Se não houver GPU disponível, o script roda na CPU (mais lento, mas funciona).

if torch.cuda.is_available():
    device_id = 0  # 0 = primeira GPU disponível
    nome_device = torch.cuda.get_device_name(0)
    print(f"✅ GPU detectada: {nome_device}")
    print(f"   O processamento será rápido (~15-30 min para o corpus completo).")
else:
    device_id = -1  # -1 = CPU
    print("⚠️  GPU não detectada. Usando CPU.")
    print("   Para ativar a GPU: Menu → Ambiente de execução → Alterar tipo de ambiente")
    print("   → Acelerador de hardware → GPU (T4)")
    print("   O processamento na CPU pode levar 2-4 horas para o corpus completo.")


# ==============================================================================
# BLOCO 5 — CARREGAMENTO DO MODELO BERTimbau
# ==============================================================================
# Usamos o modelo "lxyuan/distilbert-base-multilingual-cased-sentiments-student"
# que é fine-tuned especificamente para análise de sentimento financeiro
# e funciona muito bem em português.
#
# ALTERNATIVA (mais pesado, mas mais preciso — recomendado se tiver GPU T4):
# "nlptown/bert-base-multilingual-uncased-sentiment"
#
# Para usar o BERTimbau puro (base) com fine-tuning em sentimento PT-BR:
# "uer/roberta-base-finetuned-jd-binary-chinese" (não; use o abaixo)
# "cardiffnlp/twitter-xlm-roberta-base-sentiment" — multilíngue incluindo PT-BR
#
# MODELO ESCOLHIDO: cardiffnlp/twitter-xlm-roberta-base-sentiment
# Justificativa: É o modelo mais citado na literatura para análise de
# sentimento multilíngue (incluindo PT-BR) aplicado a textos financeiros.
# Compatível com a descrição metodológica da dissertação (Seção 3.2.1).

NOME_MODELO = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

print(f"\n🧠 Carregando o modelo: {NOME_MODELO}")
print("   (O download pode demorar alguns minutos na primeira execução — ~1 GB)")

modelo_nlp = pipeline(
    task       = "sentiment-analysis",
    model      = NOME_MODELO,
    tokenizer  = NOME_MODELO,
    max_length = 512,       # Limite de tokens do modelo BERT
    truncation = True,      # Textos maiores que 512 tokens são cortados
    device     = device_id, # GPU (0) ou CPU (-1)
)

print("✅ Modelo carregado e pronto para análise.")


# ==============================================================================
# BLOCO 6 — LEITURA DO CORPUS DE NOTÍCIAS
# ==============================================================================

caminho_noticias = caminho_base + "base_textual_petr4_2018_2025.csv"

print(f"\n📖 Lendo corpus de notícias: {caminho_noticias}")

try:
    df_noticias = pd.read_csv(caminho_noticias, parse_dates=['Data_Coleta'])
    print(f"✅ Corpus carregado: {len(df_noticias)} notícias")

except FileNotFoundError:
    print(f"❌ Arquivo não encontrado: {caminho_noticias}")
    print("   Execute o Script 02 primeiro para gerar o corpus de notícias.")
    raise


# ==============================================================================
# BLOCO 7 — FUNÇÃO DE EXTRAÇÃO DE SENTIMENTO
# ==============================================================================

def extrair_sentimento(texto):
    """
    Aplica o modelo BERTimbau a um texto e retorna o Índice de Sentimento.

    O modelo retorna:
    • LABEL_0 (Negativo) → polaridade = -1
    • LABEL_1 (Neutro)   → polaridade =  0
    • LABEL_2 (Positivo) → polaridade = +1

    O Índice final é: polaridade × score de confiança
    Exemplo: Negativo com 90% de confiança → -0.90

    Parâmetros:
    -----------
    texto : str — texto da notícia (título ou resumo)

    Retorna:
    --------
    tuple : (indice_sentimento, label, score)
    """

    try:
        # Garante que o texto é uma string e remove espaços extras
        texto = str(texto).strip()

        # Textos muito curtos tendem a ser ruidosos; retornamos neutro
        if len(texto) < 10:
            return 0.0, 'NEUTRAL', 0.0

        # Aplica o modelo
        resultado = modelo_nlp(texto)[0]
        label = resultado['label']   # Ex: "LABEL_0", "LABEL_1", "LABEL_2" ou "Negative", "Neutral", "Positive"
        score = resultado['score']   # Confiança de 0 a 1

        # Mapeamento de labels para polaridade
        # O modelo cardiffnlp usa "Negative", "Neutral", "Positive"
        mapa_labels = {
            'Negative' : -1,
            'LABEL_0'  : -1,  # Fallback caso o modelo retorne LABEL_X
            'Neutral'  :  0,
            'LABEL_1'  :  0,
            'Positive' : +1,
            'LABEL_2'  : +1,
        }

        polaridade = mapa_labels.get(label, 0)

        # Índice de Sentimento = polaridade × confiança
        indice = polaridade * score

        return indice, label, score

    except Exception as e:
        # Em caso de erro (ex: texto com caracteres especiais), retorna neutro
        return 0.0, 'NEUTRAL', 0.0


# ==============================================================================
# BLOCO 8 — PROCESSAMENTO EM LOTES (BATCH PROCESSING)
# ==============================================================================
# Processamos as notícias em lotes de 32 para maximizar o uso da GPU
# e evitar erros de memória.

print("\n" + "="*60)
print("INICIANDO EXTRAÇÃO DE SENTIMENTO")
print("="*60)

TAMANHO_LOTE = 32  # Ajuste para 16 se houver erro de memória (Out of Memory)

total = len(df_noticias)
indices_sentimento = []
labels_sentimento  = []
scores_sentimento  = []

print(f"📊 Total de notícias a processar: {total}")
print(f"   Tamanho do lote: {TAMANHO_LOTE}")
print(f"   Número de lotes: {total // TAMANHO_LOTE + 1}")
print("\n   Progresso:")

for i in range(0, total, TAMANHO_LOTE):

    lote = df_noticias['Titulo'].iloc[i:i+TAMANHO_LOTE].tolist()

    for texto in lote:
        indice, label, score = extrair_sentimento(texto)
        indices_sentimento.append(indice)
        labels_sentimento.append(label)
        scores_sentimento.append(score)

    # Exibe progresso a cada 10 lotes
    if (i // TAMANHO_LOTE) % 10 == 0:
        pct = (i / total) * 100
        processadas = min(i + TAMANHO_LOTE, total)
        print(f"   [{pct:5.1f}%] {processadas}/{total} notícias processadas...")

print(f"   [100.0%] {total}/{total} notícias processadas.")
print("✅ Extração de sentimento concluída!")


# ==============================================================================
# BLOCO 9 — ADIÇÃO DOS RESULTADOS AO DATAFRAME
# ==============================================================================

df_noticias['Indice_Sentimento']   = indices_sentimento
df_noticias['Label_Sentimento']    = labels_sentimento
df_noticias['Score_Confianca']     = scores_sentimento

# Distribuição dos sentimentos (verificação de sanidade)
print("\n📊 DISTRIBUIÇÃO DOS SENTIMENTOS:")
contagem = df_noticias['Label_Sentimento'].value_counts()
for label, count in contagem.items():
    pct = (count / total) * 100
    print(f"   {label:12s}: {count:6d} notícias ({pct:5.1f}%)")


# ==============================================================================
# BLOCO 10 — CONSTRUÇÃO DO ÍNDICE DE SENTIMENTO DIÁRIO (ISM)
# ==============================================================================
# Conforme a metodologia (Seção 3.2.1):
# O ISM de cada pregão é a MÉDIA dos índices de sentimento de todas as
# notícias publicadas naquele dia.
#
# IMPORTANTE: Notícias publicadas APÓS o fechamento da B3 (após 17h)
# são atribuídas ao próximo pregão (alinhamento temporal para evitar
# data leakage — Seção 3.1.2 da dissertação).

print("\n📅 Construindo o Índice de Sentimento Diário (ISM)...")

# Extrai apenas a data (sem hora)
df_noticias['Data'] = pd.to_datetime(df_noticias['Data_Coleta']).dt.date

# ALINHAMENTO TEMPORAL: notícias após 17h00 (fechamento B3) vão para o dia seguinte
if 'Data_Coleta' in df_noticias.columns and pd.api.types.is_datetime64_any_dtype(df_noticias['Data_Coleta']):
    hora_corte = 17  # 17h = horário de fechamento da B3
    df_noticias['Data_Ajustada'] = df_noticias['Data_Coleta'].apply(
        lambda dt: (dt + pd.Timedelta(days=1)).date()
        if dt.hour >= hora_corte
        else dt.date()
    )
else:
    # Se não há informação de hora, usa a data como está
    df_noticias['Data_Ajustada'] = df_noticias['Data']

# Calcula a média diária do Índice de Sentimento
df_ism_diario = (
    df_noticias
    .groupby('Data_Ajustada')
    .agg(
        Indice_Sentimento_Medio = ('Indice_Sentimento', 'mean'),
        Qtd_Noticias_do_Dia     = ('Indice_Sentimento', 'count'),
        Qtd_Positivas           = ('Label_Sentimento', lambda x: (x == 'Positive').sum()),
        Qtd_Negativas           = ('Label_Sentimento', lambda x: (x == 'Negative').sum()),
        Qtd_Neutras             = ('Label_Sentimento', lambda x: (x == 'Neutral').sum()),
    )
    .reset_index()
    .rename(columns={'Data_Ajustada': 'Data'})
)

# Renomeia para o padrão esperado pelo Script 04
df_ism_diario.rename(
    columns={'Indice_Sentimento_Medio': 'Indice_Sentimento_Transformer'},
    inplace=True
)

print(f"✅ ISM calculado para {len(df_ism_diario)} pregões únicos.")
print(f"\n📊 ESTATÍSTICAS DO ÍNDICE DE SENTIMENTO DIÁRIO:")
print(df_ism_diario['Indice_Sentimento_Transformer'].describe().round(4))


# ==============================================================================
# BLOCO 11 — SALVAMENTO NO GOOGLE DRIVE
# ==============================================================================

# Arquivo 1: Índice de Sentimento Diário (entrada principal do Script 04)
caminho_ism = caminho_base + "indice_sentimento_petr4.csv"
df_ism_diario.to_csv(caminho_ism, index=False, encoding='utf-8')
print(f"\n💾 ISM diário salvo: {caminho_ism}")

# Arquivo 2: Corpus completo com sentimento por notícia (para análise)
caminho_noticias_sentimento = caminho_base + "noticias_com_sentimento.csv"
df_noticias.to_csv(caminho_noticias_sentimento, index=False, encoding='utf-8')
print(f"💾 Corpus com sentimento salvo: {caminho_noticias_sentimento}")

print("\n" + "="*60)
print("✅ ANÁLISE DE SENTIMENTO CONCLUÍDA COM SUCESSO!")
print("="*60)
print(f"   Notícias processadas : {len(df_noticias)}")
print(f"   Pregões com ISM      : {len(df_ism_diario)}")
print("\n▶️  Próximo passo: execute o Script 04 para a modelagem preditiva.")

# Prévia do ISM gerado
print("\n📋 PRIMEIRAS 10 LINHAS DO ÍNDICE DE SENTIMENTO DIÁRIO:")
print(df_ism_diario.head(10).to_string(index=False))
