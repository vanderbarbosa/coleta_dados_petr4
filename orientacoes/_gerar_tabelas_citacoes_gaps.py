# -*- coding: utf-8 -*-
"""
Gera as duas tabelas estruturadas pedidas pelo orientador:

  1. citacoes_por_trabalho.csv — para cada trabalho que cita Santos, Bianchi e
     Costa (2023): o trecho LITERAL da citacao, a secao, por que citou, se o
     modelo foi executado e a ligacao com a nossa pesquisa.

  2. gaps_pesquisa.csv — os 13 gaps identificados, com evidencia, aderencia,
     como resolver, prioridade, esforco e dependencia de rotulagem.

Trechos transcritos do texto integral dos artigos (arquivos _*.txt nesta pasta)
e cruzados com o campo `contexts` da API do Semantic Scholar.
"""
import csv
from pathlib import Path

AQUI = Path(__file__).parent

# ─────────────────────────────────────────────────────────────────────────────
COL_CIT = [
    "#", "Trabalho", "Data", "Veiculo", "N. de citacoes", "Secao onde cita",
    "Trecho LITERAL da citacao", "Por que citou (funcao retorica)",
    "Executou o FinBERT-PT-BR?", "Encoder/tecnologia propria",
    "Ligacao com a nossa pesquisa", "O que aproveitar", "Relevancia",
]

