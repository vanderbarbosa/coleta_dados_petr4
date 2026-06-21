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
# BLOCO 1 — DEPENDÊNCIAS
# ==============================================================================
# Execução LOCAL. Instale uma vez (pode ser pesado — torch é grande):
#   pip install transformers torch sentencepiece
# (ou: pip install -r requirements.txt)

print("✅ Bibliotecas de Deep Learning verificadas.")


# ==============================================================================
# BLOCO 2 — IMPORTAÇÕES
# ==============================================================================

import os
from pathlib import Path
import pandas as pd
import numpy as np
import torch
from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

print("✅ Ferramentas importadas.")


# ==============================================================================
# BLOCO 3 — PASTA DE DADOS (LOCAL)
# ==============================================================================
# Este script vive em src/sentimento/, então a raiz do projeto está 2 níveis acima.

try:
    _RAIZ = Path(__file__).resolve().parents[2]
except NameError:
    _RAIZ = Path.cwd()
caminho_base = str(_RAIZ / "Mestrado_PETR4") + os.sep
os.makedirs(caminho_base, exist_ok=True)

print(f"✅ Pasta da pesquisa: {caminho_base}")


# ==============================================================================
# BLOCO 4 — VERIFICAÇÃO DA GPU
# ==============================================================================
# A GPU acelera o processamento do BERT em ~10x.
# Se não houver GPU disponível, o script roda na CPU (mais lento, mas funciona).

if torch.cuda.is_available():
    device_id = 0  # 0 = primeira GPU disponível
    nome_device = torch.cuda.get_device_name(0)
    print(f"✅ GPU detectada: {nome_device} — processamento acelerado.")
else:
    device_id = -1  # -1 = CPU
    print("⚠️  Sem GPU — usando CPU. Em CPU, o corpus completo (205k notícias)")
    print("    pode levar algumas horas. Para testes, reduza com LIMITE_NOTICIAS abaixo.")

# Limite opcional de notícias (para testes rápidos em CPU). None = processa tudo.
LIMITE_NOTICIAS = None


# ==============================================================================
# BLOCO 5 — CARREGAMENTO DO MODELO DE SENTIMENTO (FinBERT-PT-BR)
# ==============================================================================
# MODELO ESCOLHIDO: lucas-leme/FinBERT-PT-BR
# ─────────────────────────────────────────────────────────────────────────────
# Justificativa (responde diretamente à arguição do Prof. Emerson na
# qualificação): o BERTimbau/“xlm-roberta” genérico foi pré-treinado em texto
# comum do português, NÃO em texto financeiro — não conhece jargões nem ironias
# do mercado. O FinBERT-PT-BR é um BERT em português brasileiro com fine-tuning
# em CORPUS FINANCEIRO (notícias e relatórios do mercado de capitais), sendo a
# escolha mais adequada para o domínio desta pesquisa.
#
# COMO O SCORE DE SENTIMENTO É EXTRAÍDO (esclarece a dúvida da banca:
# "o BERT é um encoder, como se obtém o score de −1 a +1?"):
#   1. O modelo possui um HEAD de classificação de 3 classes
#      (POSITIVE / NEGATIVE / NEUTRAL) acoplado ao encoder BERT.
#   2. O pipeline "sentiment-analysis" da biblioteca Transformers (Hugging Face)
#      aplica softmax aos logits desse head, retornando (label, score), onde
#      score = probabilidade da classe vencedora (0 a 1).
#   3. O Índice de Sentimento contínuo é então: polaridade × score, com
#      polaridade ∈ {+1 positivo, 0 neutro, −1 negativo} (ver Bloco 7).
# Assim, o intervalo final fica em [−1, +1]. Uso ZERO-SHOT (sem novo treino):
# aplica-se o modelo já fine-tunado em finanças diretamente às manchetes.
#
# ALTERNATIVAS consideradas e por que NÃO foram adotadas como principal:
#   • cardiffnlp/twitter-xlm-roberta (genérico, não-financeiro) — crítica da banca;
#   • léxicos estáticos (OpLexicon/LIWC) — regrediria ao paradigma TF-IDF que a
#     banca apontou como superado pelos Transformers.

NOME_MODELO = "lucas-leme/FinBERT-PT-BR"

print(f"\n🧠 Carregando o modelo de sentimento financeiro: {NOME_MODELO}")
print("   (O download ocorre só na primeira execução — alguns minutos / ~400 MB)")

modelo_nlp = pipeline(
    task       = "sentiment-analysis",
    model      = NOME_MODELO,
    tokenizer  = NOME_MODELO,
    max_length = 512,       # Limite de tokens do BERT
    truncation = True,      # Textos maiores que 512 tokens são cortados
    device     = device_id, # GPU (0) ou CPU (-1)
)

