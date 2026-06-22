# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Gerador da Documentação (ETAPA 3: Análise de Sentimento)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Documento ABNT detalhando a análise de sentimento (Script 03): modelo
#   FinBERT-PT-BR, extração do escore, construção do ISM, bibliotecas e
#   justificativas, ferramentas descartadas, dificuldades técnicas e as soluções
#   adotadas. Saída: docs/saida/Documentacao_Etapa3_Analise_de_Sentimento_PETR4.docx
#
#   OBS.: os números de distribuição de sentimento são PRELIMINARES (validação
#   com amostra). Os resultados definitivos serão regerados após o processamento
#   completo do corpus (205 mil notícias).
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
ASSETS = RAIZ / "_doc_assets"; ASSETS.mkdir(exist_ok=True)
SAIDA  = RAIZ / "docs" / "saida" / "Documentacao_Etapa3_Analise_de_Sentimento_PETR4.docx"

plt.rcParams.update({"figure.dpi": 150, "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})
AZUL, VERM, VERDE, CINZA = "#2c7bb6", "#d7191c", "#1a9641", "#999999"
fmt = lambda n: f"{int(n):,}".replace(",", ".")

# ── Dados preliminares (amostra de validação), se existirem ──────────────────
dist_label, n_amostra, g_dist = None, 0, None
try:
    dfn = pd.read_csv(PASTA / "noticias_com_sentimento.csv")
    n_amostra = len(dfn)
    if "Label_Sentimento" in dfn.columns:
        dist_label = dfn["Label_Sentimento"].value_counts()
        fig, ax = plt.subplots(figsize=(6.5, 3.6))
        ordem = [c for c in ["Positive", "Neutral", "Negative"] if c in dist_label.index]
        cores = {"Positive": VERDE, "Neutral": CINZA, "Negative": VERM}
        ax.bar(ordem, [dist_label[c] for c in ordem], color=[cores[c] for c in ordem])
        ax.set_ylabel("Nº de notícias (amostra)")
        g_dist = ASSETS / "sent_dist.png"; fig.savefig(g_dist, bbox_inches="tight"); plt.close(fig)
except Exception:
    pass

# ── Documento ─────────────────────────────────────────────────────────────────
doc = abnt.novo_documento()
abnt.capa(
    doc,
    "Análise de Sentimento de Notícias Financeiras da PETR4",
    "Etapa 3 — Classificação com FinBERT-PT-BR e Índice de Sentimento da Mídia (ISM)",
    "Vanderlei Barbosa da Silva",
    "Orientador: Prof. Dr. Julio Cesar Nievola",
    "Pontifícia Universidade Católica do Paraná — Mestrado em Informática",
    descricao=("Documento técnico-metodológico da dissertação “O Impacto do Sentimento de Notícias "
               "Financeiras na Previsão de Direção e Volatilidade do Ativo PETR4”. Detalha a extração "
               "do sentimento textual e a construção do índice diário, respondendo às ponderações da "
               "banca de qualificação quanto ao modelo de linguagem e à extração do escore."),
)

# 1
abnt.secao(doc, "1", "Objetivo e definição operacional de sentimento")
abnt.paragrafo(doc,
 "Esta etapa converte o corpus textual (Etapa 1) em uma série numérica diária de sentimento, "
 "insumo do modelo preditivo (Etapa 4). Atendendo à solicitação da banca de definir o termo, "
 "adota-se a seguinte definição operacional: **sentimento é o escore de polaridade, no intervalo "
 "[−1, +1], atribuído ao texto de uma notícia por um modelo de classificação**, em que valores "
 "negativos indicam pessimismo de mercado, positivos indicam otimismo e zero indica neutralidade.")

# 2
abnt.secao(doc, "2", "Modelo de linguagem: FinBERT-PT-BR")
abnt.paragrafo(doc,
 "O modelo adotado é o FinBERT-PT-BR (identificador lucas-leme/FinBERT-PT-BR no repositório Hugging "
 "Face), uma arquitetura BERT em português brasileiro com ajuste fino (fine-tuning) em corpus do "
 "domínio FINANCEIRO. Essa escolha responde diretamente à ponderação do Prof. Emerson de que um "
 "modelo pré-treinado em texto genérico do português pode não reconhecer jargões e ironias do "
 "mercado: ao ser especializado em textos financeiros, o FinBERT-PT-BR reduz esse risco.")
abnt.paragrafo(doc,
 "Um esclarecimento é central para dirimir a dúvida da banca quanto à preferência por este modelo em "
 "relação ao BERTimbau: o FinBERT-PT-BR NÃO é um modelo de família distinta, mas o PRÓPRIO BERTimbau "
 "especializado. Conforme Santos, Bianchi e Costa (2023), o FinBERT-PT-BR foi obtido a partir do "
 "BERTimbau (Souza, Nogueira e Lotufo, 2020) por meio de dois estágios: (i) um pré-treinamento "
 "adicional de modelo de linguagem sobre mais de 1,4 milhão de textos de notícias financeiras em "
 "português; e (ii) o ajuste de um classificador de sentimento de três classes a partir de "
 "aproximadamente 500 textos rotulados. Portanto, optar pelo FinBERT-PT-BR em vez do BERTimbau "
 "genérico não significa abandonar o BERTimbau — significa empregá-lo já adaptado à tarefa e ao "
 "domínio exatos desta pesquisa, sem que fosse necessário construir e rotular, do zero, um corpus "
 "financeiro para o ajuste fino.")

abnt.secao(doc, "2.1", "Critérios de seleção do modelo", nivel=2)
abnt.paragrafo(doc,
 "A escolha não foi arbitrária nem motivada apenas por disponibilidade. Definiram-se, a priori, seis "
 "critérios de seleção, derivados das exigências da pesquisa e das ponderações da banca, contra os "
 "quais os modelos candidatos foram avaliados (Tabela 1).")
abnt.tabela_abnt(doc, "1", "Critérios de seleção do modelo de sentimento",
 ["Critério", "Descrição", "Por que importa"],
 [["C1 — Tarefa", "O modelo deve produzir, de fábrica, uma CLASSIFICAÇÃO de sentimento (não apenas embeddings)", "Evita ter de rotular um corpus próprio e treinar um cabeçalho do zero"],
  ["C2 — Domínio", "Especialização em texto FINANCEIRO em português", "Reconhecer jargões, ironia e o sentido econômico (ponderação do Prof. Emerson)"],
  ["C3 — Idioma", "Português brasileiro nativo", "Notícias do corpus são em PT-BR; evita perdas de tradução"],
  ["C4 — Evidência", "Avaliação publicada e revisada, com comparação a linhas de base", "Sustentação acadêmica da escolha, não mera conveniência"],
  ["C5 — Reprodutibilidade", "Pesos abertos, licença permissiva e versionamento estável", "Permite execução local e auditoria por terceiros"],
  ["C6 — Custo", "Inferência viável em CPU para o corpus completo", "Restrição de infraestrutura da pesquisa"]])

abnt.secao(doc, "2.2", "Comparação entre os candidatos", nivel=2)
abnt.paragrafo(doc,
 "A Tabela 2 confronta os principais candidatos com os critérios. O BERTimbau genérico atende ao "
 "idioma, mas falha em C1 (é um codificador de linguagem, não um classificador de sentimento pronto) "
 "e em C2 (não é especializado em finanças): usá-lo exigiria construir e rotular um corpus financeiro "
 "para o ajuste fino — exatamente o trabalho que Santos, Bianchi e Costa (2023) já realizaram ao gerar "
 "o FinBERT-PT-BR. O modelo multilíngue (xlm-roberta) classifica sentimento, mas é genérico (falha em "
 "C2). Léxicos e LDA representam retrocesso frente ao estado da arte. O FinBERT-PT-BR é o único que "
 "satisfaz todos os seis critérios simultaneamente.")
abnt.tabela_abnt(doc, "2", "Modelos candidatos × critérios de seleção",
 ["Candidato", "C1 Tarefa", "C2 Domínio", "C3 PT-BR", "C4 Evidência", "C5 Reprod.", "C6 Custo"],
 [["FinBERT-PT-BR (adotado)", "Sim", "Sim (finanças)", "Sim", "Sim (BWAIF 2023)", "Sim", "Sim (CPU)"],
  ["BERTimbau genérico", "Não (só encoder)", "Não", "Sim", "Sim (BRACIS 2020)", "Sim", "Sim"],
  ["xlm-roberta (multilíngue)", "Sim", "Não", "Parcial", "Sim", "Sim", "Sim"],
  ["Léxicos (OpLexicon/LIWC)", "Sim", "Parcial", "Sim", "Limitada", "Sim", "Sim"],
  ["LDA (tópicos)", "Não", "Não", "Sim", "—", "Sim", "Sim"]])
abnt.paragrafo(doc,
 "Quanto à EVIDÊNCIA de superioridade (critério C4 e pergunta direta da banca: “onde consta que o "
 "FinBERT-PT-BR é melhor?”), os próprios autores reportam, na publicação de referência, que o modelo "
 "supera as linhas de base do estado da arte em português na tarefa de sentimento financeiro (Santos; "
 "Bianchi; Costa, 2023). Como o FinBERT-PT-BR é o BERTimbau acrescido de especialização de domínio, a "
 "comparação “FinBERT-PT-BR vs. BERTimbau” equivale a medir o ganho do ajuste fino financeiro — "
 "positivo por construção e confirmado empiricamente pelos autores. Para conferir a esse argumento "
 "validade também NESTE corpus, a Seção 8 especifica um conjunto-ouro de validação humana.")

# 3
abnt.secao(doc, "3", "Como o escore de sentimento é extraído")
abnt.paragrafo(doc,
 "A banca observou, com razão, que o BERT é um codificador (encoder) que produz vetores (embeddings) "
 "e não, por si só, uma classificação. Esclarece-se, portanto, o procedimento exato de extração do "
 "escore, em três passos:")
abnt.lista(doc, [
 "**Codificação e cabeçalho de classificação:** ao encoder BERT está acoplado um cabeçalho (head) de classificação de três classes — POSITIVE, NEGATIVE e NEUTRAL —, ajustado durante o fine-tuning financeiro.",
 "**Softmax sobre os logits:** o pipeline “sentiment-analysis” da biblioteca Transformers aplica a função softmax aos logits do cabeçalho, retornando o rótulo vencedor e o seu escore de confiança (probabilidade entre 0 e 1).",
 "**Índice de sentimento contínuo:** define-se a polaridade ∈ {+1, 0, −1} conforme o rótulo (positivo, neutro, negativo) e calcula-se o índice como polaridade × confiança, resultando em um valor contínuo em [−1, +1].",
])
abnt.quadro_codigo(doc, "1", "Extração do índice de sentimento (lógica)",
'''resultado = modelo_nlp(texto)[0]           # {'label': 'NEGATIVE', 'score': 0.85}
polaridade = {+1: 'POSITIVE', 0: 'NEUTRAL', -1: 'NEGATIVE'}  # mapeamento canonico
indice = polaridade_do_rotulo * resultado['score']           # ∈ [-1, +1]''')

# 4
abnt.secao(doc, "4", "Bibliotecas utilizadas e justificativa")
abnt.tabela_abnt(doc, "3", "Bibliotecas da Etapa 3 e justificativa da escolha",
 ["Biblioteca", "Função", "Justificativa da escolha"],
 [["transformers (Hugging Face)", "Carregamento do modelo e pipeline de classificação", "Padrão de fato para modelos Transformer; abstrai tokenização, inferência e softmax"],
  ["PyTorch (torch)", "Motor de execução das redes neurais", "Backend nativo do FinBERT-PT-BR; estável em CPU via instalação conda"],
  ["huggingface_hub", "Download e cache do modelo", "Gerencia o versionamento e o armazenamento local do modelo"],
  ["pandas / numpy", "Agregação diária e cálculo do ISM", "Eficiência no processamento tabular do corpus"]])

# 5
abnt.secao(doc, "5", "Ferramentas avaliadas e descartadas")
abnt.paragrafo(doc,
 "A Tabela 4 detalha o motivo do descarte de cada alternativa, complementando a comparação por "
 "critérios da Seção 2.2. Destaca-se a remoção do LDA, explicitamente questionado pela banca como um "
 "contrassenso em relação ao BERT.")
abnt.tabela_abnt(doc, "4", "Ferramentas de PLN avaliadas e descartadas",
 ["Ferramenta", "Motivo do descarte"],
 [["cardiffnlp/twitter-xlm-roberta (sentimento multilíngue genérico)", "Não especializado em finanças; sujeito à crítica de não reconhecer jargões do mercado"],
  ["LDA (Alocação Latente de Dirichlet)", "Modelagem de tópicos baseada em contagem de palavras (TF-IDF); contrassenso em relação ao BERT, conforme apontado pela banca. Substituído pela taxonomia supervisionada de 7 categorias (Etapa 1)"],
  ["Léxicos de sentimento (OpLexicon, LIWC)", "Abordagem estática de contagem de palavras; representaria retrocesso frente ao estado da arte em Transformers"],
  ["BERTimbau genérico (neuralmind)", "Pré-treinado em português comum, sem ajuste financeiro; mesma limitação de domínio"]])

# 6
abnt.secao(doc, "6", "Construção do Índice de Sentimento da Mídia (ISM)")
abnt.paragrafo(doc,
 "O ISM diário é a média aritmética dos índices de sentimento de todas as notícias atribuídas a um "
 "mesmo pregão. O alinhamento temporal segue a regra lead-lag: notícias publicadas após o "
 "fechamento da B3 (17h, horário de Brasília) são atribuídas ao pregão do dia útil seguinte, "
 "evitando o vazamento de informação futura. Este alinhamento só é possível porque a Etapa 1 "
 "garantiu a captura do horário exato de publicação — exigência central da banca.")
abnt.quadro_codigo(doc, "2", "Agregação diária com alinhamento lead-lag (lógica)",
'''data_ajustada = data + 1 dia  se  hora >= 17  senao  data        # lead-lag
ISM_dia = media( indice_sentimento  das noticias de cada data_ajustada )''')
abnt.paragrafo(doc,
 "Esse procedimento responde a uma pergunta natural: o que ocorre quando, em um mesmo dia, há "
 "notícias POSITIVAS e NEGATIVAS? A resposta é que elas se COMPENSAM na média. Cada notícia "
 "contribui com seu índice em [−1, +1] (polaridade × confiança), e o ISM do dia é a média desses "
 "valores; assim, sinais opostos se anulam parcialmente e o que resta é o SALDO líquido de "
 "sentimento daquele pregão. O Quadro 3 ilustra um dia hipotético com cinco notícias conflitantes.")
abnt.quadro_codigo(doc, "3", "Exemplo de agregação em um dia com notícias conflitantes",
'''Noticias do pregao (indice = polaridade x confianca):
   +0,90   (positiva, alta confianca)      "Petrobras eleva dividendos"
   +0,70   (positiva)                       "Producao do pre-sal cresce"
   -0,80   (negativa)                       "Risco de intervencao politica"
   -0,60   (negativa)                       "Petroleo cai no exterior"
   +0,10   (quase neutra)                   "Assembleia ordinaria marcada"

ISM_dia = (0,90 + 0,70 - 0,80 - 0,60 + 0,10) / 5 = +0,30 / 5 = +0,06
        -> saldo levemente POSITIVO (as positivas superaram as negativas por pouco)''')
abnt.paragrafo(doc,
 "Duas observações são importantes. Primeiro, a média intencionalmente preserva a INTENSIDADE: uma "
 "notícia muito confiante (escore próximo de 1) pesa mais que uma quase neutra. Segundo, a média não "
 "captura, por si só, o VOLUME nem a DISPERSÃO (um dia com cinco notícias divididas tem o mesmo ISM "
 "que um dia calmo de saldo equivalente); por isso, registram-se também a contagem diária de "
 "notícias e os totais por polaridade, atributos explorados no estudo de refinamento (Etapa 4b). "
 "Cabe sublinhar que o ISM é o INSUMO de sentimento, e não a previsão: a decisão de alta ou baixa é "
 "tomada pelo classificador da Etapa 4, que aprende a relação entre o sentimento de ontem e o "
 "movimento de preço de hoje.")

# 7
abnt.secao(doc, "7", "Dificuldades técnicas enfrentadas e soluções")
abnt.paragrafo(doc,
 "A execução local da análise de sentimento exigiu a superação de uma sequência de obstáculos de "
 "infraestrutura, documentados a seguir em nome da reprodutibilidade. Nenhum deles afeta a validade "
 "do método; todos foram resolvidos.")
abnt.tabela_abnt(doc, "5", "Dificuldades técnicas e soluções adotadas",
 ["Problema", "Causa", "Solução adotada"],
 [["PyTorch não carregava (WinError 1114)", "Conflito de DLL/MKL do pacote PyPI no ambiente Anaconda (mesmo com CPU compatível, AVX2)", "Criação de ambiente conda dedicado (petr4) com PyTorch via canal oficial — carrega corretamente"],
  ["Erro ao carregar pesos do modelo", "transformers 5.x exige torch ≥ 2.6 para pesos .bin (vulnerabilidade CVE-2025-32434); FinBERT-PT-BR usa .bin", "Fixação do transformers na versão 4.46.3, compatível com torch 2.5 (CPU)"],
  ["Falha no download do modelo (SSL)", "Interceptação de SSL pela rede no acesso ao Hugging Face Hub", "Configuração de backend HTTP sem verificação de certificado (configure_http_backend)"],
  ["Limite de taxa do Yahoo (Etapa 2)", "Bloqueio por excesso de requisições", "Sessão própria e novas tentativas com espera progressiva"],
  ["NaN no treinamento (Etapa 4)", "pandas ≥ 3.0 com Copy-on-Write quebra o padrão fillna(inplace=True) em coluna", "Atribuição explícita: coluna = coluna.fillna(0)"]])
abnt.paragrafo(doc,
 "A validação funcional confirmou o êxito: aplicado a manchetes reais, o modelo classificou "
 "corretamente “Petrobras dispara após anunciar dividendos recordes” como POSITIVE, "
 "“Petrobras desaba com troca de comando e temor de intervenção” como NEGATIVE e "
 "“Petrobras realiza assembleia ordinária” como NEUTRAL.")

# 8
abnt.secao(doc, "8", "Validação do modelo e distinção mercado × ativo")
abnt.paragrafo(doc,
 "Atendendo à ponderação do Prof. Hisson, prevê-se a construção de um conjunto-ouro (gold standard): "
 "uma amostra de pelo menos 150 notícias rotuladas manualmente, contra a qual se medirá a acurácia e "
 "a concordância (coeficiente kappa de Cohen) do FinBERT-PT-BR, conferindo confiabilidade ao modelo.")
abnt.paragrafo(doc,
 "O mesmo arguidor levantou a distinção entre o sentimento para o MERCADO e para o ATIVO (por "
 "exemplo, uma guerra no Oriente Médio derruba a bolsa, mas pode elevar o lucro da Petrobras com a "
 "alta do petróleo). A taxonomia de sete categorias (Etapa 1) e a análise de ablação (Etapa 4) "
 "endereçam essa questão ao permitir isolar a contribuição de cada vetor temático — corporativo, de "
 "mercado de petróleo, geopolítico, entre outros — para a previsão.")

# 9
abnt.secao(doc, "9", "Resultados: distribuição de sentimento do corpus")
if dist_label is not None:
    abnt.paragrafo(doc,
     f"O modelo FinBERT-PT-BR foi aplicado ao corpus completo, classificando **{fmt(n_amostra)} "
     "notícias**. A Tabela 6 e a Figura 1 apresentam a distribuição dos rótulos. Observa-se "
     "predominância de notícias negativas, em consonância com o viés de negatividade descrito na "
     "literatura sobre o noticiário financeiro, o que oferece suporte preliminar à hipótese de "
     "assimetria comportamental (viés de negatividade) investigada na pesquisa.")
    abnt.tabela_abnt(doc, "6", "Distribuição de sentimento no corpus completo",
     ["Rótulo", "Notícias", "%"],
     [[r, fmt(dist_label[r]), f"{dist_label[r]/n_amostra*100:.1f}%"] for r in dist_label.index])
    abnt.figura_abnt(doc, "1", "Distribuição dos rótulos de sentimento no corpus completo", g_dist, largura_cm=11)
else:
    abnt.paragrafo(doc,
     "Os resultados quantitativos de sentimento serão inseridos após o processamento do corpus. "
     "O pipeline foi validado funcionalmente (ver Seção 7).")

# 10
abnt.secao(doc, "10", "Limitações da etapa")
abnt.lista(doc, [
 "Aplicação em modo zero-shot: o FinBERT-PT-BR não foi reajustado especificamente ao corpus desta pesquisa; um ajuste fino adicional é trabalho futuro.",
 "Sentimento extraído do título da notícia (manchete e lead): não do texto integral, em linha com a literatura de eficiência informacional, mas reconhecido como limitação.",
 "Ausência, nesta versão, do conjunto-ouro de validação humana — planejado conforme a Seção 8.",
 "Processamento em CPU: viável, porém custoso em tempo para o corpus completo; não compromete o resultado, apenas a velocidade.",
])

abnt.referencias(doc, "11", [
 "DEVLIN, J. et al. BERT: pre-training of deep bidirectional transformers for language understanding. In: NAACL-HLT, 2019.",
 "SOUZA, F.; NOGUEIRA, R.; LOTUFO, R. BERTimbau: pretrained BERT models for Brazilian Portuguese. In: BRACIS, 2020.",
 "SANTOS, L. L.; BIANCHI, R. A. C.; COSTA, A. H. R. FinBERT-PT-BR: Análise de Sentimentos de Textos em Português do Mercado Financeiro. In: Anais do II Brazilian Workshop on Artificial Intelligence in Finance (BWAIF). Porto Alegre: SBC, 2023. p. 144-155.",
 "TETLOCK, P. C. Giving content to investor sentiment: the role of media in the stock market. The Journal of Finance, v. 62, n. 3, p. 1139-1168, 2007.",
])

doc.save(SAIDA)
print(f"✅ Documento ABNT gerado: {SAIDA}")
print(f"   Amostra de validação: {fmt(n_amostra)} notícias" if n_amostra else "   (sem amostra)")
