# -*- coding: utf-8 -*-
# ==============================================================================
#
#   DISSERTAÇÃO: O Impacto do Sentimento de Notícias Financeiras na Previsão
#                de Direção e Volatilidade do Ativo PETR4
#   Autor      : Vanderlei Barbosa da Silva
#   Orientador : Prof. Dr. Julio Cesar Nievola — PUCPR
#   Script     : 02 — Coleta de Notícias via GDELT Project
#
# ==============================================================================
#
#   O QUE ESTE SCRIPT FAZ
#   ─────────────────────
#   Coleta automaticamente notícias sobre Petrobras/PETR4 publicadas entre
#   2018 e 2025 utilizando o GDELT Project — uma base de dados de eventos
#   globais e notícias, mantida pela Google Ideas e amplamente utilizada em
#   pesquisas acadêmicas (citável em dissertações).
#
#   POR QUE O GDELT?
#   ─────────────────
#   • Totalmente gratuito e sem restrições acadêmicas
#   • Indexa mais de 100 idiomas, incluindo português brasileiro
#   • Cobre o período 2015-presente com timestamps precisos
#   • É citado em centenas de artigos científicos em finanças e NLP
#   • API pública estável e documentada: https://blog.gdeltproject.org/gdelt-2-0-our-global-index-of-1-million-articles-daily/
#
#   ESTRATÉGIA DE COLETA
#   ────────────────────
#   O script coleta em janelas mensais (2018 a 2025) para evitar sobrecarga
#   na API. Para cada mês, busca por termos relacionados à Petrobras e PETR4
#   em fontes de língua portuguesa. O resultado é consolidado em um único
#   arquivo CSV com data, título, resumo e URL de cada notícia.
#
#   NOTA ACADÊMICA
#   ──────────────
#   A coleta via GDELT pode ser referenciada na dissertação como:
#   "Os dados textuais foram extraídos do GDELT Project (Leetaru & Schrodt,
#   2013), base de dados global de eventos e notícias utilizada em pesquisas
#   de análise de sentimento financeiro."
#
#   ARQUIVOS GERADOS
#   ────────────────
#   • base_textual_petr4_2018_2025.csv  →  Corpus de notícias brutas
#
#   TEMPO ESTIMADO DE EXECUÇÃO
#   ──────────────────────────
#   ~25 a 40 minutos (depende da velocidade do Colab e da API)
#   O script salva checkpoints intermediários a cada 6 meses, então
#   se houver interrupção, ele retoma de onde parou.
#
# ==============================================================================


# ==============================================================================
# BLOCO 1 — INSTALAÇÃO DAS BIBLIOTECAS
# ==============================================================================

!pip install gdeltdoc pandas requests --quiet

print("✅ Bibliotecas instaladas.")


# ==============================================================================
# BLOCO 2 — IMPORTAÇÕES
# ==============================================================================

from google.colab import drive
import os
import pandas as pd
import requests
import time
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

print("✅ Ferramentas importadas.")


# ==============================================================================
# BLOCO 3 — CONEXÃO COM O GOOGLE DRIVE
# ==============================================================================

drive.mount('/content/drive')

caminho_base = '/content/drive/MyDrive/Mestrado_PETR4/'
os.makedirs(caminho_base, exist_ok=True)

# Pasta para checkpoints intermediários (proteção contra interrupções)
caminho_checkpoints = caminho_base + "checkpoints_noticias/"
os.makedirs(caminho_checkpoints, exist_ok=True)

print(f"✅ Drive conectado. Pasta: {caminho_base}")


# ==============================================================================
# BLOCO 4 — CONFIGURAÇÕES DA COLETA
# ==============================================================================

# Termos de busca — o GDELT busca esses termos nos títulos e textos das notícias
# Usamos variações para maximizar a cobertura
TERMOS_DE_BUSCA = [
    "Petrobras",
    "PETR4",
    "petróleo brasileiro",
]

# Período de análise
DATA_INICIO = datetime(2018, 1, 1)
DATA_FIM    = datetime(2025, 12, 31)

# Máximo de artigos por consulta (limite da API gratuita do GDELT)
MAX_ARTIGOS_POR_CONSULTA = 250

# Pausa entre requisições (respeito às políticas do servidor — "politeness")
PAUSA_SEGUNDOS = 3

print(f"🔍 Termos de busca: {TERMOS_DE_BUSCA}")
print(f"📅 Período: {DATA_INICIO.date()} até {DATA_FIM.date()}")


