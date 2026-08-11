# -*- coding: utf-8 -*-
# ==============================================================================
#   Gera a versão ABNT (.docx) do documento de citações e gaps, para apresentação
#   ao orientador (Prof. Dr. Julio Cesar Nievola) e ao Prof. Dr. Emerson Paraiso.
#
#   Parte 1 — as citações ao FinBERT-PT-BR, trabalho a trabalho, com o trecho
#             literal, a função retórica e a ligação com a pesquisa.
#   Parte 2 — os treze gaps de pesquisa identificados, com evidência,
#             viabilidade e caminho de solução.
#
#   Reaproveita src/comum/abnt_docx.py (NBR 14724/6023/6024/10520).
# ==============================================================================
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "src" / "comum"))

import abnt_docx as A  # noqa: E402

FONTE_AUTOR = "Elaborado pelo autor (2026)"
SAIDA = AQUI / "CITACOES_E_GAPS_2026-08-10.docx"


def main() -> None:
    doc = A.novo_documento()

    A.capa(
        doc,
        titulo="Citações ao FinBERT-PT-BR e gaps de pesquisa aproveitáveis",
        subtitulo="Análise trabalho a trabalho das citações e identificação de lacunas "
                  "para a dissertação",
        autor="Vanderlei Barbosa da Silva",
        orientador="Orientador: Prof. Dr. Julio Cesar Nievola",
        instituicao="PUCPR — Programa de Pós-Graduação em Informática (PPGIa)",
        descricao="Documento complementar à resposta às orientações da mentoria de 29 de julho "
                  "de 2026 (Prof. Dr. Emerson Cabrera Paraiso). Atende a dois pedidos: separar "
                  "as citações feitas por cada pesquisa, indicando qual é a citação, por que "
                  "citou e qual a ligação; e identificar gaps de pesquisa que possam ser "
                  "aproveitados e resolvidos na dissertação. Elaborado em 3 de agosto de 2026.",
    )

    # ─── 1 Correção ──────────────────────────────────────────────────────────
    A.secao(doc, "1", "Correção ao levantamento anterior")
    A.paragrafo(doc,
        "No documento entregue anteriormente afirmou-se que nenhum dos sete trabalhos citantes "
        "havia reutilizado o FinBERT-PT-BR. Após a obtenção e leitura dos textos completos, a "
        "afirmação precisa ser corrigida: **Błoch, Santana e Amantino (2026) executaram o "
        "FinBERT-PT-BR**, dentro de uma arquitetura de máquina de comitê, combinado com o "
        "pysentimiento (PÉREZ et al., 2021), para analisar o sentimento de correspondência "
        "colonial portuguesa dos séculos XVII e XVIII.")
    A.paragrafo(doc,
        "A afirmação correta, e que se mantém verificada, é mais específica e continua favorável "
        "à dissertação: **nenhum dos trabalhos citantes verificados aplicou o FinBERT-PT-BR à "
        "tarefa financeira para a qual ele foi construído**; o único que efetivamente o executou "
        "o fez fora do domínio financeiro, em documentos históricos. A distinção não enfraquece o "
        "argumento de lacuna — reforça-o, e ainda entrega um método diretamente reaproveitável, "
        "descrito na Seção 2.1 e no gap G7.")

    # ─── 2 Parte 1 ───────────────────────────────────────────────────────────
    A.secao(doc, "2", "As citações, trabalho a trabalho")
    A.paragrafo(doc,
        "Para cada trabalho registram-se: a citação literal, transcrita do texto completo do "
        "artigo; a seção em que aparece; a razão pela qual o autor citou, isto é, a função "
        "retórica da citação; se o modelo foi de fato executado; e a ligação com a pesquisa. A "
        "verificação foi feita sobre o texto integral dos artigos e cruzada com o campo de "
        "contextos da API do Semantic Scholar. A ordenação é por relevância decrescente para a "
        "dissertação.")

    # 2.1 Bloch
    A.secao(doc, "2.1", "Błoch, Santana e Amantino (2026) — o único que executou o modelo", nivel=2)
    A.paragrafo(doc,
        "**Veículo:** Estudos Ibero-Americanos, v. 52, n. 1, 2026 (PUCRS). **Citações:** uma, na "
        "Seção 4, no corpo do método. **Relevância para a pesquisa: muito alta**, apesar de o "
        "domínio ser História Digital.")
    A.citacao_longa(doc,
        "Para que a abordagem de comitê produza resultados promissores, é essencial a seleção de "
        "modelos de análise de sentimentos que tenham características distintas e complementares. "
        "Os modelos que selecionamos se enquadram nesse requisito, pois um deles — treinado em uma "
        "base financeira (Santos; Bianchi; Costa, 2023) — mostra resultados fortemente "
        "influenciados pela presença de termos negativos ou positivos, enquanto o segundo — "
        "treinado em uma base mais geral com conteúdo em português (Pérez et al., 2021) — analisa "
        "mais o contexto em que os termos aparecem. Em conjunto, os dois modelos apresentam uma boa "
        "capacidade de identificação de sentimentos, o que pode ser verificado nos experimentos em "
        "que comparamos, para um subconjunto de textos, a classificação do comitê com a de um "
        "historiador.",
        "Błoch, Santana e Amantino (2026, Seção 4)")
    A.paragrafo(doc,
        "**Por que citou:** para justificar a escolha do FinBERT-PT-BR como um dos membros do "
        "comitê, com base numa caracterização do comportamento do modelo. Não é citação de "
        "introdução nem de revisão — é citação de escolha de ferramenta, e a única, entre as sete, "
        "que revela conhecimento empírico do modelo em operação.")
    A.paragrafo(doc,
        "**Executou o modelo?** Sim. Arquitetura de máquina de comitê, com dois ou mais modelos e "
        "um moderador por voto, escolhida por ser autossupervisionada — os autores declaram "
        "explicitamente que optaram por ela tendo em vista que os textos da base não estavam "
        "classificados, para evitar o trabalho de criar uma base de treino rotulada. Validaram o "
        "comitê comparando, num subconjunto, a classificação automática com a de um historiador.")
    A.paragrafo(doc, "**Ligação com a pesquisa — três aproveitamentos concretos:**")
    A.lista(doc, [
        "**A caracterização do modelo é um achado independente que confirma o nosso.** Os autores "
        "observam que o FinBERT-PT-BR é fortemente influenciado pela presença de termos negativos "
        "ou positivos, isto é, opera mais por léxico do que por contexto. Isso explica diretamente "
        "o padrão da nossa matriz de confusão contra o conjunto-ouro, em que a classe Neutra é a "
        "mais confundida — 32 neutras classificadas como negativas e 26 como positivas, de 124. "
        "Manchetes neutras que contenham termos carregados puxam o modelo para os extremos. "
        "Passamos a ter uma explicação com respaldo externo para o kappa de 0,371, em vez de apenas "
        "constatá-lo.",
        "**A arquitetura de comitê é replicável a custo baixíssimo e sem rótulo.** Combinar o "
        "FinBERT-PT-BR, léxico e financeiro, com um modelo geral de contexto, e resolver por voto "
        "ou por média de probabilidade. É a contrapartida exata da fraqueza identificada.",
        "**O desenho de validação é o mesmo do nosso conjunto-ouro** e serve como precedente "
        "metodológico citável — comparar a classificação automática com a de um especialista humano "
        "num subconjunto. A diferença é que eles validaram um comitê, e nós um modelo isolado.",
    ])

    # 2.2 Abilio
    A.secao(doc, "2.2", "Abílio, Coelho e Silva (2024)", nivel=2)
    A.paragrafo(doc,
        "**Veículo:** Applied Soft Computing (Elsevier). **Citações:** três, todas na Seção 2.1, "
        "sobre pré-treino de modelos Transformer para o domínio financeiro. **Relevância: alta.** "
        "É o único dos sete cuja intenção de citação foi classificada pelo Semantic Scholar como "
        "de metodologia.")
    A.citacao_longa(doc,
        "Examples of these models include FinBERT [27], FinBERT PT-BR [28], and FLANG-BERT and "
        "FLANG-ELECTRA [29]. […] The FinBERT-PT-BR [28] model is based on BERTimbau [22], another "
        "BERT-based model, but pre-trained on Brazilian Portuguese corpora. In FinBERT-PT-BR, the "
        "authors continued the pre-training of BERTimbau by adding news from the Brazilian "
        "financial market. […] Besides, unlike Santos et al. [28], our dataset comprises text from "
        "earnings call transcripts for NER, while they used financial news for Sentiment Analysis.",
        "Abílio, Coelho e Silva (2024, Seção 2.1)")
    A.paragrafo(doc,
        "**Por que citou:** dois motivos encadeados. Primeiro, posicionar o FinBERT-PT-BR numa "
        "taxonomia internacional de modelos de domínio financeiro, ao lado do FinBERT em inglês e "
        "da família FLANG. Segundo, e mais importante para nós, delimitar a própria contribuição "
        "por contraste. **Executou o modelo?** Não — compararam BERTimbau, PTT5, mBERT e mT5.")
    A.paragrafo(doc, "**Ligação com a pesquisa — quatro pontos:**")
    A.lista(doc, [
        "É evidência independente, publicada em periódico de alto impacto, de que **encoders "
        "monolíngues em português superam multilíngues em domínio financeiro** — modelos BERT "
        "superam os T5, e o BERTimbau supera o PTT5. Sustenta a nossa escolha contra XLM-R e "
        "mDeBERTa.",
        "**Advertência sobre modelos generativos:** PTT5 e mT5 geraram sentenças com alteração de "
        "valores monetários e percentuais. É o contraponto obrigatório ao entusiasmo com modelos "
        "de linguagem generativos.",
        "O conjunto **BraFiNER**, com transcrições de teleconferências de resultados de bancos "
        "brasileiros, é corpus financeiro em português potencialmente utilizável na etapa de "
        "adaptação de domínio.",
        "**O padrão retórico da citação é o que devemos imitar.** Eles citam Santos para dizer "
        "“o nosso é diferente porque X”. A nossa dissertação precisa da mesma frase, com o nosso X: "
        "ativo único, volatilidade e fusão com GARCH.",
    ])

    # 2.3 Imai
    A.secao(doc, "2.3", "Imai et al. (2024) — PPGIa/PUCPR", nivel=2)
    A.paragrafo(doc,
        "**Veículo:** IEEE International Conference on Big Data, 2024. **Citações:** uma, na "
        "revisão de trabalhos relacionados. **Relevância: alta, e institucionalmente estratégica** "
        "— Alceu de Souza Britto Jr. e Jean Paul Barddal são professores do PPGIa da PUCPR.")
    A.citacao_longa(doc,
        "Even though we acknowledge the existence of similar works, such as Santos et al. [24], "
        "their approach differs from ours in the following aspects: (a) our approach considers the "
        "text stream paradigm, respecting the temporal order; (b) although the authors used "
        "BERTimbau as a base LM, they fine-tuned…",
        "Imai et al. (2024) — trecho truncado na base do Semantic Scholar; "
        "texto integral atrás do paywall do IEEE Xplore")
    A.paragrafo(doc,
        "**Por que citou:** exclusivamente para se diferenciar. Reconhecem Santos como trabalho "
        "similar e listam, ponto a ponto, por que o deles é diferente. O primeiro diferencial "
        "declarado é o mais importante para nós: **Santos não respeita a ordem temporal**. "
        "**Executou o modelo?** Não — usaram SentenceBERT com floresta aleatória adaptativa.")
    A.paragrafo(doc, "**Ligação com a pesquisa — é a mais incômoda e a mais útil das sete:**")
    A.lista(doc, [
        "**A crítica que eles fazem a Santos aplica-se hoje a nós.** Usamos um modelo congelado em "
        "13 de fevereiro de 2024 para classificar notícias de 2018 a 2026. O vocabulário da "
        "Petrobras mudou no período — política de preços, novo ciclo de dividendos, Margem "
        "Equatorial. Se a banca ler este artigo, a pergunta virá pronta; é melhor que a resposta "
        "também esteja.",
        "**Dão o método para tratar o problema:** ajuste fino periódico, anual, com amostra "
        "reduzida de textos recentes, medindo F1-macro e tempo de execução. Concluem que supera o "
        "modelo estático na maioria dos anos analisados.",
        "**Temos a infraestrutura para testar isso hoje**, sem rotular nada novo — o arquivo "
        "resultados_subperiodo_petr4.csv já particiona por subperíodo.",
        "**É uma ponte institucional real** — são dois colegas de programa, com quem se pode "
        "conversar.",
    ])

    # 2.4 Teles
    A.secao(doc, "2.4", "Teles e Figueiredo (2025)", nivel=2)
    A.paragrafo(doc,
        "**Veículo:** arXiv:2510.15929, Universidade do Estado do Amazonas. **Citações:** duas, "
        "ambas na Introdução, em parágrafos consecutivos. **Relevância: média-alta como "
        "oportunidade; baixa como precedente.**")
    A.citacao_longa(doc,
        "Sentiment analysis is one of the techniques used in the field of NLP to identify and "
        "extract information about the emotions expressed in a text, such as positivity, "
        "negativity, or neutrality [Santos et al. 2023]. […] The goal is to understand how people "
        "feel about a particular issue or product [Santos et al. 2023].",
        "Teles e Figueiredo (2025, Introdução)")
    A.paragrafo(doc,
        "**Por que citou:** de forma puramente definicional. Santos é usado para definir o que é "
        "análise de sentimento — função que qualquer revisão da área cumpriria igualmente bem. Não "
        "há engajamento com o método, com os resultados nem com o modelo.")
    A.paragrafo(doc,
        "**Executou o modelo?** Não, e este é o ponto. O artigo é brasileiro, de análise de "
        "sentimento, de notícias, de mercado financeiro, cita Santos duas vezes e ainda assim "
        "avalia nove modelos **sem incluir o FinBERT-PT-BR**, sobre três conjuntos em inglês. Os "
        "modelos comparados são SVM, Random Forest e MLP contra Gemma, DeBERTa, DeBERTaV3, "
        "XLM-RoBERTa, BART e Gemini 2.0-flash.")
    A.tabela_abnt(doc, 1, "Acurácia (%) dos modelos avaliados por Teles e Figueiredo (2025)",
        ["Modelo", "FPB", "StockEmotions", "TFN"],
        [
            ["SVM", "66,1", "77,0", "55,0"],
            ["Random Forest", "54,3", "71,2", "53,1"],
            ["MLP", "65,8", "77,5", "56,0"],
            ["Gemma", "54,3", "67,3", "61,7"],
            ["DeBERTa", "86,2", "63,1", "47,8"],
            ["DeBERTaV3", "65,8", "62,1", "64,1"],
            ["XLM-RoBERTa", "58,4", "61,1", "57,4"],
            ["BART", "65,0", "62,6", "61,7"],
            ["Gemini 2.0-flash", "80,4", "74,1", "78,9"],
        ], fonte="Teles e Figueiredo (2025, Tabela 7)")
    A.paragrafo(doc,
        "**Ligação com a pesquisa — uma oportunidade e uma ressalva.** A oportunidade: o Gemini foi "
        "o modelo mais consistente, com acurácia acima de 70% nos três conjuntos. Se um modelo "
        "generativo supera encoders especializados em sentimento financeiro em inglês, classificar "
        "as nossas 300 manchetes com um modelo desses via instrução é um experimento de baixo "
        "custo, alto valor e que não consome rotulagem humana. A ressalva, que precisa constar do "
        "texto: o trabalho não sustenta que modelos generativos superariam o FinBERT-PT-BR em "
        "manchetes brasileiras, pois avalia corpora em inglês, e o desempenho do DeBERTa oscila de "
        "86,2% a 47,8% conforme o conjunto. **Fazer esse teste em português é justamente o vão que "
        "este artigo deixa aberto.**")

    # 2.5 Alves
    A.secao(doc, "2.5", "Alves et al. (2024)", nivel=2)
    A.paragrafo(doc,
        "**Veículo:** Anais do XIII BraSNAM, SBC, 2024. **Citações:** uma, na Introdução. "
        "**Relevância: baixa**, mas com uma frase aproveitável.")
    A.citacao_longa(doc,
        "Porém, existe uma predominação de análises de textos em inglês, demonstrando assim uma "
        "falta de trabalhos na língua portuguesa [Santos et al. 2023].",
        "Alves et al. (2024, Introdução)")
    A.paragrafo(doc,
        "**Por que citou:** para sustentar a afirmação de escassez de trabalhos de análise de "
        "sentimento em português. A intenção da citação foi classificada pelo Semantic Scholar "
        "como de contextualização. **Executou o modelo?** Não — domínio de entretenimento.")
    A.paragrafo(doc,
        "**Ligação com a pesquisa:** é uma citação de terceiro que corrobora a premissa de escassez "
        "da nossa introdução. Vale mais escrever “Alves et al. (2024), apoiando-se em Santos et al. "
        "(2023), registram a predominância de análises em inglês e a falta de trabalhos em "
        "português” do que afirmar a escassez por conta própria. Serve também para demonstrar que a "
        "difusão do FinBERT-PT-BR transbordou o domínio financeiro.")

    # 2.6 Reichert
    A.secao(doc, "2.6", "Reichert e Perlin (2025)", nivel=2)
    A.paragrafo(doc,
        "**Veículo:** Computational Economics, Springer, 2025. **Relevância: média-alta.** Marcelo "
        "Perlin é professor da Escola de Administração da UFRGS e autor de referência em finanças "
        "quantitativas no Brasil.")
    A.paragrafo(doc,
        "**Citação literal: não foi possível transcrever.** O texto completo está atrás do paywall "
        "da Springer. A citação a Santos et al. (2023) está registrada por OpenAlex e Semantic "
        "Scholar, mas o trecho não consta de nenhuma das duas bases, e a página de resumo aberta ao "
        "público não exibe a lista de referências. **É a única das sete citações que permanece não "
        "verificada quanto ao trecho literal.** Recomenda-se obter o PDF pelo Portal de Periódicos "
        "da CAPES via PUCPR antes da versão final da dissertação.")
    A.paragrafo(doc,
        "**Ligação com a pesquisa — três pontos, derivados do resumo verificado.** Primeiro, o "
        "português está entre as línguas cobertas, e a validação foi feita sobre os últimos "
        "cinquenta comunicados do COPOM, isto é, texto financeiro brasileiro institucional. "
        "Segundo, o resumo declara que o dicionário foi comparado a modelos de texto completo e "
        "apresentou um perfil de classificação mais equilibrado; **se esses modelos incluírem o "
        "FinBERT-PT-BR, este é o único trabalho que o compara diretamente a uma alternativa — e o "
        "resultado não lhe é favorável.** Terceiro, um dicionário financeiro em português é a linha "
        "de base léxica que nos falta, o equivalente brasileiro do Loughran-McDonald.")

    # 2.7 Tanaka
    A.secao(doc, "2.7", "Tanaka et al. (2026)", nivel=2)
    A.paragrafo(doc,
        "**Veículo:** Algorithms, v. 19, n. 3, MDPI, 2026. **Citações:** uma, na metodologia. "
        "**Relevância: muito baixa — a citação é, muito provavelmente, imprecisa.**")
    A.citacao_longa(doc,
        "Training and validation relied on stratified subsets to mitigate sampling bias [39,40], "
        "reflecting the CRISP-DM emphasis on representativeness during model assessment. "
        "[a referência 39 é Santos, Bianchi e Costa (2023); a 40 é Chawla et al. (2002), do SMOTE]",
        "Tanaka et al. (2026, seção de metodologia)")
    A.paragrafo(doc,
        "**Por que citou:** para sustentar o uso de amostragem estratificada como mitigação de viés "
        "amostral. **Observação honesta: o artigo de Santos não trata de amostragem estratificada "
        "como contribuição metodológica** — usa validação cruzada com cinco divisões, o que é "
        "assunto próximo mas não igual. A citação parece imprecisa ou de conveniência, pois o par "
        "de referências faz muito mais sentido para o SMOTE, que trata de balanceamento de classes. "
        "**Executou o modelo?** Não — o trabalho nem sequer opera com texto.")
    A.paragrafo(doc,
        "**Ligação com a pesquisa:** apenas um aproveitamento lateral, o uso de SHAP para "
        "explicabilidade de modelos tabulares. Uma análise SHAP mostrando quanto o sentimento "
        "contribui marginalmente para a previsão de volatilidade responderia a uma das ponderações "
        "da banca. **Não se recomenda citar este trabalho como evidência de adoção do "
        "FinBERT-PT-BR**; se citado, citar apenas pelo uso de SHAP.")

    # 2.8 Sintese
    A.secao(doc, "2.8", "Síntese quantitativa das citações", nivel=2)
    A.tabela_abnt(doc, 2, "As sete citações a Santos, Bianchi e Costa (2023)",
        ["Trabalho", "N.º", "Onde", "Função da citação", "Executou?", "Relevância"],
        [
            ["Błoch, Santana e Amantino (2026)", "1", "Método", "Escolha de ferramenta", "SIM", "Muito alta"],
            ["Abílio, Coelho e Silva (2024)", "3", "Revisão", "Taxonomia e delimitação por contraste", "Não", "Alta"],
            ["Imai et al. (2024)", "1", "Revisão", "Delimitação por contraste", "Não", "Alta"],
            ["Teles e Figueiredo (2025)", "2", "Introdução", "Definicional", "Não", "Média-alta"],
            ["Alves et al. (2024)", "1", "Introdução", "Contextualização (escassez em PT)", "Não", "Baixa"],
            ["Reichert e Perlin (2025)", "?", "Não verificada", "Não verificada (paywall)", "Provavelmente não", "Média-alta"],
            ["Tanaka et al. (2026)", "1", "Método", "Amostragem estratificada — provável imprecisão", "Não", "Muito baixa"],
        ], fonte=FONTE_AUTOR)
    A.paragrafo(doc, "**Leitura do padrão, em quatro observações:**")
    A.lista(doc, [
        "Das sete, **apenas uma executou o modelo — e fora do domínio financeiro**.",
        "**Duas citam Santos para se diferenciar dele**, sinal de que o trabalho é reconhecido como "
        "referência obrigatória da área, mesmo sem ser reutilizado.",
        "**Duas o citam de forma meramente definicional ou de contexto** — a citação poderia ser "
        "substituída por qualquer revisão da área sem perda.",
        "**Uma citação é provavelmente imprecisa e outra não é verificável.**",
    ])
    A.paragrafo(doc,
        "**Consequência para a dissertação:** o FinBERT-PT-BR é um artefato com 177.384 downloads "
        "mensais e reconhecimento acadêmico como referência, mas com adoção acadêmica aplicada "
        "praticamente nula na tarefa para a qual foi construído. Esse contraste — muito uso "
        "prático, quase nenhuma validação acadêmica — é o núcleo do argumento de contribuição.")

    # ─── 3 Parte 2 — gaps ────────────────────────────────────────────────────
    A.secao(doc, "3", "Gaps de pesquisa identificados")
    A.paragrafo(doc,
        "A cada candidato a gap aplicam-se três filtros, explicitados quando algum falha: "
        "**evidência**, isto é, se o gap está demonstrado pelo levantamento ou é apenas plausível; "
        "**aderência**, se resolvê-lo pertence ao escopo da dissertação; e **viabilidade**, se é "
        "executável até a defesa com os dados e a infraestrutura disponíveis e, sobretudo, sem "
        "depender de rotulagem manual enquanto ela estiver suspensa.")
    A.paragrafo(doc,
        "**Ressalva metodológica obrigatória.** Um gap só pode ser afirmado como tal na dissertação "
        "se estiver respaldado pela revisão sistemática, com protocolo de busca declarado. O que "
        "segue é uma **hipótese de gap fundamentada em levantamento dirigido** — sete trabalhos "
        "citantes, vinte e oito referências do artigo-base e busca em OpenAlex, Semantic Scholar e "
        "Hugging Face —, **e não** uma revisão sistemática. Antes de qualquer afirmação de "
        "ineditismo no texto final, cada gap priorizado precisa passar pela revisão formal, cuja "
        "infraestrutura já existe na pasta datasets_refino.")

    A.secao(doc, "3.1", "Os treze gaps", nivel=2)
    A.tabela_abnt(doc, 3, "Gaps de prioridade máxima e alta",
        ["ID", "Gap", "Evidência", "Como resolver"],
        [
            ["G1", "Previsão de volatilidade de ativo brasileiro a partir de sentimento",
             "Dos 7 citantes e das 28 referências do artigo-base, nenhum prevê volatilidade — todos "
             "operam sobre direção, retorno ou carteira",
             "Já resolvido computacionalmente (GARCH, Mincer-Zarnowitz/QLIKE, regressão quantílica). "
             "Falta reposicionar editorialmente: volatilidade como resultado principal, direção como "
             "resultado negativo reportado"],
            ["G2", "Degradação por transferência de domínio: notícias gerais para ativo específico",
             "Santos relata 0,76 e F1 0,73 sobre notícias gerais; medimos 0,58 e kappa 0,371 sobre "
             "manchetes de PETR4. Ninguém quantifica essa degradação",
             "Decompor as causas (unidade textual, escopo, gabarito); explicar o mecanismo com a "
             "hipótese léxico-versus-contexto de Błoch et al. (2026); elevar a resultado"],
            ["G3", "Adaptação de domínio ao nível de setor/ativo",
             "Santos propõe explicitamente em Trabalhos Futuros “aplicar a metodologia para setores "
             "específicos da bolsa”; passados três anos, nenhum citante o fez",
             "Masked language modeling com máscara de 15% e taxa 2e-5 sobre as ~205 mil notícias, "
             "partindo do FinBERT-PT-BR e do BERTimbau large; métrica de perplexidade em holdout"],
            ["G4", "Concept drift em sentimento financeiro em português",
             "Imai et al. (2024) demonstram degradação de modelos estáticos e citam Santos por não "
             "respeitar a ordem temporal. Usamos modelo de 02/2024 sobre corpus 2018–2026",
             "Três níveis: declarar a limitação; medir a degradação por subperíodo (infraestrutura "
             "já existe); adaptação incremental por ano"],
            ["G5", "Ausência de benchmark público de sentimento financeiro rotulado em português",
             "Santos não publicou os 503 textos; Teles e Figueiredo recorrem a conjuntos em inglês; "
             "não há equivalente ao Financial PhraseBank em português",
             "Dupla anotação de 100–150 manchetes das 300 já rotuladas; Krippendorff’s alpha; "
             "categoria “não se aplica” com descarte; pré-seleção por modelagem de tópicos; "
             "publicação com DOI"],
            ["G6", "Modelo generativo versus encoder especializado em português financeiro",
             "Teles e Figueiredo (2025) mostram vantagem de modelos generativos, mas apenas em "
             "inglês. A comparação em português não existe",
             "Classificar as 300 manchetes com um modelo generativo via instrução literal de Santos "
             "e comparar com FinBERT-PT-BR e rótulo humano"],
        ], fonte=FONTE_AUTOR)

    A.tabela_abnt(doc, 4, "Gaps de prioridade média e média-baixa",
        ["ID", "Gap", "Evidência", "Como resolver"],
        [
            ["G7", "Comitê de modelos complementares em sentimento financeiro em português",
             "Błoch et al. (2026) aplicam máquina de comitê (FinBERT-PT-BR léxico + pysentimiento "
             "contextual) em História; ninguém fez em finanças",
             "Combinar os dois modelos por voto, média de probabilidades e regra de abstenção; medir "
             "contra o gabarito humano"],
            ["G8", "Dicionário léxico financeiro em português como linha de base",
             "Reichert e Perlin (2025) constroem dicionário com português incluído, validado sobre "
             "comunicados do COPOM. Ninguém compara dicionário e encoder em português financeiro",
             "Obter o dicionário pela CAPES e comparar com FinBERT-PT-BR, com o comitê (G7) e com o "
             "modelo generativo (G6) no mesmo conjunto-ouro"],
            ["G9", "Efeito da granularidade textual (manchete, subtítulo, corpo)",
             "Santos avaliou sentenças; nós avaliamos manchetes. O modelo suporta 512 tokens. "
             "Ninguém mede o efeito da granularidade",
             "Ablação em três níveis sobre o mesmo conjunto; medir acurácia, kappa e efeito no "
             "índice de sentimento e na previsão de volatilidade"],
            ["G10", "Filtro de relevância ao ativo antes da agregação do índice",
             "Apenas 111 de 300 manchetes (37,0%) foram marcadas como relevantes à PETR4. Os "
             "trabalhos agregam todas as notícias sem filtrar relevância por ativo",
             "Ablação: índice com todas as notícias, apenas com as relevantes e ponderado por "
             "relevância; comparar poder preditivo sobre volatilidade"],
            ["G11", "Comparação de formulações do índice de sentimento",
             "A fórmula de Hiew et al. (2019) é herdada sem discussão de alternativas; ninguém "
             "compara formulações",
             "Ablação entre contagem simples, média de polaridade vezes confiança, índice ponderado "
             "por relevância e janela exponencial"],
            ["G12", "Significância estatística ausente nas comparações de encoder",
             "Santos aplicou bootstrap e teste Z; a nossa tabela reporta diferenças de −1,67 a "
             "−16,00 pontos percentuais sem qualquer teste",
             "Bootstrap com reamostragem, intervalos de confiança e teste Z, replicando o protocolo "
             "de Santos"],
            ["G13", "Explicabilidade da contribuição marginal do sentimento",
             "Tanaka et al. (2026) usam SHAP em modelos tabulares; ninguém quantifica quanto o "
             "componente textual contribui para a previsão",
             "SHAP sobre o XGBoost de fusão, separando as variáveis de sentimento das de preço e "
             "volatilidade"],
        ], fonte=FONTE_AUTOR)

    A.secao(doc, "3.2", "Priorização", nivel=2)
    A.tabela_abnt(doc, 5, "Priorização dos gaps por viabilidade e dependência de rotulagem",
        ["Gap", "Prioridade", "Consome rótulo?", "Até 10/08?", "Esforço", "Onde entra"],
        [
            ["G1 Volatilidade", "Máxima", "Não", "Sim (editorial)", "Baixo", "Contribuição principal"],
            ["G2 Transferência de domínio", "Máxima", "Não", "Sim (editorial)", "Baixo", "Resultados"],
            ["G3 Adaptação de domínio", "Alta", "Não", "Sim (Colab, 6–10 h)", "Médio", "Método e resultados"],
            ["G6 Generativo × encoder", "Alta", "Não", "Sim (~4 h)", "Baixo", "Resultados"],
            ["G12 Significância", "Média-baixa", "Não", "Sim (~2 h)", "Baixo", "Método"],
            ["G4 Concept drift", "Alta", "Não", "Parcial", "Baixo/Médio", "Limitações e resultados"],
            ["G7 Comitê de modelos", "Média-alta", "Não", "Sim (~3 h)", "Baixo", "Resultados"],
            ["G9 Granularidade", "Média", "Não", "Não", "Médio", "Método"],
            ["G10 Filtro de relevância", "Média", "Não", "Não", "Médio", "Resultados"],
            ["G13 SHAP", "Média-baixa", "Não", "Não", "Baixo", "Resultados"],
            ["G11 Formulações do índice", "Média-baixa", "Não", "Não", "Médio", "Robustez"],
            ["G8 Dicionário léxico", "Média", "Não", "Não (acesso)", "Médio", "Resultados"],
            ["G5 Benchmark público", "Alta", "SIM", "Não (suspensa)", "Alto", "Contribuição de artefato"],
        ], fonte=FONTE_AUTOR)
    A.paragrafo(doc,
        "**Observação decisiva para a mentoria: doze dos treze gaps não dependem de rotulagem "
        "manual.** A suspensão da rotulagem não paralisa a pesquisa — apenas adia o G5, que é o "
        "mais ambicioso. Os cinco a levar à mentoria são G1 e G2, de reposicionamento editorial e "
        "custo quase zero; G3, a frente técnica principal, autossupervisionada; G6, o experimento "
        "de melhor relação entre resultado e esforço; e G7, descoberta desta rodada, que ataca "
        "exatamente a fraqueza medida. O G5 deve ser apresentado como proposta de retomada "
        "estruturada, e não como pedido para voltar ao que estava sendo feito.")

    A.secao(doc, "3.3", "O que não se recomenda perseguir", nivel=2)
    A.paragrafo(doc,
        "Registra-se por honestidade metodológica, porque nem tudo que parece gap é gap "
        "aproveitável.")
    A.tabela_abnt(doc, 6, "Linhas descartadas e a razão do descarte",
        ["Linha descartada", "Razão"],
        [
            ["Treinar um encoder do zero para o domínio",
             "Custo computacional incompatível com o prazo, e Santos já mostrou que a adaptação por "
             "modelagem de linguagem captura a maior parte do ganho"],
            ["Estender a estratégia de investimento de Santos",
             "É finanças de carteira, não previsão de ativo; descaracteriza o objeto e abre um "
             "flanco em que não temos competência declarada"],
            ["Relacionar o índice de sentimento a dados macroeconômicos",
             "É trabalho futuro do próprio Santos e pertence à macroeconomia, não à nossa pergunta; "
             "só faria sentido no doutorado"],
            ["Ampliar o conjunto-ouro de 300 para 600 manchetes com o protocolo atual",
             "Dobra o custo mantendo o defeito estrutural — anotador único, sem métrica de "
             "concordância"],
            ["Aplicar reconhecimento de entidades nomeadas",
             "Tarefa diferente, exige novo corpus anotado; interessante para o doutorado"],
            ["Migrar o pipeline inteiro para modelo generativo",
             "Perde reprodutibilidade e determinismo, e Abílio et al. (2024) documentam alteração de "
             "valores numéricos por modelos generativos. Usar como comparação (G6), não como "
             "substituição"],
        ], fonte=FONTE_AUTOR)

    # ─── 4 Perguntas esperadas ───────────────────────────────────────────────
    A.secao(doc, "4", "Perguntas esperadas e respostas preparadas")
    A.tabela_abnt(doc, 7, "Antecipação de arguição",
        ["Pergunta provável", "Resposta preparada"],
        [
            ["“Como você sabe que é um gap, e não só que você não achou?”",
             "É hipótese de gap fundamentada em levantamento dirigido — 7 citantes, 28 referências e "
             "buscas em OpenAlex, Semantic Scholar e Hugging Face —, e não revisão sistemática. "
             "Antes de afirmar ineditismo no texto final, cada gap priorizado passa pela revisão "
             "formal, cuja infraestrutura já existe"],
            ["“Por que não usar um modelo generativo e resolver logo?”",
             "É exatamente o G6, e a intenção é medir em vez de opinar. Ressalva: Abílio et al. "
             "(2024) documentam que modelos generativos alteraram valores monetários e percentuais "
             "em texto financeiro"],
            ["“Se o gabarito não é confiável, como você valida qualquer coisa?”",
             "Por isso o G3 usa perplexidade, métrica intrínseca que não depende de gabarito. E por "
             "isso o G5 propõe refundar o gabarito, e não ampliá-lo"],
            ["“A acurácia de 58% não invalida a pesquisa?”",
             "Não — mede a transferência de domínio (G2), que é um resultado. E o eixo da "
             "dissertação é volatilidade (G1), não classificação de sentimento"],
            ["“Qual é a contribuição, afinal?”",
             "Três: previsão de volatilidade de ativo brasileiro a partir de sentimento (G1); "
             "quantificação da degradação por transferência de domínio (G2); e um encoder adaptado "
             "ao subdomínio Petrobras (G3). Mais, se houver tempo, o benchmark público (G5)"],
        ], fonte=FONTE_AUTOR)

    # ─── 5 Referências ───────────────────────────────────────────────────────
    A.referencias(doc, "5", [
        "ABÍLIO, R.; COELHO, G. P.; SILVA, A. D. Evaluating Named Entity Recognition: a comparative "
        "analysis of mono- and multilingual transformer models on a novel Brazilian corporate "
        "earnings call transcripts dataset. Applied Soft Computing, 2024. "
        "DOI: 10.1016/j.asoc.2024.112158.",

        "ALCOFORADO, A. et al. ZeroBERTo: leveraging zero-shot text classification by topic "
        "modeling. arXiv:2201.01337, 2022.",

        "ALVES, M. A. R. et al. Sentimentos em Cena: uma análise dos comentários em trailers de "
        "filmes da Netflix Brasil no YouTube. In: BraSNAM, 13., 2024. Anais [...]. Porto Alegre: "
        "SBC, 2024. DOI: 10.5753/brasnam.2024.2974.",

        "ARTSTEIN, R.; POESIO, M. Inter-coder agreement for computational linguistics. "
        "Computational Linguistics, v. 34, n. 4, p. 555-596, 2008.",

        "BŁOCH, A.; SANTANA, C.; AMANTINO, M. Os jesuítas e a Era do Algoritmo: uma introdução à "
        "análise de sentimentos da correspondência colonial ultramarina portuguesa. Estudos "
        "Ibero-Americanos, Porto Alegre, v. 52, n. 1, p. 1-23, 2026. "
        "DOI: 10.15448/1980-864x.2026.1.46315.",

        "BOLLEN, J.; MAO, H.; ZENG, X. Twitter mood predicts the stock market. Journal of "
        "Computational Science, v. 2, n. 1, p. 1-8, 2011.",

        "EFRON, B. Bootstrap methods: another look at the jackknife. In: Breakthroughs in "
        "statistics. New York: Springer, 1992. p. 569-593.",

        "HIEW, J. Z. G. et al. BERT-based financial sentiment index and LSTM-based stock return "
        "predictability. arXiv:1906.09024, 2019.",

        "IMAI, B. Y. L. et al. Is it fine to tune? Evaluating SentenceBERT fine-tuning for "
        "Brazilian Portuguese text stream classification. In: IEEE INTERNATIONAL CONFERENCE ON BIG "
        "DATA, 2024. DOI: 10.1109/BigData62323.2024.10825456.",

        "JANUÁRIO, B. A. et al. Sentiment analysis applied to news from the Brazilian stock "
        "market. IEEE Latin America Transactions, v. 20, n. 3, p. 512-518, 2022.",

        "KRIPPENDORFF, K. Content analysis: an introduction to its methodology. 4. ed. Thousand "
        "Oaks: Sage, 2018.",

        "LIU, B. Sentiment analysis and opinion mining. Synthesis Lectures on Human Language "
        "Technologies, v. 5, n. 1, p. 1-167, 2012.",

        "MALO, P. et al. Good debt or bad debt: detecting semantic orientations in economic texts. "
        "Journal of the Association for Information Science and Technology, v. 65, n. 4, "
        "p. 782-796, 2014.",

        "PÉREZ, J. M. et al. pysentimiento: a Python toolkit for opinion mining and social NLP "
        "tasks. arXiv:2106.09462, 2021.",

        "POURSABZI-SANGDEH, F.; BOYD-GRABER, J. Speeding document annotation with topic models. "
        "In: NAACL STUDENT RESEARCH WORKSHOP, 2015. p. 126-132.",

        "REICHERT, M. H.; PERLIN, M. S. Using ChatGPT for creating multi-language finance related "
        "sentiment dictionaries. Computational Economics, 2025. DOI: 10.1007/s10614-025-11233-3.",

        "SANTOS, L. L. FinBERT-PT-BR: análise de sentimentos de textos em português referentes ao "
        "mercado financeiro. 2022. Trabalho de Conclusão de Curso (Engenharia de Computação) — "
        "Escola Politécnica, Universidade de São Paulo, São Paulo, 2022.",

        "SANTOS, L. L.; BIANCHI, R. A. C.; COSTA, A. H. R. FinBERT-PT-BR: análise de sentimentos "
        "de textos em português do mercado financeiro. In: BRAZILIAN WORKSHOP ON ARTIFICIAL "
        "INTELLIGENCE IN FINANCE (BWAIF), 2., 2023. Anais [...]. Porto Alegre: SBC, 2023. "
        "p. 144-155. DOI: 10.5753/bwaif.2023.231151.",

        "TANAKA, S. A. et al. A machine learning-driven CRM approach for identifying member churn "
        "in a Brazilian agro-industrial cooperative: a practical case study. Algorithms, v. 19, "
        "n. 3, 2026. DOI: 10.3390/a19030180.",

        "TELES, L. E. P.; FIGUEIREDO, C. M. S. Comparing LLMs for sentiment analysis in financial "
        "market news. arXiv:2510.15929, 2025.",
    ])

    doc.save(SAIDA)
    print(f"OK -> {SAIDA.name}")


if __name__ == "__main__":
    main()
