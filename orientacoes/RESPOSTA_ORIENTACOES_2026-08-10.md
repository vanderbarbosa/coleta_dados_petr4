# Resposta às Orientações da Mentoria de 29/07/2026 (Prof. Dr. Emerson Cabrera Paraiso)

**Mestrando:** Vanderlei Barbosa da Silva
**Orientador:** Prof. Dr. Julio Cesar Nievola (PUCPR)
**Mentoria de origem:** 29/07/2026 · **Entrega prevista:** 10/08/2026
**Documento elaborado em:** 03/08/2026
**Objeto:** Dissertação *"O Impacto do Sentimento de Notícias Financeiras na Previsão de Direção e Volatilidade do Ativo PETR4"*

---

## Sumário

1. [Nota metodológica e delimitação de escopo](#1-nota-metodológica-e-delimitação-de-escopo)
2. [Sumário executivo — as sete conclusões que importam](#2-sumário-executivo--as-sete-conclusões-que-importam)
3. [Tarefa 1 — O BERT financeiro em pesquisas diversas](#3-tarefa-1--o-bert-financeiro-em-pesquisas-diversas)
4. [Tarefa 2 — Como os trabalhos utilizaram o FinBERT-PT-BR](#4-tarefa-2--como-os-trabalhos-utilizaram-o-finbert-pt-br)
5. [Tarefa 3 — Há outro encoder BERT melhor para a pesquisa?](#5-tarefa-3--há-outro-encoder-bert-melhor-para-a-pesquisa)
6. [Tarefa 4 — Há trabalhos tentando fazer o mesmo que nós?](#6-tarefa-4--há-trabalhos-tentando-fazer-o-mesmo-que-nós)
7. [Tarefa 5 — Artigo SBC/BWAIF nº 24960](#7-tarefa-5--artigo-sbcbwaif-nº-24960)
   - 7.1 [Resumo do artigo](#71-resumo-do-artigo)
   - 7.2 [Relação com a nossa pesquisa e o que podemos usar](#72-relação-com-a-nossa-pesquisa-e-o-que-podemos-usar)
   - 7.3 [Resumo compilado das 28 referências do artigo](#73-resumo-compilado-das-28-referências-do-artigo)
8. [Tarefa 6 — Estudo do repositório HuggingFace `lucas-leme/FinBERT-PT-BR`](#8-tarefa-6--estudo-do-repositório-huggingface-lucas-lemefinbert-pt-br)
9. [Tarefa 7 — Trabalhos que citam Lucas Leme (Google Scholar)](#9-tarefa-7--trabalhos-que-citam-lucas-leme-google-scholar)
10. [Achados operacionais sobre o nosso próprio código e dados](#10-achados-operacionais-sobre-o-nosso-próprio-código-e-dados)
11. [Plano de ação recomendado até 10/08/2026](#11-plano-de-ação-recomendado-até-10082026)
12. [Referências consultadas neste levantamento](#12-referências-consultadas-neste-levantamento)

---

## 1. Nota metodológica e delimitação de escopo

Este documento responde, item a item, às sete orientações registradas em
`orientacoes/orientacoes.txt`. Todas as afirmações apresentadas foram obtidas de fontes
primárias — o PDF integral do artigo do BWAIF, o PDF integral da monografia do autor,
os arquivos de configuração do repositório HuggingFace e as APIs bibliográficas OpenAlex
e Semantic Scholar. Os arquivos-fonte baixados durante a elaboração ficaram na própria
pasta `orientacoes/` (arquivos com prefixo `_`), de modo que qualquer afirmação possa ser
reconferida sem nova coleta.

Três limitações precisam ser declaradas com transparência, porque afetam a completude de
partes específicas da entrega:

**(a) O vídeo da mentoria não foi transcrito.** O arquivo
`monitoria_Emerson_2026-07-29.mp4` (227 MB) não pôde ser processado nesta máquina: não há
`ffmpeg` instalado e a instalação de um transcritor automático (`faster-whisper`) esbarrou
em uma falha pré-existente da biblioteca PyTorch, descrita na Seção 10.3. O trabalho foi,
portanto, conduzido a partir de `orientacoes.txt`, que o próprio mestrando descreve como o
compilado das orientações e tarefas solicitadas. **Recomenda-se conferir se o vídeo contém
alguma orientação adicional que não tenha sido registrada no arquivo de texto.**

**(b) A lista integral das citações do Google Scholar não pôde ser extraída.** O endereço
indicado na orientação nº 7 (`scholar.google.com.br/scholar?cites=3248174171765827162`)
informa "12 resultados", mas responde com CAPTCHA a qualquer acesso automatizado — inclusive
por serviços intermediários de leitura. A Seção 9 apresenta **sete trabalhos citantes
integralmente verificados** por meio das bases OpenAlex e Semantic Scholar, mais os
candidatos identificados por busca dirigida. A diferença entre 7 e 12 é esperada: o Google
Scholar indexa trabalhos de conclusão de curso, dissertações em repositórios institucionais
e *preprints* que as bases com DOI não cobrem. O procedimento manual para fechar a lista
está descrito na Seção 9.3.

**(c) O que é evidência e o que é recomendação.** As seções 3 a 9 relatam o que a literatura
diz. As seções 10 e 11 são recomendações de autoria própria, derivadas do cruzamento entre
essa literatura e o estado atual dos nossos dados e do nosso código. A separação é
deliberada, para que a banca possa avaliar as duas coisas separadamente.

### 1.1 Sobre a suspensão da rotulagem manual

A orientação do Prof. Emerson de suspender a rotulagem manual encontra respaldo direto na
literatura examinada, e por uma razão mais precisa do que a inicialmente formulada.

O argumento apresentado na mentoria foi o da **qualificação do anotador**: a rotulagem de
sentimento financeiro exigiria um especialista em finanças para produzir rótulos com
validade de construto. A monografia de Santos (2022, Seção 4.2.3) mostra que o próprio autor
do FinBERT-PT-BR **não** usou especialistas em finanças — usou "três pessoas, sendo duas com
formação em engenharia e uma com formação em linguística". O que garantiu a qualidade do
gabarito dele não foi a formação dos anotadores, e sim três controles metodológicos:

1. **Uma definição operacional de rótulo ancorada em consequência econômica, não em
   emoção:** *"Classifique a notícia considerando se o texto implicaria em uma rentabilidade
   Positiva, Negativa ou Neutra. 'Não se aplica' para textos não relacionados a finanças, de
   políticos ou sem sentido."*
2. **Dupla anotação de todo texto**, com descarte agressivo do que não teve concordância —
   dos 1.000 textos anotados, **497 (49,7%) foram descartados**, restando 503.
3. **Medição formal de concordância** por percentual e por *Krippendorff's alpha*
   (90,4% e α = 0,88).

Isso reposiciona a orientação de forma construtiva: o problema do nosso gabarito não é
necessariamente *quem* rotula, mas **a ausência dos três controles acima**. Nosso conjunto-ouro
atual tem 300 manchetes rotuladas por **um único anotador**, sem segunda anotação e, portanto,
sem qualquer métrica de concordância — o que impede afirmar que o gabarito é confiável e,
por consequência, invalida o uso do gabarito como *ground truth* para escolher entre
encoders. Esse é, a rigor, um argumento mais forte para suspender a rotulagem na forma atual
do que o argumento da qualificação, e é o que se recomenda levar à mentoria de 10/08.

O detalhamento operacional e as alternativas estão na Seção 10.1 e no plano da Seção 11.

---

## 2. Sumário executivo — as sete conclusões que importam

| # | Conclusão | Onde está a evidência |
|---|---|---|
| 1 | O artigo do link indicado na orientação nº 5 **é o próprio artigo do FinBERT-PT-BR** (Santos, Bianchi e Costa, BWAIF 2023). O item 5 e o item 6 das orientações tratam, portanto, do mesmo trabalho, visto por dois ângulos: o artigo e o artefato publicado. | Seção 7 |
| 2 | O FinBERT-PT-BR foi treinado e validado sobre **notícias gerais de mercado** (Valor, Exame, InfoMoney), com acurácia de 0,76 e F1 de 0,73 em 3 classes. O nosso uso — manchetes de um **ativo específico** — é uma transferência de domínio não testada pelo autor, e é isso que explica os 58% que medimos. | Seções 7.1, 7.2 e 10.1 |
| 3 | **Nenhum dos trabalhos citantes verificados aplicou o FinBERT-PT-BR à tarefa financeira para a qual ele foi construído.** Apenas um o executou — e fora do domínio financeiro (documentos históricos). As demais citações são conceituais. Isso é uma **lacuna favorável à dissertação**, não uma fragilidade. | Seção 9 e `CITACOES_E_GAPS_2026-08-10.md` |
| 4 | Nossos três testes de encoder (BERTimbau base, BERTimbau large e Albertina-100M) foram **inconclusivos por defeito de protocolo**, não por inferioridade dos modelos: 300 exemplos, 3 épocas, sem adaptação de domínio e sem *gradual unfreezing*. Santos usou 503 exemplos, **11 épocas**, *lr* = 5e-6, *gradual unfreezing* e um modelo de linguagem previamente adaptado com 1,4 milhão de textos. | Seções 5 e 10.2 |
| 5 | O caminho com maior relação custo-benefício **não é trocar de encoder** — é replicar a **primeira etapa** de Santos: adaptação de domínio por *masked language modeling* do BERTimbau (ou do próprio FinBERT-PT-BR) sobre o nosso corpus de ~205 mil notícias. Isso é *self-supervised*: **não consome rótulo nenhum**, o que o torna compatível com a suspensão da rotulagem. | Seções 5.4 e 11 |
| 6 | O `config.json` publicado do FinBERT-PT-BR contém um **`label2id` inconsistente** com o `id2label`. O nosso Script 03 tem um mapeamento de contingência (`LABEL_0`/`LABEL_1`/`LABEL_2`) que está **invertido** em relação ao modelo real. Hoje o caminho de contingência não é acionado, mas é uma bomba-relógio de reprodutibilidade. | Seções 8.3 e 10.2 |
| 7 | O ambiente Python local está com o **PyTorch quebrado** (falha de carregamento de DLL). Nenhum experimento de encoder pode ser executado nesta máquina antes de corrigir isso. | Seção 10.3 |

---

## 3. Tarefa 1 — O BERT financeiro em pesquisas diversas

> *Orientação: "buscar informações sobre o uso do Bert financeiro em pesquisas diversas, como classificação, etc. (por ex., o próprio autor)"*

### 3.1 A linhagem do "BERT financeiro"

A ideia de um BERT financeiro nasce de uma constatação empírica que Araci (2019) formalizou:
modelos de linguagem de propósito geral erram sistematicamente em textos financeiros porque
o vocabulário do domínio inverte polaridades. Termos como *"queda do dólar"*, *"corte de
juros"*, *"provisão"*, *"alavancagem"* ou *"short"* têm carga positiva ou negativa que depende
do contexto financeiro e não da conotação usual da palavra. Araci propôs o **FinBERT (EN)**:
partir de um BERT genérico e continuar o pré-treinamento sobre corpus financeiro antes de
ajustar para a tarefa final.

Essa receita de **duas etapas** — (i) adaptação de domínio por modelagem de linguagem
mascarada, (ii) ajuste fino supervisionado para a tarefa — é a coluna vertebral de toda a
família. É exatamente a receita que Santos, Bianchi e Costa (2023) transportam para o
português brasileiro.

### 3.2 O uso pelo próprio autor (Santos, Bianchi e Costa)

O autor do FinBERT-PT-BR empregou o modelo em quatro tarefas distintas, documentadas no
artigo do BWAIF e, com mais detalhe, na monografia de 2022:

| Tarefa | Como foi feita | Resultado relatado |
|---|---|---|
| **Modelagem de linguagem** (adaptação de domínio) | *Fine-tuning* do BERTimbau com 1.428.867 sentenças de notícias financeiras (de 2,7 milhões coletadas, 1,6 milhão após limpeza, filtradas a ≤ 512 tokens); 2 épocas em 11 h; *lr* = 2e-5; máscara de 15%; 2× Nvidia T4 no Kaggle | Perplexidade **1,24** contra **1,51** do BERTimbau original |
| **Classificação de sentimento** (3 classes) | Camada de classificação sobre a primeira dimensão de saída do BERT; *transfer learning* com *gradual unfreezing* das 11 camadas de *encoder*; *lr* = 5e-6; **11 épocas**; validação cruzada 5-*fold* sobre 70% da base; teste nos 30% restantes | Acurácia **0,76** e F1 **0,73**; contra 0,67/0,63 do BERTimbau, 0,67/0,67 do FinBERT (EN) com texto traduzido e 0,45/0,35 do Random Forest + TF-IDF |
| **Construção de índice de sentimento** | Série temporal com Índice = (Pos − Neg) / (Pos + Neu + Neg) em janela [t−k, t] | Análise qualitativa aderente a oito eventos econômicos brasileiros (junho/2013, Lava Jato, *impeachment*, *Joesley Day*, eleição de 2018, COVID-19, vacinas, invasão da Ucrânia) |
| **Estratégia de investimento** | *"Apostando contra o sentimento"* — seleção mensal das ações com maior correlação **negativa** entre retorno e o índice de sentimento | Retorno acumulado de **683%** em 8 anos (2014–2022) contra **254%** do Ibovespa — 2,7× |

A monografia acrescenta uma quinta aplicação, ausente do artigo: a **correlação entre o
índice de sentimento e a inflação** (Figura 18 da monografia), e uma **regressão linear**
tendo o índice de mercado como variável dependente e fatores de investimento como
independentes (Tabela 5).

### 3.3 Rigor estatístico que o autor aplicou e que devemos replicar

Um ponto da monografia que **não aparece no artigo** e que é diretamente aproveitável na
nossa dissertação: Santos não se contentou com a comparação pontual de acurácias. Ele
aplicou **bootstrapping** (Efron, 1992) sobre o conjunto de teste para estimar intervalos de
confiança de acurácia e F1 (Figuras 15 e 16), verificou que os intervalos de 80% do
FinBERT-PT-BR **não se sobrepõem** aos dos concorrentes, e ainda construiu um **teste Z**
sobre a distribuição empírica reamostrada, obtendo p-valor numericamente igual a zero.

Isso responde antecipadamente a uma crítica previsível da banca sobre a nossa Tabela de
comparação de encoders (`conjunto_ouro/resultado_encoders_petr4.csv`), que hoje reporta
diferenças de −1,67 pp, −5,33 pp e −16,00 pp **sem qualquer teste de significância**. Com
n = 300 e desvios-padrão entre 2,7 e 8,4 pontos, a diferença de −1,67 pp do BERTimbau large é
seguramente indistinguível de zero. **Recomenda-se adotar o protocolo de bootstrap de Santos
antes de levar essa tabela à banca.**

### 3.4 Outros usos de BERT financeiro na literatura examinada

- **Hiew et al. (2019)** — combinam um índice de sentimento construído com BERT e um LSTM
  para prever retorno de ações; é a referência metodológica de onde Santos tira a própria
  fórmula do índice de sentimento.
- **Abílio, Coelho e Silva (2024)**, em *Applied Soft Computing* — **reconhecimento de
  entidades nomeadas (NER)** em transcrições de *earnings calls* de bancos brasileiros
  (dataset BraFiNER). Comparam BERTimbau, PTT5, mBERT e mT5; **modelos BERT superam
  consistentemente os T5**, e o BERTimbau monolíngue supera o PTT5. Registram que os modelos
  generativos (PTT5 e mT5) **alteraram valores monetários e percentuais** nas sentenças
  geradas — advertência relevante para qualquer tentação de usar LLM generativo em pipeline
  financeiro sem validação.
- **Januário et al. (2022)**, em *IEEE Latin America Transactions* — análise de sentimento
  aplicada a notícias do mercado de ações brasileiro; é o trabalho da literatura nacional
  mais próximo do nosso objeto.

---

## 4. Tarefa 2 — Como os trabalhos utilizaram o FinBERT-PT-BR

> *Orientação: "Identificar como os artigos utilizaram o fimbert_Pt"*

Esta é a resposta mais importante — e mais surpreendente — do levantamento.

### 4.1 O achado central

> ⚠️ **Esta seção foi corrigida em 03/08/2026, após a leitura integral dos textos.** A redação
> original afirmava que *nenhum* trabalho havia reutilizado o modelo. A verificação nos textos
> completos mostrou que **um deles o executou**. A análise citação por citação, com os trechos
> literais transcritos, está em `CITACOES_E_GAPS_2026-08-10.md`.

**Dos sete trabalhos citantes verificados, apenas um executou o FinBERT-PT-BR — e fora do
domínio financeiro.** Błoch, Santana e Amantino (2026) o utilizaram numa **máquina de comitê**,
combinado com o `pysentimiento`, para analisar correspondência colonial portuguesa dos séculos
XVII e XVIII. **Nenhum trabalho o aplicou à tarefa financeira para a qual foi construído.**

Nos seis restantes, o padrão de citação é **conceitual ou de delimitação**: o trabalho de
Santos é invocado para definir análise de sentimento, para sustentar a escassez de trabalhos em
português, para posicionar o modelo numa taxonomia, ou para que o autor diga em que o próprio
trabalho difere dele — e não para ser executado.

O caso mais ilustrativo é Teles e Figueiredo (2025), *"Comparing LLMs for Sentiment Analysis
in Financial Market News"*: apesar de ser um artigo brasileiro, de análise de sentimento, de
notícias, de mercado financeiro, e de citar Santos et al. (2023) **duas vezes** logo na
introdução, o trabalho **não inclui o FinBERT-PT-BR entre os modelos avaliados**. Compara
SVM, Random Forest e MLP contra Gemma, DeBERTa, DeBERTaV3, XLM-RoBERTa, BART e Gemini — e o
faz sobre três *datasets* em inglês (Financial Phrase Bank, StockEmotions e Tweet Financial
News). As duas citações a Santos são estritamente definicionais.

### 4.2 Implicação direta para a dissertação

Isso caracteriza uma **lacuna de literatura verificável e defensável em banca**: o
FinBERT-PT-BR é um artefato com **177.384 downloads mensais** no HuggingFace, mas com
adoção acadêmica documentada quase nula na tarefa para a qual foi construído. A nossa
dissertação é, pelo que este levantamento alcança, **um dos primeiros trabalhos a aplicar o
FinBERT-PT-BR a um ativo específico da B3 com validação contra gabarito humano e avaliação
de impacto em previsão de direção e volatilidade**.

Esse é um argumento de contribuição que deve ser incorporado ao texto da dissertação —
e é substancialmente mais forte do que o posicionamento atual. A redação sugerida está na
Seção 11.

### 4.3 Ressalva de escopo

A afirmação acima está limitada aos trabalhos que foi possível verificar (Seção 9). Os
cinco trabalhos que o Google Scholar contabiliza e que as bases com DOI não indexam podem
conter um uso aplicado. O procedimento para fechar essa verificação está na Seção 9.3 e
**deve ser executado antes de a afirmação entrar na versão final da dissertação**.

---

## 5. Tarefa 3 — Há outro encoder BERT melhor para a pesquisa?

> *Orientação: "Verificar se há outro encoder BERT melhor para usar na pesquisa"*

### 5.1 O que já testamos, e por que os testes não decidem nada

Os experimentos registrados em `Mestrado_PETR4/conjunto_ouro/resultado_encoders_petr4.csv`
e em `Mestrado_PETR4/experimentos_encoder/` produziram:

| Encoder testado | Acurácia | ± dp | F1-macro | Kappa | Δ vs. FinBERT |
|---|---|---|---|---|---|
| FinBERT-PT-BR (linha de base) | 58,00% | 4,88 | 57,63% | 0,370 | — |
| BERTimbau large (`bert-large-portuguese-cased`) | 56,33% | 5,52 | 54,26% | 0,330 | −1,67 pp |
| BERTimbau base (`bert-base-portuguese-cased`) | 52,67% | 8,41 | 48,14% | 0,261 | −5,33 pp |
| Albertina-100M PT-BR | 42,00% – 45,67% | 2,67 – 6,20 | 25,20% – 29,17% | 0,033 – 0,095 | −12,33 a −16,00 pp |

**Esses números não sustentam a conclusão de que o FinBERT-PT-BR é o melhor encoder.** Eles
sustentam apenas que, sob o protocolo empregado, os concorrentes não convergiram. As razões
são identificáveis e todas corrigíveis:

1. **Volume de rótulos insuficiente para ajuste fino.** 300 exemplos, divididos em 5 *folds*,
   deixam ~240 exemplos de treino por *fold* — cerca de 80 por classe. Santos usou 503 e,
   ainda assim, só obteve convergência **porque partiu de um modelo de linguagem já adaptado
   ao domínio**. Nós ajustamos modelos genéricos direto sobre 240 exemplos.
2. **Épocas insuficientes.** Usamos **3 épocas**; Santos usou **11**.
3. **Ausência de *gradual unfreezing*.** O log do experimento
   (`log_albertina.txt`) mostra a assinatura clássica do colapso para a classe majoritária:
   nos *folds* 2, 3 e 5 o **kappa foi exatamente 0,000** e o F1-macro ficou em 25–29%. Um
   modelo que prediz sempre a mesma classe produz precisamente esse padrão. Santos previne
   isso descongelando as camadas de *encoder* gradativamente.
4. **Taxa de aprendizado provavelmente inadequada.** Santos usa *lr* = 5e-6 para a etapa de
   sentimento — uma ordem de grandeza abaixo do usual — justamente para evitar o esquecimento
   catastrófico.
5. **Comparação assimétrica.** O FinBERT-PT-BR entra na comparação **já treinado** para
   sentimento financeiro; os concorrentes entram como *encoders* crus, com cabeça de
   classificação inicializada aleatoriamente (o log confirma:
   `classifier.bias, classifier.weight ... newly initialized`). Não é uma comparação entre
   encoders, é uma comparação entre um modelo pronto e três modelos sendo treinados do zero
   com poucos dados.
6. **Escolha de porte inadequada.** Testamos o Albertina **100M**, a menor variante da
   família. As variantes competitivas são a de **900M** e a de **1,5B**.

**Conclusão da Tarefa 3, em uma frase:** ainda não sabemos se há encoder melhor, porque o
protocolo aplicado até aqui não é capaz de responder à pergunta.

### 5.2 Panorama dos encoders candidatos (verificado no HuggingFace em 03/08/2026)

| Modelo | Arquitetura | Porte | Downloads/mês | Última atualização | Situação |
|---|---|---|---|---|---|
| `lucas-leme/FinBERT-PT-BR` | BERT (BERTimbau) + cabeça de sentimento | 110M | 177.384 | 13/02/2024 | **Em uso** |
| `neuralmind/bert-base-portuguese-cased` (BERTimbau base) | BERT | 110M | 502.821 | 14/06/2022 | Testado |
| `neuralmind/bert-large-portuguese-cased` (BERTimbau large) | BERT | 335M | 1.702.587 | 20/05/2021 | Testado |
| `PORTULAN/albertina-100m-portuguese-ptbr-encoder` | DeBERTa | 100M | 828 | 23/06/2025 | Testado (porte inadequado) |
| `PORTULAN/albertina-900m-portuguese-ptbr-encoder` | DeBERTa-v2 | 900M | 357 | 23/06/2025 | **Candidato** |
| `PORTULAN/albertina-1b5-portuguese-ptbr-encoder` | DeBERTa-v2 | 1,5B | 14 | 23/06/2025 | Candidato (custo alto) |
| `ricardoz/BERTugues-base-portuguese-cased` | BERT | 110M | 355 | 31/12/2024 | Candidato |
| `sagui-nlp/debertinha-ptbr-xsmall` | DeBERTa-v2 | ~40M | 689 | 02/08/2024 | Candidato leve |
| `turing-usp/FinBertPTBR` | BERT | 110M | 47 | 04/04/2023 | **Não usar** (ver 5.3) |
| `microsoft/mdeberta-v3-base` | DeBERTa-v3 multilíngue | 280M | 4.290.788 | 06/04/2023 | Candidato multilíngue |
| `FacebookAI/xlm-roberta-large` | XLM-R | 550M | 7.787.512 | 19/02/2024 | Linha de base multilíngue |
| `eliasjacob/ModernBERT-large-portuguese` | ModernBERT | 395M | 5 | 09/10/2025 | Experimental — não recomendado |

### 5.3 Observação sobre o `turing-usp/FinBertPTBR`

O modelo `turing-usp/FinBertPTBR`, que consta como candidato na nossa memória de projeto,
**é o antecessor descontinuado do modelo que já usamos**. O próprio *model card* traz o
aviso, em destaque:

> *"FinBertPTBR : Financial Bert PT BR (**Depreciated model**) — Newer version available on
> https://huggingface.co/lucas-leme/FinBERT-PT-BR"*

Entre os autores listados está **Lucas Leme**, ao lado de Vinicius Carmo, Julia Pocciotti e
Luísa Heise — os mesmos nomes que aparecem nos agradecimentos da monografia de 2022. Trata-se
de um trabalho anterior do grupo Turing USP, do qual o FinBERT-PT-BR é a evolução direta.
**Deve ser retirado da lista de candidatos** e, se citado na dissertação, citado como
antecedente histórico.

### 5.4 Recomendação da Tarefa 3

A recomendação **não é trocar de encoder**. É replicar a etapa que Santos executou e que nós
pulamos:

> **Adaptação de domínio por *masked language modeling*.** Continuar o pré-treinamento
> (MLM, máscara de 15%, *lr* = 2e-5) de um encoder sobre o nosso corpus de ~205 mil notícias
> de PETR4, e só então ajustar a cabeça de sentimento.

As razões pelas quais essa é a recomendação prioritária:

- **É *self-supervised*: não consome um único rótulo.** É, portanto, integralmente
  compatível com a suspensão da rotulagem manual determinada pelo Prof. Emerson — e é a única
  linha de trabalho substantiva que pode avançar sob essa restrição.
- **É a etapa de maior ganho documentado.** Foi ela que levou a perplexidade de 1,51 para
  1,24 e que viabilizou a convergência do classificador com apenas 503 rótulos.
- **É metodologicamente auditável.** A perplexidade é uma métrica intrínseca: mede-se
  em um *holdout* de notícias não vistas, **sem gabarito humano**. Produz um resultado
  reportável à banca em 10/08 sem depender do conjunto-ouro.
- **Especializa o domínio duas vezes.** Santos adaptou ao mercado financeiro brasileiro em
  geral; nós adaptaríamos ao subdomínio *Petrobras/petróleo/estatais*, onde estão os termos
  que mais nos interessam (*"paridade de importação"*, *"política de preços"*, *"campo do
  pré-sal"*, *"dividendo extraordinário"*, *"interferência estatal"*).

**Ordem de prioridade sugerida:**

1. MLM de domínio sobre `lucas-leme/FinBERT-PT-BR` (que já é financeiro) — maior ganho
   esperado, menor custo, sem consumo de rótulo.
2. MLM de domínio sobre `neuralmind/bert-large-portuguese-cased` — replica a receita completa
   de Santos, em porte maior.
3. `PORTULAN/albertina-900m` **somente** se (1) e (2) forem executados e o orçamento
   computacional permitir; jamais o 100M novamente.
4. `mdeberta-v3-base` como linha de base multilíngue de controle, para a tabela comparativa.

---

## 6. Tarefa 4 — Há trabalhos tentando fazer o mesmo que nós?

> *Orientação: "Verificar se alguns desses Bert está tentando fazer o mesmo que eu"*

A resposta é **não** — e o mapa abaixo mostra exatamente onde cada trabalho para.

Nosso objeto tem quatro elementos simultâneos: **(i)** português brasileiro, **(ii)** ativo
único da B3, **(iii)** previsão de **direção e de volatilidade**, **(iv)** fusão de sentimento
com modelo econométrico (GARCH) e *machine learning*.

| Trabalho | PT-BR | Ativo único | Direção | **Volatilidade** | Fusão GARCH+ML | Distância do nosso objeto |
|---|---|---|---|---|---|---|
| Santos, Bianchi e Costa (2023) | Sim | Não (carteira) | Não | **Não** | Não | Índice agregado de mercado e estratégia de carteira; não prevê ativo |
| Teles e Figueiredo (2025) | Não (corpora EN) | Não | Não | **Não** | Não | Compara modelos de sentimento; não liga a preço |
| Januário et al. (2022) | Sim | Não | Parcial | **Não** | Não | O mais próximo na literatura nacional |
| Abílio, Coelho e Silva (2024) | Sim | Não | Não | **Não** | Não | NER em *earnings calls*; tarefa diferente |
| Hiew et al. (2019) | Não | Não | Sim | **Não** | Não (LSTM) | Índice BERT + LSTM para retorno |
| Imai et al. (2024) | Sim | — | Não | **Não** | Não | *Concept drift* em fluxo de notícias |
| Reichert e Perlin (2025) | Parcial | Não | Não | **Não** | Não | Dicionários de sentimento via ChatGPT |
| **Esta dissertação** | **Sim** | **PETR4** | **Sim** | **Sim** | **Sim** | — |

### 6.1 A coluna que ninguém preenche

**Nenhum dos trabalhos examinados prevê volatilidade.** Todos operam sobre direção, retorno
ou estratégia de carteira.

Isso converge de forma notável com o achado que já registramos na revisão da banca de
julho/2026: **a previsão de direção fica próxima do acaso, e o ganho real do sentimento está
na volatilidade.** O que era, até aqui, um resultado empírico nosso passa a ter respaldo de
lacuna de literatura: a direção fica próxima do acaso **em todo mundo** — por isso os
trabalhos migram para carteira, para índice agregado ou para comparação de classificadores, e
não para o ativo isolado.

**A recomendação editorial que decorre disso é direta:** a volatilidade deve deixar de ser
tratada como resultado secundário e passar a ser a **contribuição principal** da dissertação,
com a direção reposicionada como resultado negativo devidamente reportado — o que, aliás, é
boa prática científica e responde a uma das ponderações da banca.

### 6.2 Um trabalho adjacente que merece leitura

Imai et al. (2024), *"Is it Fine to Tune?"*, avalia o impacto de **atualizar periodicamente**
modelos de linguagem em fluxo de notícias brasileiras, em vez de mantê-los estáticos. Conclui
que o ajuste fino anual com uma amostra reduzida de textos recentes supera o uso do modelo
estático na maioria dos anos analisados, com bom compromisso de tempo de execução.

Isso é diretamente pertinente ao nosso desenho: usamos um modelo congelado em **fevereiro de
2024** para classificar notícias de **2018 a 2026**. As notícias de 2025 e 2026 sobre a
Petrobras contêm vocabulário e enquadramento que o modelo não viu (mudanças na política de
preços, novo ciclo de dividendos, discussão sobre a Margem Equatorial). Vale ao menos
**reportar essa limitação explicitamente** na dissertação; e, se houver tempo, testá-la por
subperíodos — infraestrutura que já temos em
`Mestrado_PETR4/resultados_subperiodo_petr4.csv`.

---

## 7. Tarefa 5 — Artigo SBC/BWAIF nº 24960

> *Orientação: "Entrar no link ... Ler, entender, e fazer um resumo desse artigo; verificar se há relação e se há algo que possamos usar; ler todas as referências citadas neste artigo e fazer um resumo compilado."*

**Constatação preliminar:** o artigo do link **é o artigo do FinBERT-PT-BR**, isto é, o
trabalho que fundamenta o modelo que já utilizamos no Script 03 da nossa pipeline.

### 7.1 Resumo do artigo

**Referência completa (ABNT):**

> SANTOS, L. L.; BIANCHI, R. A. C.; COSTA, A. H. R. FinBERT-PT-BR: Análise de Sentimentos de
> Textos em Português do Mercado Financeiro. In: BRAZILIAN WORKSHOP ON ARTIFICIAL
> INTELLIGENCE IN FINANCE (BWAIF), 2., 2023, João Pessoa. **Anais** [...]. Porto Alegre: SBC,
> 2023. p. 144-155. DOI: 10.5753/bwaif.2023.231151.

**Afiliações:** Escola Politécnica da USP (Santos e Costa) e Centro Universitário FEI
(Bianchi). Fomento: CNPq, processo nº 310085/2020-9.

**Objetivo.** Apresentar um modelo de linguagem do estado da arte para o mercado financeiro
em português do Brasil (**FinBERT-PT-BR**) e, a partir dele, um classificador de sentimento
(**SentFinBERT-PT-BR**), demonstrando que o classificador viabiliza a construção de sinais
para análise e estratégias de investimento.

**Nota terminológica importante.** O artigo distingue dois artefatos: **FinBERT-PT-BR** é o
*modelo de linguagem* adaptado ao domínio, e **SentFinBERT-PT-BR** é o *classificador de
sentimento* derivado dele. O repositório HuggingFace publica **um único artefato**, sob o
nome `FinBERT-PT-BR`, que é na verdade o **SentFinBERT-PT-BR** (a arquitetura declarada no
`config.json` é `BertForSequenceClassification`, com três rótulos). **O modelo de linguagem
puro, sem cabeça de classificação, não foi publicado.** Isso tem consequência prática direta
sobre a Seção 5.4 e está detalhado na Seção 8.4.

**Metodologia — Etapa 1 (modelo de linguagem).**

- **Coleta:** *web scraping* com Scrapy sobre Valor Econômico, Exame e InfoMoney, capturando
  título, subtítulo, data de publicação, data de atualização, autor e *links*.
- **Volume:** 2,7 milhões de sentenças entre 2006 e 2022, totalizando 130 milhões de palavras
  — Valor Econômico 1,23 mi, Exame 1,01 mi, InfoMoney 0,46 mi.
- **Limpeza:** expressões regulares para remover textos malformados, caracteres especiais e
  código-fonte → 1,6 milhão de sentenças; filtro de ≤ 512 tokens → **1.428.867 sentenças**.
- **Treinamento:** PyTorch + HuggingFace, pesos iniciais do BERTimbau; Kaggle com 30 GB de
  RAM e 2× Nvidia T4; *batch size* 16 (limitação de GPU); alocação dinâmica de memória;
  **2 épocas em 11 horas**; *lr* = 2e-5 (conforme Sun et al., 2019); máscara de 15% (conforme
  Devlin et al., 2018).
- **Avaliação:** perplexidade em amostra de 100 mil sentenças não vistas —
  **1,24** contra 1,51 do BERTimbau.

**Metodologia — Etapa 2 (classificador de sentimento).**

- **Anotação:** três pessoas (duas de engenharia, uma de linguística), cada texto anotado por
  ao menos duas. Categorias: positivo, negativo, neutro e "não se aplica". Instrução literal:
  *"Classifique a notícia considerando se o texto implicaria em uma rentabilidade Positiva,
  Negativa ou Neutra."*
- **Base final:** de 1.000 textos anotados, **497 descartados** (classificados como "não se
  aplica" ou sem concordância) → **503 textos**: 160 positivos, 203 negativos, 140 neutros.
- **Concordância:** percentual de **90,4%** e *Krippendorff's alpha* de **0,88**.
- **Arquitetura:** camada de classificação sobre a primeira dimensão de saída do BERT.
- **Treinamento:** *gradual unfreezing* das 11 camadas de *encoder*; *lr* = 5e-6;
  **11 épocas**; validação cruzada 5-*fold* sobre 70% da base; teste nos 30% restantes.

**Resultados.**

| Modelo | Acurácia | F1-Score |
|---|---|---|
| Random Forest + TF-IDF | 0,45 | 0,35 |
| FinBERT (EN) sobre texto traduzido | 0,67 | 0,67 |
| Sent-BERTimbau | 0,67 | 0,63 |
| **SentFinBERT-PT-BR** | **0,76** | **0,73** |

*(A Tabela 4 da monografia atribui 0,69 de acurácia ao BERTimbau e 0,67 ao FinBERT (EN);
a Tabela 3 do artigo registra 0,67 para o BERTimbau. A divergência é do próprio autor entre
as duas versões do trabalho — vale citar a versão do artigo, que é a peer-reviewed.)*

**Aplicações demonstradas.** Índice de sentimento
Índice = (Pos − Neg) / (Pos + Neu + Neg), com validação qualitativa contra oito eventos da
economia brasileira; e a estratégia *"apostando contra o sentimento"*, com 683% de retorno
acumulado em 8 anos contra 254% do Ibovespa.

**Trabalhos futuros propostos pelo autor** — todos eles, sem exceção, apontam para o que
estamos fazendo: base maior e mais específica para o modelo de linguagem; mais textos
rotulados com concordância alta; aprimoramento do cálculo do índice; **aplicação da
metodologia a setores específicos da bolsa**; e relação do índice com dados macroeconômicos
(inflação, PIB, desemprego).

### 7.2 Relação com a nossa pesquisa e o que podemos usar

**Relação: máxima.** É a fundamentação do modelo que já está em produção na nossa pipeline
(`src/sentimento/03_analise_sentimento_bertimbau_petr4.py`, linha 166).

**Elementos diretamente aproveitáveis, em ordem de valor:**

| # | O que aproveitar | Onde aplicar na dissertação |
|---|---|---|
| 1 | **Receita completa de adaptação de domínio** (MLM, máscara 15%, *lr* 2e-5, filtro ≤512 tokens, perplexidade como métrica) | Novo experimento sobre o corpus de ~205 mil notícias — Seção 5.4 e plano da Seção 11 |
| 2 | **Protocolo de ajuste fino** (*gradual unfreezing*, *lr* 5e-6, 11 épocas, CV 5-*fold*) | Corrigir os experimentos de encoder que hoje são inconclusivos |
| 3 | **Protocolo de anotação de 6 etapas** (monografia, Seção 2.3.1) | Refundar o conjunto-ouro quando a rotulagem for retomada |
| 4 | **Categoria "não se aplica" e descarte por discordância** | Nosso gabarito já registra relevância (111/300 = 37%); a categoria de descarte falta |
| 5 | ***Krippendorff's alpha* e percentual de concordância** | Métrica que hoje **não temos** e que a banca cobrará |
| 6 | ***Bootstrapping* + teste Z sobre distribuição empírica** (monografia, Seção 4.2.4) | Dar significância estatística à tabela de comparação de encoders |
| 7 | **Fórmula do índice de sentimento** | Comparar formalmente com o nosso ISM; documentar a escolha |
| 8 | **Modelagem de tópicos / *zero-shot* para pré-selecionar textos** (monografia, Seção 2.3.1.1, apoiada em Poursabzi-Sangdeh e Boyd-Graber, 2015) | Reduzir o custo da rotulagem quando ela for retomada — ver Seção 11 |
| 9 | **Validação qualitativa contra eventos econômicos** | Já fazemos parcialmente (`grafico_petr4_guerra.png`); replicar o rigor da Figura 3 |
| 10 | **Benchmark declarado (0,76 / 0,73)** | Contraste explícito com os nossos 58% — a diferença **é** um resultado, ver 7.2.1 |

#### 7.2.1 Sobre a diferença entre 0,76 e 0,58

A diferença entre a acurácia declarada pelo autor (0,76) e a que medimos contra o nosso
conjunto-ouro (0,58, κ = 0,371) **não indica erro de implementação nossa**. Indica uma
**transferência de domínio não testada pelo autor**, por três razões conjugadas:

1. **Unidade textual distinta.** Santos avaliou sobre **sentenças de notícia**; nós avaliamos
   sobre **manchetes**, que são mais curtas, mais elípticas e mais ambíguas.
2. **Escopo distinto.** Santos avaliou notícias **gerais de mercado**; nós avaliamos notícias
   de **um ativo específico**, onde a polaridade frequentemente depende de conhecimento
   contextual sobre a empresa (uma alta do petróleo é positiva para a PETR4 e negativa para
   as aéreas — o modelo genérico não distingue).
3. **Gabarito distinto.** O gabarito de Santos passou por dupla anotação com descarte de 49,7%
   dos casos; o nosso, não (Seção 10.1).

Essa é uma **contribuição publicável**: documentar a degradação de desempenho de um modelo de
sentimento financeiro em português quando transferido de notícias gerais para um ativo
específico. Recomenda-se elevá-la à condição de resultado da dissertação, e não tratá-la como
limitação a ser justificada.

### 7.3 Resumo compilado das 28 referências do artigo

A lista de referências do artigo contém **28 entradas**. Todas foram catalogadas conforme os
oito campos solicitados na orientação 5.C. A tabela integral, em formato consultável e
ordenável, está no arquivo:

> **`orientacoes/referencias_artigo_bwaif_24960.csv`**

com as colunas: `#`, `Referência (ABNT)`, `Data`, `Encoders e tecnologias`, `Objetivo`,
`Resultados obtidos`, `Aplicação`, `Tem relação com nossa pesquisa?`, `O que podemos
aproveitar`.

Abaixo, a síntese narrativa por grupo temático, com destaque para as **oito referências de
alta relevância** para a dissertação.

#### Grupo A — Fundamentos de arquitetura e modelos de linguagem

**A.1 · VASWANI et al. (2017). *Attention is all you need*. NeurIPS, v. 30. — RELAÇÃO: MÉDIA**
*Tecnologias:* Transformer, *self-attention*, *multi-head attention*. *Objetivo:* substituir
recorrência e convolução por atenção pura. *Resultados:* estado da arte em tradução com menor
custo de treino. *Aplicação:* base de toda a família BERT. *Aproveitar:* citação obrigatória
no capítulo teórico; a monografia de Santos (Figuras 4 e 5) traz um detalhamento didático das
camadas de atenção que pode ser adaptado.

**A.2 · DEVLIN et al. (2018). *BERT: Pre-training of deep bidirectional transformers*. arXiv:1810.04805. — RELAÇÃO: ALTA**
*Tecnologias:* BERT, MLM, *next sentence prediction*. *Objetivo:* pré-treino bidirecional
profundo. *Resultados:* estado da arte em 11 tarefas de PLN. *Aplicação:* arquitetura de
todos os encoders que usamos. *Aproveitar:* **dois hiperparâmetros operacionais** que Santos
herda diretamente daqui — a probabilidade de máscara de **15%** e a recomendação de acoplar a
camada de classificação **à primeira dimensão de saída** ([CLS]). São os parâmetros a usar no
nosso MLM de domínio.

**A.3 · SOUZA, NOGUEIRA e LOTUFO (2020). *BERTimbau*. BRACIS, p. 403-417. — RELAÇÃO: ALTA**
*Tecnologias:* BERT base e large para PT-BR, corpus brWaC. *Objetivo:* modelos de linguagem
pré-treinados para o português brasileiro. *Resultados:* superam modelos treinados do zero e
multilíngues disponíveis. *Aplicação:* é o **ponto de partida do FinBERT-PT-BR** e um dos
encoders que já testamos. *Aproveitar:* os autores indicam explicitamente a utilidade do
BERTimbau para análise de sentimento no mercado financeiro — foi essa indicação que motivou
Santos. **É a referência a citar para justificar por que partimos de um modelo PT-BR e não
de tradução para o inglês.**

**A.4 · ARACI (2019). *FinBERT*. arXiv:1908.10063. — RELAÇÃO: ALTA**
*Tecnologias:* FinBERT (EN), pré-treino sobre corpus financeiro, *Financial PhraseBank*.
*Objetivo:* adaptar BERT ao domínio financeiro. *Resultados:* supera modelos genéricos em
sentimento financeiro. *Aplicação:* fundamento conceitual do domínio. *Aproveitar:* é a
**referência canônica para justificar a adaptação de domínio** — a tese central de que
vocabulário financeiro exige modelo financeiro. Santos cita Araci exatamente para essa
justificativa, e nós devemos fazer o mesmo.

**A.5 · SUN et al. (2019). *How to fine-tune BERT for text classification?*. CCL, p. 194-206. — RELAÇÃO: ALTA**
*Tecnologias:* estratégias de *fine-tuning*, taxas de aprendizado, *layer-wise decay*.
*Objetivo:* investigar sistematicamente como ajustar BERT. *Resultados:* recomendações
consolidadas, entre elas *lr* = 2e-5 para *fine-tuning* de modelo de linguagem. *Aplicação:*
protocolo experimental. *Aproveitar:* **é a fonte do *lr* = 2e-5 que Santos usa e que
devemos usar**; é também a referência para justificar metodologicamente os hiperparâmetros do
nosso experimento perante a banca, em vez de apresentá-los como escolha arbitrária.

**A.6 · MANNING e SCHÜTZE (1999). *Foundations of Statistical NLP*. MIT Press. — RELAÇÃO: BAIXA**
*Objetivo:* obra de referência em PLN estatístico. *Aproveitar:* citação de enquadramento
histórico no capítulo teórico.

**A.7 · CHEN, BEEFERMAN e ROSENFELD (1998). *Evaluation metrics for language models*. — RELAÇÃO: MÉDIA**
*Tecnologias:* perplexidade e métricas de avaliação de modelos de linguagem. *Objetivo:*
avaliar modelos de linguagem. *Aplicação:* é a métrica com que Santos avalia a etapa de
adaptação de domínio. *Aproveitar:* **se executarmos o MLM de domínio (Seção 5.4), esta é a
referência que sustenta a perplexidade como métrica de avaliação** — e, portanto, uma
referência que passará de "baixa" a "essencial" no nosso texto.

#### Grupo B — Análise de sentimento: fundamentos e *surveys*

**B.1 · PANG e LEE (2004). *A sentimental education*. ACL, p. 271-278. — RELAÇÃO: MÉDIA**
Fundamento clássico de análise de sentimento com sumarização por subjetividade. *Aproveitar:*
citação de fundamentação conceitual.

**B.2 · LIU (2012). *Sentiment analysis and opinion mining*. Morgan & Claypool. — RELAÇÃO: MÉDIA**
Obra de referência da área; define os níveis de análise (documento, sentença, aspecto).
*Aproveitar:* **a distinção entre níveis é pertinente à nossa decisão de classificar
manchetes** (nível de sentença) em vez de notícias completas (nível de documento) — decisão
que hoje não está formalmente justificada na dissertação.

**B.3 · MAN, LUO e LIN (2019). *Financial sentiment analysis (FSA): a survey*. IEEE ICPS, p. 617-622. — RELAÇÃO: ALTA**
*Objetivo:* revisão sistemática de análise de sentimento financeiro. *Aplicação:* mapeamento
da área. *Aproveitar:* **é o *survey* de referência para posicionar a nossa RSL**; útil para
demonstrar à banca que a nossa revisão dialoga com o estado da arte consolidado da área e
não apenas com trabalhos pontuais.

**B.4 · TAN, LEE e LIM (2023). *A survey of sentiment analysis: approaches, datasets, and future research*. Applied Sciences, v. 13, n. 7. — RELAÇÃO: ALTA**
*Objetivo:* revisão atualizada de abordagens, *datasets* e direções futuras. *Aproveitar:*
**é a revisão mais recente citada por Santos**; deve entrar na nossa RSL e serve para o
argumento de atualidade. Publicação em periódico com fator de impacto, o que a torna
citação forte.

#### Grupo C — Sentimento e mercado financeiro (o núcleo aplicado)

**C.1 · BOLLEN, MAO e ZENG (2011). *Twitter mood predicts the stock market*. — RELAÇÃO: ALTA**
*Tecnologias:* OpinionFinder, GPOMS, rede neural *fuzzy*. *Objetivo:* verificar se o humor
coletivo no Twitter prevê o mercado. *Resultados:* **acurácia de até 87,6%** na previsão de
direção do Dow Jones. *Aplicação:* é o artigo fundador da área. *Aproveitar:* **citação
obrigatória** — mas com uma ressalva que nos serve estrategicamente: os 87,6% de Bollen nunca
foram replicados de forma robusta, e a literatura posterior converge para desempenho de
direção próximo ao acaso. **Isso é munição direta para o nosso reposicionamento da direção
como resultado negativo (Seção 6.1).**

**C.2 · HIEW et al. (2019). *BERT-based financial sentiment index and LSTM-based stock return predictability*. arXiv:1906.09024. — RELAÇÃO: MUITO ALTA**
*Tecnologias:* BERT + LSTM. *Objetivo:* construir índice de sentimento com BERT e prever
retorno com LSTM. *Aplicação:* previsão de retorno de ações. *Aproveitar:* **é a origem da
fórmula do índice de sentimento que Santos adota** — e, portanto, a origem indireta do nosso
ISM. **É a referência mais próxima do nosso desenho metodológico em toda a lista** e deve ser
lida na íntegra e citada na fundamentação do ISM.

**C.3 · PAGOLU et al. (2016). *Sentiment analysis of Twitter data for predicting stock market movements*. SCOPES, p. 1345-1350. — RELAÇÃO: ALTA**
*Tecnologias:* Word2Vec, N-gram, Random Forest, SVM, regressão logística. *Objetivo:* prever
movimento do mercado a partir de sentimento no Twitter. *Aproveitar:* **usa exatamente a
mesma família de classificadores da nossa pipeline** (SVM, Random Forest, regressão
logística) — é uma referência direta para justificar as nossas escolhas de modelo e para
compor a tabela comparativa de trabalhos relacionados.

**C.4 · KORDONIS, SYMEONIDIS e ARAMPATZIS (2016). *Stock price forecasting via sentiment analysis on Twitter*. PCI '16. — RELAÇÃO: MÉDIA**
*Tecnologias:* Naïve Bayes, SVM. *Objetivo:* previsão de preço a partir de sentimento.
*Aproveitar:* compõe o bloco de trabalhos correlatos baseados em Twitter; útil para
argumentar por que **optamos por notícias e não por redes sociais** — decisão que precisa
estar justificada no texto.

**C.5 · KRAAIJEVELD e DE SMEDT (2020). *The predictive power of public Twitter sentiment for forecasting cryptocurrency prices*. JIFMIM, v. 65. — RELAÇÃO: MÉDIA**
*Objetivo:* poder preditivo do sentimento sobre criptomoedas. *Resultados:* poder preditivo
existente porém limitado, com forte presença de *bots*. *Aproveitar:* a discussão sobre
**ruído e contaminação da fonte** é transponível à nossa justificativa de usar portais
jornalísticos com curadoria editorial.

**C.6 · OTABEK e CHOI (2022). *Twitter attribute classification with Q-learning on bitcoin price prediction*. IEEE Access, v. 10. — RELAÇÃO: BAIXA**
*Tecnologias:* Q-learning, aprendizado por reforço. *Aproveitar:* pouco aproveitável
diretamente; registra a fronteira de aprendizado por reforço aplicado a sentimento.

**C.7 · JUNJIE e MENGONI (2020). *Spot gold price prediction using financial news sentiment analysis*. IEEE/WIC/ACM WI-IAT, p. 758-763. — RELAÇÃO: MÉDIA-ALTA**
*Objetivo:* prever o preço à vista do ouro a partir do sentimento de notícias financeiras.
*Aproveitar:* **é o trabalho estruturalmente mais próximo do nosso na lista** — *commodity*
única, notícias como fonte (não redes sociais), previsão de preço. A PETR4 é fortemente
acoplada ao petróleo, o que torna o paralelo metodológico direto. **Recomenda-se leitura
integral.**

**C.8 · ARDIA, CHOPARD e BOUDT (2015). *Using Twitter to model the EUR/USD exchange rate*. Economics Letters, v. 132. — RELAÇÃO: MÉDIA-ALTA**
*Objetivo:* modelar a taxa de câmbio euro-dólar com sentimento do Twitter. *Aproveitar:*
publicado em periódico de **economia**, não de computação — é uma referência útil para
demonstrar à banca que a abordagem tem aceitação na literatura econômica, e não só na de
ciência da computação. Trabalhos de câmbio costumam tratar **volatilidade**, o que o
aproxima do nosso eixo principal.

**C.9 · LO (2004). *The adaptive markets hypothesis*. Journal of Portfolio Management, v. 30, n. 5. — RELAÇÃO: ALTA**
*Objetivo:* reconciliar a hipótese de mercados eficientes com finanças comportamentais.
*Aproveitar:* **é a âncora teórica que justifica a pesquisa inteira.** Se os mercados fossem
perfeitamente eficientes, o sentimento de notícias não teria conteúdo preditivo. Santos abre
o artigo com Lo, e a nossa dissertação deve fazer o mesmo na fundamentação. Complementar com
Fuller (1998), citado na monografia, sobre fontes de alfa em finanças comportamentais.

#### Grupo D — Análise de sentimento em português (contexto nacional)

**D.1 · MEDEIROS e BORGES (2019). *Tweet sentiment analysis regarding the Brazilian stock market*. BraSNAM, p. 71-82. — RELAÇÃO: ALTA**
*Objetivo:* sentimento em tuítes sobre o mercado de ações brasileiro. *Aproveitar:* um dos
**poucos trabalhos nacionais** da interseção sentimento × mercado brasileiro; deve constar da
nossa RSL e da tabela de trabalhos relacionados.

**D.2 · DE SOUZA, DE SOUZA e MEINERZ (2021). *Análise de sentimento em tempo real de notícias do mercado de ações*. Brazilian Journal of Development, v. 7, n. 1. — RELAÇÃO: ALTA**
*Objetivo:* análise de sentimento **em tempo real** de notícias do mercado de ações.
*Aproveitar:* usa **notícias** (não redes sociais) e opera em **tempo real** — dialoga
diretamente com o nosso recorte de notícias após as 17h e com o componente de demonstração
do site da pesquisa.

**D.3 · JANUÁRIO et al. (2022). *Sentiment analysis applied to news from the Brazilian stock market*. IEEE Latin America Transactions, v. 20, n. 3. — RELAÇÃO: MUITO ALTA**
*Objetivo:* análise de sentimento aplicada a notícias do mercado de ações brasileiro.
*Aplicação:* mercado brasileiro. *Aproveitar:* **é o trabalho brasileiro mais próximo do
nosso objeto**, publicado em periódico IEEE indexado. Combina tuítes e outras fontes de
notícia. **Leitura integral obrigatória** — é a referência contra a qual a banca comparará a
nossa contribuição, e precisamos ter uma resposta pronta sobre o que fazemos de diferente
(resposta: ativo único, volatilidade e fusão com GARCH).

**D.4 · SILVA, M. C. A. (2018). *Percepções sobre corrupção durante as eleições presidenciais no Brasil em 2018: uma análise baseada no Twitter*. — RELAÇÃO: BAIXA**
*Objetivo:* percepção de corrupção via Twitter nas eleições de 2018. *Aproveitar:* pouco
aproveitável — domínio político, não financeiro.

> ⚠️ **Atenção — risco de confusão de referência.** Consta no nosso registro de projeto um
> plano de enriquecimento capítulo a capítulo da dissertação "usando a tese da Silva (2018)".
> **A Silva (2018) citada por Santos é sobre percepção de corrupção no Twitter**, e muito
> provavelmente **não** é a mesma obra do nosso plano de enriquecimento. Recomenda-se
> conferir a referência completa da tese que estamos usando antes de qualquer citação
> cruzada, sob pena de erro de referenciação na versão final.

**D.5 · PEREIRA (2019). *Análise de sentimentos da população brasileira em relação à eleição presidencial de 2018 através da rede social Twitter*. — RELAÇÃO: BAIXA**
Mesmo caso de D.4 — domínio político.

**D.6 · XAVIER et al. (2020). *Análise de redes sociais como estratégia de apoio à vigilância em saúde durante a COVID-19*. Estudos Avançados, v. 34, n. 99. — RELAÇÃO: BAIXA**
Domínio de saúde pública. *Aproveitar:* demonstra a amplitude de aplicação de análise de
sentimento em PT-BR; utilidade apenas ilustrativa.

#### Grupo E — Metodologia de anotação e validação

**E.1 · ARTSTEIN e POESIO (2008). *Inter-coder agreement for computational linguistics*. Computational Linguistics, v. 34, n. 4. — RELAÇÃO: MUITO ALTA**
*Objetivo:* revisar e formalizar métricas de concordância entre anotadores. *Aplicação:*
construção de corpora anotados. *Aproveitar:* **é a referência metodológica que sustenta
tudo o que precisamos corrigir no conjunto-ouro.** Define percentual de concordância,
*Fleiss's Kappa* e *Krippendorff's alpha*, com as vantagens e limitações de cada um — a
monografia de Santos (Seção 2.3.1.2) traz as três fórmulas já transcritas e prontas para
adaptação. **Referência de leitura prioritária.**

**E.2 · KRIPPENDORFF (2018). *Content analysis: an introduction to its methodology*. 4. ed. Sage. — RELAÇÃO: MUITO ALTA**
*Objetivo:* metodologia de análise de conteúdo, incluindo o *alpha*. *Aproveitar:* fonte
primária do α que precisamos passar a reportar. **Vantagem decisiva sobre o kappa de Cohen
que usamos hoje:** o α de Krippendorff admite **número variável de anotadores por item** e
**dados faltantes**, ao passo que o kappa de Cohen exige exatamente dois anotadores
avaliando todos os itens. Como qualquer retomada da nossa rotulagem envolverá anotadores com
disponibilidade desigual, **o α é a métrica correta para o nosso caso**, e não o kappa.

#### Grupo F — Referências citadas apenas na monografia (não no artigo)

Três referências presentes **somente** na monografia de 2022 merecem registro por serem
diretamente acionáveis:

**F.1 · POURSABZI-SANGDEH e BOYD-GRABER (2015). *Speeding document annotation with topic models*. NAACL SRW, p. 126-132. — RELAÇÃO: MUITO ALTA (contexto atual)**
*Objetivo:* acelerar a anotação de documentos usando modelagem de tópicos. *Resultados:*
ganho de eficiência quando anotadores recebem informação de modelos de tópicos.
*Aproveitar:* **é a resposta técnica ao problema levantado pelo Prof. Emerson.** Se a
rotulagem for retomada, a modelagem de tópicos permite (i) pré-selecionar textos
representativos, reduzindo o volume a rotular, e (ii) apresentar ao anotador uma sugestão de
classe, o que reduz a carga cognitiva e mitiga a falta de especialização em finanças.

**F.2 · ALCOFORADO et al. (2022). *ZeroBERTo: leveraging zero-shot text classification by topic modeling*. arXiv:2201.01337. — RELAÇÃO: ALTA**
*Tecnologias:* classificação *zero-shot* por modelagem de tópicos, voltada a línguas de
poucos recursos. *Aproveitar:* Santos aponta o ZeroBERTo como alternativa ao XLM-R para
*zero-shot* em português. **Permite obter uma pré-classificação sem rótulo algum** — mais uma
linha compatível com a suspensão da rotulagem.

**F.3 · EFRON (1992). *Bootstrap methods: another look at the jackknife*. — RELAÇÃO: ALTA**
*Aproveitar:* fundamenta os intervalos de confiança que precisamos calcular sobre a nossa
tabela de encoders (Seção 3.3).

#### Balanço quantitativo da análise de referências

| Grau de relação com a nossa pesquisa | Quantidade | Referências |
|---|---|---|
| **Muito alta** | 4 | Hiew et al. (2019); Januário et al. (2022); Artstein e Poesio (2008); Krippendorff (2018) |
| **Alta** | 11 | Devlin et al. (2018); Souza et al. (2020); Araci (2019); Sun et al. (2019); Man et al. (2019); Tan et al. (2023); Bollen et al. (2011); Pagolu et al. (2016); Lo (2004); Medeiros e Borges (2019); de Souza et al. (2021) |
| **Média-alta / média** | 8 | Vaswani et al. (2017); Chen et al. (1998); Pang e Lee (2004); Liu (2012); Kordonis et al. (2016); Kraaijeveld e De Smedt (2020); Junjie e Mengoni (2020); Ardia et al. (2015) |
| **Baixa** | 5 | Manning e Schütze (1999); Otabek e Choi (2022); Silva (2018); Pereira (2019); Xavier et al. (2020) |
| **Total no artigo** | **28** | |
| *Adicionais só na monografia* | *3* | *Poursabzi-Sangdeh e Boyd-Graber (2015); Alcoforado et al. (2022); Efron (1992)* |

**Quinze referências (54%) têm relação alta ou muito alta com a dissertação.** Recomenda-se
incorporar ao referencial teórico, prioritariamente, as quatro de relação muito alta e as
três exclusivas da monografia.

---

## 8. Tarefa 6 — Estudo do repositório HuggingFace `lucas-leme/FinBERT-PT-BR`

> *Orientação: "Estudar tudo que tem no site ... fazer um resumo e ver o que podemos usar na nossa pesquisa"*

### 8.1 Ficha técnica (verificada em 03/08/2026)

| Atributo | Valor |
|---|---|
| Identificador | `lucas-leme/FinBERT-PT-BR` |
| Arquitetura | `BertForSequenceClassification` |
| Camadas ocultas | 12 |
| Dimensão oculta | 768 |
| Vocabulário | 29.794 tokens |
| Posições máximas | 512 tokens |
| Parâmetros (estimados) | ~110 milhões |
| Tarefa (*pipeline tag*) | `text-classification` |
| Idioma | `pt` |
| Licença | **Apache 2.0** |
| Biblioteca | `transformers` (PyTorch) |
| Downloads no último mês | **177.384** |
| *Likes* | 30 |
| Discussões na comunidade | 7 |
| Última modificação | **13/02/2024** |

### 8.2 Conteúdo do repositório

Dez arquivos, sem nenhum artefato oculto ou dado de treinamento:

`.gitattributes` · `README.md` · **`config.json`** · **`pytorch_model.bin`** ·
`special_tokens_map.json` · `tokenizer.json` · `tokenizer_config.json` · `vocab.txt` ·
`sentiment_index_and_economy.png` · `sentiment_inflation.png`

**Três observações operacionais:**

1. **Não há `model.safetensors`.** O modelo é distribuído apenas como `pytorch_model.bin`
   (formato *pickle*). Versões recentes da biblioteca `transformers` exigem
   `use_safetensors=False` ou emitem advertência de segurança ao carregar esse formato.
   **Isso deve ser documentado no capítulo de método**, porque afeta a reprodutibilidade em
   ambientes mais novos.
2. **Não há dados de treinamento nem `training_args.bin`.** O corpus de 1,4 milhão de textos e
   os 503 textos rotulados **não foram publicados**. Isso impede replicação direta e
   **reforça a originalidade do nosso conjunto-ouro** — por menor que ele seja, é dado que a
   comunidade não tem.
3. **As duas imagens** (`sentiment_index_and_economy.png` e `sentiment_inflation.png`)
   correspondem às Figuras 3 do artigo e 18 da monografia. Sob licença Apache 2.0,
   **podem ser reproduzidas na dissertação com a devida atribuição** — úteis como ilustração
   comparativa no capítulo de fundamentação.

### 8.3 Achado crítico: inconsistência no mapeamento de rótulos

O `config.json` publicado contém:

```json
"id2label": { "0": "POSITIVE", "1": "NEGATIVE", "2": "NEUTRAL" },
"label2id": { "LABEL_0": 0, "LABEL_1": 1, "LABEL_2": 2 }
```

O `id2label` está correto e é o que a `pipeline` do `transformers` utiliza — por isso a
nossa pipeline funciona hoje. Mas o `label2id` **não é o inverso do `id2label`**: em vez de
mapear `POSITIVE → 0`, mapeia `LABEL_0 → 0`. É um defeito do artefato publicado.

Isso importa porque a ordem dos rótulos é **contraintuitiva**: em quase todos os modelos de
sentimento de três classes a convenção é `0 = negativo`, `1 = neutro`, `2 = positivo`. **Aqui
é o oposto:** `0 = POSITIVE`, `1 = NEGATIVE`, `2 = NEUTRAL`. Qualquer código que assuma a
convenção usual inverterá completamente o sinal do índice de sentimento — um erro que **não
gera exceção** e que, portanto, passaria despercebido até a análise dos resultados.

A consequência direta para o nosso código está na Seção 10.2.

### 8.4 O modelo de linguagem puro não foi publicado

Conforme antecipado na Seção 7.1: o artigo descreve **dois** artefatos (FinBERT-PT-BR, o
modelo de linguagem, e SentFinBERT-PT-BR, o classificador), mas o HuggingFace publica
**apenas um** — o classificador, sob o nome do primeiro.

**Consequência para o plano da Seção 5.4:** ao continuar o pré-treinamento MLM a partir de
`lucas-leme/FinBERT-PT-BR`, estaremos partindo de um modelo que **já passou por ajuste fino
supervisionado**, e não do modelo de linguagem puro. Tecnicamente é viável — carrega-se com
`AutoModelForMaskedLM`, descartando a cabeça de classificação e reinicializando a cabeça de
MLM — mas é metodologicamente menos limpo do que a receita original de Santos.

**Isso reforça a recomendação de executar as duas variantes** do experimento previsto na
Seção 5.4: uma partindo do FinBERT-PT-BR (mais próxima do domínio, menos limpa) e outra
partindo do BERTimbau large (replica fielmente Santos, com corpus e porte diferentes). A
comparação entre as duas é, ela própria, um resultado reportável.

### 8.5 Código de uso oficial e citação

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("lucas-leme/FinBERT-PT-BR")
model = AutoModelForSequenceClassification.from_pretrained(
    "lucas-leme/FinBERT-PT-BR", device_map="auto")
```

BibTeX oficial fornecido pelo autor:

```bibtex
@inproceedings{santos2023finbert,
  title={FinBERT-PT-BR: Análise de Sentimentos de Textos em Português do Mercado Financeiro},
  author={Santos, Lucas L and Bianchi, Reinaldo AC and Costa, Anna HR},
  booktitle={Anais do II Brazilian Workshop on Artificial Intelligence in Finance},
  pages={144--155},
  year={2023}
}
```

### 8.6 O que podemos usar — síntese da Tarefa 6

| Item | Uso na dissertação |
|---|---|
| Licença Apache 2.0 | Permite uso, modificação e redistribuição — inclusive publicar um `FinBERT-PETR4` adaptado. **Registrar no capítulo de método.** |
| 177.384 downloads/mês | Evidência quantitativa de relevância do artefato escolhido — responde à pergunta "por que este modelo?" |
| Ficha técnica completa | Preenche a descrição formal do modelo no capítulo de método (12 camadas, 768 dim., 29.794 tokens, 512 posições) |
| Limite de 512 tokens | **Justifica formalmente** a decisão de classificar manchetes e não notícias completas |
| Ausência de *safetensors* | Limitação de reprodutibilidade a declarar |
| Ausência dos dados de treino | Reforça a originalidade do conjunto-ouro |
| Inconsistência `label2id` | Achado técnico verificável, reportável como contribuição de engenharia |
| Duas figuras sob Apache 2.0 | Reprodução autorizada com atribuição |
| BibTeX oficial | Citação correta na versão final |

---

## 9. Tarefa 7 — Trabalhos que citam Lucas Leme (Google Scholar)

> *Orientação: "esse link contem 12 citações ... verificar se esses trabalhos usaram o encoder, como, resultados, se usou outro encoder/tecnologia qual o resultado, resumo, data, autor, e se eu posso/devo usar algum desses na minha pesquisa"*

Conforme a Seção 1(b), o Google Scholar bloqueia acesso automatizado. Os **sete trabalhos
abaixo foram integralmente verificados** via OpenAlex e Semantic Scholar. Estão ordenados por
relevância decrescente para a dissertação.

### 9.1 Trabalhos citantes verificados

---

**① Teles, L. E. P.; Figueiredo, C. M. S. (2025). *Comparing LLMs for Sentiment Analysis in Financial Market News*.**
📅 03/10/2025 · arXiv:2510.15929 · Universidade do Estado do Amazonas (UEA) · Fomento: FAPEAM
🔴 **RELEVÂNCIA: MUITO ALTA**

**Resumo.** Estudo comparativo entre LLMs e modelos clássicos na análise de sentimento de
notícias do mercado financeiro. Avalia três *datasets* — Financial Phrase Bank (4.845
registros), StockEmotions (10.000) e Tweet Financial News (2.486) — todos em inglês.

**Usou o FinBERT-PT-BR?** **Não.** Cita Santos et al. (2023) três vezes na introdução, como
referência conceitual para a definição de análise de sentimento, mas **não o inclui entre os
modelos avaliados**.

**Encoders e tecnologias usados.** Clássicos: SVM, Random Forest e MLP, com TF-IDF + SVD
(redução a 500 colunas), remoção de *stopwords* e balanceamento por *undersampling*.
LLMs e *transformers*: Gemma (`gemma-2-2b-it`), DeBERTa, DeBERTaV3, XLM-RoBERTa, BART
(*zero-shot*) e Gemini 2.0-flash.

**Resultados (acurácia, %).**

| Modelo | FPB | StockEmotions | TFN |
|---|---|---|---|
| SVM | 66,1 | 77,0 | 55,0 |
| Random Forest | 54,3 | 71,2 | 53,1 |
| MLP | 65,8 | 77,5 | 56,0 |
| Gemma | 54,3 | 67,3 | 61,7 |
| DeBERTa | **86,2** | 63,1 | 47,8 |
| DeBERTaV3 | 65,8 | 62,1 | 64,1 |
| XLM-RoBERTa | 58,4 | 61,1 | 57,4 |
| BART | 65,0 | 62,6 | 61,7 |
| **Gemini 2.0-flash** | 80,4 | 74,1 | **78,9** |

**Conclusão dos autores.** O Gemini foi o **mais consistente**, mantendo acurácia acima de
70% nos três conjuntos. LLMs superam modelos clássicos na maioria dos casos. Os autores
propõem, como trabalho futuro, exatamente o que já fazemos: alinhar a análise de sentimento
com previsão de série temporal.

**Devo usar na minha pesquisa? SIM — em duas frentes.**
- **Frente 1, oportunidade experimental.** Se um LLM generativo (Gemini, GPT, Sabiá) supera
  encoders especializados em sentimento financeiro, então **classificar as nossas 300
  manchetes do conjunto-ouro com um LLM via *prompt*** é um experimento de baixo custo, alto
  valor e — decisivo no contexto atual — **que não consome rotulagem humana**. Ver Seção 11.
- **Frente 2, ressalva crítica a explicitar.** O trabalho avalia sobre corpora em **inglês**,
  e portanto **não sustenta** a conclusão de que LLMs superariam o FinBERT-PT-BR em manchetes
  brasileiras. Além disso, o desempenho fortíssimo do DeBERTa no FPB (86,2%) e fraquíssimo no
  TFN (47,8%) sugere sensibilidade ao *dataset*. **Fazer esse teste em português é, ele
  próprio, uma contribuição — e é justamente o vão que este artigo deixa aberto.**

---

**② Abílio, R.; Coelho, G. P.; Silva, A. D. (2024). *Evaluating Named Entity Recognition: a comparative analysis of mono- and multilingual transformer models on a novel Brazilian corporate earnings call transcripts dataset*. Applied Soft Computing.**
📅 18/03/2024 · DOI: 10.1016/j.asoc.2024.112158 · arXiv:2403.12212
🟠 **RELEVÂNCIA: ALTA**

**Resumo.** Constroem o **BraFiNER**, *dataset* de NER financeiro em português brasileiro
a partir de transcrições de *earnings calls* de bancos, anotado por supervisão fraca.
Comparam BERTimbau, PTT5 (monolíngues) e mBERT, mT5 (multilíngues). Propõem reformular
classificação de *tokens* como problema de geração de texto.

**Usou o FinBERT-PT-BR?** Não — cita como referência de modelo de domínio financeiro em PT-BR.

**Resultados.** Modelos baseados em BERT **superam consistentemente** os baseados em T5. Os
multilíngues têm F1-macro comparável entre si, mas o **BERTimbau supera o PTT5**. Nas métricas
de erro, o BERTimbau é superior a todos. **Achado de alerta:** PTT5 e mT5 **geraram sentenças
com alteração de valores monetários e percentuais**.

**Devo usar? SIM.** Três aproveitamentos: (i) é **evidência independente, publicada em
periódico Q1, de que encoders monolíngues PT-BR superam multilíngues em domínio
financeiro** — sustenta a nossa escolha por FinBERT-PT-BR/BERTimbau contra XLM-R e mDeBERTa;
(ii) a advertência sobre alteração de valores por modelos generativos é **contraponto
obrigatório** ao entusiasmo com LLMs do trabalho ①; (iii) o BraFiNER é fonte de corpus
financeiro em PT-BR potencialmente utilizável na etapa de MLM de domínio.

---

**③ Imai, B. Y. L.; Garcia, C. M.; Rocha, M. V.; Koerich, A.; Britto, A. S.; Barddal, J. P. (2024). *Is it Fine to Tune? Evaluating SentenceBERT Fine-tuning for Brazilian Portuguese Text Stream Classification*. IEEE BigData 2024.**
📅 15/12/2024 · DOI: 10.1109/BigData62323.2024.10825456
🟠 **RELEVÂNCIA: ALTA — e institucionalmente estratégica**

> **Nota:** Jean Paul Barddal e Alceu de Souza Britto Jr. são pesquisadores do **PPGIa da
> PUCPR** — o nosso próprio programa. Recomenda-se fortemente citar este trabalho, e
> considerar consultá-los diretamente sobre *concept drift* aplicado ao nosso corpus.

**Resumo.** Avaliam o impacto de **atualizar periodicamente** modelos SentenceBERT em
classificação de notícias brasileiras em regime de fluxo (*text stream*), contra o uso de
modelos estáticos. Tratam de *concept drift* e *semantic shift*. Atualizam o SBERT
**anualmente** com número reduzido de textos recentes e classificam com *Adaptive Random
Forest*.

**Usou o FinBERT-PT-BR?** Não — cita como referência de modelo PT-BR de domínio.

**Resultados.** O ajuste fino periódico com amostra de textos recentes **supera o modelo
estático na maioria dos anos analisados**, em F1-macro, com bom compromisso de tempo de
execução.

**Devo usar? SIM, com prioridade.** Endereça diretamente uma vulnerabilidade não tratada da
nossa dissertação: **usamos um modelo congelado em fevereiro de 2024 sobre um corpus que vai
de 2018 a 2026.** As notícias de 2025–2026 sobre a Petrobras contêm vocabulário que o modelo
nunca viu. Este trabalho fornece (i) a fundamentação teórica para declarar essa limitação com
propriedade, (ii) a metodologia para testá-la por subperíodos e (iii) uma referência
institucional interna. **Leitura integral recomendada.**

---

**④ Reichert, M. H.; Perlin, M. S. (2025). *Using ChatGPT for Creating Multi-Language Finance Related Sentiment Dictionaries*. Computational Economics.**
📅 23/12/2025 · DOI: 10.1007/s10614-025-11233-3
🟡 **RELEVÂNCIA: MÉDIA-ALTA**

**Resumo.** Uso de ChatGPT para gerar dicionários de sentimento financeiro multilíngues.
Marcelo Perlin é professor da **UFRGS** e autor de referência em finanças quantitativas no
Brasil (criador do pacote `GetHFData` e do `BatchGetSymbols`), o que torna provável a
inclusão do português.

**Usou o FinBERT-PT-BR?** Não — cita no contexto de recursos de sentimento financeiro
em português.

**Devo usar? Provavelmente sim, como abordagem alternativa.** Um **dicionário** de sentimento
financeiro em português seria uma **linha de base léxica** para contrastar com o FinBERT-PT-BR
— aquilo que Loughran e McDonald representam para o inglês. Uma comparação
"encoder × dicionário × LLM" fortaleceria substancialmente o capítulo de resultados.
**Ressalva:** o texto integral está atrás de *paywall* da Springer; recomenda-se acesso pelo
Portal de Periódicos da CAPES via PUCPR.

---

**⑤ Alves, M. A. R.; Macedo, M. B.; Ribeiro, J.; Mancine, L.; Pereira Júnior, C. P. (2024). *Sentimentos em Cena: uma Análise dos Comentários em Trailers de Filmes da Netflix Brasil no YouTube*. BraSNAM 2024.**
📅 21/07/2024 · DOI: 10.5753/brasnam.2024.2974
🟢 **RELEVÂNCIA: BAIXA**

Análise de sentimento de comentários do YouTube em português. Domínio de entretenimento.
Citação metodológica ao FinBERT-PT-BR, sem uso aplicado a finanças. Serve apenas para
demonstrar a difusão do modelo além do domínio financeiro.

---

**⑥ Tanaka, S. A. et al. (2026). *A Machine Learning-Driven CRM Approach for Identifying Member Churn in a Brazilian Agro-Industrial Cooperative*. Algorithms, v. 19, n. 3.**
📅 27/02/2026 · DOI: 10.3390/a19030180
🟢 **RELEVÂNCIA: BAIXA — com um aproveitamento pontual**

Previsão de *churn* em cooperativa agroindustrial. Usa Random Forest, XGBoost, SVC, *ensemble*
por votação, validação cruzada estratificada e **SHAP** para explicabilidade.

**Aproveitamento pontual:** o uso de **SHAP** para explicabilidade em modelos tabulares é
transponível ao nosso Script 04/05. Uma análise SHAP mostrando **quanto o sentimento
contribui para a previsão de volatilidade** responderia com elegância à ponderação da banca
sobre a contribuição marginal do componente textual.

---

**⑦ Błoch, A.; Santana, C.; Amantino, M. (2026). *Os jesuítas e a Era do Algoritmo: uma introdução à análise de sentimentos da correspondência colonial ultramarina portuguesa*. Estudos Ibero-Americanos.**
📅 13/04/2026 · DOI: 10.15448/1980-864x.2026.1.46315
🟢 **RELEVÂNCIA: BAIXA — com uma citação aproveitável**

Análise de sentimento em correspondência colonial portuguesa (1642–1822). Humanidades
digitais.

**Aproveitamento pontual:** o artigo discute como **a qualidade dos dados condiciona o
desempenho da IA** e defende o papel indispensável do humano no processo. É uma citação
elegante — de fora da área — para o parágrafo em que justificarmos a necessidade do
conjunto-ouro humano e as limitações do rótulo automático.

---

### 9.2 Síntese da Tarefa 7

| Trabalho | Data | Usou o encoder? | Encoder/tecnologia própria | Devo usar? |
|---|---|---|---|---|
| ① Teles e Figueiredo | 10/2025 | **Não** (citação conceitual) | Gemini, DeBERTa, Gemma, BART, XLM-R, SVM, RF, MLP | **Sim — experimento com LLM** |
| ② Abílio, Coelho e Silva | 03/2024 | Não | BERTimbau, PTT5, mBERT, mT5 | **Sim — sustenta encoder monolíngue** |
| ③ Imai et al. (PUCPR) | 12/2024 | Não | SentenceBERT + Adaptive RF | **Sim — *concept drift*** |
| ④ Reichert e Perlin | 12/2025 | Não | ChatGPT p/ dicionários | Sim — linha de base léxica |
| ⑤ Alves et al. | 07/2024 | Não | — | Não |
| ⑥ Tanaka et al. | 02/2026 | Não | RF, XGBoost, SVC, SHAP | Pontual — SHAP |
| ⑦ Błoch, Santana e Amantino | 04/2026 | Não | — | Pontual — citação |

**Duas leituras do padrão observado.** Primeira: **nenhum trabalho reaplicou o FinBERT-PT-BR
na tarefa para a qual foi criado** — a lacuna documentada na Seção 4. Segunda: **as citações
mais recentes migram para LLMs generativos** (①, ④). Isso é um sinal de tendência da área que
a dissertação precisa endereçar explicitamente, ainda que seja para justificar, com dados,
por que mantivemos um encoder especializado.

### 9.3 Procedimento para fechar a lista de 12

Para completar a verificação antes da versão final:

1. Abrir manualmente, em navegador logado, o endereço da orientação nº 7 e exportar as 12
   entradas (o Scholar permite exportar a página de citações em BibTeX pelo menu de cada
   item).
2. Confrontar com os sete títulos da Seção 9.1 e isolar os ~5 restantes.
3. Verificar, em cada um, apenas duas coisas: **(a)** se o FinBERT-PT-BR foi de fato
   executado, e não somente citado; **(b)** se há previsão de ativo. Só isso altera as
   conclusões das Seções 4 e 6.
4. Candidatos já identificados por busca dirigida, a conferir: *"The Role of Fiscal Sentiment
   in Brazil's Yield Curve"* (Tatiana Pinheiro); *"Análise de sentimento no contexto do
   mercado financeiro de ações"* (repositório do IPP, Porto); e o material técnico de Ian
   Araujo sobre *fine-tuning* de modelos de linguagem para sentimento financeiro.

---

## 10. Achados operacionais sobre o nosso próprio código e dados

Esta seção não foi solicitada nas orientações. É resultado do cruzamento entre a literatura
examinada e o estado atual do repositório, e contém três achados que afetam decisões
imediatas.

### 10.1 O conjunto-ouro precisa ser refundado, não ampliado

Estado atual (`Mestrado_PETR4/conjunto_ouro/relatorio_validacao_ouro.txt`):

- 300 manchetes rotuladas, avaliadas contra o FinBERT-PT-BR
- Acurácia bruta **58,00%**; reponderada à população **57,65%**
- **Kappa de Cohen 0,371** — "concordância razoável (*fair*)"
- Relevância humana: 111/300 (37,0%) marcadas como relevantes à PETR4
- Matriz de confusão: a classe Neutra é a mais confundida — 32 neutras classificadas como
  negativas e 26 como positivas

Comparando com o protocolo de Santos (2022), faltam **três controles**, e a ausência do
terceiro é a mais grave:

| Controle | Santos (2022) | Nosso conjunto-ouro |
|---|---|---|
| Nº de anotadores | 3 (cada texto por ≥ 2) | **1** |
| Categoria "não se aplica" | Sim | Parcial (há marcação de relevância) |
| Descarte por discordância | Sim — 49,7% descartados | **Impossível** (não há segunda anotação) |
| Percentual de concordância | 90,4% | **Não calculável** |
| *Krippendorff's alpha* | 0,88 | **Não calculável** |

**A consequência é decisiva:** sem segunda anotação não existe métrica de concordância; sem
métrica de concordância não é possível afirmar que o gabarito é confiável; e sem gabarito
confiável, **os 58% não medem o FinBERT-PT-BR — medem a distância entre o FinBERT-PT-BR e um
anotador único não calibrado.** O κ = 0,371 é ambíguo entre "o modelo erra" e "o gabarito é
ruidoso", e nada no desenho atual permite separar as duas hipóteses.

Isso fundamenta tecnicamente a orientação do Prof. Emerson. **Ampliar o gabarito de 300 para
600 manchetes nas condições atuais não resolveria nada** — dobraria o volume mantendo o
mesmo defeito estrutural. Se e quando a rotulagem for retomada, a prioridade é **dupla
anotação de um subconjunto**, não mais volume.

### 10.2 Mapeamento de rótulos invertido no Script 03

Em [`src/sentimento/03_analise_sentimento_bertimbau_petr4.py:312-317`](../src/sentimento/03_analise_sentimento_bertimbau_petr4.py#L312-L317):

```python
if L in ('POSITIVE', 'POSITIVO', 'POS', 'LABEL_2'):
    polaridade, label = +1, 'Positive'
elif L in ('NEGATIVE', 'NEGATIVO', 'NEG', 'LABEL_0'):
    polaridade, label = -1, 'Negative'
else:  # NEUTRAL / NEUTRO / LABEL_1
    polaridade, label = 0, 'Neutral'
```

Confrontando com o `id2label` real do modelo (Seção 8.3), o mapeamento de contingência está
**invertido**: `LABEL_0` é `POSITIVE` no FinBERT-PT-BR, mas o código o trata como negativo; e
`LABEL_2` é `NEUTRAL`, mas o código o trata como positivo.

**Situação atual: sem impacto nos resultados já produzidos.** O `config.json` traz o
`id2label` correto, de modo que a `pipeline` retorna as *strings* `POSITIVE`/`NEGATIVE`/
`NEUTRAL` e o caminho `LABEL_*` **nunca é acionado**. Todos os resultados até aqui estão
corretos.

**Risco:** o `label2id` publicado é inconsistente (Seção 8.3). Basta uma mudança de versão da
biblioteca `transformers`, um carregamento por caminho alternativo ou o uso de outro modelo
cujo `config` não traga `id2label` para o caminho de contingência ser acionado — e então
**todo o sinal do ISM se inverte silenciosamente, sem erro, sem exceção, sem aviso**.

**Correção recomendada** (não aplicada — decisão do mestrando): restringir o mapeamento
`LABEL_*` ao modelo efetivamente carregado, ou eliminá-lo e falhar explicitamente diante de
rótulo desconhecido. Em pipeline científica, falhar alto é preferível a inverter em silêncio.

### 10.3 O ambiente Python local está com o PyTorch quebrado

```
OSError: [WinError 1114] Uma rotina de inicialização da biblioteca de vínculo dinâmico (DLL)
falhou. Error loading "...\site-packages\torch\lib\c10.dll" or one of its dependencies.
```

**A falha é pré-existente** — foi verificada isoladamente, sem qualquer pacote adicional
instalado. O `torch` 2.12.1 está registrado no ambiente, mas não carrega. Como os
experimentos de encoder de julho rodaram (`device: cpu`, conforme
`experimentos_encoder/log_albertina.txt`), algo mudou no ambiente desde então.

**Impacto:** **nenhum experimento de encoder ou de sentimento pode ser executado nesta
máquina** até a correção. Causas mais prováveis, em ordem: ausência ou desatualização do
*Microsoft Visual C++ Redistributable* (x64); conflito de `libiomp5md.dll` entre MKL do
Anaconda e a do PyTorch; ou incompatibilidade da versão do `torch` com o `numpy` 1.26.4
instalado.

**Recomendação:** dado que o plano da Seção 11 envolve MLM sobre ~205 mil textos, **a solução
mais rápida e adequada não é depurar o ambiente local, e sim usar o Google Colab** — que é o
ambiente para o qual a maior parte da pipeline já foi escrita, e é o mesmo tipo de ambiente
(Kaggle com 2× T4) que Santos utilizou.

---

## 11. Plano de ação recomendado até 10/08/2026

A ordenação obedece a dois critérios: **não depender de rotulagem manual** (respeitando a
orientação do Prof. Emerson) e **produzir resultado apresentável em uma semana**.

### Prioridade 1 — Executáveis até 10/08

| # | Ação | Por quê | Esforço | Depende de rótulo? |
|---|---|---|---|---|
| **1.1** | **MLM de domínio** sobre `lucas-leme/FinBERT-PT-BR` e sobre `bert-large-portuguese-cased`, usando as ~205 mil notícias. Máscara 15%, *lr* 2e-5, 2 épocas, filtro ≤ 512 tokens. Métrica: **perplexidade** em *holdout* de 10 mil textos não vistos. | Replica a etapa de maior ganho de Santos (1,51 → 1,24). Resultado quantitativo sem gabarito. | Colab, ~6–10 h | **Não** |
| **1.2** | **Classificar o conjunto-ouro com um LLM** (Gemini ou equivalente) via *prompt*, usando a instrução literal de Santos, e comparar com o FinBERT-PT-BR e com o rótulo humano. | Testa em português a tese central de Teles e Figueiredo (2025) e preenche a lacuna que aquele artigo deixa. | ~4 h | **Não** |
| **1.3** | **Bootstrap + intervalos de confiança** sobre `resultado_encoders_petr4.csv`, conforme monografia Seção 4.2.4. | Sem isso, a tabela de encoders não sustenta conclusão nenhuma. Provavelmente mostrará que o BERTimbau large **não** difere do FinBERT-PT-BR. | ~2 h | **Não** |
| **1.4** | **Corrigir o ambiente** ou migrar definitivamente os experimentos para o Colab. | Bloqueia 1.1 e 1.3. | ~1–3 h | Não |

### Prioridade 2 — Redação, sem custo computacional

| # | Ação |
|---|---|
| **2.1** | Incorporar ao referencial teórico as **4 referências de relação muito alta** (Hiew et al., 2019; Januário et al., 2022; Artstein e Poesio, 2008; Krippendorff, 2018) e as **3 exclusivas da monografia** (Poursabzi-Sangdeh e Boyd-Graber, 2015; Alcoforado et al., 2022; Efron, 1992). |
| **2.2** | Escrever a subseção **"Lacuna de literatura"** com o achado da Seção 4: o FinBERT-PT-BR tem 177 mil downloads/mês e adoção acadêmica aplicada praticamente nula na tarefa para a qual foi criado. |
| **2.3** | **Reposicionar a volatilidade como contribuição principal** e a direção como resultado negativo reportado, com apoio na Seção 6.1 e em Bollen et al. (2011). |
| **2.4** | Escrever a subseção **"Transferência de domínio"**: por que 0,76 (notícias gerais) vira 0,58 (manchetes de ativo único) — Seção 7.2.1. |
| **2.5** | Declarar formalmente a limitação de ***concept drift***: modelo congelado em 02/2024 sobre corpus 2018–2026, com apoio em Imai et al. (2024). |
| **2.6** | Documentar no capítulo de método: licença Apache 2.0, ficha técnica do modelo, ausência de *safetensors*, limite de 512 tokens como justificativa do uso de manchetes. |
| **2.7** | **Conferir a referência "Silva (2018)"** do plano de enriquecimento, para descartar confusão com a Silva (2018) citada por Santos — ver alerta em 7.3/D.4. |

### Prioridade 3 — Quando a rotulagem for retomada

| # | Ação |
|---|---|
| **3.1** | **Dupla anotação de um subconjunto** (100–150 manchetes das 300 já rotuladas) e cálculo do **Krippendorff's alpha**. É a menor intervenção que torna o gabarito defensável — e é mais valiosa do que ampliar para 600 sob o protocolo atual. |
| **3.2** | Adotar a **definição operacional literal de Santos** e a categoria **"não se aplica"** com descarte por discordância. |
| **3.3** | Aplicar **modelagem de tópicos ou *zero-shot*** para pré-selecionar textos representativos e sugerir classe ao anotador (Poursabzi-Sangdeh e Boyd-Graber, 2015; Alcoforado et al., 2022) — reduz custo e mitiga a falta de especialização em finanças, que é precisamente a objeção levantada pelo Prof. Emerson. |
| **3.4** | Retreinar os encoders com o protocolo completo: ***gradual unfreezing***, ***lr*** **= 5e-6**, **11 épocas**, CV 5-*fold* — só então a comparação entre encoders passa a ser válida. |

### 11.1 Sugestão de pauta para a mentoria de 10/08

1. Apresentar o achado da Seção 10.1 — a rotulagem tem um problema estrutural **anterior** ao
   da qualificação do anotador, e a suspensão está tecnicamente correta por essa razão
   também.
2. Apresentar os resultados de 1.1 e 1.2 (MLM de domínio e LLM contra o gabarito) como as
   frentes que avançam **sem** rotulagem.
3. Apresentar a lacuna de literatura da Seção 4 e propor o reposicionamento da volatilidade
   como contribuição principal (Seção 6.1).
4. Consultar sobre a possibilidade de aproximação com o **Prof. Jean Paul Barddal (PPGIa
   PUCPR)** a respeito de *concept drift* no corpus — trabalho ③ da Seção 9.1.

---

## 12. Referências consultadas neste levantamento

**Fontes primárias analisadas integralmente**

SANTOS, L. L.; BIANCHI, R. A. C.; COSTA, A. H. R. FinBERT-PT-BR: Análise de Sentimentos de
Textos em Português do Mercado Financeiro. In: BRAZILIAN WORKSHOP ON ARTIFICIAL INTELLIGENCE
IN FINANCE (BWAIF), 2., 2023. **Anais** [...]. Porto Alegre: SBC, 2023. p. 144-155.
DOI: 10.5753/bwaif.2023.231151.

SANTOS, L. L. **FinBERT-PT-BR: análise de sentimentos de textos em português referentes ao
mercado financeiro**. 2022. Trabalho de Conclusão de Curso (Engenharia de Computação) —
Escola Politécnica, Universidade de São Paulo, São Paulo, 2022. Orientadora: Anna Helena
Reali Costa. 61 f.

**Repositório de modelo**

SANTOS, L. L. **lucas-leme/FinBERT-PT-BR**. Hugging Face, 2023. Última modificação:
13 fev. 2024. Licença Apache 2.0. Disponível em:
https://huggingface.co/lucas-leme/FinBERT-PT-BR. Acesso em: 3 ago. 2026.

**Trabalhos citantes verificados** — ver Seção 9.1 para as referências completas de Teles e
Figueiredo (2025); Abílio, Coelho e Silva (2024); Imai et al. (2024); Reichert e Perlin
(2025); Alves et al. (2024); Tanaka et al. (2026); Błoch, Santana e Amantino (2026).

**Bases bibliográficas utilizadas**

OpenAlex API (`api.openalex.org`) · Semantic Scholar Graph API
(`api.semanticscholar.org`) · Hugging Face Hub API (`huggingface.co/api`).
Consultas realizadas em 3 ago. 2026.

---

## Anexo — Arquivos gerados nesta pasta

| Arquivo | Conteúdo |
|---|---|
| `RESPOSTA_ORIENTACOES_2026-08-10.md` | Este documento |
| `RESPOSTA_ORIENTACOES_2026-08-10.docx` | Versão em Word, formatação ABNT |
| `referencias_artigo_bwaif_24960.csv` | As 28 referências do artigo com os 8 campos solicitados |
| `_artigo_bwaif_24960.pdf` / `.txt` | PDF e texto integral do artigo do BWAIF |
| `_monografia_texto.txt` | Texto integral extraído da monografia de 2022 |
| `_teles2025.pdf` / `.txt` | PDF e texto de Teles e Figueiredo (2025) |
| `_scholar.html` | Resposta do Google Scholar (com CAPTCHA), preservada como evidência da limitação declarada na Seção 1(b) |