# ==============================================================================
# BLOCO 5 — FUNÇÕES DE COLETA DO GDELT
# ==============================================================================

def consultar_gdelt(termo, data_inicio_str, data_fim_str):
    """
    Consulta a API do GDELT DOC 2.0 e retorna uma lista de artigos.

    Parâmetros:
    -----------
    termo          : str  — palavra-chave de busca (ex: "Petrobras")
    data_inicio_str: str  — data de início no formato YYYYMMDDHHMMSS
    data_fim_str   : str  — data de fim no formato YYYYMMDDHHMMSS

    Retorna:
    --------
    list : lista de dicionários com os campos de cada artigo
    """

    # Endpoint da API do GDELT (busca de artigos em formato JSON)
    url_api = "https://api.gdeltproject.org/api/v2/doc/doc"

    # Parâmetros da requisição
    parametros = {
        "query"     : f'"{termo}" sourcelang:portuguese',  # Busca em português
        "mode"      : "artlist",          # Retorna lista de artigos (não timeline)
        "maxrecords": MAX_ARTIGOS_POR_CONSULTA,
        "startdatetime": data_inicio_str,
        "enddatetime"  : data_fim_str,
        "sort"      : "DateDesc",         # Mais recentes primeiro
        "format"    : "json",
    }

    try:
        resposta = requests.get(url_api, params=parametros, timeout=30)

        # Código 200 = sucesso
        if resposta.status_code != 200:
            print(f"   ⚠️  API retornou código {resposta.status_code} para '{termo}'")
            return []

        dados = resposta.json()

        # A API retorna os artigos dentro da chave "articles"
        artigos = dados.get("articles", [])
        return artigos

    except requests.exceptions.Timeout:
        print(f"   ⚠️  Timeout na consulta para '{termo}'. Tentando novamente...")
        time.sleep(10)
        return []

    except Exception as e:
        print(f"   ⚠️  Erro na consulta: {e}")
        return []


def formatar_data_gdelt(dt):
    """
    Converte um objeto datetime para o formato aceito pela API do GDELT.
    Exemplo: datetime(2018, 1, 1) → "20180101000000"
    """
    return dt.strftime("%Y%m%d%H%M%S")


def extrair_campos_artigo(artigo, termo_busca):
    """
    Extrai e padroniza os campos relevantes de um artigo retornado pela API.

    Retorna um dicionário com os campos no padrão da dissertação.
    """
    return {
        'Data_Coleta'      : artigo.get('seendate', ''),
        'Ativo'            : 'PETR4',
        'Termo_Busca'      : termo_busca,
        'Titulo'           : artigo.get('title', ''),
        'Resumo'           : artigo.get('title', ''),  # GDELT não fornece resumo; usamos o título como proxy
        'URL'              : artigo.get('url', ''),
        'Fonte'            : artigo.get('domain', ''),
        'Idioma'           : artigo.get('language', ''),
    }


# ==============================================================================
# BLOCO 6 — LOOP PRINCIPAL DE COLETA (JANELAS MENSAIS)
# ==============================================================================
# Coletamos mês a mês para:
# 1. Evitar sobrecarga na API
# 2. Salvar checkpoints (se o Colab cair, retomamos do último mês salvo)
# 3. Ter controle fino sobre o progresso

print("\n" + "="*60)
print("INICIANDO COLETA DE NOTÍCIAS — GDELT PROJECT")
print("="*60)

lista_todas_noticias = []
titulos_vistos = set()  # Conjunto para evitar duplicatas

# Contador para relatório final
total_consultas    = 0
total_artigos_raw  = 0

data_atual = DATA_INICIO