CITACOES = [
    (1,
     "BLOCH, A.; SANTANA, C.; AMANTINO, M. Os jesuitas e a Era do Algoritmo: uma introducao a "
     "analise de sentimentos da correspondencia colonial ultramarina portuguesa.",
     "13/04/2026", "Estudos Ibero-Americanos, v. 52, n. 1 (PUCRS) - DOI 10.15448/1980-864x.2026.1.46315",
     "1",
     "Secao 4 - Metodo (justificativa da composicao do comite)",
     "\"Para que a abordagem de comite produza resultados promissores, e essencial a selecao de "
     "modelos de analise de sentimentos que tenham caracteristicas distintas e complementares. Os "
     "modelos que selecionamos se enquadram nesse requisito, pois um deles - treinado em uma base "
     "financeira (Santos; Bianchi; Costa, 2023) - mostra resultados fortemente influenciados pela "
     "presenca de termos negativos ou positivos, enquanto o segundo - treinado em uma base mais "
     "geral com conteudo em portugues (Perez et al., 2021) - analisa mais o contexto em que os "
     "termos aparecem. Em conjunto, os dois modelos apresentam uma boa capacidade de identificacao "
     "de sentimentos, o que pode ser verificado nos experimentos em que comparamos, para um "
     "subconjunto de textos, a classificacao do comite com a de um historiador.\"",
     "ESCOLHA DE FERRAMENTA. Unica citacao, entre as sete, que revela conhecimento empirico do "
     "modelo em operacao - justifica por que o FinBERT-PT-BR foi escolhido como membro do comite, "
     "com base numa caracterizacao do seu comportamento.",
     "SIM - unico dos sete que executou o modelo, em Maquina de Comite com o pysentimiento, "
     "abordagem autossupervisionada escolhida para evitar criar base de treino rotulada; "
     "validada contra a classificacao de um historiador num subconjunto.",
     "FinBERT-PT-BR + pysentimiento (Perez et al., 2021) em comite com moderador por voto",
     "(1) A caracterizacao 'fortemente influenciado pela presenca de termos negativos ou positivos' "
     "e achado independente que EXPLICA a nossa matriz de confusao - a classe Neutra e a mais "
     "confundida (58 de 124 casos neutros foram para os extremos), assinatura de modelo dominado "
     "por lexico e nao por contexto. Passamos a ter explicacao com respaldo externo para o kappa "
     "de 0,371. (2) O desenho de validacao e o mesmo do nosso conjunto-ouro (automatico x "
     "especialista humano num subconjunto), o que o torna precedente metodologico citavel.",
     "Replicar a MAQUINA DE COMITE no nosso corpus: FinBERT-PT-BR (lexico, financeiro) + modelo "
     "geral de contexto, por voto / media de probabilidades / regra de abstencao. E a contrapartida "
     "exata da fraqueza medida, custa pouco e NAO consome rotulo. Ver gap G7. Aproveitar tambem a "
     "discussao da secao 'Desafios enfrentados' sobre a qualidade dos dados condicionar o "
     "desempenho da IA - citacao elegante, de fora da area, para justificar o conjunto-ouro humano.",
     "MUITO ALTA"),

    (2,
     "ABILIO, R.; COELHO, G. P.; SILVA, A. D. Evaluating Named Entity Recognition: a comparative "
     "analysis of mono- and multilingual transformer models on a novel Brazilian corporate "
     "earnings call transcripts dataset.",
     "18/03/2024", "Applied Soft Computing (Elsevier, Q1) - DOI 10.1016/j.asoc.2024.112158",
     "3",
     "Secao 2.1 - Pre-training Transformer-based models for the Financial domain",
     "(i) \"Examples of these models include FinBERT [27], FinBERT PT-BR [28], and FLANG-BERT and "
     "FLANG-ELECTRA [29].\" | (ii) \"The FinBERT-PT-BR [28] model is based on BERTimbau [22], "
     "another BERT-based model, but pre-trained on Brazilian Portuguese corpora. In FinBERT-PT-BR, "
     "the authors continued the pre-training of BERTimbau by adding news from the Brazilian "
     "financial market.\" | (iii) \"Besides, unlike Santos et al. [28], our dataset comprises text "
     "from earnings call transcripts for NER, while they used financial news for Sentiment "
     "Analysis.\"",
     "DUPLA: (a) posicionar o FinBERT-PT-BR numa taxonomia internacional de modelos de dominio "
     "financeiro, ao lado do FinBERT (EN) e da familia FLANG; (b) DELIMITAR A PROPRIA CONTRIBUICAO "
     "POR CONTRASTE. Intent classificado pelo Semantic Scholar como 'methodology' - o unico dos "
     "sete com essa classificacao.",
     "Nao",
     "BERTimbau, PTT5, mBERT, mT5 - dataset proprio BraFiNER (earnings calls de bancos brasileiros)",
     "Evidencia INDEPENDENTE, em periodico Q1, de que encoders monolingues PT-BR superam "
     "multilingues em dominio financeiro (BERT supera T5; BERTimbau supera PTT5). Sustenta a nossa "
     "escolha por FinBERT-PT-BR/BERTimbau contra XLM-R e mDeBERTa. Registram ainda que PTT5 e mT5 "
     "GERARAM SENTENCAS COM ALTERACAO DE VALORES MONETARIOS E PERCENTUAIS - advertencia critica "
     "para qualquer uso de LLM generativo em pipeline financeiro.",
     "(1) Citar como sustentacao da escolha do encoder monolingue. (2) Usar a advertencia sobre "
     "modelos generativos como contraponto obrigatorio ao entusiasmo com LLMs (trabalho 4). "
     "(3) Avaliar o BraFiNER como corpus adicional para a etapa de MLM de dominio. (4) IMITAR O "
     "PADRAO RETORICO: eles citam Santos para dizer 'o nosso e diferente porque X'; a nossa "
     "dissertacao precisa da mesma frase, com o nosso X = ativo unico + volatilidade + fusao GARCH.",
     "ALTA"),

    (3,
     "IMAI, B. Y. L.; GARCIA, C. M.; ROCHA, M. V.; KOERICH, A. L.; BRITTO JR., A. S.; BARDDAL, J. P. "
     "Is it fine to tune? Evaluating SentenceBERT fine-tuning for Brazilian Portuguese text stream "
     "classification.",
     "15/12/2024", "IEEE International Conference on Big Data - DOI 10.1109/BigData62323.2024.10825456",
     "1",
     "Trabalhos relacionados (paragrafo de delimitacao da contribuicao)",
     "\"Even though we acknowledge the existence of similar works, such as Santos et al. [24], "
     "their approach differs from ours in the following aspects: (a) our approach considers the "
     "text stream paradigm, respecting the temporal order; (b) although the authors used BERTimbau "
     "as a base LM, they fine-tuned...\" [TRECHO TRUNCADO na base do Semantic Scholar; texto "
     "integral atras do paywall do IEEE Xplore - obter pelo Portal CAPES/PUCPR]",
     "EXCLUSIVAMENTE PARA SE DIFERENCIAR. Reconhecem Santos como trabalho similar e listam, ponto "
     "a ponto, por que o deles e diferente. O primeiro diferencial declarado e o mais importante "
     "para nos: Santos NAO respeita a ordem temporal.",
     "Nao",
     "SentenceBERT (SBERT) com fine-tuning anual + Adaptive Random Forest",
     "ATENCAO INSTITUCIONAL: Barddal e Britto Jr. sao professores do PPGIa da PUCPR - o nosso "
     "programa. A critica que fazem a Santos APLICA-SE HOJE A NOS: usamos modelo congelado em "
     "13/02/2024 sobre corpus de 2018 a 2026, sem respeitar deriva temporal. Se a banca ler este "
     "artigo, a pergunta vem pronta. Eles tambem dao o metodo: fine-tuning anual com amostra "
     "reduzida de textos recentes supera o modelo estatico na maioria dos anos.",
     "(1) Declarar formalmente a limitacao de concept drift com este respaldo. (2) Medir a "
     "degradacao por subperiodo - ja temos resultados_subperiodo_petr4.csv. (3) Considerar "
     "adaptacao incremental por ano. (4) Consultar os autores diretamente - e colaboracao interna "
     "de baixo custo. Ver gap G4.",
     "ALTA"),

    (4,
     "TELES, L. E. P.; FIGUEIREDO, C. M. S. Comparing LLMs for sentiment analysis in financial "
     "market news.",
     "03/10/2025", "arXiv:2510.15929 - Universidade do Estado do Amazonas (UEA), fomento FAPEAM",
     "2",
     "Introducao, primeiro e segundo paragrafos",
     "(i) \"Sentiment analysis is one of the techniques used in the field of NLP to identify and "
     "extract information about the emotions expressed in a text, such as positivity, negativity, "
     "or neutrality [Santos et al. 2023].\" | (ii) \"The goal is to understand how people feel "
     "about a particular issue or product [Santos et al. 2023].\"",
     "PURAMENTE DEFINICIONAL. Santos e usado apenas para definir o que e analise de sentimento - "
     "funcao que qualquer survey cumpriria igualmente bem. Nao ha engajamento com o metodo, com os "
     "resultados nem com o modelo.",
     "Nao - e este e o ponto: artigo brasileiro, de analise de sentimento, de noticias, de mercado "
     "financeiro, cita Santos duas vezes e mesmo assim avalia NOVE modelos SEM incluir o "
     "FinBERT-PT-BR, sobre TRES conjuntos em ingles.",
     "SVM, Random Forest, MLP (classicos) x Gemma, DeBERTa, DeBERTaV3, XLM-RoBERTa, BART, "
     "Gemini 2.0-flash (LLMs). Datasets: Financial Phrase Bank, StockEmotions, Tweet Financial News",
     "OPORTUNIDADE: o Gemini foi o mais consistente (acuracia 80,4% / 74,1% / 78,9%). Se um LLM "
     "generativo supera encoders especializados EM INGLES, o mesmo teste EM PORTUGUES nao existe - "
     "e e o vao que este artigo deixa aberto. RESSALVA: o trabalho NAO sustenta que LLMs superariam "
     "o FinBERT-PT-BR em manchetes brasileiras (corpora em ingles; DeBERTa oscila de 86,2% a 47,8% "
     "conforme o dataset). E o exemplo mais nitido do padrao que caracteriza a lacuna: o trabalho "
     "tematicamente mais proximo e o que menos engaja com o artefato.",
     "Classificar as 300 manchetes do conjunto-ouro com um LLM via prompt, usando a instrucao "
     "literal de Santos, e comparar contra o FinBERT-PT-BR e o rotulo humano. NAO consome rotulagem "
     "nova. Ver gap G6.",
     "MEDIA-ALTA (como oportunidade); BAIXA (como precedente)"),

    (5,
     "ALVES, M. A. R.; MACEDO, M. B.; RIBEIRO, J.; MANCINE, L.; PEREIRA JUNIOR, C. P. Sentimentos "
     "em Cena: uma analise dos comentarios em trailers de filmes da Netflix Brasil no YouTube.",
     "21/07/2024", "Anais do XIII BraSNAM (SBC) - DOI 10.5753/brasnam.2024.2974",
     "1",
     "Introducao (motivacao do trabalho)",
     "\"Porem, existe uma predominacao de analises de textos em ingles, demonstrando assim uma "
     "falta de trabalhos na lingua portuguesa [Santos et al. 2023].\"",
     "BACKGROUND. Sustentar a afirmacao de escassez de trabalhos de analise de sentimento em "
     "portugues. Intent classificado pelo Semantic Scholar como 'background'.",
     "Nao",
     "Nao declarado no trecho; dominio de entretenimento (comentarios de YouTube)",
     "Utilidade modesta porem direta: e citacao de TERCEIRO que corrobora a premissa de escassez da "
     "nossa introducao. Demonstra tambem que a difusao do FinBERT-PT-BR transbordou o dominio "
     "financeiro, o que e um dado sobre o artefato.",
     "Citar como 'Alves et al. (2024), apoiando-se em Santos et al. (2023), registram a "
     "predominancia de analises em ingles e a falta de trabalhos em portugues' - mais forte do que "
     "afirmar a escassez por conta propria.",
     "BAIXA"),

    (6,
     "REICHERT, M. H.; PERLIN, M. S. Using ChatGPT for creating multi-language finance related "
     "sentiment dictionaries.",
     "23/12/2025", "Computational Economics (Springer) - DOI 10.1007/s10614-025-11233-3",
     "nao verificado",
     "NAO VERIFICADA - texto integral atras do paywall da Springer",
     "NAO FOI POSSIVEL TRANSCREVER. A citacao a Santos et al. (2023) esta registrada por OpenAlex e "
     "Semantic Scholar, mas o trecho nao consta de nenhuma das duas bases e a pagina de resumo "
     "publica nao exibe a lista de referencias. E a UNICA das sete citacoes que permanece nao "
     "verificada quanto ao trecho literal. Obter o PDF pelo Portal de Periodicos da CAPES via PUCPR.",
     "Pendente de acesso ao texto integral.",
     "Provavelmente nao como classificador - o artefato central e um dicionario lexico, nao um "
     "modelo neural",
     "ChatGPT (API) para construcao de dicionarios de sentimento financeiro multilingues",
     "O PORTUGUES ESTA ENTRE AS LINGUAS COBERTAS e a validacao foi feita sobre os ultimos 50 "
     "comunicados do COPOM - texto financeiro brasileiro institucional. O resumo declara que o "
     "dicionario foi comparado a 'full-text NLP models' e apresentou 'a more balanced sentiment "
     "classification profile'. SE esses modelos de texto completo incluirem o FinBERT-PT-BR, este e "
     "o unico trabalho que o compara diretamente a uma alternativa - e o resultado nao lhe e "
     "favoravel. Vale confirmar. Marcelo Perlin e professor da UFRGS e autor de referencia em "
     "financas quantitativas no Brasil.",
     "Obter o dicionario e usa-lo como LINHA DE BASE LEXICA - o equivalente brasileiro do "
     "Loughran-McDonald, que hoje nos falta. Comparacao 'encoder x dicionario x LLM' no mesmo "
     "conjunto-ouro. Ver gap G8.",
     "MEDIA-ALTA"),

    (7,
     "TANAKA, S. A.; ANDRADE, J. V. C.; BOVO, A. B.; CONVERTI, A.; SANCHES, D. S.; SIQUEIRA, H. V. "
     "A machine learning-driven CRM approach for identifying member churn in a Brazilian "
     "agro-industrial cooperative: a practical case study.",
     "27/02/2026", "Algorithms, v. 19, n. 3 (MDPI) - DOI 10.3390/a19030180",
     "1",
     "Metodologia - fase de Modeling (CRISP-DM)",
     "\"Training and validation relied on stratified subsets to mitigate sampling bias [39,40], "
     "reflecting the CRISP-DM emphasis on representativeness during model assessment.\" "
     "[a referencia 39 e Santos, Bianchi e Costa (2023); a 40 e Chawla et al. (2002), do SMOTE]",
     "Sustentar o uso de AMOSTRAGEM ESTRATIFICADA como mitigacao de vies amostral. OBSERVACAO "
     "HONESTA: o artigo de Santos NAO trata de amostragem estratificada como contribuicao "
     "metodologica - usa validacao cruzada 5-fold, que e assunto proximo mas nao igual. A citacao "
     "parece IMPRECISA ou de conveniencia; o par [39,40] faz muito mais sentido para o SMOTE.",
     "Nao - o trabalho nem sequer opera com texto (dados tabulares de CRM)",
     "Random Forest, XGBoost, SVC, ensemble por votacao, AutoML e SHAP",
     "Relacao muito baixa. Unico aproveitamento e lateral: o uso de SHAP para explicabilidade de "
     "modelos tabulares.",
     "Aplicar SHAP ao nosso XGBoost de fusao (modelo_xgb_fusion.json) para quantificar a "
     "contribuicao MARGINAL do sentimento na previsao de volatilidade - responde a ponderacao da "
     "banca sobre se o sentimento realmente ajuda. NAO citar este trabalho como evidencia de adocao "
     "do FinBERT-PT-BR. Ver gap G13.",
     "MUITO BAIXA"),
]

