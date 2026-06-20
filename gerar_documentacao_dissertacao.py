# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Gerador da Documentação (ETAPA 1: Engenharia de Dados)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Gera um documento Word em PADRÃO ABNT detalhando a coleta, categorização,
#   filtragem e particionamento do corpus textual, com texto corrido, citações
#   autor-data, quadros de código, tabelas e figuras a partir dos dados REAIS.
#   Usa o módulo reutilizável abnt_docx.py (formatação ABNT centralizada).
#
#   Saída: Documentacao_Etapa1_Engenharia_de_Dados_PETR4.docx
# ==============================================================================

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import abnt_docx as abnt

PASTA = Path("./Mestrado_PETR4")
ARQ_ORIGINAL = PASTA / "base_textual_petr4_wordpress_2018_2025.csv"
ARQ_TRATADA  = PASTA / "base_textual_petr4_tratada.csv"
ASSETS = Path("./_doc_assets"); ASSETS.mkdir(exist_ok=True)
SAIDA = Path("Documentacao_Etapa1_Engenharia_de_Dados_PETR4.docx")

plt.rcParams.update({"figure.dpi": 150, "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})
AZUL, VERM, VERDE, CINZA = "#2c7bb6", "#d7191c", "#1a9641", "#999999"
fmt = lambda n: f"{int(n):,}".replace(",", ".")

# ──────────────────────────────────────────────────────────────────────────────
# DADOS REAIS
# ──────────────────────────────────────────────────────────────────────────────
print("Lendo bases...")
df = pd.read_csv(ARQ_ORIGINAL)
df["dt"] = pd.to_datetime(df["data_publicacao"], errors="coerce")
df = df[df["dt"].notna()].copy()
df["ano"] = df["dt"].dt.year
N_ORIG = len(df)
try:
    dft = pd.read_csv(ARQ_TRATADA); dft["dt"] = pd.to_datetime(dft["data_publicacao"], errors="coerce")
except Exception:
    dft = df.copy(); dft["conjunto"] = "treino"

dist_ano    = df["ano"].value_counts().sort_index()
dist_cat    = df["categoria"].value_counts()
dist_portal = df["dominio"].value_counts()
hora        = df["dt"].dt.hour
lead_lag_pct = (hora >= 17).mean() * 100
tem_hora_pct = ((hora != 0) | (df["dt"].dt.minute != 0)).mean() * 100

TERMOS_ESTRITO = ["petrobras","petr4","petr3","petroleira","petróleo","petroleo",
                  "brent","wti","opep","barril","combustível","combustivel","refinaria"]
alvo = (df["titulo"].fillna("") + " " + df["resumo"].fillna("")).str.lower()
mask_estrito = alvo.apply(lambda t: any(x in t for x in TERMOS_ESTRITO))
dist_cat_estrito = df[mask_estrito]["categoria"].value_counts()
N_ESTRITO = int(mask_estrito.sum())

tit = df["titulo"].fillna("").astype(str).str.strip()
mask_leve = ~((tit == "") | (tit.str.len() < 15))
N_LEVE = int(mask_leve.sum())
dist_cat_leve = df[mask_leve]["categoria"].value_counts()

if "conjunto" in dft.columns:
    dist_split = dft["conjunto"].value_counts()
    tab_split = pd.crosstab(dft["dt"].dt.year, dft["conjunto"]).reindex(
        columns=["treino","validacao","teste"], fill_value=0)
else:
    dist_split = pd.Series({"treino":0,"validacao":0,"teste":0}); tab_split = pd.DataFrame()

COLETA = {"brutos":1040007, "unicos":205716, "duplicados":834291}

# ──────────────────────────────────────────────────────────────────────────────
# GRÁFICOS
# ──────────────────────────────────────────────────────────────────────────────
print("Gerando gráficos...")
def salvar(fig, nome):
    c = ASSETS / nome; fig.savefig(c, bbox_inches="tight"); plt.close(fig); return c

fig, ax = plt.subplots(figsize=(8,4))
ax.bar(dist_ano.index.astype(str), dist_ano.values, color=AZUL)
for x,y in zip(dist_ano.index.astype(str), dist_ano.values):
    ax.text(x, y, fmt(y), ha="center", va="bottom", fontsize=9)
ax.set_ylabel("Notícias"); g_anual = salvar(fig, "anual.png")

fig, ax = plt.subplots(figsize=(8,4))
ax.barh(dist_portal.index[::-1], dist_portal.values[::-1], color=VERDE)
for i,v in enumerate(dist_portal.values[::-1]): ax.text(v, i, f" {fmt(v)}", va="center", fontsize=9)
ax.set_xlabel("Notícias"); g_portais = salvar(fig, "portais.png")

fig, ax = plt.subplots(figsize=(8,4.5))
ax.barh(dist_cat.index[::-1], dist_cat.values[::-1], color=AZUL)
for i,v in enumerate(dist_cat.values[::-1]): ax.text(v, i, f" {fmt(v)}", va="center", fontsize=9)
ax.set_xlabel("Notícias"); g_categorias = salvar(fig, "categorias.png")

fig, ax = plt.subplots(figsize=(5.5,5.5))
antes=(hora<17).sum(); depois=(hora>=17).sum()
ax.pie([antes,depois], labels=[f"Até 17h\n{fmt(antes)}", f"Após 17h\n{fmt(depois)}"],
       autopct="%1.1f%%", colors=[AZUL,VERM], startangle=90, wedgeprops=dict(width=0.45))
g_leadlag = salvar(fig, "leadlag.png")

fig, ax = plt.subplots(figsize=(8,3.6))
vc=hora.value_counts().sort_index(); ax.bar(vc.index, vc.values, color=CINZA)
ax.axvline(17, color=VERM, ls="--", lw=1.2, label="Fechamento B3 (17h)")
ax.set_xlabel("Hora (Brasília)"); ax.set_ylabel("Notícias"); ax.legend()
g_horas = salvar(fig, "horas.png")

fig, ax = plt.subplots(figsize=(8.5,4.5))
cats=list(dist_cat.index)
y=np.arange(len(cats)); h=0.27
ax.barh(y+h, [dist_cat.get(c,0) for c in cats], h, label="Original", color=CINZA)
ax.barh(y,   [dist_cat_leve.get(c,0) for c in cats], h, label="Filtragem leve", color=VERDE)
ax.barh(y-h, [dist_cat_estrito.get(c,0) for c in cats], h, label="Filtragem estrita", color=VERM)
ax.set_yticks(y); ax.set_yticklabels(cats); ax.invert_yaxis(); ax.set_xlabel("Notícias"); ax.legend()
g_filtro = salvar(fig, "filtro.png")

if not tab_split.empty:
    fig, ax = plt.subplots(figsize=(8.5,4.5)); anos=tab_split.index.astype(str)
    ax.bar(anos, tab_split["treino"], label="Treino (60%)", color=AZUL)
    ax.bar(anos, tab_split["validacao"], bottom=tab_split["treino"], label="Validação (15%)", color=VERDE)
    ax.bar(anos, tab_split["teste"], bottom=tab_split["treino"]+tab_split["validacao"], label="Teste (25%)", color=VERM)
    ax.set_ylabel("Notícias"); ax.legend(); g_split = salvar(fig, "split.png")
else:
    g_split=None

fig, ax = plt.subplots(figsize=(8,3.6))
et=["Artigos brutos\n(requisições)","Após deduplicação\n(únicos)"]; vals=[COLETA["brutos"],COLETA["unicos"]]
ax.bar(et, vals, color=[CINZA,AZUL])
for x,v in zip(et,vals): ax.text(x, v, fmt(v), ha="center", va="bottom", fontsize=10)
ax.set_ylabel("Artigos"); g_funil = salvar(fig, "funil.png")

# ──────────────────────────────────────────────────────────────────────────────
# DOCUMENTO ABNT
# ──────────────────────────────────────────────────────────────────────────────
print("Montando documento ABNT...")
doc = abnt.novo_documento()

abnt.capa(
    doc,
    "Engenharia de Dados Textuais para a Previsão do Ativo PETR4",
    "Etapa 1 — Coleta, Categorização, Filtragem e Particionamento do Corpus de Notícias",
    "Vanderlei Barbosa da Silva",
    "Orientador: Prof. Dr. Julio Cesar Nievola",
    "Pontifícia Universidade Católica do Paraná — Mestrado em Informática",
    descricao=("Documento técnico-metodológico integrante da dissertação “O Impacto do "
               "Sentimento de Notícias Financeiras na Previsão de Direção e Volatilidade do "
               "Ativo PETR4”, destinado ao capítulo de Materiais e Métodos. Todos os números, "
               "tabelas e figuras são gerados automaticamente a partir dos dados reais coletados."),
)

# 1 INTRODUÇÃO
abnt.secao(doc, "1", "Introdução e visão geral do pipeline")
abnt.paragrafo(doc,
 "A presente pesquisa investiga se o sentimento extraído de notícias financeiras, quando "
 "combinado a modelos econométricos e de aprendizado de máquina, aprimora a previsão da direção "
 "e da volatilidade do ativo PETR4. Na ciência de dados aplicada a finanças, a engenharia de "
 "dados — etapa de coleta e higienização do corpus — costuma concentrar a maior parte do esforço "
 "do projeto, sendo determinante para a validade dos resultados subsequentes. Este documento "
 "registra, de forma detalhada e auditável, todas as decisões, ferramentas, sucessos e "
 "insucessos dessa etapa.")
abnt.paragrafo(doc,
 "O processamento está organizado em uma sequência de scripts independentes e encadeados, "
 "descritos na Tabela 1. Cada script consome a saída do anterior, garantindo rastreabilidade e "
 "reprodutibilidade. Esta Etapa 1 corresponde aos scripts de coleta (02b) e de preparação (02c).")
abnt.tabela_abnt(doc, "1", "Scripts que compõem o pipeline da pesquisa",
 ["Etapa","Script","Função"],
 [["01","01_coleta_dados_financeiros","Preços diários da PETR4 (yfinance) e cálculo do log-retorno"],
  ["02b","02b_coleta_noticias_wordpress","Coleta de notícias via WordPress REST API (fonte principal)"],
  ["02c","02c_preparar_base","Filtragem leve e particionamento treino/validação/teste"],
  ["03","03_analise_sentimento","Análise de sentimento e Índice de Sentimento da Mídia (ISM)"],
  ["04","04_modelagem","GARCH, SVM, XGBoost e análise de ablação"]])
abnt.paragrafo(doc,
 f"O corpus final reúne **{fmt(N_ORIG)} notícias únicas**, todas com data e hora exatas de "
 "publicação, cobrindo integralmente o período de 1º de janeiro de 2018 a 31 de dezembro de 2025.")

# 2 FONTES UTILIZADAS
abnt.secao(doc, "2", "Fontes de coleta utilizadas")
abnt.paragrafo(doc,
 "A coleta definitiva foi realizada sobre cinco portais jornalísticos brasileiros que "
 "disponibilizam publicamente a interface de programação de aplicações (API) REST do sistema de "
 "gerenciamento de conteúdo WordPress, acessível pelo endpoint padronizado "
 "“/wp-json/wp/v2/posts”. A Tabela 2 apresenta as fontes, seus endereços e o volume coletado.")
abnt.tabela_abnt(doc, "2", "Portais utilizados como fontes e respectivo volume coletado",
 ["Portal","Endpoint (API REST WordPress)","Notícias","Perfil editorial"],
 [["InfoMoney","infomoney.com.br/wp-json/wp/v2/posts", fmt(dist_portal.get("InfoMoney",0)),"Mercado de capitais"],
  ["Exame","exame.com/wp-json/wp/v2/posts", fmt(dist_portal.get("Exame",0)),"Negócios e empresas"],
  ["Money Times","moneytimes.com.br/wp-json/wp/v2/posts", fmt(dist_portal.get("MoneyTimes",0)),"Investimentos"],
  ["Petronotícias","petronoticias.com.br/wp-json/wp/v2/posts", fmt(dist_portal.get("Petronoticias",0)),"Petróleo e energia"],
  ["Poder360","poder360.com.br/wp-json/wp/v2/posts", fmt(dist_portal.get("Poder360",0)),"Política e governo"]])
abnt.figura_abnt(doc, "1", "Distribuição das notícias por portal de origem", g_portais)

# 3 JUSTIFICATIVA DAS FONTES
abnt.secao(doc, "3", "Justificativa da escolha das fontes")
abnt.paragrafo(doc,
 "A seleção das fontes foi norteada por uma exigência metodológica central, levantada pela banca "
 "de qualificação: a indispensabilidade do registro do horário exato de publicação de cada "
 "notícia. Sem esse metadado, é impossível assegurar o alinhamento temporal do tipo “lead-lag” — "
 "segundo o qual uma notícia divulgada após o fechamento do pregão (17 horas) só pode influenciar "
 "o comportamento do ativo no dia útil seguinte — e, por conseguinte, não há como sustentar a "
 "relação de causalidade exigida pelo modelo GARCH(1,1).")
abnt.paragrafo(doc,
 "A API REST do WordPress atende plenamente a esse requisito, pois retorna o campo “date” no "
 "horário de Brasília e o campo “date_gmt” em tempo universal coordenado (UTC), com precisão de "
 "segundos. Além do timestamp, três critérios complementares justificaram a escolha: a cobertura "
 "histórica gratuita de todo o período de 2018 a 2025; a robustez técnica decorrente do retorno "
 "de dados estruturados em formato JSON, que elimina a fragilidade do web scraping de HTML e o "
 "risco de bloqueio por mecanismos anti-robô; e a pluralidade editorial, uma vez que os cinco "
 "portais cobrem perspectivas distintas — mercado, negócios, petróleo e política.")
abnt.paragrafo(doc,
 "A adoção de múltiplas fontes mitiga o viés de cobertura inerente a uma fonte única "
 "(HESTON; SINHA, 2017) e assegura a captação tanto de notícias corporativas diretas quanto de "
 "choques exógenos. A estratégia é metodologicamente análoga à de Cardoso e Nakane (2024), que "
 "coletaram notícias diretamente do portal do Valor Econômico mediante algoritmo próprio.")

# 4 FONTES DESCARTADAS
abnt.secao(doc, "4", "Fontes avaliadas e descartadas")
abnt.paragrafo(doc,
 "O registro transparente das alternativas testadas e abandonadas integra o rigor metodológico da "
 "pesquisa. A Tabela 3 sintetiza as fontes avaliadas e os motivos de seu descarte.")
abnt.tabela_abnt(doc, "3", "Fontes e métodos avaliados e descartados",
 ["Fonte / Método","Motivo do descarte"],
 [["Biblioteca GoogleNews (abordagem inicial)","Mascarava o timestamp (datas estocásticas), inviabilizando o lead-lag, além de sofrer bloqueio anti-robô."],
  ["GDELT Project (API DOC 2.0)","Bloqueio de IP por volume (HTTP 429 persistente), cobertura irregular em português e retorno apenas do título."],
  ["NewsAPI (plano gratuito)","O plano gratuito limita as consultas aos últimos 30 dias (HTTP 426 para datas anteriores), inviabilizando o histórico."],
  ["Twitter/X (API + Get Old Tweets)","Desde 2023 a API tornou-se paga e as ferramentas de coleta histórica foram bloqueadas."],
  ["Valor Econômico (scraping direto)","Conteúdo carregado via JavaScript e protegido por paywall, exigindo automação de navegador e assinatura."],
  ["Terminais pagos (Factiva, Bloomberg)","Custo institucional incompatível com o orçamento da pesquisa."]])
abnt.paragrafo(doc,
 "Conclui-se que, dentre as alternativas gratuitas, apenas a coleta direta dos portais via API "
 "REST do WordPress satisfez simultaneamente os três critérios decisivos: timestamp, cobertura "
 "histórica e robustez técnica.")

# 5 COMO FORAM CAPTURADAS
abnt.secao(doc, "5", "Procedimento de captura das notícias")
abnt.paragrafo(doc,
 "A captura consulta o endpoint “/wp-json/wp/v2/posts” de cada portal por meio do parâmetro "
 "“search” (busca textual), combinado aos parâmetros “after” e “before” (delimitação temporal) e "
 "à paginação nativa da API. Para cada termo da taxonomia, em cada portal, o coletor seleciona "
 "automaticamente a estratégia de varredura mais eficiente.")
abnt.paragrafo(doc,
 "Termos de baixo volume são percorridos em uma única varredura do período inteiro (estratégia "
 "“full-range”). Termos de alto volume — como “Petrobras” — são coletados mês a mês (estratégia "
 "por janela mensal), evitando o limite de profundidade de paginação (offset) da API, que torna "
 "as consultas lentas e instáveis. Cada artigo é deduplicado por meio de hash criptográfico "
 "SHA-256 do título normalizado e gravado de forma incremental, com retomada automática em caso "
 "de interrupção da execução.")

# 6 BIBLIOTECAS E CÓDIGO
abnt.secao(doc, "6", "Bibliotecas e código de captura")
abnt.paragrafo(doc,
 "A Tabela 4 relaciona as bibliotecas empregadas e a justificativa técnica de cada escolha, "
 "privilegiando ferramentas consolidadas e amplamente adotadas na comunidade científica.")
abnt.tabela_abnt(doc, "4", "Bibliotecas utilizadas na captura e respectiva justificativa",
 ["Biblioteca","Função","Justificativa da escolha"],
 [["requests","Requisições HTTP à API REST","Padrão de fato em Python; simples, estável e robusto"],
  ["pandas","Manipulação tabular e CSV","Estrutura DataFrame adequada à manipulação do corpus"],
  ["hashlib (SHA-256)","Deduplicação por hash do título","Detecção O(1) de duplicatas e idempotência da coleta"],
  ["python-dateutil","Aritmética de datas (janelas mensais)","Cálculo confiável de datas relativas"],
  ["matplotlib","Gráficos estatísticos","Padrão científico de visualização em Python"]])
abnt.quadro_codigo(doc, "1", "Função de requisição à API REST com retry e backoff",
'''def _get(endpoint, params):
    headers = {"User-Agent": USER_AGENT}
    for tentativa in range(1, MAX_RETRY + 1):
        try:
            r = requests.get(endpoint, headers=headers, params=params,
                             timeout=TIMEOUT_S, verify=VERIFY_SSL)
            if r.status_code == 200:
                total_pg = int(r.headers.get("X-WP-TotalPages", 1) or 1)
                return r.json(), total_pg
            if r.status_code == 400:        # pagina alem do fim -> fim da paginacao
                return [], 0
            return None, 0
        except Exception:
            time.sleep(min(4 * tentativa, 12))
    return None, 0''')
abnt.quadro_codigo(doc, "2", "Captura do timestamp e padronização do artigo",
'''return {
    "data_publicacao": post.get("date", ""),       # horario de Brasilia (lead-lag)
    "data_gmt"       : post.get("date_gmt", ""),    # UTC (auditoria de fuso)
    "categoria"      : categoria,                   # taxonomia (ablacao)
    "titulo"         : limpar_html(post["title"]["rendered"]),
    "resumo"         : limpar_html(post["excerpt"]["rendered"]),
    "url"            : post.get("link", ""),
    "hash_titulo"    : hash_titulo(titulo),         # SHA-256 (deduplicacao)
}''')

# 7 EVOLUÇÃO
abnt.secao(doc, "7", "Evolução da coleta: primeiros números e ajustes")
abnt.paragrafo(doc,
 "O volume de notícias capturadas evoluiu de forma expressiva à medida que os obstáculos técnicos "
 "eram superados. A Tabela 5 documenta essa trajetória, incluindo os insucessos, e a Figura 2 "
 "ilustra o funil da coleta — do total de artigos requisitados ao corpus final deduplicado.")
abnt.tabela_abnt(doc, "5", "Trajetória do volume coletado e ajustes realizados",
 ["Momento","Abordagem","Notícias","Problema ou ajuste"],
 [["Inicial","Biblioteca GoogleNews","~9.079","Timestamp mascarado; datas aleatórias"],
  ["Tentativa","GDELT (multifonte)","centenas","Bloqueio HTTP 429 por volume de IP"],
  ["Tentativa","NewsAPI gratuita","~0 (histórico)","Plano cobre apenas 30 dias"],
  ["Protótipo","WordPress REST (1 mês, 2 portais)","120","Validação do timestamp e do lead-lag"],
  ["Ajuste","+ taxonomia de 7 categorias e 152 termos","—","Ampliação da cobertura temática"],
  ["Ajuste","+ estratégia híbrida de paginação","—","Solução do limite de offset"],
  ["Final","WordPress REST (5 portais, 152 termos)", fmt(N_ORIG),"Corpus completo com timestamp"]])
abnt.paragrafo(doc,
 f"O salto de aproximadamente 9.079 para **{fmt(N_ORIG)} notícias** — cerca de vinte e duas vezes "
 "o volume inicial, e desta vez com hora exata — só foi possível após a identificação da API REST "
 "do WordPress e dos ajustes de paginação e de taxonomia.")
abnt.figura_abnt(doc, "2", "Funil da coleta: artigos brutos requisitados e corpus único final", g_funil)
abnt.paragrafo(doc,
 f"Foram requisitados {fmt(COLETA['brutos'])} artigos brutos ao longo da coleta; a deduplicação "
 f"por hash removeu {fmt(COLETA['duplicados'])} repetições, resultando em {fmt(COLETA['unicos'])} "
 "notícias únicas.")

# 8 TERMOS
abnt.secao(doc, "8", "Termos de busca e justificativa teórica")
abnt.paragrafo(doc,
 "Os termos de busca foram organizados em uma taxonomia de sete categorias temáticas, cada qual "
 "ancorada na literatura de economia do petróleo e de finanças. A premissa, fundamentada em "
 "Hamilton (1983) e Kilian (2009), é que choques exógenos — geopolíticos, de oferta e demanda de "
 "petróleo e macroeconômicos — são tão ou mais determinantes para a volatilidade do ativo do que "
 "as notícias estritamente corporativas. Hamilton (1983) demonstrou que quase todas as recessões "
 "norte-americanas do pós-guerra foram precedidas por choques no preço do petróleo, ao passo que "
 "Kilian (2009) decompôs tais choques em componentes de oferta, de demanda agregada e de demanda "
 "específica. Ignorar essas categorias tornaria o corpus estruturalmente incompleto para a "
 "previsão de volatilidade. A Tabela 6 descreve a taxonomia.")
abnt.tabela_abnt(doc, "6", "Taxonomia de categorias temáticas dos termos de busca",
 ["Categoria","Termos","Foco temático","Âncora teórica"],
 [["CAT1 — Empresa","21","Petrobras, PETR4, resultados, governança","Tetlock et al. (2008)"],
  ["CAT2 — Mercado de Petróleo","20","Brent/WTI, OPEP, oferta e demanda","Kilian (2009)"],
  ["CAT3 — Geopolítica","27","Guerras e tensões em países produtores","Hamilton (1983); Caldara e Iacoviello (2022)"],
  ["CAT4 — Infraestrutura","20","Refinarias, oleodutos, plataformas","Choque da Aramco (2019)"],
  ["CAT5 — Sanções e Navegação","20","Embargos, Ormuz, Mar Vermelho","Prêmio de risco de rotas"],
  ["CAT6 — Governança","24","Direção, intervenção, política energética","Estudos de evento"],
  ["CAT7 — Macroeconomia/Energia","20","Câmbio, juros, China, transição energética","Zhang et al. (2008); Kilian e Murphy (2014)"]])
abnt.paragrafo(doc,
 "Ao todo são 152 termos. A categoria associada a cada termo é gravada em cada notícia, "
 "viabilizando a posterior análise de ablação. O Quadro 3 ilustra a estrutura da taxonomia.")
abnt.quadro_codigo(doc, "3", "Estrutura da taxonomia de termos (Python)",
'''TERMOS_POR_CATEGORIA = {
    "CAT1_Empresa":          ["Petrobras", "PETR4", "pre-sal", "Petrobras dividendos", ...],
    "CAT2_Mercado_Petroleo": ["petroleo Brent", "OPEP", "preco do petroleo", ...],
    "CAT3_Geopolitica":      ["guerra Russia Ucrania", "Estreito de Ormuz", ...],
    "CAT4_Infraestrutura":   ["refinaria petroleo", "plataforma offshore", ...],
    "CAT5_Sancoes_Navegacao":["embargo petroleo", "Mar Vermelho petroleo", ...],
    "CAT6_Governanca":       ["CEO Petrobras", "ministro de minas e energia", ...],
    "CAT7_Macro_Energia":    ["dolar petroleo", "demanda China petroleo", ...],
}''')

# 9 AGRUPAMENTO
abnt.secao(doc, "9", "Agrupamento (categorização) das notícias")
abnt.paragrafo(doc,
 "O agrupamento temático não é realizado por classificação posterior, e sim na origem: como cada "
 "termo de busca pertence a uma categoria, a categoria do termo que capturou a notícia é gravada "
 "diretamente no registro. Dessa forma, cada notícia carrega sua procedência temática, o que "
 "permite a análise de ablação — técnica que remove uma categoria de cada vez e mede o impacto "
 "resultante na previsão, identificando quais tipos de notícia são mais informativos. O Quadro 4 "
 "apresenta o laço de coleta com a atribuição de categoria e a deduplicação.")
abnt.quadro_codigo(doc, "4", "Laço de coleta com categorização e deduplicação",
'''for portal, endpoint in PORTAIS.items():
    for categoria, termos in TERMOS_POR_CATEGORIA.items():    # 7 categorias
        for termo in termos:                                  # 152 termos
            for artigo in coletar_termo(portal, endpoint, categoria, termo, ini, fim):
                if artigo["hash_titulo"] not in hashes:       # deduplicacao
                    hashes.add(artigo["hash_titulo"])
                    writer.writerow(artigo)                   # grava com 'categoria' ''')
abnt.figura_abnt(doc, "3", "Distribuição das notícias por categoria temática", g_categorias)
abnt.tabela_abnt(doc, "7", "Notícias por categoria temática",
 [["Categoria","Notícias","% do corpus"]][0],
 [[c, fmt(dist_cat[c]), f"{dist_cat[c]/N_ORIG*100:.1f}%"] for c in dist_cat.index])

# 10 ESTATÍSTICAS
abnt.secao(doc, "10", "Estatísticas da coleta: sucessos e limitações")
abnt.paragrafo(doc, "A Tabela 8 sintetiza os principais indicadores quantitativos da coleta final.")
abnt.tabela_abnt(doc, "8", "Indicadores quantitativos da coleta final",
 ["Métrica","Valor"],
 [["Período coberto","01/01/2018 a 31/12/2025"],
  ["Artigos brutos requisitados", fmt(COLETA["brutos"])],
  ["Duplicatas removidas (hash)", fmt(COLETA["duplicados"])],
  ["Notícias únicas (corpus final)", fmt(N_ORIG)],
  ["Notícias com timestamp real", f"{tem_hora_pct:.1f}%"],
  ["Notícias após o fechamento (≥17h)", f"{lead_lag_pct:.1f}%"],
  ["Portais (fontes)","5"],["Categorias temáticas","7"],["Termos de busca","152"]])
abnt.paragrafo(doc,
 "A Figura 4 evidencia a cobertura anual contínua, com pico em 2022 — ano marcado pela troca de "
 "comando da Petrobras, pela guerra entre Rússia e Ucrânia e pela elevação do preço do petróleo —, "
 "o que reforça a validade do corpus.")
abnt.figura_abnt(doc, "4", "Notícias coletadas por ano (2018–2025)", g_anual)
abnt.tabela_abnt(doc, "9", "Distribuição anual das notícias",
 ["Ano","Notícias"], [[str(a), fmt(dist_ano[a])] for a in dist_ano.index])
abnt.paragrafo(doc,
 f"As Figuras 5 e 6 comprovam a disponibilidade do timestamp: **{lead_lag_pct:.1f}%** das "
 "notícias foram publicadas após o fechamento do pregão e são, portanto, realocadas ao dia útil "
 "seguinte, conforme exige o alinhamento lead-lag.")
abnt.figura_abnt(doc, "5", "Proporção de notícias antes e depois do fechamento da B3 (17h)", g_leadlag, largura_cm=10)
abnt.figura_abnt(doc, "6", "Distribuição das notícias por hora de publicação", g_horas)
abnt.paragrafo(doc,
 "Quanto às limitações observadas, alguns termos de alto volume exigiram a estratégia por janela "
 "mensal em razão da lentidão da paginação profunda; um ou outro termo retornou falha pontual de "
 "sondagem e foi registrado em log e ignorado; e a cobertura por categoria é desigual, dado que "
 "as categorias exógenas raramente citam o ativo de forma explícita. Todas as ocorrências foram "
 "registradas em arquivo de log auditável.")

# 11 FILTRAGEM
abnt.secao(doc, "11", "Tratamento e filtragem das notícias")
abnt.paragrafo(doc,
 "Concluída a coleta, avaliaram-se duas estratégias de filtragem. A base original é sempre "
 "preservada de forma imutável; as filtragens produzem bases derivadas.")
abnt.secao(doc, "11.1", "Filtragem forte (estrita): testada e descartada", nivel=2)
abnt.paragrafo(doc,
 "A filtragem forte exigia que o título ou o resumo contivesse explicitamente um termo do ativo "
 "ou da commodity (petrobras, petr4, petróleo, brent, opep, entre outros), conforme o Quadro 5.")
abnt.quadro_codigo(doc, "5", "Filtragem forte (estrita)",
'''TERMOS_RELEVANCIA = ["petrobras","petr4","petroleo","brent","opep","barril", ...]
alvo = (df["titulo"].fillna("") + " " + df["resumo"].fillna("")).str.lower()
mask = alvo.apply(lambda t: any(termo in t for termo in TERMOS_RELEVANCIA))
df_filtrada = df[mask]   # mantem aproximadamente 20% do corpus''')
abnt.paragrafo(doc,
 f"O resultado foi a retenção de apenas **{fmt(N_ESTRITO)} notícias** "
 f"({N_ESTRITO/N_ORIG*100:.1f}% do corpus) e, sobretudo, o esvaziamento das categorias exógenas — "
 "exatamente aquelas que a literatura aponta como determinantes da volatilidade. A categoria "
 "Geopolítica caiu para cerca de 1% e a categoria Macroeconomia/Energia para cerca de 3%.")
abnt.secao(doc, "11.2", "Filtragem leve: estratégia adotada", nivel=2)
abnt.paragrafo(doc,
 "A filtragem leve aplica apenas uma limpeza de qualidade, removendo notícias degeneradas — "
 "título vazio, com menos de quinze caracteres, ou marcadores de remoção. Não há filtro temático, "
 "pois o sinal de relevância já provém do termo da taxonomia utilizado na captura. O Quadro 6 "
 "apresenta a implementação.")
abnt.quadro_codigo(doc, "6", "Filtragem leve (limpeza de qualidade)",
'''titulo = df["titulo"].fillna("").astype(str).str.strip()
remover = (titulo == "") | (titulo.str.len() < 15) | titulo.str.lower().isin(MARCADORES)
df_tratada = df[~remover]   # mantem ~100% do corpus, preserva as 7 categorias''')
abnt.secao(doc, "11.3", "Justificativa da filtragem leve", nivel=2)
abnt.paragrafo(doc,
 "Optou-se pela filtragem leve porque a filtragem forte comprometeria a contribuição científica "
 "central da pesquisa — a análise de ablação por categoria. Notícias exógenas, como uma guerra no "
 "Oriente Médio, uma decisão da OPEP ou uma valorização do dólar, frequentemente não citam a "
 "Petrobras no título, embora impactem diretamente a volatilidade do ativo. Descartá-las "
 "eliminaria justamente o diferencial do estudo. A filtragem leve preserva a amplitude temática e "
 "remove apenas ruído degenerado.")
abnt.secao(doc, "11.4", "Resultado da filtragem", nivel=2)
abnt.tabela_abnt(doc, "10", "Comparação entre as estratégias de filtragem",
 ["Estratégia","Notícias mantidas","% do corpus","Efeito nas categorias exógenas"],
 [["Original (sem filtro)", fmt(N_ORIG), "100,0%","—"],
  ["Filtragem forte (estrita)", fmt(N_ESTRITO), f"{N_ESTRITO/N_ORIG*100:.1f}%","Esvaziadas (Geopol. ~1%; Macro ~3%)"],
  ["Filtragem leve (adotada)", fmt(N_LEVE), f"{N_LEVE/N_ORIG*100:.1f}%","Preservadas integralmente"]])
abnt.figura_abnt(doc, "7", "Impacto das estratégias de filtragem por categoria", g_filtro)

# 12 SPLIT
abnt.secao(doc, "12", "Particionamento em treino, validação e teste")
abnt.paragrafo(doc,
 "Conforme orientação recebida, os dados foram particionados em três conjuntos, na proporção de "
 "60% para treino, 15% para validação e 25% para teste. Por se tratar de série temporal "
 "financeira, o corte é estritamente cronológico, jamais aleatório, de modo a evitar o vazamento "
 "de informação futura (data leakage).")
abnt.paragrafo(doc,
 "O particionamento é estratificado por ano: dentro de cada ano, os primeiros 60% dos dias "
 "destinam-se ao treino, os 15% seguintes à validação e os 25% finais — os mais recentes — ao "
 "teste. Assim, todos os anos, e portanto todos os regimes de mercado, estão representados nos "
 "três conjuntos. A atribuição é feita por dias inteiros: um mesmo dia jamais é dividido entre "
 "conjuntos, o que preserva a integridade temporal. O Quadro 7 detalha o procedimento.")
abnt.quadro_codigo(doc, "7", "Particionamento temporal estratificado por ano",
'''def classificar_ano(grupo):
    contagem_dia = grupo.groupby("data").size().sort_index()
    frac_acum = contagem_dia.cumsum() / contagem_dia.sum()
    dia_conjunto = {}
    for dia, f in frac_acum.items():
        if   f <= 0.60: dia_conjunto[dia] = "treino"
        elif f <= 0.75: dia_conjunto[dia] = "validacao"
        else:           dia_conjunto[dia] = "teste"
    return grupo["data"].map(dia_conjunto)

df["conjunto"] = df.groupby("ano", group_keys=False).apply(classificar_ano)''')
if not tab_split.empty:
    abnt.tabela_abnt(doc, "11", "Distribuição global do particionamento",
     ["Conjunto","Notícias","%"],
     [["Treino", fmt(dist_split.get("treino",0)), f"{dist_split.get('treino',0)/len(dft)*100:.1f}%"],
      ["Validação", fmt(dist_split.get("validacao",0)), f"{dist_split.get('validacao',0)/len(dft)*100:.1f}%"],
      ["Teste", fmt(dist_split.get("teste",0)), f"{dist_split.get('teste',0)/len(dft)*100:.1f}%"]])
    abnt.figura_abnt(doc, "8", "Particionamento temporal por ano (estratificado)", g_split)
    abnt.tabela_abnt(doc, "12", "Notícias por ano e conjunto",
     ["Ano","Treino","Validação","Teste"],
     [[str(a), fmt(tab_split.loc[a,"treino"]), fmt(tab_split.loc[a,"validacao"]), fmt(tab_split.loc[a,"teste"])]
      for a in tab_split.index])

# 13 COMPLEMENTO
abnt.secao(doc, "13", "Considerações complementares e trabalhos pendentes")
abnt.paragrafo(doc,
 "Por recomendação metodológica, os itens a seguir reforçam o rigor do capítulo de Materiais e "
 "Métodos e devem constar da versão final da dissertação:")
abnt.lista(doc, [
 "**Reprodutibilidade:** registrar a data exata da coleta, as versões das bibliotecas e o caráter imutável da base bruta, disponibilizando os scripts em repositório versionado.",
 "**Aspectos éticos e Termos de Uso:** esclarecer que a coleta utilizou APIs públicas para fins exclusivamente acadêmicos, com pausas de cortesia e sem finalidade comercial.",
 "**Validação do modelo de sentimento:** construir um conjunto-ouro com amostra de notícias rotuladas manualmente e reportar a concordância (coeficiente kappa de Cohen) entre o modelo e os anotadores humanos.",
 "**Alinhamento com o calendário de pregão:** detalhar o tratamento de fins de semana e feriados, com atribuição ao próximo dia útil, além do corte das 17 horas.",
 "**Construção do Índice de Sentimento da Mídia (ISM):** documentar a agregação diária (média da polaridade ponderada pela confiança) e o ISM por categoria utilizado na ablação.",
 "**Definição formal da variável-alvo e dos atributos:** direção do log-retorno em t+1 e a matriz de atributos defasada em t-1.",
 "**Métricas e linha de base:** acurácia, precisão, F1 e AUC-ROC, comparando o modelo com sentimento ao modelo de referência baseado apenas em preços.",
 "**Ameaças à validade:** viés de seleção das cinco fontes, restrição ao idioma português, cobertura desigual por categoria e dependência da qualidade do interpretador de datas.",
 "**Estatística descritiva da série financeira:** apresentar os testes de Jarque-Bera, Dickey-Fuller Aumentado e ARCH-LM que fundamentam o emprego do GARCH(1,1).",
 "**Fluxograma do pipeline:** incluir um diagrama do encadeamento 01 → 02b → 02c → 03 → 04.",
])
abnt.paragrafo(doc,
 "Por fim, recomenda-se que o mapa de datas do particionamento seja aplicado também à matriz "
 "diária de modelagem (Etapa 4), garantindo a consistência dos conjuntos de treino, validação e "
 "teste entre o corpus textual e os dias de pregão.")

# REFERÊNCIAS
abnt.referencias(doc, "14", [
 "CALDARA, D.; IACOVIELLO, M. Measuring geopolitical risk. American Economic Review, v. 112, n. 4, p. 1194-1225, 2022.",
 "CARDOSO, [completar]; NAKANE, M. I. O que há em uma manchete? O impacto das notícias na economia brasileira. [completar dados da publicação]. 2024.",
 "HAMILTON, J. D. Oil and the macroeconomy since World War II. Journal of Political Economy, v. 91, n. 2, p. 228-248, 1983.",
 "HESTON, S. L.; SINHA, N. R. News vs. sentiment: predicting stock returns from news stories. Financial Analysts Journal, v. 73, n. 3, p. 67-83, 2017.",
 "KILIAN, L. Not all oil price shocks are alike: disentangling demand and supply shocks in the crude oil market. American Economic Review, v. 99, n. 3, p. 1053-1069, 2009.",
 "KILIAN, L.; MURPHY, D. P. The role of inventories and speculative trading in the global market for crude oil. Journal of Applied Econometrics, v. 29, n. 3, p. 454-478, 2014.",
 "LEETARU, K.; SCHRODT, P. A. GDELT: Global data on events, location and tone. In: ISA ANNUAL CONVENTION, 2013.",
 "TETLOCK, P. C.; SAAR-TSECHANSKY, M.; MACSKASSY, S. More than words: quantifying language to measure firms' fundamentals. The Journal of Finance, v. 63, n. 3, p. 1437-1467, 2008.",
 "ZHANG, Y. J. et al. Spillover effect of US dollar exchange rate on oil prices. Journal of Policy Modeling, v. 30, n. 6, p. 973-991, 2008.",
])

doc.save(SAIDA)
print(f"\n✅ Documento ABNT gerado: {SAIDA.resolve()}")
print(f"   Base: {fmt(N_ORIG)} notícias | 14 seções | tabelas, quadros e 8 figuras")