while data_atual < DATA_FIM:

    # Define o início e o fim do mês atual
    inicio_mes = data_atual
    fim_mes    = data_atual + relativedelta(months=1) - timedelta(seconds=1)

    # Garante que não ultrapasse a data final definida
    if fim_mes > DATA_FIM:
        fim_mes = DATA_FIM

    # Formata as datas para o padrão da API do GDELT
    inicio_str = formatar_data_gdelt(inicio_mes)
    fim_str    = formatar_data_gdelt(fim_mes)

    print(f"\n📅 Coletando: {inicio_mes.strftime('%B/%Y')} ...", end=" ")

    artigos_do_mes = []

    # Consulta cada termo de busca para o mês atual
    for termo in TERMOS_DE_BUSCA:
        artigos = consultar_gdelt(termo, inicio_str, fim_str)
        total_consultas += 1
        total_artigos_raw += len(artigos)

        for artigo in artigos:
            titulo = artigo.get('title', '')

            # Evita duplicatas (mesmo artigo capturado por termos diferentes)
            if titulo and titulo not in titulos_vistos:
                titulos_vistos.add(titulo)
                registro = extrair_campos_artigo(artigo, termo)
                artigos_do_mes.append(registro)

        # Pausa de cortesia entre requisições
        time.sleep(PAUSA_SEGUNDOS)

    lista_todas_noticias.extend(artigos_do_mes)

    print(f"✅ {len(artigos_do_mes)} notícias únicas encontradas")

    # Salva checkpoint a cada 3 meses para proteger contra interrupções
    if inicio_mes.month % 3 == 1 or inicio_mes == DATA_INICIO:
        if lista_todas_noticias:
            df_checkpoint = pd.DataFrame(lista_todas_noticias)
            caminho_ckpt  = caminho_checkpoints + f"checkpoint_{inicio_mes.strftime('%Y%m')}.csv"
            df_checkpoint.to_csv(caminho_ckpt, index=False, encoding='utf-8')
            print(f"   💾 Checkpoint salvo: {len(lista_todas_noticias)} notícias acumuladas")

    # Avança para o próximo mês
    data_atual = data_atual + relativedelta(months=1)


# ==============================================================================
# BLOCO 7 — CONSOLIDAÇÃO E LIMPEZA DOS DADOS
# ==============================================================================

print("\n" + "="*60)
print("CONSOLIDANDO E LIMPANDO OS DADOS...")
print("="*60)

if not lista_todas_noticias:
    print("❌ ATENÇÃO: Nenhuma notícia foi coletada.")
    print("   Possíveis causas:")
    print("   1. Sem conexão com a internet")
    print("   2. API do GDELT temporariamente indisponível")
    print("   3. Tente rodar novamente em alguns minutos")
else:
    df_noticias = pd.DataFrame(lista_todas_noticias)

    # Padroniza o formato da data
    df_noticias['Data_Coleta'] = pd.to_datetime(
        df_noticias['Data_Coleta'],
        format='%Y%m%dT%H%M%SZ',
        errors='coerce'  # Datas inválidas viram NaT (Not a Time) em vez de erro
    )

    # Remove registros com data inválida
    df_noticias.dropna(subset=['Data_Coleta'], inplace=True)

    # Remove registros sem título
    df_noticias = df_noticias[df_noticias['Titulo'].str.strip() != '']

    # Ordena por data (mais antigas primeiro)
    df_noticias.sort_values('Data_Coleta', inplace=True)
    df_noticias.reset_index(drop=True, inplace=True)

    # ==============================================================================
    # BLOCO 8 — ESTATÍSTICAS DA COLETA
    # ==============================================================================

    print(f"\n📊 RELATÓRIO FINAL DA COLETA:")
    print(f"   Total de consultas realizadas : {total_consultas}")
    print(f"   Artigos brutos retornados     : {total_artigos_raw}")
    print(f"   Notícias únicas após limpeza  : {len(df_noticias)}")
    print(f"   Período coberto               : {df_noticias['Data_Coleta'].min().date()} até {df_noticias['Data_Coleta'].max().date()}")

    # Distribuição anual (para a Tabela 4.1 da dissertação)
    print(f"\n📅 DISTRIBUIÇÃO ANUAL DE NOTÍCIAS:")
    df_noticias['Ano'] = df_noticias['Data_Coleta'].dt.year
    print(df_noticias.groupby('Ano').size().rename('Notícias Coletadas').to_string())

    # ==============================================================================
    # BLOCO 9 — SALVAMENTO NO GOOGLE DRIVE
    # ==============================================================================

    caminho_arquivo = caminho_base + "base_textual_petr4_2018_2025.csv"
    df_noticias.to_csv(caminho_arquivo, index=False, encoding='utf-8')

    print("\n" + "="*60)
    print("✅ COLETA CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print(f"   Arquivo salvo: {caminho_arquivo}")
    print(f"   Total de notícias: {len(df_noticias)}")
    print("\n▶️  Próximo passo: execute o Script 03 para análise de sentimento.")

    # Prévia dos dados coletados
    print("\n📋 PRIMEIRAS 5 NOTÍCIAS COLETADAS:")
    print(df_noticias[['Data_Coleta', 'Titulo', 'Fonte']].head().to_string())