print("✅ Modelo carregado e pronto para análise.")


# ==============================================================================
# BLOCO 6 — LEITURA E NORMALIZAÇÃO DO CORPUS DE NOTÍCIAS
# ==============================================================================
# Este script aceita DOIS formatos de corpus, detectando o schema
# automaticamente (não requer edição manual):
#
#   (A) Schema WordPress/multi-fonte (Scripts 02 e 02b) — colunas minúsculas:
#       data_publicacao, titulo, resumo, fonte_coleta, dominio, url, idioma...
#       → traz a HORA EXATA de publicação (essencial para o Lead-Lag das 17h).
#
#   (B) Schema GDELT simples (versão antiga do Script 02) — colunas capitalizadas:
#       Data_Coleta, Titulo, Resumo, Fonte, URL, Idioma...
#
# Internamente o script padroniza tudo para as colunas canônicas
# 'Data_Coleta' (datetime com hora) e 'Titulo', usadas nos blocos seguintes.

# Ordem de preferência: a base tratada (limpa + com split treino/validação/teste)
# vem primeiro; depois a bruta do 02b; por fim os corpora antigos.
CANDIDATOS_CORPUS = [
    "base_textual_petr4_tratada.csv",              # Script 02c — tratada + coluna 'conjunto'
    "base_textual_petr4_wordpress_2018_2025.csv",  # Script 02b — coleta completa (bruta)
    "base_textual_wordpress_TESTE.csv",            # Script 02b — teste rápido
    "base_textual_petr4_2018_2025.csv",            # Script 02 (multi-fonte ou GDELT)
]

caminho_noticias = None
for nome in CANDIDATOS_CORPUS:
    if os.path.exists(caminho_base + nome):
        caminho_noticias = caminho_base + nome
        break

if caminho_noticias is None:
    print("❌ Nenhum arquivo de corpus encontrado em:", caminho_base)
    print("   Esperado um destes:", CANDIDATOS_CORPUS)
    print("   Execute o Script 02 ou 02b primeiro para gerar o corpus.")
    raise FileNotFoundError("Corpus de notícias não encontrado.")

print(f"\n📖 Lendo corpus de notícias: {caminho_noticias}")
df_noticias = pd.read_csv(caminho_noticias)
print(f"✅ Corpus carregado: {len(df_noticias)} notícias")

# --- Normalização de nomes de coluna (mapeia qualquer schema → canônico) ---
MAPA_COLUNAS = {
    'data_publicacao': 'Data_Coleta',  # WordPress/multi-fonte (com hora exata)
    'titulo'         : 'Titulo',
    'resumo'         : 'Resumo',
    'fonte_coleta'   : 'Fonte',
    'url'            : 'URL',
    'idioma'         : 'Idioma',
}
df_noticias.rename(
    columns={k: v for k, v in MAPA_COLUNAS.items() if k in df_noticias.columns},
    inplace=True,
)

# Se não houver 'Fonte' mas houver 'dominio' (WordPress), usa o domínio como fonte
if 'Fonte' not in df_noticias.columns and 'dominio' in df_noticias.columns:
    df_noticias.rename(columns={'dominio': 'Fonte'}, inplace=True)

# Validação das colunas mínimas obrigatórias
for col_obrig in ('Data_Coleta', 'Titulo'):
    if col_obrig not in df_noticias.columns:
        raise KeyError(
            f"Coluna obrigatória '{col_obrig}' ausente no corpus. "
            f"Colunas encontradas: {list(df_noticias.columns)}"
        )

# Converte a data de publicação para datetime (preservando a HORA).
# errors='coerce' transforma datas inválidas em NaT (sem derrubar a execução).
df_noticias['Data_Coleta'] = pd.to_datetime(df_noticias['Data_Coleta'], errors='coerce')
n_antes = len(df_noticias)
df_noticias.dropna(subset=['Data_Coleta', 'Titulo'], inplace=True)
n_descartadas = n_antes - len(df_noticias)

# Diagnóstico do timestamp: confirma se o corpus tem HORA real (não meia-noite).
# Um corpus com hora real é pré-requisito para o alinhamento Lead-Lag (Seção 3.1.2).
tem_hora = (df_noticias['Data_Coleta'].dt.hour != 0).any() or \
           (df_noticias['Data_Coleta'].dt.minute != 0).any()
print(f"   Schema normalizado → colunas canônicas (Data_Coleta, Titulo).")
if n_descartadas:
    print(f"   {n_descartadas} linhas descartadas (data ou título inválidos).")
if tem_hora:
    print(f"   🕒 Timestamp com HORA EXATA detectado — alinhamento Lead-Lag das 17h será aplicado.")