# ─────────────────────────────────────────────────────────────────────────────
COL_GAP = [
    "ID", "Gap", "Prioridade", "Evidencia (fonte concreta)", "Por que o gap existe",
    "Aderencia a dissertacao", "Como resolver", "Consome rotulagem?",
    "Executavel ate 10/08/2026?", "Esforco", "Onde entra na dissertacao", "Risco / ressalva",
]

GAPS = [
    ("G1", "Previsao de VOLATILIDADE de ativo brasileiro a partir de sentimento de noticias",
     "MAXIMA",
     "Dos 7 trabalhos citantes e dos 28 referenciados no artigo-base, NENHUM preve volatilidade. "
     "Todos operam sobre direcao, retorno ou estrategia de carteira: Santos et al. (2023) constroem "
     "indice agregado e carteira; Hiew et al. (2019) preveem retorno com LSTM; Bollen et al. (2011) "
     "e Pagolu et al. (2016) preveem direcao; Januario et al. (2022) nao tratam volatilidade.",
     "A literatura converge para desempenho de DIRECAO proximo ao acaso - os 87,6% de Bollen et al. "
     "(2011) nunca foram replicados de forma robusta. Diante disso os trabalhos migram para "
     "carteira, indice agregado ou comparacao de classificadores. Poucos migram para volatilidade, "
     "que e onde o sinal textual tem conteudo: noticia gera INCERTEZA antes de gerar direcao.",
     "TOTAL - e literalmente o titulo da dissertacao",
     "Ja esta parcialmente resolvido: GARCH(1,1), Mincer-Zarnowitz/QLIKE e regressao quantilica de "
     "volatilidade ja rodam (resultados_volatilidade_petr4.json, resultados_vol_quantilica_petr4.json, "
     "resultados_vol_sentimento_petr4.json). O que falta e EDITORIAL: reposicionar a volatilidade "
     "como resultado principal e a direcao como resultado negativo reportado, com a literatura "
     "sustentando que o acaso na direcao e o padrao da area, e nao falha nossa.",
     "Nao", "Sim (editorial)", "Baixo", "Contribuicao principal",
     "Nenhum risco relevante - e consolidacao do que ja existe."),

    ("G2", "Degradacao por TRANSFERENCIA DE DOMINIO: noticias gerais -> ativo especifico",
     "MAXIMA",
     "Santos et al. (2023) relatam acuracia 0,76 e F1 0,73 sobre sentencas de noticias gerais de "
     "mercado. Medimos 0,58 (kappa 0,371) sobre manchetes de PETR4 "
     "(conjunto_ouro/relatorio_validacao_ouro.txt). Nenhum trabalho da literatura examinada "
     "quantifica essa degradacao; o proprio autor nao a testou.",
     "Modelos de dominio financeiro sao publicados com metricas de dominio generico e reutilizados "
     "em subdominios sem revalidacao. E problema conhecido em PLN, mas NAO documentado para o par "
     "(sentimento financeiro PT-BR -> ativo unico).",
     "TOTAL - e pre-requisito de validade de todo o resto",
     "(1) Decompor as causas: unidade textual (sentenca x manchete), escopo (mercado geral x ativo "
     "unico) e gabarito (dupla anotacao x anotador unico). As duas primeiras sao isolaveis com o "
     "corpus atual, sem rotular nada (ver G9). (2) Explicar o mecanismo com a hipotese de Bloch et "
     "al. (2026): o modelo opera por lexico e nao por contexto - nossa matriz de confusao corrobora, "
     "a classe Neutra e a mais confundida. (3) Elevar a RESULTADO em vez de tratar como limitacao.",
     "Nao", "Sim (editorial)", "Baixo", "Resultado proprio (capitulo de resultados)",
     "A validade da medida depende da qualidade do gabarito (ver G5). Declarar a dependencia."),

    ("G3", "Adaptacao de dominio ao nivel de SETOR/ATIVO, e nao de mercado",
     "ALTA",
     "Santos et al. (2023) declaram em Trabalhos Futuros, literalmente: 'utilizando uma base maior "
     "e mais especifica de textos financeiros' e 'aplicar a metodologia para setores especificos da "
     "bolsa de valores'. Passados tres anos, nenhum dos sete trabalhos citantes o fez.",
     "Exige corpus setorial grande, que e caro de montar. Nos ja o temos: ~205 mil noticias de "
     "PETR4/petroleo/estatais.",
     "ALTA - melhora o insumo de todo o pipeline a jusante",
     "Replicar a Etapa 1 de Santos: masked language modeling com mascara de 15% e lr 2e-5, partindo "
     "(i) do proprio FinBERT-PT-BR e (ii) do BERTimbau large, medindo PERPLEXIDADE em holdout de 10 "
     "mil noticias nao vistas. Alvo: bater a perplexidade do modelo de partida, como Santos bateu o "
     "BERTimbau (1,51 -> 1,24).",
     "NAO - e self-supervised", "Sim (Colab, 6-10 h)", "Medio",
     "Capitulo de metodo + capitulo de resultados",
     "O HuggingFace publica apenas o CLASSIFICADOR (BertForSequenceClassification), nao o modelo de "
     "linguagem puro. Continuar o MLM a partir dele significa partir de modelo ja ajustado - viavel "
     "via AutoModelForMaskedLM, mas menos limpo. Rodar as DUAS variantes; a comparacao entre elas e, "
     "ela propria, um resultado."),

    ("G4", "CONCEPT DRIFT em sentimento financeiro PT-BR",
     "ALTA",
     "Imai et al. (2024) demonstram que modelos estaticos degradam em fluxos de noticias "
     "brasileiras e que o fine-tuning anual com amostra reduzida supera o estatico na maioria dos "
     "anos. Citam Santos justamente para dizer que ele NAO respeita a ordem temporal. Nenhum "
     "trabalho de sentimento financeiro em PT-BR trata do problema.",
     "Exige serie temporal longa e reprocessamento periodico - custoso e pouco valorizado em "
     "publicacao, mas critico para validade.",
     "ALTA - e ameaca a validade interna dos nossos resultados: usamos modelo congelado em "
     "13/02/2024 sobre corpus de 2018 a 2026",
     "Tres niveis: (1) MINIMO e obrigatorio - declarar a limitacao no capitulo de metodo com Imai et "
     "al. (2024) como respaldo (custo: um paragrafo). (2) INTERMEDIARIO e recomendado - medir a "
     "degradacao por subperiodo, ja temos resultados_subperiodo_petr4.csv; se a acuracia cair nos "
     "anos recentes, temos evidencia de drift, o que e um RESULTADO. (3) AMBICIOSO - adaptacao de "
     "dominio incremental por ano, medida por perplexidade; combina com G3 e nao consome rotulo.",
     "Nao", "Parcial (niveis 1 e 2)", "Baixo/Medio", "Limitacoes + capitulo de resultados",
     "Barddal e Britto Jr., autores do trabalho, sao do PPGIa/PUCPR - vale consulta direta."),

    ("G5", "Ausencia de BENCHMARK publico de sentimento financeiro rotulado em PT-BR",
     "ALTA",
     "Tres camadas de evidencia: (1) Santos et al. (2023) NAO publicaram os 503 textos rotulados - o "
     "repositorio HuggingFace tem dez arquivos e nenhum dado de treinamento; (2) Teles e Figueiredo "
     "(2025), diante da falta de conjunto brasileiro, recorrem a tres conjuntos em INGLES, o "
     "Financial Phrase Bank inclusive em versao traduzida; (3) nao existe em portugues equivalente "
     "ao Financial PhraseBank (Malo et al., 2014).",
     "Anotacao e cara e nao rende publicacao sozinha. Mas e precisamente o que trava a area inteira.",
     "ALTA - e e o gap que dialoga diretamente com a orientacao de suspender a rotulagem. Nao ha "
     "contradicao: o Prof. Emerson mandou parar a rotulagem NA FORMA ATUAL, que tem defeito "
     "estrutural (anotador unico, sem metrica de concordancia). Refundar o protocolo transforma um "
     "passivo em contribuicao.",
     "Quando a rotulagem for retomada, nesta ordem: (1) DUPLA ANOTACAO de 100 a 150 manchetes das "
     "300 ja rotuladas - nao mais volume, segunda opiniao; (2) calcular KRIPPENDORFF'S ALPHA "
     "(Artstein e Poesio, 2008; Krippendorff, 2018), que admite numero variavel de anotadores por "
     "item e dados faltantes, ao contrario do kappa de Cohen; (3) adotar a definicao operacional "
     "literal de Santos e a categoria 'nao se aplica' com descarte por discordancia; (4) usar "
     "modelagem de topicos ou zero-shot para pre-selecionar textos e sugerir classe ao anotador "
     "(Poursabzi-Sangdeh e Boyd-Graber, 2015; Alcoforado et al., 2022) - RESPOSTA TECNICA DIRETA a "
     "objecao sobre falta de especializacao em financas; (5) publicar com DOI (Zenodo) e licenca "
     "aberta.",
     "SIM", "NAO (rotulagem suspensa)", "Alto", "Contribuicao de artefato",
     "Um conjunto-ouro publico de sentimento financeiro PT-BR ancorado num ativo real seria citavel "
     "independentemente dos resultados de previsao - contribuicao que sobrevive a dissertacao."),

    ("G6", "LLM generativo x encoder especializado em PORTUGUES financeiro",
     "ALTA",
     "Teles e Figueiredo (2025) mostram que LLMs superam modelos classicos em sentimento financeiro, "
     "com Gemini como mais consistente (acuracia 80,4% / 74,1% / 78,9%). Mas fazem isso "
     "inteiramente EM INGLES. A comparacao em portugues, contra um encoder de dominio, nao existe "
     "na literatura examinada.",
     "Exige gabarito em portugues, que quase ninguem tem - e o mesmo motivo de G5.",
     "ALTA - responde a pergunta que a banca fara ('por que nao usar um LLM?') com DADOS nossos, e "
     "nao com opiniao",
     "Classificar as 300 manchetes do conjunto-ouro com um LLM via prompt, usando a INSTRUCAO "
     "LITERAL de Santos ('Classifique a noticia considerando se o texto implicaria em uma "
     "rentabilidade Positiva, Negativa ou Neutra...'), e comparar contra o FinBERT-PT-BR e contra o "
     "rotulo humano nos mesmos itens. Reportar acuracia, F1-macro e kappa.",
     "NAO - usa o gabarito ja existente", "Sim (~4 h)", "Baixo", "Capitulo de resultados",
     "Tres resultados possiveis, todos publicaveis: LLM ganha (evidencia para migrar, achado inedito "
     "em PT-BR); encoder ganha (justificativa empirica para mante-lo, que hoje nao temos); empate (o "
     "argumento passa a ser custo, reprodutibilidade e determinismo, que favorecem o encoder). "
     "Declarar: nao determinismo do LLM (fixar seed/temperatura), custo por chamada, e a advertencia "
     "de Abilio et al. (2024) sobre alteracao de valores numericos por modelos generativos."),

    ("G7", "COMITE DE MODELOS complementares em sentimento financeiro PT-BR",
     "MEDIA-ALTA",
     "Bloch, Santana e Amantino (2026) aplicam maquina de comite combinando FinBERT-PT-BR "
     "(comportamento LEXICO) com pysentimiento (comportamento CONTEXTUAL), justamente porque sao "
     "complementares, e validam contra especialista humano. Fizeram em Historia; ninguem fez em "
     "financas.",
     "Gap descoberto na leitura integral, nao estava no radar. Comites sao vistos como engenharia e "
     "nao como contribuicao - mas aqui atacam uma fraqueza especifica e medida.",
     "ALTA e BARATA - a fraqueza que a nossa matriz de confusao revela e exatamente a que o comite "
     "corrige: a classe Neutra e a mais confundida (58 de 124 casos neutros foram para os extremos), "
     "assinatura de modelo dominado por termos carregados. Um segundo modelo, contextual, tende a "
     "segurar esses casos.",
     "Rodar pysentimiento (versao PT) sobre o conjunto-ouro e combinar com o FinBERT-PT-BR por "
     "(i) voto simples, (ii) media das probabilidades e (iii) regra de abstencao - quando discordam, "
     "classificar como Neutro. Medir contra o gabarito humano.",
     "NAO", "Sim (~3 h)", "Baixo", "Capitulo de resultados",
     "Ganho adicional: um indice de sentimento construido sobre o comite e mais estavel, o que tende "
     "a melhorar o sinal na previsao de volatilidade (eixo de G1)."),

    ("G8", "DICIONARIO LEXICO financeiro PT-BR como linha de base",
     "MEDIA",
     "Reichert e Perlin (2025) constroem dicionarios de sentimento financeiro multilingues por "
     "ChatGPT, COM O PORTUGUES INCLUIDO e validados sobre os ultimos 50 comunicados do COPOM. "
     "Declaram comparacao contra 'full-text NLP models'. Nenhum trabalho compara diretamente "
     "dicionario lexico x encoder de dominio em portugues financeiro sobre noticias de um ativo.",
     "Dicionarios sao vistos como tecnologia antiga; a area migrou para encoders sem fechar a "
     "comparacao em portugues.",
     "MEDIA-ALTA - uma linha de base lexica e o que falta para o capitulo de resultados ter tres "
     "pontos de comparacao em vez de dois",
     "Obter o dicionario pelo Portal CAPES; aplicar as manchetes; comparar contra FinBERT-PT-BR, "
     "contra o comite de G7 e contra o LLM de G6, no mesmo conjunto-ouro.",
     "Nao", "Nao (depende de acesso)", "Medio", "Capitulo de resultados",
     "Depende de acesso ao artigo e de o dicionario estar publicado. Se nao estiver, o "
     "Loughran-McDonald traduzido serve como aproximacao, com a limitacao declarada."),

    ("G9", "Efeito da GRANULARIDADE TEXTUAL (manchete x subtitulo x corpo)",
     "MEDIA",
     "Santos avaliou SENTENCAS de noticia; nos avaliamos MANCHETES. O modelo suporta 512 tokens, o "
     "que permitiria texto muito maior. Nenhum trabalho mede o efeito da granularidade sobre a "
     "acuracia de sentimento financeiro em PT-BR.",
     "Exige corpus com os tres niveis disponiveis - nos temos, a maioria dos trabalhos nao.",
     "ALTA - hoje a nossa escolha por manchetes NAO esta formalmente justificada na dissertacao, o "
     "que e um flanco aberto",
     "Ablacao em tres niveis sobre o mesmo conjunto de noticias: manchete; manchete + subtitulo; "
     "manchete + primeiro paragrafo. Medir acuracia e kappa contra o gabarito e, em seguida, o "
     "efeito no ISM e na previsao de volatilidade.",
     "NAO - o gabarito humano e do evento noticioso, nao do recorte de texto",
     "Nao (pos-10/08)", "Medio", "Capitulo de metodo",
     "Conecta-se a Liu (2012), que distingue os niveis documento, sentenca e aspecto. A escolha "
     "passa a ser fundamentada e nao conveniencia de coleta."),

    ("G10", "FILTRO DE RELEVANCIA ao ativo antes da agregacao do indice",
     "MEDIA",
     "Nosso conjunto-ouro registra que apenas 111 de 300 manchetes (37,0%) foram marcadas como "
     "relevantes a PETR4. Os trabalhos examinados constroem indices agregando TODAS as noticias "
     "coletadas - Santos calcula o indice sobre 'uma amostra das noticias gerais coletadas'. Nenhum "
     "aplica filtro de relevancia por ativo antes de agregar.",
     "Indices de sentimento nasceram para medir o MERCADO, nao um ativo. Ao transpor para ativo "
     "unico, a etapa de relevancia foi omitida.",
     "ALTA - ja temos gerar_pipeline_relevancia.py e resultados_relevancia_2026-07-05.json",
     "Formalizar como experimento de ablacao: ISM com todas as noticias x ISM apenas com as "
     "relevantes x ISM ponderado por relevancia. Comparar o poder preditivo de cada um sobre "
     "volatilidade.",
     "Nao", "Nao (pos-10/08)", "Medio", "Capitulo de resultados",
     "Se 63% das noticias que entram no indice nao dizem respeito ao ativo, o indice mede ruido de "
     "mercado e nao sinal do ativo - o que pode explicar parte da fraqueza do sinal de direcao. Se o "
     "filtro melhorar e resultado; se nao melhorar, tambem e."),

    ("G11", "Comparacao de FORMULACOES DO INDICE de sentimento",
     "MEDIA-BAIXA",
     "A formula (Pos - Neg)/(Pos + Neu + Neg) vem de Hiew et al. (2019) e e adotada por Santos sem "
     "discussao de alternativas. Ninguem compara formulacoes. Nos ja temos uma variante - o ISM "
     "ponderado (resultados_ism_ponderado_petr4.csv) - e usamos polaridade x confianca, o que ja e "
     "variante nao documentada na literatura.",
     "A formula foi herdada sem questionamento entre trabalhos.",
     "MEDIA - contribuicao incremental",
     "Ablacao entre: contagem simples de Santos/Hiew; media de polaridade x confianca (o nosso); ISM "
     "ponderado por relevancia; e versao com janela exponencial. Avaliar por capacidade preditiva de "
     "volatilidade.",
     "Nao", "Nao (pos-10/08)", "Medio", "Secao de robustez",
     "Ressalva honesta: e contribuicao incremental. Vale como SECAO, nao como eixo."),

    ("G12", "SIGNIFICANCIA ESTATISTICA ausente nas comparacoes de encoder",
     "MEDIA-BAIXA",
     "Santos aplicou bootstrapping (Efron, 1992) com intervalos de confianca de 80% e teste Z sobre "
     "a distribuicao empirica reamostrada (monografia, Secao 4.2.4, Figuras 15 e 16). A nossa tabela "
     "resultado_encoders_petr4.csv reporta diferencas de -1,67, -5,33 e -16,00 pontos percentuais "
     "SEM qualquer teste.",
     "Nao e gap da literatura - e gap NOSSO. Registrado porque bloqueia a credibilidade de G3 e G6.",
     "ALTA - higiene metodologica obrigatoria",
     "Bootstrap com reamostragem sobre o conjunto de teste, intervalos de confianca e teste Z, "
     "replicando o protocolo de Santos.",
     "Nao", "Sim (~2 h)", "Baixo", "Capitulo de metodo",
     "Com n = 300 e desvios-padrao entre 2,7 e 8,4 pontos, a diferenca de -1,67 pp do BERTimbau "
     "large e seguramente indistinguivel de zero. Levar essa tabela a banca sem intervalo de "
     "confianca e convidar a critica."),

    ("G13", "EXPLICABILIDADE da contribuicao marginal do sentimento",
     "MEDIA-BAIXA",
     "Tanaka et al. (2026) usam SHAP para explicabilidade em modelos tabulares. Nenhum dos trabalhos "
     "de sentimento financeiro examinados aplica atribuicao de importancia para quantificar QUANTO o "
     "componente textual contribui para a previsao.",
     "A area reporta ganho agregado (com x sem sentimento) e raramente decompoe a contribuicao.",
     "ALTA - responde diretamente a ponderacao da banca sobre a contribuicao marginal do sentimento "
     "('o sentimento realmente ajuda, ou o GARCH sozinho ja explicava tudo?')",
     "SHAP sobre o XGBoost de fusao (modelo_xgb_fusion.json), separando a contribuicao das features "
     "de sentimento das de preco/volatilidade. Complementa a ablacao de categorias que ja temos "
     "(resultados_ablacao_categorias_petr4.csv).",
     "Nao", "Nao (pos-10/08)", "Baixo", "Capitulo de resultados",
     "Transforma um resultado numerico em figura que a banca entende em dez segundos."),
]


def escreve(nome, colunas, linhas):
    destino = AQUI / nome
    with destino.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";", quoting=csv.QUOTE_ALL)
        w.writerow(colunas)
        w.writerows(linhas)
    print(f"OK -> {nome} ({len(linhas)} linhas x {len(colunas)} colunas)")


if __name__ == "__main__":
    escreve("citacoes_por_trabalho.csv", COL_CIT, CITACOES)
    escreve("gaps_pesquisa.csv", COL_GAP, GAPS)
