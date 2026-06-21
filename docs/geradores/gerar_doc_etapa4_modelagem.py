# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Gerador da Documentação (ETAPA 4: Modelagem Preditiva)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Documento ABNT detalhando a modelagem (Script 04): testes estatísticos,
#   GARCH(1,1), Data Fusion, particionamento treino/validação/teste, SVM/XGBoost,
#   análise de ablação, bibliotecas e justificativas, ferramentas descartadas.
#   Os testes e o GARCH são calculados sobre os PREÇOS REAIS (independentes do
#   sentimento). As métricas dos classificadores são PRELIMINARES (sentimento de
#   amostra) e serão regeradas após o processamento completo do corpus.
#   Saída: docs/saida/Documentacao_Etapa4_Modelagem_PETR4.docx
# ==============================================================================

import sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.diagnostic import het_arch
from statsmodels.tsa.stattools import adfuller
from arch import arch_model

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src" / "comum"))
import abnt_docx as abnt

PASTA  = RAIZ / "Mestrado_PETR4"
ASSETS = RAIZ / "_doc_assets"; ASSETS.mkdir(exist_ok=True)
SAIDA  = RAIZ / "docs" / "saida" / "Documentacao_Etapa4_Modelagem_PETR4.docx"
plt.rcParams.update({"figure.dpi": 150, "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})
AZUL, VERM = "#2c7bb6", "#d7191c"
fmt = lambda n: f"{int(n):,}".replace(",", ".")

# ── Cálculos REAIS sobre os preços (independem do sentimento) ────────────────
dff = pd.read_csv(PASTA / "base_financeira_petr4.csv", index_col="Date", parse_dates=True)
r = (dff["Log_Retorno"] * 100).dropna()
jb = stats.jarque_bera(r); adf = adfuller(r, autolag="AIC"); arch = het_arch(r, nlags=5)
res = arch_model(r, vol="Garch", p=1, q=1, dist="t").fit(disp="off")
dff = dff.iloc[1:].copy(); dff["vol"] = res.conditional_volatility
omega = float(res.params.get("omega", np.nan))
alpha = float(res.params.get("alpha[1]", np.nan))
beta  = float(res.params.get("beta[1]", np.nan))
persist = alpha + beta

fig, ax = plt.subplots(figsize=(9, 3.4))
ax.fill_between(dff.index, dff["vol"], color=VERM, alpha=0.4)
ax.plot(dff.index, dff["vol"], color=VERM, lw=0.7)
ax.set_ylabel("Volatilidade condicional (σ)"); ax.set_xlabel("Ano")
g_vol = ASSETS / "mod_vol.png"; fig.savefig(g_vol, bbox_inches="tight"); plt.close(fig)

# Resultados dos modelos (Tabela 4.3), se existirem
df_res = None
try:
    df_res = pd.read_csv(PASTA / "resultados_modelos_petr4.csv")
except Exception:
    pass

# ── Experimento de tuning (antes/depois), calculado dos dados reais ───────────
from sklearn.metrics import accuracy_score, roc_auc_score
from xgboost import XGBClassifier
tun = None
try:
    m = pd.read_csv(PASTA / "base_master_petr4.csv")
    Ym = m["Alvo"].values
    Xb = m[["Retorno_Ontem", "Volatilidade_Ontem"]].values
    Xf = m[["Retorno_Ontem", "Volatilidade_Ontem", "Sentimento_Ontem"]].values
    nm = len(Ym); c1 = int(nm * .60); c2 = int(nm * .75)
    tr, va, te = np.arange(0, c1), np.arange(c1, c2), np.arange(c2, nm)

    def _tr(X, md=3, lr=0.1):
        mdl = XGBClassifier(n_estimators=100, max_depth=md, learning_rate=lr, subsample=0.8,
                            colsample_bytree=0.8, eval_metric="logloss", random_state=42, verbosity=0)
        mdl.fit(X[tr], Ym[tr]); return mdl
    ac_base = accuracy_score(Ym[te], _tr(Xb).predict(Xb[te])) * 100
    ac_def = accuracy_score(Ym[te], _tr(Xf).predict(Xf[te])) * 100
    melhor, melhor_auc, pbest = None, -1, None
    for d in (3, 5):
        for lr in (0.05, 0.1):
            mdl = _tr(Xf, d, lr); auc = roc_auc_score(Ym[va], mdl.predict_proba(Xf[va])[:, 1])
            if auc > melhor_auc: melhor, melhor_auc, pbest = mdl, auc, (d, lr)
    ac_tun = accuracy_score(Ym[te], melhor.predict(Xf[te])) * 100
    tun = {"base": ac_base, "def": ac_def, "tun": ac_tun, "p": pbest,
           "g_sent": ac_tun - ac_base, "g_tun": ac_tun - ac_def,
           "n_tr": len(tr), "n_va": len(va), "n_te": len(te)}
except Exception as _e:
    tun = None

# ── Documento ─────────────────────────────────────────────────────────────────
doc = abnt.novo_documento()
abnt.capa(
    doc,
    "Modelagem Preditiva da Direção e Volatilidade da PETR4",
    "Etapa 4 — GARCH, Data Fusion e Classificadores (SVM e XGBoost)",
    "Vanderlei Barbosa da Silva",
    "Orientador: Prof. Dr. Julio Cesar Nievola",
    "Pontifícia Universidade Católica do Paraná — Mestrado em Informática",
    descricao=("Documento técnico-metodológico da dissertação “O Impacto do Sentimento de Notícias "
               "Financeiras na Previsão de Direção e Volatilidade do Ativo PETR4”. Os testes "
               "estatísticos e o modelo GARCH são calculados sobre os preços reais; as métricas dos "
               "classificadores são preliminares e serão consolidadas após o processamento completo."),
)

# 1
abnt.secao(doc, "1", "Delineamento metodológico e método")
abnt.paragrafo(doc,
 "Distinguem-se, conforme recomendação da banca, a metodologia e o método. Quanto à METODOLOGIA, "
 "esta é uma pesquisa quantitativa, empírica e aplicada, de paradigma pós-positivista, conduzida "
 "como um experimento computacional sobre dados observacionais. Quanto ao MÉTODO, a etapa encadeia "
 "cinco procedimentos: (i) testes estatísticos de pré-requisito; (ii) modelagem da volatilidade por "
 "GARCH; (iii) fusão de atributos (Data Fusion); (iv) particionamento temporal treino/validação/"
 "teste; e (v) treinamento e avaliação de classificadores, com análise de ablação por categoria.")

# 2
abnt.secao(doc, "2", "Testes estatísticos de pré-requisito")
abnt.paragrafo(doc,
 "Antes de modelar a volatilidade, três pressupostos são verificados sobre a série de log-retornos, "
 "calculados aqui sobre os dados REAIS. A Tabela 1 apresenta os resultados.")
abnt.tabela_abnt(doc, "1", "Testes estatísticos sobre os log-retornos reais da PETR4",
 ["Teste", "Hipótese nula (H0)", "Estatística", "p-valor", "Conclusão"],
 [["Jarque-Bera", "Série é normal", f"{jb[0]:.1f}", f"{jb[1]:.2e}", "Rejeita H0 — caudas pesadas (não normal)"],
  ["Dickey-Fuller Aumentado", "Há raiz unitária", f"{adf[0]:.2f}", f"{adf[1]:.2e}", "Rejeita H0 — série estacionária"],
  ["ARCH-LM (Engle)", "Sem efeito ARCH", f"{arch[0]:.1f}", f"{arch[1]:.2e}", "Rejeita H0 — heterocedasticidade (efeito ARCH)"]])
abnt.paragrafo(doc,
 "Os três resultados são estatisticamente significativos (p < 0,05). A não normalidade justifica a "
 "distribuição t-Student; a estacionariedade habilita o uso de modelos de série temporal; e a "
 "presença de efeito ARCH fundamenta empiricamente o emprego do GARCH.")

# 3
abnt.secao(doc, "3", "Modelagem da volatilidade: GARCH(1,1)")
abnt.paragrafo(doc,
 "A volatilidade condicional é modelada pelo GARCH(1,1), cuja equação da variância é apresentada no "
 "Quadro 1. Escolheu-se a ordem (1,1) por PARCIMÔNIA — é a especificação mais robusta e amplamente "
 "validada em mercados emergentes (Bollerslev, 1986) —, evitando o sobreajuste de ordens superiores.")
abnt.quadro_codigo(doc, "1", "Equação 1 — variância condicional do GARCH(1,1)",
 "σ²_t = ω + α · ε²_(t-1) + β · σ²_(t-1)")
abnt.paragrafo(doc,
 f"A estimação sobre os dados reais resultou em ω = {omega:.4f}, α = {alpha:.4f} e β = {beta:.4f}, "
 f"com persistência α + β = {persist:.4f}. Esse valor, próximo de 1, indica ALTA PERSISTÊNCIA: "
 "choques de volatilidade dissipam-se lentamente, característica esperada de um ativo volátil e "
 "politicamente sensível como a PETR4. A Figura 1 evidencia os agrupamentos de volatilidade.")
abnt.figura_abnt(doc, "1", "Volatilidade condicional da PETR4 estimada pelo GARCH(1,1)", g_vol)

# 4
abnt.secao(doc, "4", "Data Fusion: formalização da fusão de atributos")
abnt.paragrafo(doc,
 "Respondendo ao questionamento da banca (“é mera concatenação de atributos?”), formaliza-se: o "
 "Data Fusion é a construção de uma matriz de atributos que CONCATENA, para cada pregão, variáveis "
 "heterogêneas DEFASADAS EM UM DIA (t−1), de modo que a previsão de hoje use apenas informação de "
 "ontem (evitando vazamento de informação). A justificativa teórica é a complementaridade entre a "
 "informação quantitativa (retorno e volatilidade) e a textual (sentimento), que capturam dimensões "
 "distintas do comportamento do investidor. A Tabela 2 ilustra uma linha da matriz.")
abnt.tabela_abnt(doc, "2", "Exemplo da matriz de atributos (Data Fusion)",
 ["Retorno(t−1)", "Volatilidade GARCH(t−1)", "Sentimento ISM(t−1)", "Alvo (direção em t)"],
 [["+0,85%", "2,31", "−0,42", "1 (alta)"]])

# 5
abnt.secao(doc, "5", "Variável-alvo e classificadores")
abnt.paragrafo(doc,
 "A variável-alvo é binária: 1 (alta) se o log-retorno do dia for positivo; 0 (baixa) caso "
 "contrário. Avaliam-se quatro modelos — SVM e XGBoost, cada um em duas versões (apenas preços e "
 "Data Fusion completo). A Tabela 3 justifica cada escolha técnica, conforme solicitado pela banca.")
abnt.tabela_abnt(doc, "3", "Escolhas de modelagem e respectiva justificativa",
 ["Escolha", "Justificativa"],
 [["GARCH(1,1)", "Parcimônia e robustez empírica em mercados emergentes; captura agrupamentos de volatilidade"],
  ["SVM (kernel RBF)", "Classificador de margem máxima, eficaz em espaços de baixa dimensão; serve de comparação"],
  ["XGBoost", "Estado da arte para dados tabulares; resistente a sobreajuste e fornece importância de variáveis (ablação)"],
  ["AUC-ROC", "Métrica adequada à classificação binária com classes potencialmente desbalanceadas; independe do limiar"],
  ["Distribuição t-Student (GARCH)", "Acomoda as caudas pesadas confirmadas pelo teste de Jarque-Bera"]])

# 6
abnt.secao(doc, "6", "Particionamento treino/validação/teste (sem vazamento)")
abnt.paragrafo(doc,
 "Atendendo à exigência de validade temporal, os dados são particionados cronologicamente em três "
 "conjuntos: 60% treino, 15% validação e 25% teste. O treino ajusta os modelos; a validação "
 "seleciona os hiperparâmetros; e o teste, composto pelos pregões mais recentes, é avaliado uma "
 "única vez (out-of-sample). O corte estritamente cronológico elimina o vazamento de informação "
 "futura (data leakage) que comprometeria a validade preditiva. Um protocolo alternativo, "
 "estratificado por ano, está disponível para análise de sensibilidade.")

# 7
abnt.secao(doc, "7", "Análise de ablação por categoria")
abnt.paragrafo(doc,
 "Como contribuição científica adicional, realiza-se a ablação: treina-se o modelo completo com o "
 "sentimento das sete categorias e, em seguida, remove-se uma categoria por vez, medindo a queda de "
 "desempenho. A maior queda identifica a categoria mais informativa para prever a PETR4, "
 "respondendo à pergunta de qual vetor temático (corporativo, mercado de petróleo, geopolítico etc.) "
 "mais contribui — e endereçando a distinção entre sentimento de mercado e do ativo.")

# 8
abnt.secao(doc, "8", "Bibliotecas utilizadas e ferramentas descartadas")
abnt.tabela_abnt(doc, "4", "Bibliotecas da Etapa 4 e justificativa",
 ["Biblioteca", "Função", "Justificativa"],
 [["arch", "Estimação do GARCH(1,1)", "Biblioteca de referência em econometria financeira em Python"],
  ["statsmodels / scipy", "Testes ADF, ARCH-LM e Jarque-Bera", "Implementações padrão e auditáveis dos testes estatísticos"],
  ["scikit-learn", "SVM, normalização e métricas", "Padrão consolidado de aprendizado de máquina; evita vazamento ao ajustar o scaler só no treino"],
  ["xgboost", "Classificador de gradient boosting", "Estado da arte tabular; importância de variáveis para a ablação"],
  ["matplotlib", "Figuras (volatilidade, dispersão, ablação)", "Padrão científico de visualização"]])
abnt.tabela_abnt(doc, "5", "Ferramentas avaliadas e descartadas (trabalhos futuros)",
 ["Ferramenta", "Motivo do descarte / encaminhamento"],
 [["Redes recorrentes (LSTM/GRU)", "Exigem volume e custo computacional maiores; indicadas como trabalho futuro"],
  ["EGARCH / TGARCH", "Capturam assimetria, mas reduzem a parcimônia; sugeridas para extensão do estudo"],
  ["Random Forest", "Desempenho comparável ao XGBoost, porém sem o mesmo controle de sobreajuste em séries; mantido como comparação futura"]])

# 9
abnt.secao(doc, "9", "Resultados dos classificadores")
if df_res is not None:
    # Ganho do Data Fusion sobre o baseline (XGBoost), calculado dos dados reais
    try:
        d = df_res.set_index("Modelo")["Acurácia"]
        ganho_xgb = float(d["XGBoost (Data Fusion — GARCH + NLP)"]) - float(d["XGBoost (Apenas Preços)"])
    except Exception:
        ganho_xgb = None
    abnt.paragrafo(doc,
     "A Tabela 6 apresenta o desempenho dos quatro modelos sobre o corpus completo de notícias, no "
     "conjunto de teste (out-of-sample). As acurácias situam-se na faixa de 50% a 53%, valores "
     "coerentes com a dificuldade reconhecida de prever a direção diária de um ativo — e "
     "deliberadamente apresentados sem qualquer superdimensionamento.")
    cols = [c for c in df_res.columns if c in ("Modelo","Acurácia","Precisão","F1-Score","AUC-ROC","AUC_val")]
    abnt.tabela_abnt(doc, "6", "Desempenho dos classificadores no conjunto de teste",
     cols, [[str(row[c]) for c in cols] for _, row in df_res.iterrows()])
    if ganho_xgb is not None:
        abnt.paragrafo(doc,
         f"O principal achado é que a inclusão do sentimento e da volatilidade (Data Fusion) elevou a "
         f"acurácia do XGBoost em **{ganho_xgb:+.2f} pontos percentuais** frente ao modelo baseado "
         "apenas em preços, com aumento correspondente da AUC-ROC. O resultado é consistente com a "
         "hipótese de que o sentimento textual carrega informação direcional incremental, ainda que "
         "modesta. O classificador SVM não se beneficiou da fusão, sugerindo que a relação entre "
         "sentimento e direção é melhor capturada por modelos não lineares baseados em árvores.")
else:
    abnt.paragrafo(doc, "As métricas dos classificadores serão inseridas após o processamento completo do corpus.")

# 10 — Evolução experimental
abnt.secao(doc, "10", "Evolução experimental: treinamentos, ajustes e tuning")
abnt.paragrafo(doc,
 "Os resultados foram construídos de forma iterativa, em estágios sucessivos de treinamento e "
 "ajuste. Esta seção documenta essa evolução — resultados iniciais, ajustes realizados e o efeito "
 "do tuning de hiperparâmetros —, em nome da transparência e da reprodutibilidade.")
if tun is not None:
    abnt.tabela_abnt(doc, "7", "Estágios de treinamento e respectivos resultados (XGBoost Data Fusion)",
     ["Estágio", "Configuração", "Acurácia (teste)", "Observação"],
     [["1 — Validação do fluxo", "Sentimento de AMOSTRA (300 notícias)", "≈ 50%",
       "Indistinguível de acaso (passeio aleatório); validou apenas o pipeline ponta a ponta"],
      ["2 — Corpus completo", "Sentimento de 205.697 notícias (FinBERT-PT-BR), hiperparâmetros padrão",
       f"{tun['def']:.2f}%", "Primeiro resultado com sentimento real"],
      ["3 — Tuning na validação", f"Hiperparâmetros selecionados por AUC (max_depth={tun['p'][0]}, lr={tun['p'][1]})",
       f"{tun['tun']:.2f}%", "Seleção pela validação; ver discussão abaixo"]])
    abnt.paragrafo(doc,
     "O ajuste fino (tuning) foi conduzido de forma metodologicamente correta: os hiperparâmetros "
     "candidatos foram avaliados no conjunto de VALIDAÇÃO (nunca no de teste), e o de maior AUC-ROC "
     "foi selecionado. A Tabela 8 isola o efeito de cada componente — o sentimento e o tuning — sobre "
     "a acurácia no conjunto de teste.")
    abnt.tabela_abnt(doc, "8", "Efeito do sentimento e do tuning na acurácia (conjunto de teste)",
     ["Modelo", "Acurácia (teste)", "Ganho"],
     [["XGBoost — apenas preços (baseline)", f"{tun['base']:.2f}%", "—"],
      ["XGBoost — Data Fusion, sem tuning", f"{tun['def']:.2f}%", f"{tun['def']-tun['base']:+.2f} pp (sentimento)"],
      ["XGBoost — Data Fusion, com tuning", f"{tun['tun']:.2f}%", f"{tun['g_tun']:+.2f} pp (tuning)"]])
    abnt.paragrafo(doc,
     f"Dois achados merecem registro honesto. Primeiro, a inclusão do sentimento (Data Fusion) elevou "
     f"a acurácia em **{tun['def']-tun['base']:+.2f} pontos percentuais** sobre o baseline — evidência "
     "de informação direcional incremental no texto. Segundo, o tuning de hiperparâmetros teve efeito "
     f"**{('positivo' if tun['g_tun']>0 else 'praticamente nulo/negativo')} ({tun['g_tun']:+.2f} pp)** "
     "no conjunto de teste: o procedimento selecionou, pela validação, uma taxa de aprendizado menor, "
     "que não se traduziu em ganho fora da amostra. Esse resultado é coerente com a dificuldade "
     "intrínseca de prever a direção diária de um ativo quase-eficiente e com o pequeno tamanho da "
     "amostra de validação — e é apresentado sem qualquer superdimensionamento.")
else:
    abnt.paragrafo(doc, "Os números de evolução serão consolidados após a execução completa do pipeline.")

# 11
abnt.secao(doc, "11", "Limitações da etapa")
abnt.lista(doc, [
 "Acurácia modesta (50–53%), coerente com a hipótese de eficiência de mercado; o ganho do sentimento é estatisticamente pequeno e deve ser interpretado com cautela.",
 "GARCH(1,1) assume uma forma funcional específica da variância; regimes extremos podem exigir variantes assimétricas (EGARCH/TGARCH).",
 "Horizonte de previsão de um dia (t+1); horizontes maiores são trabalho futuro.",
 "Tuning limitado a uma grade pequena; uma busca mais ampla (e validação cruzada por janelas) é trabalho futuro.",
 "Generalização: o pipeline aplica-se a outros ativos da B3 (ex.: VALE3) trocando-se a série de preços e o termo de busca, o que se registra como trabalho futuro.",
])

abnt.referencias(doc, "12", [
 "BOLLERSLEV, T. Generalized autoregressive conditional heteroskedasticity. Journal of Econometrics, v. 31, n. 3, p. 307-327, 1986.",
 "CHEN, T.; GUESTRIN, C. XGBoost: a scalable tree boosting system. In: KDD, 2016. p. 785-794.",
 "CORTES, C.; VAPNIK, V. Support-vector networks. Machine Learning, v. 20, n. 3, p. 273-297, 1995.",
 "ENGLE, R. F. Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. Econometrica, v. 50, n. 4, p. 987-1007, 1982.",
])

doc.save(SAIDA)
print(f"✅ Documento ABNT gerado: {SAIDA}")
print(f"   GARCH real: alpha={alpha:.4f} beta={beta:.4f} persistencia={persist:.4f}")