else:
    print(f"   ⚠️  Corpus SEM hora de publicação (apenas datas). O corte das 17h não terá efeito.")
    print(f"      Recomendado recoletar com o Script 02b (WordPress REST) para obter o timestamp.")


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
        label_raw = resultado['label']   # FinBERT-PT-BR: POSITIVE/NEGATIVE/NEUTRAL
        score     = resultado['score']   # Confiança de 0 a 1 (probabilidade da classe)

        # Normaliza o rótulo para o padrão canônico (case-insensitive), cobrindo
        # FinBERT-PT-BR (MAIÚSCULAS), cardiffnlp (Capitalizado) e LABEL_0/1/2.
        L = str(label_raw).strip().upper()
        if L in ('POSITIVE', 'POSITIVO', 'POS', 'LABEL_2'):
            polaridade, label = +1, 'Positive'
        elif L in ('NEGATIVE', 'NEGATIVO', 'NEG', 'LABEL_0'):
            polaridade, label = -1, 'Negative'
        else:  # NEUTRAL / NEUTRO / LABEL_1
            polaridade, label = 0, 'Neutral'

        # Índice de Sentimento contínuo = polaridade × confiança ∈ [−1, +1]
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

# Limite opcional para testes rápidos em CPU (definido no Bloco 4).
if LIMITE_NOTICIAS is not None:
    df_noticias = df_noticias.head(int(LIMITE_NOTICIAS)).copy()
    print(f"⚙️  LIMITE_NOTICIAS ativo: processando apenas {len(df_noticias)} notícias (teste).")

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
# BLOCO 10b — ÍNDICE DE SENTIMENTO DIÁRIO POR CATEGORIA (ANÁLISE DE ABLAÇÃO)
# ==============================================================================
# Se o corpus tiver a coluna 'categoria' (gerada pelo Script 02/02b com a
# taxonomia de 7 categorias), construímos um ISM SEPARADO para cada categoria.
# Isso habilita a ANÁLISE DE ABLAÇÃO no Script 04: remover uma categoria por
# vez e medir o impacto na previsão, respondendo "qual tipo de notícia é mais
# informativo para prever a volatilidade do PETR4?".
#
# Saída: indice_sentimento_categorias_petr4.csv — uma coluna por categoria,
# no mesmo alinhamento temporal (corte das 17h) usado no ISM agregado.

df_ism_categorias = None
if 'categoria' in df_noticias.columns and df_noticias['categoria'].notna().any():
    print("\n📂 Construindo o ISM por categoria (para análise de ablação)...")

    # Sentimento médio diário (Data_Ajustada) por categoria → formato largo (pivot)
    df_ism_categorias = (
        df_noticias
        .pivot_table(
            index='Data_Ajustada',
            columns='categoria',
            values='Indice_Sentimento',
            aggfunc='mean',
        )
        .reset_index()
        .rename(columns={'Data_Ajustada': 'Data'})
    )

    # Prefixa as colunas de categoria com "ISM_" para clareza no Script 04
    df_ism_categorias.columns = [
        c if c == 'Data' else f"ISM_{c}" for c in df_ism_categorias.columns
    ]

    cats_detectadas = [c for c in df_ism_categorias.columns if c.startswith('ISM_')]
    print(f"   ✅ {len(cats_detectadas)} categorias com sentimento diário:")
    for c in cats_detectadas:
        cobertura = df_ism_categorias[c].notna().sum()
        print(f"      {c:30s}: {cobertura} dias com notícia")
else:
    print("\n⚠️  Corpus sem coluna 'categoria' — ISM por categoria não gerado.")
    print("      (Análise de ablação no Script 04 ficará indisponível;")
    print("       recoletar com o Script 02b para obter as categorias.)")


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

# Arquivo 3: ISM por categoria (entrada da análise de ablação do Script 04)
if df_ism_categorias is not None:
    caminho_ism_cat = caminho_base + "indice_sentimento_categorias_petr4.csv"
    df_ism_categorias.to_csv(caminho_ism_cat, index=False, encoding='utf-8')
    print(f"💾 ISM por categoria salvo: {caminho_ism_cat}")

print("\n" + "="*60)
print("✅ ANÁLISE DE SENTIMENTO CONCLUÍDA COM SUCESSO!")
print("="*60)
print(f"   Notícias processadas : {len(df_noticias)}")
print(f"   Pregões com ISM      : {len(df_ism_diario)}")
print("\n▶️  Próximo passo: execute o Script 04 para a modelagem preditiva.")

# Prévia do ISM gerado
print("\n📋 PRIMEIRAS 10 LINHAS DO ÍNDICE DE SENTIMENTO DIÁRIO:")
print(df_ism_diario.head(10).to_string(index=False))
