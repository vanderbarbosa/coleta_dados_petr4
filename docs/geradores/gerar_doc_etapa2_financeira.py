# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Gerador da Documentação (ETAPA 2: Coleta de Dados Financeiros)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Documento ABNT detalhando a coleta da série histórica da PETR4 (Script 01):
#   método, bibliotecas e justificativas, ferramentas descartadas, dificuldades
#   enfrentadas e superadas, estatísticas, tabelas e figuras a partir dos dados
#   REAIS. Saída: docs/saida/Documentacao_Etapa2_Coleta_Financeira_PETR4.docx
# ==============================================================================

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src" / "comum"))
import abnt_docx as abnt

PASTA  = RAIZ / "Mestrado_PETR4"
ARQ    = PASTA / "base_financeira_petr4.csv"
ASSETS = RAIZ / "_doc_assets"; ASSETS.mkdir(exist_ok=True)
SAIDA  = RAIZ / "docs" / "saida" / "Documentacao_Etapa2_Coleta_Financeira_PETR4.docx"

plt.rcParams.update({"figure.dpi": 150, "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})
AZUL, VERM = "#2c7bb6", "#d7191c"
fmt = lambda n: f"{int(n):,}".replace(",", ".")

# ── Dados reais ───────────────────────────────────────────────────────────────
df = pd.read_csv(ARQ, index_col="Date", parse_dates=True)
N = len(df)
ini, fim = df.index[0].date(), df.index[-1].date()
desc_close = df["Close"].describe()
desc_ret = (df["Log_Retorno"] * 100).describe()
ret = df["Log_Retorno"].dropna() * 100

# ── Gráficos ──────────────────────────────────────────────────────────────────
def salvar(fig, nome):
    c = ASSETS / nome; fig.savefig(c, bbox_inches="tight"); plt.close(fig); return c

fig, ax = plt.subplots(figsize=(9, 3.6))
ax.plot(df.index, df["Close"], color=AZUL, lw=0.8)
ax.set_ylabel("Preço de fechamento (R$)"); ax.set_xlabel("Ano")
g_preco = salvar(fig, "fin_preco.png")

fig, ax = plt.subplots(figsize=(9, 3.2))
ax.plot(df.index, df["Log_Retorno"] * 100, color="#444", lw=0.5)
ax.axhline(0, color=VERM, lw=0.8, ls="--")
ax.set_ylabel("Log-retorno (%)"); ax.set_xlabel("Ano")
g_ret = salvar(fig, "fin_ret.png")

fig, ax = plt.subplots(figsize=(7, 3.6))
ax.hist(ret, bins=80, color=AZUL, alpha=0.8)
ax.set_xlabel("Log-retorno diário (%)"); ax.set_ylabel("Frequência")
g_hist = salvar(fig, "fin_hist.png")

# ── Documento ─────────────────────────────────────────────────────────────────
doc = abnt.novo_documento()
abnt.capa(
    doc,
    "Coleta de Dados Financeiros do Ativo PETR4",
    "Etapa 2 — Série Histórica de Preços e Cálculo do Log-Retorno",
    "Vanderlei Barbosa da Silva",
    "Orientador: Prof. Dr. Julio Cesar Nievola",
    "Pontifícia Universidade Católica do Paraná — Mestrado em Informática",
    descricao=("Documento técnico-metodológico da dissertação “O Impacto do Sentimento de Notícias "
               "Financeiras na Previsão de Direção e Volatilidade do Ativo PETR4”. Descreve a "
               "obtenção da variável dependente do estudo — a série de retornos da PETR4 —, com "
               "todos os números gerados a partir dos dados reais coletados."),
)

# 1
abnt.secao(doc, "1", "Objetivo e definição da variável dependente")
abnt.paragrafo(doc,
 "Esta etapa obtém a série histórica diária do ativo PETR4 (ação preferencial da Petróleo "
 "Brasileiro S.A., negociada na B3) e calcula o log-retorno, que constitui a variável dependente "
 "da pesquisa. A direção do log-retorno do dia seguinte (alta ou baixa) é o alvo dos modelos "
 "preditivos; a sua variância condicional, estimada na Etapa 4 por meio do modelo GARCH, "
 "representa a volatilidade.")
abnt.paragrafo(doc,
 "O log-retorno é definido operacionalmente pela Equação 1, em que P_t é o preço de fechamento "
 "ajustado no pregão t. O uso do logaritmo natural confere aditividade temporal aos retornos e "
 "aproxima a série da estacionariedade, pressuposto dos modelos econométricos e de aprendizado de "
 "máquina empregados.")
abnt.quadro_codigo(doc, "1", "Equação 1 — Log-retorno diário",
 "R_t = ln( P_t / P_(t-1) )")

# 2
abnt.secao(doc, "2", "Método de captura")
abnt.paragrafo(doc,
 f"A série foi obtida de forma programática a partir do provedor Yahoo Finance, por meio da "
 f"biblioteca yfinance, para o ticker “PETR4.SA” (o sufixo “.SA” identifica a B3). O período "
 f"requisitado foi de 1º de janeiro de 2018 a 31 de dezembro de 2025, resultando em "
 f"**{fmt(N)} pregões** efetivos, de {ini} a {fim}. Para cada pregão são obtidos os preços de "
 "abertura, máxima, mínima, fechamento e o volume negociado; o log-retorno é então calculado "
 "localmente segundo a Equação 1, e a primeira observação (sem dia anterior) é descartada.")

# 3
abnt.secao(doc, "3", "Bibliotecas utilizadas e justificativa")
abnt.tabela_abnt(doc, "1", "Bibliotecas da Etapa 2 e justificativa da escolha",
 ["Biblioteca", "Função", "Justificativa da escolha"],
 [["yfinance", "Acesso à série histórica da B3 via Yahoo Finance", "Gratuita, amplamente adotada na literatura e em pesquisas reprodutíveis; cobre a B3 com ajuste de proventos"],
  ["pandas", "Estruturação da série temporal e cálculo vetorizado", "Padrão de fato para séries temporais financeiras em Python"],
  ["numpy", "Logaritmo natural e operações numéricas", "Eficiência e precisão no cálculo do log-retorno"],
  ["requests", "Sessão HTTP customizada (contorno de proxy/SSL)", "Permite configurar verificação SSL e cabeçalhos, necessário no ambiente de coleta"]])

# 4
abnt.secao(doc, "4", "Ferramentas avaliadas e descartadas")
abnt.paragrafo(doc,
 "Outras fontes de cotações foram consideradas e descartadas, conforme a Tabela 2. A escolha do "
 "Yahoo Finance via yfinance equilibra gratuidade, cobertura da B3, ajuste de proventos e "
 "reprodutibilidade.")
abnt.tabela_abnt(doc, "2", "Fontes de cotações avaliadas e descartadas",
 ["Fonte / Ferramenta", "Motivo do descarte"],
 [["API oficial da B3 / dados de mercado", "Acesso pago/institucional e processo de credenciamento incompatível com a pesquisa"],
  ["Alpha Vantage / Twelve Data", "Planos gratuitos com forte limitação de requisições e cobertura irregular da B3"],
  ["Web scraping de portais (Investing.com)", "Frágil (HTML dinâmico), sujeito a bloqueio e sem ajuste padronizado de proventos"],
  ["Exportação manual (B3/corretora)", "Não reprodutível e suscetível a erro humano na consolidação"]])

# 5
abnt.secao(doc, "5", "Dificuldades enfrentadas e soluções")
abnt.paragrafo(doc,
 "Durante a coleta local, dois obstáculos técnicos foram enfrentados e superados, ambos "
 "registrados aqui em nome da reprodutibilidade.")
abnt.paragrafo(doc,
 "**(i) Interceptação de SSL pela rede.** No ambiente de execução, a rede intercepta o tráfego "
 "HTTPS, o que impedia o yfinance de validar o certificado do servidor do Yahoo. A solução foi "
 "instanciar uma sessão HTTP própria com a verificação de certificado desabilitada (parâmetro "
 "VERIFY_SSL) e injetá-la no yfinance, preservando o funcionamento sem comprometer a coleta.")
abnt.paragrafo(doc,
 "**(ii) Limitação de taxa (rate limit) do provedor.** O Yahoo Finance aplica bloqueio temporário "
 "por excesso de requisições (HTTP 429 / “Too Many Requests”). Implementou-se um laço de novas "
 "tentativas com espera progressiva (15 s, 30 s, 45 s, 60 s), até cinco tentativas, o que permitiu "
 "concluir a coleta com êxito. O Quadro 2 resume a lógica.")
abnt.quadro_codigo(doc, "2", "Sessão SSL configurável e novas tentativas com espera",
'''_sessao = requests.Session(); _sessao.verify = VERIFY_SSL
for tentativa in range(1, MAX_TENTATIVAS + 1):
    df = yf.Ticker(TICKER, session=_sessao).history(start=DATA_INICIO, end=DATA_FIM)
    if df is not None and not df.empty:
        break
    time.sleep(min(15 * tentativa, 60))   # espera progressiva (rate limit)''')

# 6
abnt.secao(doc, "6", "Quantitativos e estatística descritiva")
abnt.paragrafo(doc,
 f"A base final contém **{fmt(N)} pregões** ({ini} a {fim}). A Tabela 3 resume a estatística "
 "descritiva do preço de fechamento e do log-retorno percentual.")
abnt.tabela_abnt(doc, "3", "Estatística descritiva da série da PETR4",
 ["Medida", "Preço de fechamento (R$)", "Log-retorno (%)"],
 [["Observações", fmt(N), fmt(len(ret))],
  ["Média", f"{desc_close['mean']:.2f}", f"{desc_ret['mean']:.4f}"],
  ["Desvio-padrão", f"{desc_close['std']:.2f}", f"{desc_ret['std']:.4f}"],
  ["Mínimo", f"{desc_close['min']:.2f}", f"{desc_ret['min']:.4f}"],
  ["Máximo", f"{desc_close['max']:.2f}", f"{desc_ret['max']:.4f}"]])
abnt.paragrafo(doc,
 "A Figura 1 apresenta a evolução do preço de fechamento; a Figura 2, a série de log-retornos, na "
 "qual se observam agrupamentos de volatilidade (períodos de oscilação intensa concentrados no "
 "tempo); e a Figura 3, o histograma dos retornos, cujas caudas pesadas motivam o uso da "
 "distribuição t-Student no GARCH (Etapa 4).")
abnt.figura_abnt(doc, "1", "Preço de fechamento diário da PETR4 (2018–2025)", g_preco)
abnt.figura_abnt(doc, "2", "Log-retorno diário da PETR4 (%)", g_ret)
abnt.figura_abnt(doc, "3", "Histograma dos log-retornos diários da PETR4", g_hist)

# 7
abnt.secao(doc, "7", "Limitações da etapa")
abnt.lista(doc, [
 "Dependência de um provedor gratuito (Yahoo Finance): eventuais ajustes retroativos de proventos podem alterar marginalmente a série; recomenda-se registrar a data da coleta.",
 "Frequência diária (fechamento): não captura a dinâmica intradiária, coerente com o alinhamento lead-lag adotado para as notícias (Etapa 1).",
 "Ativo único (PETR4): os procedimentos são generalizáveis a outros ativos da B3 trocando-se o ticker, o que é tratado como trabalho futuro.",
])

abnt.referencias(doc, "8", [
 "BOLLERSLEV, T. Generalized autoregressive conditional heteroskedasticity. Journal of Econometrics, v. 31, n. 3, p. 307-327, 1986.",
 "FAMA, E. F. Efficient capital markets: a review of theory and empirical work. The Journal of Finance, v. 25, n. 2, p. 383-417, 1970.",
])

doc.save(SAIDA)
print(f"✅ Documento ABNT gerado: {SAIDA}")
print(f"   Base: {fmt(N)} pregões | período {ini}–{fim}")
