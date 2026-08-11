# Citações ao FinBERT-PT-BR, trabalho a trabalho, e gaps de pesquisa aproveitáveis

**Mestrando:** Vanderlei Barbosa da Silva
**Orientador:** Prof. Dr. Julio Cesar Nievola (PUCPR — PPGIa)
**Mentoria de origem:** 29/07/2026 (Prof. Dr. Emerson Cabrera Paraiso) · **Entrega:** 10/08/2026
**Documento elaborado em:** 03/08/2026
**Complementa:** `RESPOSTA_ORIENTACOES_2026-08-10.md`

---

## Sumário

- [Parte 0 — Correção relevante ao documento anterior](#parte-0--correção-relevante-ao-documento-anterior)
- [Parte 1 — As citações, trabalho a trabalho](#parte-1--as-citações-trabalho-a-trabalho)
  - [Como ler esta parte](#como-ler-esta-parte)
  - [① Błoch, Santana e Amantino (2026)](#-błoch-santana-e-amantino-2026--o-único-que-executou-o-modelo)
  - [② Abílio, Coelho e Silva (2024)](#-abílio-coelho-e-silva-2024)
  - [③ Imai et al. (2024)](#-imai-et-al-2024--ppgiapucpr)
  - [④ Teles e Figueiredo (2025)](#-teles-e-figueiredo-2025)
  - [⑤ Alves et al. (2024)](#-alves-et-al-2024)
  - [⑥ Reichert e Perlin (2025)](#-reichert-e-perlin-2025)
  - [⑦ Tanaka et al. (2026)](#-tanaka-et-al-2026)
  - [Síntese quantitativa](#síntese-quantitativa-das-citações)
- [Parte 2 — Gaps de pesquisa](#parte-2--gaps-de-pesquisa)
  - [Critério de classificação](#critério-de-classificação)
  - [G1 a G13 — os gaps](#os-treze-gaps)
  - [Priorização](#priorização-quais-gaps-atacar)
  - [O que NÃO recomendo perseguir](#o-que-não-recomendo-perseguir)
- [Parte 3 — Como levar isso à mentoria](#parte-3--como-levar-isso-à-mentoria)

---

## Parte 0 — Correção relevante ao documento anterior

No documento entregue anteriormente afirmei que **nenhum** dos sete trabalhos citantes havia
reutilizado o FinBERT-PT-BR. Após obter e ler os textos completos, a afirmação precisa ser
corrigida:

> **Błoch, Santana e Amantino (2026) executaram o FinBERT-PT-BR**, dentro de uma arquitetura de
> *máquina de comitê*, combinado com o `pysentimiento` (PÉREZ et al., 2021), para analisar o
> sentimento de correspondência colonial portuguesa dos séculos XVII e XVIII.

A afirmação correta, e que se mantém verificada, é mais específica e continua favorável à
dissertação:

> **Nenhum dos trabalhos citantes verificados aplicou o FinBERT-PT-BR à tarefa financeira para
> a qual ele foi construído.** O único que efetivamente o executou o fez **fora do domínio
> financeiro**, em documentos históricos.

A distinção não enfraquece o argumento de lacuna — reforça-o, e ainda entrega um método
diretamente reaproveitável (Seção ① e gap **G7**). O arquivo
`RESPOSTA_ORIENTACOES_2026-08-10.md` foi corrigido nos pontos afetados.

---

## Parte 1 — As citações, trabalho a trabalho

### Como ler esta parte

Para cada trabalho registro: **(a)** a citação literal, transcrita do texto completo do artigo;
**(b)** em que seção aparece; **(c)** por que o autor citou — a função retórica da citação;
**(d)** se o modelo foi de fato executado; e **(e)** qual é a ligação com a nossa pesquisa.

A verificação foi feita sobre o **texto integral** dos artigos, baixado e indexado (os arquivos
`_*.pdf` e `_*.txt` estão nesta pasta), e cruzada com o campo `contexts` da API do Semantic
Scholar. A ordenação é por relevância decrescente para a dissertação — **não** é a mesma ordem
do documento anterior, que era por relevância estimada antes da leitura integral.

---

### ① Błoch, Santana e Amantino (2026) — o único que executou o modelo

> BŁOCH, A.; SANTANA, C.; AMANTINO, M. Os jesuítas e a Era do Algoritmo: uma introdução à
> análise de sentimentos da correspondência colonial ultramarina portuguesa. **Estudos
> Ibero-Americanos**, Porto Alegre, v. 52, n. 1, p. 1-23, jan.-dez. 2026.
> DOI: 10.15448/1980-864x.2026.1.46315.

**🔴 RELEVÂNCIA PARA A NOSSA PESQUISA: MUITO ALTA** (apesar do domínio ser História Digital)

**(a) Citação literal** — Seção 4, "Descobrindo sentimentos na correspondência sobre os
jesuítas: abordagens metodológicas e resultados preliminares":

> *"Para que a abordagem de comitê produza resultados promissores, é essencial a seleção de
> modelos de análise de sentimentos que tenham características distintas e complementares. Os
> modelos que selecionamos se enquadram nesse requisito, pois um deles — **treinado em uma base
> financeira (Santos; Bianchi; Costa, 2023)** — mostra resultados fortemente influenciados pela
> presença de termos negativos ou positivos, enquanto o segundo — treinado em uma base mais
> geral com conteúdo em português (Pérez et al., 2021) — analisa mais o contexto em que os
> termos aparecem. Em conjunto, os dois modelos apresentam uma boa capacidade de identificação
> de sentimentos, o que pode ser verificado nos experimentos em que comparamos, para um
> subconjunto de textos, a classificação do comitê com a de um historiador."*

**(b) Onde aparece:** corpo do método, na justificativa da composição do comitê. Não é citação
de introdução nem de revisão — é **citação de escolha de ferramenta**.

**(c) Por que citou:** para justificar a **escolha do FinBERT-PT-BR como um dos membros do
comitê**, com base numa caracterização do comportamento do modelo. É a única citação, entre as
sete, que revela conhecimento empírico do modelo em operação.

**(d) Executou o modelo?** **Sim.** Arquitetura de *Máquina de Comitê* (dois ou mais modelos +
moderador por voto), escolhida por ser **autossupervisionada** — os autores declaram
explicitamente que optaram por ela *"tendo em vista que os textos na nossa base não estão
classificados, para evitar o trabalho de criar uma base de treino classificada"*. Validaram o
comitê comparando, num subconjunto, a classificação automática contra a de um historiador.

**(e) Ligação com a nossa pesquisa — três aproveitamentos concretos:**

1. **A caracterização do modelo é um achado independente que confirma o nosso.** Os autores
   observam que o FinBERT-PT-BR é *"fortemente influenciado pela presença de termos negativos
   ou positivos"* — ou seja, opera mais por **léxico** do que por **contexto**. Isso explica
   diretamente o padrão da nossa matriz de confusão contra o conjunto-ouro, em que a classe
   **Neutra** é a mais confundida (32 neutras classificadas como negativas e 26 como positivas,
   de 124). Manchetes neutras que contêm termos carregados — *"Petrobras avalia corte de
   investimentos"* — puxam o modelo para o extremo. **Passamos a ter uma explicação com
   respaldo externo para o κ = 0,371, em vez de apenas constatá-lo.**
2. **A arquitetura de comitê é replicável no nosso caso a custo baixíssimo e sem rótulo.**
   Combinar o FinBERT-PT-BR (léxico, financeiro) com um modelo geral de contexto — o próprio
   `pysentimiento`, que tem versão em português — e resolver por voto ou por média de
   probabilidade. É a **contrapartida exata da fraqueza identificada**. Ver gap **G7**.
3. **O desenho de validação é o mesmo do nosso conjunto-ouro**, e serve como precedente
   metodológico citável: comparar a classificação automática contra a de um especialista humano
   num subconjunto. A diferença é que eles validaram um **comitê**, e nós validamos um **modelo
   isolado**.

**Aproveitamento adicional, de retórica:** o artigo discute, na seção "Desafios enfrentados",
como *a qualidade dos dados condiciona o desempenho da IA* e defende o papel indispensável do
humano no processo. É uma citação elegante, vinda de fora da área, para o parágrafo em que
justificarmos a necessidade do conjunto-ouro humano.

---

### ② Abílio, Coelho e Silva (2024)

> ABÍLIO, R.; COELHO, G. P.; SILVA, A. D. Evaluating Named Entity Recognition: a comparative
> analysis of mono- and multilingual transformer models on a novel Brazilian corporate earnings
> call transcripts dataset. **Applied Soft Computing**, 2024. DOI: 10.1016/j.asoc.2024.112158.

**🟠 RELEVÂNCIA: ALTA** · *Intent* classificado pelo Semantic Scholar: **`methodology`** (o
único dos sete com essa classificação)

**(a) Citações literais** — são **três**, todas na Seção 2.1, "Pre-training Transformer-based
models for the Financial domain":

> *"Examples of these models include FinBERT [27], **FinBERT PT-BR [28]**, and FLANG-BERT and
> FLANG-ELECTRA [29]."*

> *"The **FinBERT-PT-BR [28]** model is based on BERTimbau [22], another BERT-based model, but
> pre-trained on Brazilian Portuguese corpora. In FinBERT-PT-BR, the authors continued the
> pre-training of BERTimbau by adding news from the Brazilian financial market."*

> *"Besides, **unlike Santos et al. [28]**, our dataset comprises text from earnings call
> transcripts for NER, while they used financial news for Sentiment Analysis."*

**(b) Onde aparece:** revisão de trabalhos relacionados, subseção específica sobre pré-treino
de modelos Transformer para o domínio financeiro.

**(c) Por que citou:** dois motivos encadeados. Primeiro, **posicionar o FinBERT-PT-BR numa
taxonomia internacional** de modelos de domínio financeiro, ao lado do FinBERT (EN) e da
família FLANG. Segundo — e mais importante para nós — **delimitar a própria contribuição por
contraste**: "diferentemente de Santos et al., nosso conjunto é de *earnings calls* para NER,
enquanto eles usaram notícias financeiras para análise de sentimento".

**(d) Executou o modelo?** Não. Compararam BERTimbau, PTT5, mBERT e mT5.

**(e) Ligação com a nossa pesquisa — quatro pontos:**

1. **É evidência independente, publicada em periódico Q1, de que encoders monolíngues PT-BR
   superam multilíngues em domínio financeiro.** Sustenta a nossa escolha por
   FinBERT-PT-BR/BERTimbau contra XLM-R e mDeBERTa, com citação forte.
2. **Advertência sobre modelos generativos:** PTT5 e mT5 *geraram sentenças com alteração de
   valores monetários e percentuais*. É o contraponto obrigatório ao entusiasmo com LLMs do
   trabalho ④, e vale citar em qualquer discussão sobre substituir o encoder por um LLM.
3. **O dataset BraFiNER** é corpus financeiro em PT-BR (transcrições de *earnings calls* de
   bancos) potencialmente utilizável na etapa de adaptação de domínio por MLM.
4. **O padrão retórico da citação é o que devemos imitar.** Eles citam Santos para dizer "o
   nosso é diferente porque X". A nossa dissertação precisa exatamente da mesma frase, com o
   nosso X: *ativo único, volatilidade e fusão com GARCH*.

---

### ③ Imai et al. (2024) — PPGIa/PUCPR

> IMAI, B. Y. L.; GARCIA, C. M.; ROCHA, M. V.; KOERICH, A. L.; BRITTO JR., A. S.; BARDDAL, J. P.
> Is it fine to tune? Evaluating SentenceBERT fine-tuning for Brazilian Portuguese text stream
> classification. In: **IEEE INTERNATIONAL CONFERENCE ON BIG DATA**, 2024.
> DOI: 10.1109/BigData62323.2024.10825456.

**🟠 RELEVÂNCIA: ALTA — e institucionalmente estratégica**

> ⚠️ **Alceu de Souza Britto Jr. e Jean Paul Barddal são professores do PPGIa da PUCPR** — o
> nosso próprio programa. Alessandro Koerich é da ÉTS/Canadá, ex-PUCPR.

**(a) Citação literal** — seção de trabalhos relacionados:

> *"Even though we acknowledge the existence of similar works, such as **Santos et al. [24]**,
> their approach differs from ours in the following aspects: (a) our approach considers the
> **text stream paradigm, respecting the temporal order**; (b) although the authors used
> BERTimbau as a base LM, they fine-tuned…"*

*(O trecho está truncado na base do Semantic Scholar; o texto completo está atrás do paywall do
IEEE Xplore. Recomenda-se baixar o PDF pela biblioteca da PUCPR para completar a citação — é a
única lacuna de transcrição deste levantamento.)*

**(b) Onde aparece:** revisão de trabalhos relacionados, no parágrafo de delimitação da
contribuição.

**(c) Por que citou:** **exclusivamente para se diferenciar.** Reconhecem Santos como trabalho
similar e listam, ponto a ponto, por que o deles é diferente. O primeiro diferencial declarado
é o mais importante para nós: **Santos não respeita a ordem temporal.**

**(d) Executou o modelo?** Não. Usaram SentenceBERT + *Adaptive Random Forest*.

**(e) Ligação com a nossa pesquisa — é a mais incômoda e a mais útil das sete:**

1. **A crítica que eles fazem a Santos aplica-se, hoje, a nós.** Usamos um modelo congelado em
   **fevereiro de 2024** para classificar notícias de **2018 a 2026**. O vocabulário da
   Petrobras mudou no período — política de preços, novo ciclo de dividendos, Margem
   Equatorial. Se a banca ler este artigo, a pergunta virá pronta. **É melhor que a resposta
   também esteja.**
2. **Eles dão o método para tratar o problema:** ajuste fino periódico (anual) com amostra
   reduzida de textos recentes, medindo F1-macro e tempo de execução. Concluem que supera o
   modelo estático na maioria dos anos.
3. **Temos a infraestrutura para testar isso hoje**, sem rotular nada novo:
   `Mestrado_PETR4/resultados_subperiodo_petr4.csv` já particiona por subperíodo.
4. **É uma ponte institucional real.** Não é citar um autor distante — é citar dois colegas de
   programa, com quem se pode conversar. Ver gap **G4** e a sugestão de pauta da Parte 3.

---

### ④ Teles e Figueiredo (2025)

> TELES, L. E. P.; FIGUEIREDO, C. M. S. Comparing LLMs for sentiment analysis in financial
> market news. **arXiv:2510.15929**, 3 out. 2025. Universidade do Estado do Amazonas (UEA).
> Fomento: FAPEAM.

**🟡 RELEVÂNCIA: MÉDIA-ALTA como oportunidade; BAIXA como precedente**

**(a) Citações literais** — são **duas**, ambas na Introdução, em parágrafos consecutivos:

> *"Sentiment analysis is one of the techniques used in the field of NLP to identify and extract
> information about the emotions expressed in a text, such as positivity, negativity, or
> neutrality **[Santos et al. 2023]**."*

> *"The goal is to understand how people feel about a particular issue or product **[Santos et
> al. 2023]**."*

**(b) Onde aparece:** Introdução, primeiro e segundo parágrafos.

**(c) Por que citou:** **puramente definicional.** Santos é usado para definir o que é análise
de sentimento — uma função que qualquer *survey* cumpriria igualmente bem. Não há qualquer
engajamento com o método, com os resultados ou com o modelo.

**(d) Executou o modelo?** **Não** — e este é o ponto. O artigo é brasileiro, de análise de
sentimento, de notícias, de mercado financeiro, cita Santos duas vezes, e ainda assim **avalia
nove modelos sem incluir o FinBERT-PT-BR**, sobre **três conjuntos em inglês** (Financial
Phrase Bank, StockEmotions e Tweet Financial News). Os modelos comparados: SVM, Random Forest e
MLP contra Gemma, DeBERTa, DeBERTaV3, XLM-RoBERTa, BART e Gemini 2.0-flash.

**(e) Ligação com a nossa pesquisa — uma oportunidade e uma ressalva:**

- **Oportunidade.** O melhor resultado global foi do **Gemini**, o mais consistente (acurácia
  acima de 70% nos três conjuntos: 80,4%, 74,1% e 78,9%). Se um LLM generativo supera encoders
  especializados em sentimento financeiro **em inglês**, classificar as nossas 300 manchetes
  com um LLM via *prompt* é um experimento de baixo custo, alto valor e — decisivo no contexto
  atual — **que não consome rotulagem humana**. Ver gap **G6**.
- **Ressalva a explicitar no texto.** O trabalho **não** sustenta que LLMs superariam o
  FinBERT-PT-BR em manchetes brasileiras: avalia corpora em inglês, e o desempenho do DeBERTa
  oscila de 86,2% (FPB) a 47,8% (TFN), sinal de forte sensibilidade ao conjunto. **Fazer esse
  teste em português é justamente o vão que este artigo deixa aberto.**
- **Nota sobre a citação em si:** ela é o exemplo mais nítido do padrão que caracteriza a
  lacuna. O trabalho mais próximo tematicamente é também o que menos engaja com o artefato.

---

### ⑤ Alves et al. (2024)

> ALVES, M. A. R.; MACEDO, M. B.; RIBEIRO, J.; MANCINE, L.; PEREIRA JÚNIOR, C. P. Sentimentos em
> Cena: uma análise dos comentários em trailers de filmes da Netflix Brasil no YouTube. In:
> **BraSNAM**, 13., 2024. Anais [...]. Porto Alegre: SBC, 2024. DOI: 10.5753/brasnam.2024.2974.

**🟢 RELEVÂNCIA: BAIXA — mas com uma frase aproveitável**

**(a) Citação literal** — Introdução:

> *"Porém, existe uma predominação de análises de textos em inglês, demonstrando assim uma
> **falta de trabalhos na língua portuguesa** [Santos et al. 2023]."*

**(b) Onde aparece:** Introdução, na motivação do trabalho.

**(c) Por que citou:** para sustentar a afirmação de **escassez de trabalhos de análise de
sentimento em português**. *Intent* classificado pelo Semantic Scholar como **`background`**.

**(d) Executou o modelo?** Não. Domínio de entretenimento (comentários de YouTube).

**(e) Ligação com a nossa pesquisa:**

- **Utilidade direta, ainda que modesta:** é uma citação de terceiro que **corrobora a premissa
  de escassez** da nossa introdução. Vale mais citar "Alves et al. (2024), apoiando-se em Santos
  et al. (2023), registram a predominância de análises em inglês e a falta de trabalhos em
  português" do que afirmar a escassez por conta própria.
- Serve também para demonstrar que a difusão do FinBERT-PT-BR **transbordou o domínio
  financeiro**, o que é um dado sobre o artefato.

---

### ⑥ Reichert e Perlin (2025)

> REICHERT, M. H.; PERLIN, M. S. Using ChatGPT for creating multi-language finance related
> sentiment dictionaries. **Computational Economics**, 2025. DOI: 10.1007/s10614-025-11233-3.

**🟡 RELEVÂNCIA: MÉDIA-ALTA** · Marcelo Perlin é professor da Escola de Administração da
**UFRGS** e autor de referência em finanças quantitativas no Brasil.

**(a) Citação literal:** **não foi possível transcrever.** O texto completo está atrás do
*paywall* da Springer. A citação a Santos et al. (2023) está registrada por **OpenAlex** e
**Semantic Scholar**, mas o trecho não está disponível em nenhuma das duas bases, e a página de
resumo aberta ao público não exibe a lista de referências. **Esta é a única das sete citações
que permanece não verificada quanto ao trecho literal.**

**(b) e (c)** — pendentes de acesso ao texto integral. **Recomenda-se obter o PDF pelo Portal
de Periódicos da CAPES via PUCPR** antes da versão final da dissertação.

**(d) Executou o modelo?** Provavelmente não como classificador. Pelo resumo, o artefato central
é um **dicionário léxico**, não um modelo neural.

**(e) Ligação com a nossa pesquisa — três pontos, todos derivados do resumo verificado:**

1. **O português está entre as línguas cobertas**, e a validação foi feita sobre os **últimos 50
   comunicados do COPOM** — ou seja, texto financeiro brasileiro institucional.
2. O resumo declara que o dicionário foi comparado a *"full-text NLP models"* e apresentou
   *"a more balanced sentiment classification profile"*. **Se esses "modelos de texto completo"
   incluírem o FinBERT-PT-BR, este é o único trabalho que o compara diretamente a uma
   alternativa — e o resultado não lhe é favorável.** Vale a pena confirmar.
3. **Um dicionário financeiro em português é a linha de base léxica que nos falta** — o
   equivalente brasileiro do Loughran-McDonald. Uma comparação "encoder × dicionário × LLM"
   fortaleceria substancialmente o capítulo de resultados. Ver gap **G8**.

---

### ⑦ Tanaka et al. (2026)

> TANAKA, S. A.; ANDRADE, J. V. C.; BOVO, A. B.; CONVERTI, A.; SANCHES, D. S.; SIQUEIRA, H. V. A
> machine learning-driven CRM approach for identifying member churn in a Brazilian
> agro-industrial cooperative: a practical case study. **Algorithms**, v. 19, n. 3, 2026.
> DOI: 10.3390/a19030180.

**🟢 RELEVÂNCIA: MUITO BAIXA — a citação é, muito provavelmente, imprecisa**

**(a) Citação literal** — Seção de metodologia, sobre *Modeling*:

> *"Training and validation relied on **stratified subsets to mitigate sampling bias [39,40]**,
> reflecting the CRISP-DM emphasis on representativeness during model assessment."*

*(A referência [39] é Santos, Bianchi e Costa (2023); a [40] é Chawla et al. (2002), o artigo do
SMOTE.)*

**(b) Onde aparece:** metodologia, justificando o uso de subconjuntos estratificados.

**(c) Por que citou:** para sustentar o uso de **amostragem estratificada** como mitigação de
viés amostral. **Observação honesta: o artigo de Santos não trata de amostragem estratificada
como contribuição metodológica.** Ele usa validação cruzada 5-*fold*, o que é assunto próximo
mas não igual. A citação parece ser **imprecisa ou de conveniência** — o par [39,40] faz muito
mais sentido para o SMOTE, que é sobre balanceamento de classes, do que para o FinBERT-PT-BR.

**(d) Executou o modelo?** Não. Nem sequer trabalha com texto — o trabalho é sobre *churn* em
cooperativa agroindustrial, com dados tabulares de CRM.

**(e) Ligação com a nossa pesquisa — apenas um aproveitamento lateral:**

- **A única coisa aproveitável é o uso de SHAP** para explicabilidade dos modelos tabulares
  (Random Forest, XGBoost, SVC e *ensemble* por votação). Uma análise SHAP mostrando **quanto o
  sentimento contribui, marginalmente, para a previsão de volatilidade** responderia com
  elegância a uma das ponderações da banca. Ver gap **G13**.
- **Não recomendo citar este trabalho** como evidência de adoção do FinBERT-PT-BR. Se citado,
  citar apenas pelo uso de SHAP.

---

### Síntese quantitativa das citações

| # | Trabalho | N.º de citações | Onde | Função da citação | Executou o modelo? | Relevância |
|---|---|---|---|---|---|---|
| ① | Błoch, Santana e Amantino (2026) | 1 | Método | **Escolha de ferramenta** | **SIM** (comitê c/ pysentimiento) | Muito alta |
| ② | Abílio, Coelho e Silva (2024) | 3 | Revisão | Taxonomia + **delimitação por contraste** | Não | Alta |
| ③ | Imai et al. (2024) | 1 | Revisão | **Delimitação por contraste** | Não | Alta |
| ④ | Teles e Figueiredo (2025) | 2 | Introdução | Definicional | Não | Média-alta (oportunidade) |
| ⑤ | Alves et al. (2024) | 1 | Introdução | *Background* (escassez em PT) | Não | Baixa |
| ⑥ | Reichert e Perlin (2025) | ? | ? | **Não verificada** (*paywall*) | Provavelmente não | Média-alta |
| ⑦ | Tanaka et al. (2026) | 1 | Método | Amostragem estratificada — **provável imprecisão** | Não | Muito baixa |

**Leitura do padrão, em quatro observações:**

1. **Das sete, apenas uma executou o modelo — e fora do domínio financeiro.**
2. **Duas citam Santos para se diferenciar dele** (② e ③), o que é sinal de que o trabalho é
   reconhecido como referência obrigatória da área, mesmo sem ser reutilizado.
3. **Duas citam-no de forma meramente definicional ou de contexto** (④ e ⑤) — a citação poderia
   ser substituída por qualquer *survey* sem perda.
4. **Uma citação é provavelmente imprecisa** (⑦), e uma não é verificável (⑥).

**Consequência para a dissertação:** o FinBERT-PT-BR é um artefato com **177.384 downloads
mensais** e **reconhecimento acadêmico como referência**, mas com **adoção acadêmica aplicada
praticamente nula na tarefa para a qual foi construído**. Esse contraste — muito uso prático,
quase nenhuma validação acadêmica — é o núcleo do argumento de contribuição.

---

## Parte 2 — Gaps de pesquisa

### Critério de classificação

O Prof. Emerson pediu gaps que possam ser **usados e resolvidos** na pesquisa. Aplico três
filtros a cada candidato, e sou explícito quando um deles falha:

- **Evidência.** O gap está demonstrado pelo levantamento, ou é apenas plausível? Registro a
  fonte concreta.
- **Aderência.** Resolvê-lo pertence ao escopo da dissertação, ou seria outra pesquisa?
- **Viabilidade.** É executável até a defesa (mar/2027) com os dados e a infraestrutura que
  temos, e **sem depender de rotulagem manual** enquanto ela estiver suspensa?

> ⚠️ **Ressalva metodológica obrigatória.** Um gap só pode ser afirmado como tal na dissertação
> se estiver **respaldado pela nossa RSL**, com protocolo de busca declarado. O que segue é uma
> **hipótese de gap fundamentada em levantamento dirigido** (7 trabalhos citantes + 28
> referências do artigo-base + busca em OpenAlex, Semantic Scholar e HuggingFace), **não** em
> revisão sistemática. Antes de qualquer afirmação de ineditismo no texto final, cada gap
> priorizado precisa passar pela RSL formal — temos a infraestrutura em
> `datasets_refino/04_revisao_sistematica_estudos_v1.csv` e `gerar_rsl_dataset.py`.

---

### Os treze gaps

---

#### G1 — Previsão de **volatilidade** de ativo brasileiro a partir de sentimento de notícias

**🔴 PRIORIDADE MÁXIMA — é a contribuição central da dissertação**

**Evidência.** Dos sete trabalhos citantes e dos 28 referenciados no artigo-base, **nenhum prevê
volatilidade**. Todos operam sobre direção, retorno ou estratégia de carteira: Santos et al.
(2023) constroem índice agregado e carteira; Hiew et al. (2019) preveem retorno com LSTM;
Bollen et al. (2011) e Pagolu et al. (2016) preveem direção; Januário et al. (2022) trabalham
notícias sem previsão de volatilidade.

**Por que o gap existe.** A literatura converge para desempenho de direção **próximo ao acaso** —
os 87,6% de Bollen et al. (2011) nunca foram replicados de forma robusta. Diante disso, os
trabalhos migram para carteira, índice agregado ou comparação de classificadores. **Poucos
migram para volatilidade**, que é onde o sinal textual efetivamente tem conteúdo — notícia gera
incerteza antes de gerar direção.

**Aderência.** Total. É literalmente o título da dissertação.

**Como resolver — já está parcialmente resolvido.** Temos GARCH(1,1), avaliação
Mincer-Zarnowitz/QLIKE e regressão quantílica de volatilidade rodando
(`resultados_volatilidade_petr4.json`, `resultados_vol_quantilica_petr4.json`,
`resultados_vol_sentimento_petr4.json`). **O que falta é editorial, não computacional:**
reposicionar a volatilidade como resultado principal e a direção como **resultado negativo
reportado**, com a literatura acima sustentando que o acaso na direção é o padrão da área, e não
uma falha nossa.

**Risco.** Nenhum relevante. É consolidação do que já existe.

---

#### G2 — Degradação por **transferência de domínio**: notícias gerais → ativo específico

**🔴 PRIORIDADE MÁXIMA — o dado já está na mão**

**Evidência.** Santos et al. (2023) relatam acurácia **0,76** e F1 **0,73** sobre sentenças de
notícias gerais de mercado. Medimos **0,58** (κ = 0,371) sobre manchetes de PETR4
(`conjunto_ouro/relatorio_validacao_ouro.txt`). **Nenhum trabalho da literatura examinada
quantifica essa degradação.** O próprio autor não a testou.

**Por que o gap existe.** Modelos de domínio financeiro são publicados com métricas de domínio
genérico, e reutilizados em subdomínios sem revalidação. É um problema conhecido em PLN, mas
**não documentado para o par (sentimento financeiro PT-BR → ativo único)**.

**Aderência.** Total. É pré-requisito de validade de todo o resto da dissertação.

**Como resolver — três componentes, todos viáveis:**
1. **Decomposição das causas.** A queda tem três fontes conjugadas: unidade textual (sentença vs.
   manchete), escopo (mercado geral vs. ativo único) e gabarito (dupla anotação vs. anotador
   único). **É possível isolar as duas primeiras** com o corpus atual, sem rotular nada:
   classificar o mesmo conjunto de notícias em três granularidades (manchete / manchete+subtítulo
   / primeiro parágrafo) e medir a variação. Ver **G9**.
2. **Explicação do mecanismo.** Błoch et al. (2026) fornecem a hipótese: o modelo opera por
   léxico, não por contexto. Nossa matriz de confusão a corrobora — a classe Neutra é a mais
   confundida.
3. **Elevação a resultado.** Deixar de tratar os 58% como limitação a justificar, e passar a
   tratá-los como **medida de um fenômeno**.

**Risco.** A validade da medida depende da qualidade do gabarito (ver **G5**). É preciso declarar
essa dependência com honestidade.

---

#### G3 — Adaptação de domínio ao nível de **setor/ativo**, e não de mercado

**🔴 PRIORIDADE ALTA — é a frente que avança sem rótulo**

**Evidência.** Santos et al. (2023) declaram, em Trabalhos Futuros, literalmente: *"é possível
aprimorar o modelo de análise de sentimentos, utilizando uma base maior e mais específica de
textos financeiros"* e *"aplicar a metodologia para setores específicos da bolsa de valores"*.
**Passados três anos, nenhum dos sete trabalhos citantes o fez.**

**Por que o gap existe.** Exige corpus setorial grande, que é caro de montar. **Nós já o
temos:** ~205 mil notícias de PETR4/petróleo/estatais.

**Aderência.** Alta. Melhora o insumo de todo o pipeline a jusante.

**Como resolver.** Replicar a Etapa 1 de Santos: *masked language modeling* com máscara de 15% e
*lr* 2e-5, partindo (i) do próprio FinBERT-PT-BR e (ii) do BERTimbau large, medindo
**perplexidade** em *holdout* de 10 mil notícias não vistas. Alvo: bater a perplexidade do
modelo de partida, como Santos bateu o BERTimbau (1,51 → 1,24).

**Por que é a frente certa agora — três razões:**
- **É *self-supervised*: não consome um único rótulo.** É integralmente compatível com a
  suspensão da rotulagem.
- **A métrica é intrínseca:** perplexidade não depende de gabarito humano. Produz resultado
  reportável mesmo com o conjunto-ouro sob suspeita.
- **É a etapa de maior ganho documentado** no trabalho original.

**Risco técnico a declarar.** O HuggingFace publica apenas o **classificador**
(`BertForSequenceClassification`), não o modelo de linguagem puro. Continuar o MLM a partir dele
significa partir de um modelo que já passou por ajuste supervisionado — viável
(`AutoModelForMaskedLM`, descartando a cabeça de classificação), mas menos limpo. **Daí a
recomendação de rodar as duas variantes:** a comparação entre elas é, ela própria, um resultado.

---

#### G4 — ***Concept drift*** em sentimento financeiro PT-BR

**🟠 PRIORIDADE ALTA — e é a crítica que a banca fará se não anteciparmos**

**Evidência.** Imai et al. (2024) demonstram que modelos de linguagem estáticos degradam em
fluxos de notícias brasileiras e que o ajuste fino anual com amostra reduzida supera o modelo
estático **na maioria dos anos analisados**. Citam Santos justamente para dizer que ele **não
respeita a ordem temporal**. Nenhum trabalho de sentimento financeiro em PT-BR trata do
problema.

**Por que nos atinge diretamente.** Usamos um modelo congelado em **13/02/2024** sobre corpus de
**2018 a 2026**. As notícias de 2025 e 2026 sobre a Petrobras contêm vocabulário e enquadramento
que o modelo não viu.

**Aderência.** Alta. É uma ameaça à validade interna dos nossos resultados.

**Como resolver — em três níveis de ambição:**
1. **Mínimo (obrigatório):** declarar a limitação explicitamente no capítulo de método, com
   Imai et al. (2024) como respaldo. Custo: um parágrafo.
2. **Intermediário (recomendado):** medir a degradação por subperíodo. Já temos
   `resultados_subperiodo_petr4.csv`. Se a acurácia contra o conjunto-ouro cair nos anos
   recentes, temos evidência de *drift* — e isso é um **resultado**.
3. **Ambicioso (se houver tempo):** adaptação de domínio incremental por ano, na linha de Imai,
   medida por perplexidade. Combina com **G3** e continua sem consumir rótulo.

---

#### G5 — Ausência de ***benchmark*** público de sentimento financeiro rotulado em PT-BR

**🟠 PRIORIDADE ALTA — é a contribuição de artefato mais durável da dissertação**

**Evidência, em três camadas:**
- Santos et al. (2023) **não publicaram** os 503 textos rotulados. O repositório HuggingFace tem
  dez arquivos e **nenhum dado de treinamento**.
- Teles e Figueiredo (2025), diante da falta de um conjunto brasileiro, recorrem a **três
  conjuntos em inglês** — o Financial Phrase Bank inclusive numa versão traduzida.
- Não existe, em português, um equivalente ao **Financial PhraseBank** (MALO et al., 2014).

**Por que o gap existe.** Anotação é cara e não rende publicação sozinha. Mas é precisamente o
que trava a área inteira.

**Aderência.** Alta — **e é o gap que dialoga diretamente com a orientação de suspender a
rotulagem.** Não é contradição: o Prof. Emerson mandou parar a rotulagem *na forma atual*, e a
Seção 1.1 do documento anterior mostra que a forma atual tem defeito estrutural. **Refundar o
protocolo é o caminho para transformar um passivo em contribuição.**

**Como resolver — quando a rotulagem for retomada, e nesta ordem:**
1. **Dupla anotação de 100 a 150 manchetes** das 300 já rotuladas — não mais volume, **segunda
   opinião**. É a menor intervenção que torna o gabarito defensável.
2. **Calcular *Krippendorff's alpha*** (ARTSTEIN; POESIO, 2008; KRIPPENDORFF, 2018). O α admite
   número variável de anotadores por item e dados faltantes, ao contrário do kappa de Cohen que
   usamos hoje — é a métrica correta para anotadores com disponibilidade desigual.
3. **Adotar a definição operacional literal de Santos** e a categoria **"não se aplica"**, com
   descarte por discordância.
4. **Usar modelagem de tópicos ou *zero-shot*** para pré-selecionar textos e sugerir classe ao
   anotador (POURSABZI-SANGDEH; BOYD-GRABER, 2015; ALCOFORADO et al., 2022). **É a resposta
   técnica direta à objeção do Prof. Emerson sobre a falta de especialização em finanças:** a
   sugestão automática reduz a carga cognitiva e a dependência de conhecimento de domínio.
5. **Publicar o conjunto** com DOI (Zenodo), licença aberta e ficha de anotação.

**Ganho estratégico.** Um conjunto-ouro público de sentimento financeiro PT-BR **ancorado num
ativo real** seria citável independentemente dos resultados de previsão — é o tipo de
contribuição que sobrevive à dissertação.

---

#### G6 — LLM generativo × encoder especializado em **português financeiro**

**🟠 PRIORIDADE ALTA — melhor relação resultado/esforço do plano**

**Evidência.** Teles e Figueiredo (2025) mostram que LLMs superam modelos clássicos em
sentimento financeiro, com o Gemini como mais consistente (acurácia > 70% nos três conjuntos).
**Mas fazem isso inteiramente em inglês.** A comparação em português, contra um encoder de
domínio, **não existe na literatura examinada**.

**Aderência.** Alta. Responde à pergunta que a banca fará: *"por que não usar um LLM?"* — e
responde **com dados nossos**, não com opinião.

**Como resolver.** Classificar as 300 manchetes do conjunto-ouro com um LLM via *prompt*,
usando a **instrução literal de Santos** (*"Classifique a notícia considerando se o texto
implicaria em uma rentabilidade Positiva, Negativa ou Neutra…"*), e comparar contra o
FinBERT-PT-BR e contra o rótulo humano nos mesmos itens. Reportar acurácia, F1-macro e kappa.

**Por que é viável agora.** Não consome rotulagem nova — usa o gabarito que já existe. Custo
estimado: 4 horas.

**Três resultados possíveis, todos publicáveis:**
- O LLM ganha → temos evidência para migrar, e um achado inédito em PT-BR.
- O encoder ganha → temos justificativa empírica para mantê-lo, o que hoje não temos.
- Empatam → o argumento passa a ser custo, reprodutibilidade e determinismo, que favorecem o
  encoder.

**Ressalvas a declarar:** não determinismo do LLM (fixar *seed*/temperatura e reportar), custo
por chamada, e a advertência de Abílio et al. (2024) sobre modelos generativos alterarem valores
numéricos.

---

#### G7 — **Comitê de modelos complementares** em sentimento financeiro PT-BR

**🟠 PRIORIDADE MÉDIA-ALTA — gap descoberto na leitura integral, não estava no radar**

**Evidência.** Błoch, Santana e Amantino (2026) aplicam uma **máquina de comitê** combinando o
FinBERT-PT-BR (comportamento **léxico**) com o `pysentimiento` (comportamento **contextual**),
justamente porque são complementares — e validam contra especialista humano. **Fizeram isso em
História; ninguém fez em finanças.**

**Por que interessa especificamente a nós.** A fraqueza que a nossa matriz de confusão revela é
exatamente a que o comitê corrige: a classe **Neutra** é a mais confundida (58 dos 124 casos
neutros foram para os extremos), o que é a assinatura de um modelo dominado por termos
carregados. Um segundo modelo, contextual, tende a segurar esses casos.

**Aderência.** Alta, e **barata**.

**Como resolver.** Rodar `pysentimiento` (versão PT) sobre o conjunto-ouro e combinar com o
FinBERT-PT-BR por (i) voto simples, (ii) média das probabilidades e (iii) regra de abstenção —
quando discordam, classificar como Neutro. Medir contra o gabarito humano. **Não consome
rótulo novo.**

**Ganho adicional.** Um índice de sentimento construído sobre o comitê é mais estável, o que
tende a melhorar o sinal na previsão de volatilidade — que é o eixo de **G1**.

---

#### G8 — **Dicionário léxico financeiro PT-BR** como linha de base

**🟡 PRIORIDADE MÉDIA**

**Evidência.** Reichert e Perlin (2025) constroem dicionários de sentimento financeiro
multilíngues por ChatGPT, **com o português incluído** e validados sobre os últimos 50
comunicados do **COPOM**. Declaram comparação contra *"full-text NLP models"*. Nenhum trabalho
compara diretamente dicionário léxico × encoder de domínio em português financeiro **sobre
notícias de um ativo**.

**Aderência.** Média-alta. Uma linha de base léxica é o que falta para o nosso capítulo de
resultados ter três pontos de comparação em vez de dois.

**Como resolver.** Obter o dicionário pelo Portal CAPES; aplicar às manchetes; comparar contra
FinBERT-PT-BR, contra o comitê de **G7** e contra o LLM de **G6**, no mesmo conjunto-ouro.

**Ressalva.** Depende de acesso ao artigo e de o dicionário estar publicado. Se não estiver,
o Loughran-McDonald traduzido serve como aproximação, com a limitação devidamente declarada.

---

#### G9 — Efeito da **granularidade textual** (manchete × subtítulo × corpo)

**🟡 PRIORIDADE MÉDIA — barato e fecha um flanco da banca**

**Evidência.** Santos avaliou **sentenças de notícia**; nós avaliamos **manchetes**. O modelo
suporta 512 tokens, o que permitiria texto muito maior. **Nenhum trabalho mede o efeito da
granularidade** sobre a acurácia de sentimento financeiro em PT-BR.

**Aderência.** Alta — hoje a nossa escolha por manchetes **não está formalmente justificada** na
dissertação, o que é um flanco aberto.

**Como resolver.** Ablação em três níveis sobre o mesmo conjunto de notícias: manchete;
manchete + subtítulo; manchete + primeiro parágrafo. Medir acurácia e kappa contra o gabarito e,
em seguida, o efeito no ISM e na previsão de volatilidade. **Não consome rótulo novo** — o
gabarito humano é do evento noticioso, não do recorte de texto.

**Ganho conceitual.** Conecta-se a Liu (2012), que distingue os níveis documento, sentença e
aspecto. A escolha passa a ser fundamentada, e não conveniência de coleta.

---

#### G10 — **Filtro de relevância ao ativo** antes da agregação do índice

**🟡 PRIORIDADE MÉDIA — contribuição já existente, ainda não formalizada**

**Evidência.** Nosso conjunto-ouro registra que apenas **111 de 300 manchetes (37,0%)** foram
marcadas como relevantes à PETR4. Os trabalhos examinados constroem índices de sentimento
agregando **todas** as notícias coletadas: Santos calcula o índice sobre "uma amostra das
notícias gerais coletadas". **Nenhum aplica filtro de relevância por ativo antes de agregar.**

**Por que importa.** Se 63% das notícias que entram no índice não dizem respeito ao ativo, o
índice mede ruído de mercado, não sinal do ativo. Isso pode explicar parte da fraqueza do sinal
de direção.

**Aderência.** Alta. Já temos `gerar_pipeline_relevancia.py` e
`resultados_relevancia_2026-07-05.json`.

**Como resolver.** Formalizar como **experimento de ablação**: ISM com todas as notícias × ISM
apenas com as relevantes × ISM ponderado por relevância. Comparar o poder preditivo de cada
um sobre volatilidade. **Se o filtro melhorar, é resultado; se não melhorar, também é** — e
responde à pergunta de por que o sinal de direção é fraco.

---

#### G11 — Comparação de **formulações do índice de sentimento**

**🟢 PRIORIDADE MÉDIA-BAIXA**

**Evidência.** A fórmula (Pos − Neg) / (Pos + Neu + Neg) vem de Hiew et al. (2019) e é adotada
por Santos sem discussão de alternativas. **Ninguém compara formulações.** Nós já temos uma
variante — o ISM ponderado (`resultados_ism_ponderado_petr4.csv`) — e usamos polaridade ×
confiança, o que **já é uma variante não documentada na literatura**.

**Como resolver.** Ablação entre: contagem simples de Santos/Hiew; média de polaridade ×
confiança (o nosso); ISM ponderado por relevância; e versão com janela exponencial. Avaliar por
capacidade preditiva de volatilidade.

**Ressalva honesta.** É contribuição incremental. Vale como **seção**, não como eixo.

---

#### G12 — **Significância estatística** ausente nas comparações de encoder

**🟢 PRIORIDADE MÉDIA-BAIXA — mas é higiene metodológica obrigatória**

**Evidência.** Santos aplicou *bootstrapping* (EFRON, 1992) com intervalos de confiança de 80% e
teste Z sobre a distribuição empírica reamostrada (monografia, Seção 4.2.4, Figuras 15 e 16).
**A nossa tabela `resultado_encoders_petr4.csv` reporta diferenças de −1,67, −5,33 e −16,00
pontos percentuais sem qualquer teste.**

**Por que é urgente.** Com n = 300 e desvios-padrão entre 2,7 e 8,4 pontos, a diferença de
−1,67 pp do BERTimbau large é **seguramente indistinguível de zero**. Levar essa tabela à banca
sem intervalo de confiança é convidar a crítica.

**Como resolver.** *Bootstrap* com reamostragem sobre o conjunto de teste, intervalos de
confiança e teste Z, replicando o protocolo de Santos. Custo: cerca de 2 horas.

**Nota.** Não é um gap da literatura — é um gap **nosso**. Registro aqui porque bloqueia a
credibilidade de **G3** e **G6**.

---

#### G13 — **Explicabilidade** da contribuição marginal do sentimento

**🟢 PRIORIDADE MÉDIA-BAIXA — alto valor de comunicação**

**Evidência.** Tanaka et al. (2026) usam SHAP para explicabilidade em modelos tabulares. Nenhum
dos trabalhos de sentimento financeiro examinados aplica atribuição de importância para
quantificar **quanto o componente textual contribui** para a previsão.

**Aderência.** Alta. Responde diretamente à ponderação da banca sobre a contribuição marginal do
sentimento — a pergunta "o sentimento realmente ajuda, ou o GARCH sozinho já explicava tudo?".

**Como resolver.** SHAP sobre o XGBoost de fusão (`modelo_xgb_fusion.json`), separando a
contribuição das *features* de sentimento das de preço/volatilidade. Complementa a ablação de
categorias que já temos (`resultados_ablacao_categorias_petr4.csv`).

**Ganho.** Transforma um resultado numérico em uma figura que a banca entende em dez segundos.

---

### Priorização: quais gaps atacar

| Gap | Prioridade | Consome rótulo? | Executável até 10/08? | Esforço | Onde entra na dissertação |
|---|---|---|---|---|---|
| **G1** Volatilidade | 🔴 Máxima | Não | Sim (editorial) | Baixo | Contribuição principal |
| **G2** Transferência de domínio | 🔴 Máxima | Não | Sim (editorial) | Baixo | Resultado próprio |
| **G3** Adaptação de domínio (MLM) | 🔴 Alta | **Não** | Sim (Colab, 6–10 h) | Médio | Cap. método + resultados |
| **G6** LLM × encoder | 🟠 Alta | **Não** | Sim (~4 h) | Baixo | Cap. resultados |
| **G12** Significância estatística | 🟢 Média-baixa | Não | Sim (~2 h) | Baixo | Cap. método |
| **G4** *Concept drift* | 🟠 Alta | Não | Parcial (nível 1 e 2) | Baixo/Médio | Limitações + resultados |
| **G7** Comitê de modelos | 🟠 Média-alta | **Não** | Sim (~3 h) | Baixo | Cap. resultados |
| **G9** Granularidade textual | 🟡 Média | Não | Não (pós-10/08) | Médio | Cap. método |
| **G10** Filtro de relevância | 🟡 Média | Não | Não (pós-10/08) | Médio | Cap. resultados |
| **G13** SHAP | 🟢 Média-baixa | Não | Não (pós-10/08) | Baixo | Cap. resultados |
| **G11** Formulações do ISM | 🟢 Média-baixa | Não | Não (pós-10/08) | Médio | Seção de robustez |
| **G8** Dicionário léxico | 🟡 Média | Não | Não (depende de acesso) | Médio | Cap. resultados |
| **G5** *Benchmark* público | 🟠 Alta | **Sim** | **Não** (rotulagem suspensa) | Alto | Contribuição de artefato |

**Observação sobre a coluna "consome rótulo".** **Doze dos treze gaps não dependem de rotulagem
manual.** Isso é relevante para a mentoria de 10/08: a suspensão da rotulagem **não paralisa a
pesquisa** — apenas adia o G5, que é o mais ambicioso.

### Os cinco que recomendo levar à mentoria

1. **G1 + G2** — reposicionamento editorial, custo quase zero, resolve a crítica de que a
   direção fica no acaso.
2. **G3** — a frente técnica principal, *self-supervised*, sem rótulo.
3. **G6** — o experimento de melhor relação resultado/esforço.
4. **G7** — descoberta desta rodada, barata, e ataca exatamente a fraqueza medida.
5. **G5** — apresentar como **proposta de retomada estruturada** da rotulagem, não como pedido
   para voltar ao que estava sendo feito.

---

### O que NÃO recomendo perseguir

Registro por honestidade metodológica, porque nem tudo que parece gap é gap aproveitável:

| Ideia | Por que não |
|---|---|
| **Treinar um encoder do zero para o domínio** | Custo computacional incompatível com o prazo, e Santos já mostrou que a adaptação por MLM captura a maior parte do ganho. |
| **Estender a estratégia "apostando contra o sentimento"** de Santos | É finanças de carteira, não previsão de ativo. Descaracteriza o objeto da dissertação e abre um flanco em que não temos competência declarada. |
| **Reproduzir o índice de sentimento vs. dados macroeconômicos** (inflação, PIB, desemprego) | Santos propõe como trabalho futuro dele. É pesquisa de macroeconomia, não da nossa pergunta. Só faria sentido no doutorado. |
| **Ampliar o conjunto-ouro de 300 para 600 manchetes** com o protocolo atual | Dobra o custo mantendo o defeito estrutural — anotador único, sem métrica de concordância. Ver Seção 9.1 do documento anterior. |
| **Aplicar NER financeiro** na linha de Abílio et al. (2024) | Tarefa diferente, exige novo corpus anotado. Interessante para o doutorado. |
| **Migrar o pipeline inteiro para LLM generativo** | Perde reprodutibilidade e determinismo, e Abílio et al. (2024) documentam alteração de valores numéricos por modelos generativos. Usar LLM como **comparação** (G6), não como substituição. |

---

## Parte 3 — Como levar isso à mentoria

### Roteiro sugerido (30 minutos)

**1. Abrir pela correção, não pelo resultado (2 min).**
Começar dizendo que a leitura integral corrigiu uma afirmação do levantamento anterior — um
trabalho **usou** o modelo, fora do domínio financeiro. Isso estabelece que o levantamento foi
verificado a fundo, e não montado por resumos.

**2. A tabela de citações (5 min).**
Mostrar a síntese quantitativa da Parte 1. A mensagem em uma frase: *"o FinBERT-PT-BR é citado
como referência obrigatória e quase nunca usado na tarefa para a qual foi feito."*

**3. Os dois gaps de custo zero (5 min).**
G1 e G2. São reposicionamento editorial de resultados que já temos. Mostrar a tabela comparativa
da coluna "Volatilidade", em que **todas as linhas são "Não" exceto a nossa**.

**4. A frente técnica (8 min).**
G3, G6 e G7 — as três que avançam **sem rotulagem**. Enfatizar que a suspensão da rotulagem não
paralisou nada: doze dos treze gaps não dependem dela.

**5. A proposta sobre a rotulagem (7 min).**
G5. Apresentar como **proposta de retomada estruturada**, com o protocolo de Santos como
respaldo: dupla anotação de 100–150, *Krippendorff's alpha*, categoria "não se aplica",
pré-seleção por modelagem de tópicos. Ser explícito de que **não é um pedido para voltar ao que
estava sendo feito** — é o reconhecimento de que o que estava sendo feito tinha um defeito
anterior ao apontado.

**6. O pedido (3 min).**
Consultar sobre aproximação com o **Prof. Jean Paul Barddal (PPGIa/PUCPR)**, coautor do trabalho
③, a respeito de *concept drift* no nosso corpus. É colaboração interna, de baixo custo e alto
retorno.

### Perguntas que provavelmente virão, e as respostas

| Pergunta provável | Resposta preparada |
|---|---|
| *"Como você sabe que é um gap, e não só que você não achou?"* | É hipótese de gap fundamentada em levantamento dirigido (7 citantes + 28 referências + OpenAlex/S2/HuggingFace), **não** RSL. Antes de afirmar ineditismo no texto final, cada gap priorizado passa pela RSL formal, cuja infraestrutura já existe em `datasets_refino/`. |
| *"Por que não usar um LLM e resolver logo?"* | É exatamente o G6, e vou medir em vez de opinar. Ressalva: Abílio et al. (2024) documentam que modelos generativos alteraram valores monetários e percentuais em texto financeiro. |
| *"Se o gabarito não é confiável, como você valida qualquer coisa?"* | Por isso o G3 usa **perplexidade**, que é métrica intrínseca e não depende de gabarito. E por isso o G5 propõe refundar o gabarito, não ampliá-lo. |
| *"A acurácia de 58% não invalida a pesquisa?"* | Não — mede a transferência de domínio (G2), que é um resultado. E o eixo da dissertação é volatilidade (G1), não classificação de sentimento. |
| *"Qual é a contribuição, afinal?"* | Três: previsão de **volatilidade** de ativo brasileiro a partir de sentimento (G1); quantificação da **degradação por transferência de domínio** (G2); e um encoder **adaptado ao subdomínio Petrobras** (G3). Mais, se der tempo, o *benchmark* público (G5). |

---

## Anexo — Arquivos desta entrega

| Arquivo | Conteúdo |
|---|---|
| `CITACOES_E_GAPS_2026-08-10.md` | Este documento |
| `CITACOES_E_GAPS_2026-08-10.docx` | Versão ABNT para o orientador |
| `citacoes_por_trabalho.csv` | Tabela das citações: trecho literal, seção, função, uso do modelo, ligação |
| `gaps_pesquisa.csv` | Tabela dos 13 gaps: evidência, aderência, como resolver, prioridade, esforço |
| `_bloch2026.pdf` / `.txt` | Texto integral de Błoch, Santana e Amantino (2026) |
| `_abilio2024.pdf` / `.txt` | Texto integral de Abílio, Coelho e Silva (2024) |
| `_alves2024.pdf` / `.txt` | Texto integral de Alves et al. (2024) |
| `_tanaka2026.pdf` / `.txt` | Texto integral de Tanaka et al. (2026) |
| `_teles2025.pdf` / `.txt` | Texto integral de Teles e Figueiredo (2025) |

**Não obtidos:** Imai et al. (2024), *paywall* do IEEE Xplore — citação parcial via Semantic
Scholar; e Reichert e Perlin (2025), *paywall* da Springer — apenas o resumo. Ambos são
acessíveis pelo Portal de Periódicos da CAPES via PUCPR.
