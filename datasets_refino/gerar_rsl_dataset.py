# -*- coding: utf-8 -*-
# ==============================================================================
#  gerar_rsl_dataset.py — Dataset estruturado da Revisão Sistemática (item 5)
#  Dissertação PETR4 | Vanderlei Barbosa da Silva
#
#  FONTES (nada inventado):
#   • Referencial Cap.2 — longtable "tab:rsl_artigos" (25 estudos) + discussão.
#   • references.bib — título e veículo de cada estudo.
#   • PDFs em Referencial_Teorico/ — RESUMO/método de cada artigo, de onde foram
#     extraídos: FONTE das notícias, MÉTODO de coleta, parâmetros e resultados.
#
#  Campos não reportados no resumo do artigo ficam como "ver artigo" — nunca
#  preenchidos com valores inventados.
# ==============================================================================
from pathlib import Path
import csv

OUT = Path(__file__).resolve().parents[1] / "datasets_refino"
VER = "ver artigo (não consta no resumo lido)"

# num, autor, ano, idioma, veiculo, titulo, objetivo, metodo, encoder,
# fonte_noticias, metodo_coleta, parametros, resultados, fonte_registro
R = [
 (1,"Tetlock","2007","Inglês","The Journal of Finance","Giving content to investor sentiment: the role of media in the stock market",
  "Provar que o pessimismo da mídia antecede quedas de retorno e ↑ volatilidade","VAR; análise de conteúdo","Léxico/dicionário (Harvard-IV)",
  "Wall Street Journal — coluna diária 'Abreast of the Market'","Contagem de palavras da coluna do WSJ",
  "Dicionário psicossocial Harvard-IV","Pessimismo alto prevê queda de retorno e reversão; ↑ volatilidade","Cap.2 + Tetlock(2007) (sem PDF local)"),
 (2,"Schumaker e Chen","2009","Inglês","Information Processing & Management","A quantitative stock prediction system based on financial news (AZFinText)",
  "Unir preços e texto por SVM (sistema AZFinText)","SVM supervisionado","Bag-of-words / Proper Nouns / Named Entities",
  "Yahoo Finance (compilação de ~45 fontes: Associated Press, Financial Times, PRNewsWire…)","Coleta de artigos de notícias financeiras (S&P 500)",
  "SVR/SVM; representação por Proper Nouns",VER,"PDF #26 (Referencial_Teorico)"),
 (3,"Nizer","2011","Português","PUCPR (dissertação)","Método para detecção do efeito de publicações de notícias no mercado de ações do Brasil",
  "Precursor de PLN aplicado à Bovespa (contexto BR)","Classificação de texto","TF-IDF (contagem)",
  "Notícias do mercado de ações brasileiro (Bovespa)","Coleta de publicações de notícias",VER,VER,"PDF #0 (dissertação PUCPR)"),
 (4,"Bollen et al.","2011","Inglês","Journal of Computational Science","Twitter mood predicts the stock market",
  "Mostrar que o humor de microblogs prevê o mercado","Séries temporais + rede neural (SOFNN)","Dimensões de humor (OpinionFinder + GPOMS)",
  "Twitter (tweets públicos)","Coleta de tweets; ferramentas OpinionFinder e Google Profile of Mood States",
  "6 dimensões de humor (GPOMS); alvo DJIA","~87,6% de acurácia na direção do DJIA","PDF #16"),
 (5,"Groß-Klußmann e Hautsch","2011","Inglês","Journal of Empirical Finance","When machines read the news: automated text analytics (alta frequência)",
  "Quantificar reações intradiárias à leitura automatizada de notícias","VAR de alta frequência (dados de 20s)","Sentimento pré-processado (relevância/novidade/direção)",
  "Reuters NewsScope Sentiment Engine (notícias por empresa)","Feed automatizado de notícias; ações da London Stock Exchange",
  "VAR; janelas de 20 segundos","Respostas distintas em retorno, VOLATILIDADE, volume e spread por chegada de notícia","PDF #21"),
 (6,"Wang et al.","2012","Inglês","Omega","Stock index forecasting based on a hybrid model",
  "Combinar modelos lineares e não lineares para índices","Modelo híbrido ESM+ARIMA+BPNN, peso por GA","Séries de preços (sem texto)",
  "Preços de índices (Shenzhen Integrated Index e Dow Jones) — SEM notícias","Cotações dos índices",
  "ESM+ARIMA+BPNN; pesos por algoritmo genético","Híbrido supera os modelos individuais","PDF #20"),
 (7,"Hagenau et al.","2013","Inglês","Decision Support Systems","Automated news reading: context-capturing features",
  "Elevar a acurácia com atributos sensíveis ao contexto + feedback de mercado","Seleção de atributos + classificação (SVM)","N-gramas / 2-word combinations (context features)",
  "Notícias corporativas (ad-hoc announcements, mercados alemão/UK)","Feed de anúncios corporativos",
  "Seleção robusta de atributos; SVM","Acurácia significativamente acima de abordagens anteriores (próximas ao acaso)","PDF #11"),
 (8,"Corredor et al.","2013","Inglês","Int. Review of Economics & Finance","Investor sentiment effect in stock markets",
  "Evidenciar efeitos assimétricos do sentimento (mercados europeus)","Econométrico (painel)","Proxies de sentimento do investidor",
  "Proxies de sentimento (não coleta notícias); FR, DE, ES, UK","Índices/proxies de sentimento",VER,
  "Sentimento influencia retornos, com intensidade variável por mercado e características do ativo","PDF #8"),
 (9,"Li et al.","2014","Inglês","Information Sciences","The effect of news and public mood on stock movements",
  "Impacto conjunto de notícias corporativas e humor público","Text mining + análise de sentimento","Léxico + sentimento de fóruns",
  "Notícias + postagens do Yahoo! Finance (fóruns/discussion boards)","Coleta de notícias e posts de fóruns",VER,
  "Notícias e humor público afetam significativamente os movimentos","PDF #15"),
 (10,"Ballings et al.","2015","Inglês","Expert Systems with Applications","Evaluating multiple classifiers for stock price direction prediction",
  "Comparar (benchmark) classificadores na direção binária","Benchmark: RF, AdaBoost, Kernel Factory vs NN, LR, SVM, KNN","Atributos de preço/indicadores (sem texto)",
  "Dados de 5.767 empresas europeias listadas (preços/fundamentos) — SEM notícias","Base de mercado (1 ano à frente)",
  "Ensembles vs classificadores únicos; métrica AUC","Random Forest é o melhor; ensembles superam classificadores únicos","PDF #4"),
 (11,"Nguyen et al.","2015","Inglês","Expert Systems with Applications","Sentiment analysis on social media for stock movement prediction",
  "Incorporar sentimento por TÓPICO de mídias sociais","Modelo tópico-sentimento (TSLDA) + classificação","TSLDA (tópico + sentimento conjuntos)",
  "Mídias sociais (message boards) + preços do Yahoo Finance","Posts de fóruns; rótulos de alta/baixa por data",
  "TSLDA (variante de LDA)","+6,07% de acurácia sobre modelo só-preços; supera LDA/JST","PDF #1"),
 (12,"Fernández-Gavilanes et al.","2016","Inglês","Expert Systems with Applications","Unsupervised method for sentiment analysis in online texts",
  "Reduzir dependência de léxicos estáticos","Parsing de dependências não supervisionado","Léxicos expandidos semiautomaticamente",
  "Textos online (tweets/reviews: Cornell Movie Review, Obama-McCain, SemEval-2015) — NÃO é previsão de ações","Datasets públicos de sentimento",
  "Algoritmo de expansão de polaridade","Desempenho competitivo e robusto nos datasets de sentimento","PDF #13"),
 (13,"Oliveira et al.","2017","Inglês","Expert Systems with Applications","The impact of microblogging data for stock market prediction",
  "Avaliar indicadores de sentimento para retorno, VOLATILIDADE e volume","Regressão; janelas deslizantes; testes formais de previsão","Indicadores de sentimento/atenção (StockTwits/Twitter)",
  "Grande dataset do Twitter + índices de survey (AAII, II, USMC, Sentix)","Coleta de microblogs; agregação diária de sentimento/atenção",
  "Vários esquemas de agregação diária; validação com janelas deslizantes","Valor preditivo para retorno, volatilidade e volume de negociação","PDF #17"),
 (14,"Barak et al.","2017","Inglês","Information Fusion","Fusion of multiple diverse predictors in stock market",
  "Fundir preditores diversos para retorno e risco","Fusão (Bagging/Boosting/AdaBoost) + meta-classificador","Múltiplos classificadores heterogêneos",
  "Não especificado no resumo (dados de mercado)","Clustering do dataset + seleção de classificadores",
  "Bagging/Boosting/AdaBoost; Decision/LAD/Rep Tree","Até 83,6% (retorno) e 88,2% (risco) de acurácia","PDF #9"),
 (15,"Vargas et al.","2017","Inglês","IEEE (conf.)","Deep learning for stock market prediction from financial news articles",
  "Prever movimento intradiário com notícias + indicadores técnicos","Aprendizado profundo (CNN e RNN)","word2vec (média dos vetores do título) + CNN/RNN",
  "Títulos de notícias financeiras + indicadores técnicos; índice S&P 500","Coleta de títulos de notícias e séries do S&P 500",
  "word2vec; CNN e RNN","CNN capta melhor a semântica; RNN o contexto temporal; melhora sobre estudos anteriores","PDF #3"),
 (16,"Silva","2018","Português","Universidade de Brasília (tese doutorado)","O efeito do sentimento das notícias sobre o comportamento dos preços no mercado acionário brasileiro",
  "Mostrar, via GARCH, que o sentimento afeta VOLATILIDADE e retorno no Brasil (base direta desta pesquisa)","Léxico + regressão penalizada + regressão quantílica + GARCH","Contagem léxica",
  "Jornal Valor Econômico (mais de 45 mil notícias) + índice IBOVESPA","Coleta de notícias do Valor Econômico",
  "Regressão quantílica condicionada à incerteza; GARCH","Efeito assimétrico do sentimento ao longo da distribuição do retorno; contribui para prever volatilidade","PDF #14 + Cap.2"),
 (17,"Calomiris e Mamaysky","2019","Inglês","Journal of Financial Economics","How news and its context drive risk and returns around the world",
  "Prever risco e retorno em 51 países via contexto das notícias","Econométrico + NLP (classificação de contexto/tópico)","Tópicos e sentimento de notícias",
  "Thomson Reuters — base completa de notícias (1996–2015)","Base histórica cedida pela Thomson Reuters; 51 mercados",
  "Resumo parcimonioso de notícias (tópico/sentimento/frequência)","Notícias preveem risco e retorno; efeito mais severo em mercados emergentes","PDF #7"),
 (18,"Henrique et al.","2019","Inglês","Expert Systems with Applications","Literature review: machine learning techniques applied to financial market prediction",
  "Revisar algoritmos de ML na previsão financeira","Revisão sistemática + main path analysis","— (survey)",
  "— (revisão; sem coleta de notícias)","Análise de caminho principal da literatura",VER,
  "Mapeia técnicas de ML e o crescimento das publicações (usado como Fig. de crescimento no Cap.2)","PDF #24"),
 (19,"Nobre e Neves","2019","Inglês","Expert Systems with Applications","Combining PCA, Discrete Wavelet Transform and XGBoost to trade",
  "Demonstrar eficácia do XGBoost com pré-processamento","ML + pré-processamento; otimização MOO-GA","PCA + Wavelet; XGBoost",
  "Preços de índices financeiros — SEM notícias","Séries de preços/indicadores",
  "PCA (redução) + DWT (denoise); XGBoost com hiperparâmetros por MOO-GA","Sinal de negociação lucrativo (entrada/saída)","PDF #6"),
 (20,"Li et al.","2020","Inglês","Information Processing & Management","Incorporating stock prices and news sentiments for stock market prediction (Hong Kong)",
  "Fundir preços e sentimento de notícias com aprendizado sequencial","Deep learning (fusão preços + texto)","Vetores de sentimento + indicadores técnicos",
  "Artigos de notícias + preços de ações — mercado de Hong Kong (HKEX)","Coleta de notícias e cotações",VER,
  "A fusão de indicadores técnicos e sentimento melhora a previsão","PDF #10"),
 (21,"Carta et al.","2021","Inglês","Expert Systems with Applications","Multi-DQN: ensemble of Deep Q-learning agents for stock forecasting",
  "Usar ensembles de RL; apontar necessidade de alta frequência","Aprendizado por reforço (Deep Q-Learning), TD-learning","Ensemble de agentes DQN",
  "Dados históricos de mercado (preços) — SEM notícias","Séries de preços; sinais intradiários","Ensemble de DQN; recompensa por retorno",VER,"PDF #12"),
 (22,"Odhiambo Omuya et al.","2021","Inglês","Expert Systems with Applications","Feature selection for classification using PCA and Information Gain",
  "Melhorar classificação por seleção de atributos","Seleção de atributos (filtro) + classificação","PCA + ganho de informação",
  "Datasets genéricos de classificação/sentimento (não financeiros específicos)","Datasets públicos",
  "PCA + ganho de informação (modelo de filtro)","Seleção de atributos melhora desempenho e reduz dimensionalidade","PDF #25"),
 (23,"Farimani et al.","2022","Inglês","Information","From text representation to financial market prediction: a review",
  "Mapear TF-IDF → representações profundas na previsão","Revisão sistemática (>150 publicações)","— (survey: TF-IDF → embeddings → Transformers)",
  "— (revisão; fusão de dados heterogêneos)","Levantamento de publicações",VER,
  "Documenta a transição das representações de contagem para vetores profundos (Transformers)","PDF #23"),
 (24,"Narde et al.","2024","Português","Symposium on Knowledge Discovery (KDMiLe)","Classificação de notícias em português com transferência de aprendizagem e Transformers",
  "Validar modelos BERT na classificação de notícias/tweets em PT (tarefa: veracidade/fake news)","Aprendizado por transferência (fine-tuning)","BERT/BERTimbau (5 Transformers)",
  "X (ex-Twitter) em português (PT-BR) — base própria rotulada e aberta","Extração de postagens do X; rotulagem de veracidade",
  "5 modelos Transformer treinados em PT; BERT ajustado","BERT ajustado: 95,1% de acurácia (classificação de veracidade, não previsão de ações)","PDF #5"),
 (25,"Cardoso e Nakane","2024","Português","Preprint","What's in a headline? News impact on the Brazilian economy",
  "Analisar o impacto sistêmico das manchetes na economia BR","LDA → índices mensais → VAR estrutural","LDA (modelagem de tópicos)",
  "Jornal Valor Econômico (jul/2011 a dez/2022)","Coleta de artigos do Valor Econômico; agregação mensal",
  "LDA; dois índices de notícias; VAR estrutural (news vs noise shocks)","Choques de notícias impactam significativamente preços de ativos e indicadores macro","PDF #18"),
]

CAB = ["#","Autor(es)","Ano","Idioma","Veiculo","Titulo","Objetivo_Contribuicao","Metodo",
       "Encoder_Representacao","Fonte_Noticias","Metodo_Coleta","Parametros","Resultados_obtidos","Fonte_do_registro"]

for f in OUT.glob("04_revisao_sistematica_estudos_v1.csv"):
    f.unlink()
with open(OUT / "04_revisao_sistematica_estudos_v1.csv", "w", newline="", encoding="utf-8-sig") as fp:
    w = csv.writer(fp); w.writerow(CAB)
    for row in R:
        w.writerow(row)
print("✓ 04_revisao_sistematica_estudos_v1.csv:", len(R), "estudos, com Fonte_Noticias e Metodo_Coleta.")
