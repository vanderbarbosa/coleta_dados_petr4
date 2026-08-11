# Respostas às duas perguntas do Prof. Emerson sobre a rotulagem

**Mestrando:** Vanderlei Barbosa da Silva · **Orientador:** Prof. Dr. Julio Cesar Nievola
**Co-orientador:** Prof. Dr. Emerson Cabrera Paraiso · **Para a mentoria de 10/08/2026**
**Elaborado em:** 08/08/2026

> **As duas perguntas**
> 1. *"A rotulagem, para ser útil e válida, precisaria ser feita por especialistas em finanças."*
> 2. *"Como você usaria, na prática, essas notícias rotuladas?"*

---

## Sumário da resposta em cinco linhas

1. **O gabarito tem quatro rótulos, não um.** A objeção do especialista se aplica com força a
   **um** deles, parcialmente a outro, e não se sustenta nos outros dois.
2. **Testei a objeção empiricamente**, e ela tem base: a coluna que exige finanças acertou
   **46,7%** da direção da PETR4 — abaixo do acaso e abaixo da regra ingênua "sempre alta"
   (52,8%).
3. **Mas o próprio anotador já sinalizava isso**: marcou "Indefinida" em 80% dos casos e baixa
   confiança justamente nas notícias relevantes. O instrumento se autodiagnosticou.
4. **Sobre o uso prático:** o conjunto-ouro **não é base de treino** — é **instrumento de
   medida e de calibração**. 300 rótulos não treinam um encoder de 110 milhões de parâmetros;
   mas corrigem o viés do índice de sentimento que alimenta o GARCH, ao longo dos 8 anos.
5. **Proposta:** o especialista entra como **árbitro de ~55 casos**, não como anotador de 300 —
   e a coluna que exige finanças é **substituída pelo retorno realizado**, que não precisa de
   anotador nenhum.

---

# Parte 1 — "precisaria ser feita por especialistas em finanças"

## 1.1 O ponto de partida: o gabarito tem quatro rótulos

Isto é o que muda a conversa. A planilha
`conjunto_ouro/conjunto_ouro_para_rotular.xlsx` não pede um julgamento — pede quatro, e a
própria rubrica da rodada 2 já os separa:

> *"1) **Sentimento_Humano** — o TOM financeiro (Positivo/Negativo/Neutro), **ignorando a
> Petrobras**. 2) **Relevante_PETR4** — a notícia plausivelmente afeta a PETR4? (Sim/Não).
> 3) **Direcao_Esperada_PETR4** — efeito no preço: Alta/Baixa/Indefinida. 4)
> **Confianca_Rotulador** — sua certeza."*

Cada coluna exige um tipo diferente de competência:

| Coluna | O que mede | Competência exigida | Objeção do especialista se aplica? |
|---|---|---|---|
| **1. `Sentimento_Humano`** | O **tom** do texto, explicitamente *ignorando a Petrobras* | Compreensão de leitura + vocabulário financeiro básico | **Não** — ver 1.2 |
| **2. `Relevante_PETR4`** | A notícia plausivelmente afeta a PETR4? | Conhecimento de domínio **leve** | **Parcialmente** |
| **3. `Direcao_Esperada_PETR4`** | O preço sobe ou cai? | Conhecimento de finanças **pesado** | **Sim, integralmente** |
| **4. `Confianca_Rotulador`** | Autoavaliação | Nenhuma | Não se aplica |

**Distribuição efetiva dos 300 itens:**

| Coluna | Distribuição |
|---|---|
| `Sentimento_Humano` | Neutro 124 · Positivo 96 · Negativo 80 |
| `Relevante_PETR4` | **Não 189 · Sim 111** (37,0% relevantes) |
| `Direcao_Esperada_PETR4` | **Indefinida 240 (80%)** · Alta 39 · Baixa 21 |
| `Confianca_Rotulador` | Alta 233 · Média 57 · Baixa 9 |

> **A coluna 3 — a única que realmente exige um especialista — está 80% vazia de conteúdo.**
> O anotador se absteve na esmagadora maioria dos casos. Isso não é falha: é o instrumento
> funcionando. Ele registrou que não sabia.

## 1.2 Por que a coluna 1 não exige especialista — evidência da literatura

O próprio autor do FinBERT-PT-BR, o modelo que usamos, **não empregou especialistas em
finanças**. Empregou (SANTOS, 2022, Seção 4.2.3):

> *"três pessoas, sendo **duas com formação em engenharia e uma com formação em linguística**"*

E obteve **90,4% de concordância** e ***Krippendorff's alpha* de 0,88** — patamar de
excelência em anotação de corpus.

O que produziu essa qualidade não foi a formação dos anotadores, e sim **três controles
metodológicos**:

| Controle | Santos (2022) | **Nosso gabarito hoje** |
|---|---|---|
| Definição operacional ancorada em **consequência econômica** | *"se o texto implicaria em uma rentabilidade Positiva, Negativa ou Neutra"* | ✅ Rubrica equivalente |
| **Dupla anotação** de todo texto | Sim, ao menos 2 pessoas por item | ❌ **Anotador único** |
| **Descarte por discordância** | Sim — **497 de 1.000 (49,7%) descartados** | ❌ Impossível sem 2ª anotação |
| Métrica formal de concordância | α = 0,88 | ❌ **Não calculável** |

> **Este é o ponto mais importante da Parte 1.** O nosso gabarito tem um problema real e
> grave — mas **não é o que o Prof. Emerson apontou**. É a ausência de segunda anotação. Sem
> ela não há métrica de concordância; sem métrica de concordância não é possível afirmar que
> o gabarito é confiável; e então os 58% de acurácia do FinBERT **não medem o modelo** — medem
> a distância entre o modelo e um anotador único não calibrado.
>
> É um argumento **mais forte** para suspender a rotulagem na forma atual do que o argumento
> da qualificação. E é honesto reconhecê-lo.

## 1.3 Onde a objeção do Prof. Emerson tem base — e os dados mostram

### Evidência A — o próprio anotador sinalizou o déficit

Cruzando `Confianca_Rotulador` com `Relevante_PETR4`:

| Confiança | Não relevante | **Relevante** |
|---|---|---|
| **Alta** | 178 (94,2%) | **55 (50,0%)** |
| Média | 10 (5,3%) | **47 (42,7%)** |
| Baixa | 1 (0,5%) | **8 (7,3%)** |

**Quando a notícia não afeta a PETR4, o anotador tem alta confiança em 94% dos casos. Quando
afeta, só em 50%.** A confiança despenca exatamente onde o conhecimento de finanças passa a
ser necessário.

> Isto é uma confirmação empírica e independente da intuição do Prof. Emerson — e **localiza**
> o problema: não são os 300 itens, são os **55 itens relevantes com confiança média ou baixa**.

### Evidência B — a aposta direcional não bateu o acaso

Confrontei a coluna `Direcao_Esperada_PETR4` com o **retorno realizado da PETR4 no pregão
seguinte**. Script auditável em
[`src/sentimento/validar_rotulos_contra_mercado.py`](../src/sentimento/validar_rotulos_contra_mercado.py);
resultados em `Mestrado_PETR4/validacao_rotulos_contra_mercado.json`.

| Métrica | Valor |
|---|---|
| Casos com aposta direcional | **60** (39 "Alta" + 21 "Baixa") |
| Pregões distintos | **60** — uma notícia por pregão, observações independentes |
| **Taxa de acerto** | **46,7%** (28/60) |
| Teste binomial contra 50% | **p = 0,699** |
| IC 95% da taxa | **[33,7% ; 60,0%]** |
| Acerto em "Alta" | 48,7% (19/39) |
| Acerto em "Baixa" | 42,9% (9/21) |
| **Referência: PETR4 subiu em** | **52,8%** dos pregões da série |

**O anotador acertou 46,7%. A regra ingênua "sempre responda Alta" teria acertado 52,8%.**

> ⚠️ **Como reportar isso com honestidade — e é essencial não exagerar.** O intervalo de
> confiança vai até 60%. Com n = 60, **este teste não prova que um especialista falharia**.
> Prova apenas que **este anotador, nestes 60 casos, não superou o acaso**. É uma diferença
> que a banca vai cobrar, e é melhor sermos nós a fazê-la.

### Evidência C — o tom não determina a direção neste ativo

Cruzando as duas colunas, só nas 111 notícias relevantes:

| Tom → | Alta | Baixa | Indefinida |
|---|---|---|---|
| **Negativo** | **11** | **13** | 14 |
| Neutro | 4 | 1 | 20 |
| **Positivo** | **24** | 7 | 17 |

**Tom negativo dividiu-se quase igualmente: 11 apostas de alta contra 13 de baixa.**

Isso não é ruído — é a natureza do ativo. A PETR4 é uma **produtora de petróleo**, e para ela
várias notícias de tom negativo são economicamente positivas:

- *"Conflito no Oriente Médio escala"* → tom negativo, **preço do petróleo sobe**, positivo para a produtora
- *"OPEP corta produção"* → tom neutro/negativo, **preço sobe**, positivo
- *"Petrobras aumenta preço da gasolina"* → tom negativo para o consumidor, **positivo para a margem**
- *"Governo estuda intervenção em preços"* → tom neutro, **fortemente negativo** para o minoritário

> **Esta tabela é a explicação, ao nível do dado bruto, de por que a previsão de direção fica
> próxima do acaso na nossa pesquisa.** Não é falha do encoder nem do anotador: **o mapeamento
> tom → direção é genuinamente ambíguo para uma produtora de petróleo.** É um achado, e deve
> entrar na dissertação como tal.

## 1.4 O argumento que dissolve boa parte da objeção

A coluna 3 pede que um humano preveja a direção de um ativo lendo uma manchete. Há duas razões
para duvidar que qualquer pessoa consiga:

1. **Se um especialista conseguisse fazer isso de forma confiável, ele estaria operando no
   mercado, não anotando planilhas.** A hipótese de eficiência de mercado em forma fraca prevê
   que informação pública já está no preço.
2. **Toda a literatura que levantamos converge para direção ≈ acaso.** Os 87,6% de Bollen,
   Mao e Zeng (2011) nunca foram replicados de forma robusta. O repositório público mais
   próximo do nosso objeto (PRIO3, mesma indústria, mesmo modelo) conclui:
   *"headline tone doesn't move PRIO3 intraday"*.

> **Mas há um ponto ainda mais decisivo: essa coluna não precisa de anotador nenhum.**
>
> O retorno realizado da PETR4 **já é o rótulo**. É público, é objetivo, não tem viés de
> anotador e está disponível para as **~205 mil notícias**, não só para 300. A coluna 3 pode
> ser **aposentada e substituída pelo mercado**.
>
> Isso não é um contorno — é metodologicamente superior. E responde à objeção do Prof. Emerson
> da forma mais limpa possível: **onde a expertise seria indispensável, não usamos julgamento
> humano nenhum.**

## 1.5 Proposta concreta — o especialista como árbitro, não como anotador

| # | Medida | Custo | Endereça |
|---|---|---|---|
| 1 | **Aposentar a coluna `Direcao_Esperada_PETR4`.** Substituir pelo retorno realizado. | Zero | A objeção, na sua forma mais forte |
| 2 | **Dupla anotação da coluna `Sentimento_Humano`** em 100–150 itens dos 300, e cálculo do **Krippendorff's alpha**. | 2 anotadores × ~3 h | O problema **real** (1.2) |
| 3 | **Especialista arbitra só as discordâncias** + os **55 itens relevantes com confiança média/baixa**. | **~2 h de especialista**, não 300 itens | A objeção, na parte em que procede |
| 4 | **Codificar a expertise no guia, não no anotador**: rubrica com exemplos resolvidos das inversões típicas de uma produtora de petróleo. | ~4 h, uma vez | Transfere o conhecimento para o instrumento |
| 5 | **Adotar a categoria "Não se aplica"** com descarte por discordância, como Santos. | Zero | Qualidade do gabarito |
| 6 | **Migrar a planilha para o `doccano`** — interface aberta com suporte nativo a múltiplos anotadores e concordância. | ~2 h de configuração | Viabiliza 2 e 3 |

**Sobre a medida 4**, que é a mais subestimada. Um guia de anotação com exemplos resolvidos é
prática consolidada em linguística de corpus (HOVY; LAVID, 2010 — a referência que Santos usa).
Exemplos a incluir:

> *"Alta do petróleo → **positivo** para a PETR4 (produtora), ainda que o tom da notícia seja
> de crise."*
> *"Corte de produção da OPEP → **positivo** (sustenta preço), embora 'corte' soe negativo."*
> *"Interferência do governo na política de preços → **negativo** para o acionista minoritário,
> ainda que o tom seja neutro e institucional."*
> *"Dividendo já anunciado e repercutido → **neutro** (já precificado)."*

**Isso transfere o conhecimento do especialista para dentro do instrumento**, que é
reproduzível e auditável — em vez de deixá-lo na cabeça de uma pessoa que precisaria estar
presente em cada item.

---

# Parte 2 — "como você usaria, na prática, essas notícias rotuladas?"

## 2.1 Primeiro, desfazer o mal-entendido: não é base de treino

A resposta começa por onde a pergunta provavelmente esperava ir — e não vai:

> **O conjunto-ouro não treina modelo nenhum.** Trezentos itens não ajustam um encoder de 110
> milhões de parâmetros. Santos precisou de 503 rótulos **e** de um modelo de linguagem já
> adaptado com 1,4 milhão de textos para conseguir convergência. Nossos próprios experimentos
> confirmam: ao tentar ajustar BERTimbau e Albertina sobre 300 itens, o Albertina **colapsou
> para a classe majoritária** — κ = 0,000 em 3 dos 5 *folds*.
>
> **O conjunto-ouro é um instrumento de medida e de calibração.** Como um termômetro aferido:
> não aquece nada, mas sem ele todos os números que reportamos são leituras sem escala.

Isso posto, há **seis usos concretos**, e cada um responde a uma pergunta que a banca vai fazer.

## 2.2 Uso 1 — medir o erro do modelo **no nosso domínio**

Sem o gabarito, reportaríamos os 0,76 de acurácia de Santos como se fossem nossos. Com ele,
medimos o que de fato acontece quando o modelo sai de notícias gerais e vai para manchetes de
um ativo:

| | Acurácia | F1 | κ |
|---|---|---|---|
| Santos (2023), notícias gerais de mercado | 0,76 | 0,73 | — |
| **Nós, manchetes de PETR4** | **0,58** | 0,577 | **0,371** |

> **A diferença entre "usamos um modelo com acurácia publicada de 0,76" e "medimos 0,58 no
> nosso domínio" é a diferença entre repetir e verificar.** Só a segunda é ciência — e ela só
> existe por causa dos 300 rótulos.
>
> E mais: essa degradação **é um resultado publicável**. Nenhum trabalho da literatura que
> levantamos quantifica a perda de desempenho de um modelo de sentimento financeiro em
> português ao ser transferido de notícias gerais para um ativo específico.

## 2.3 Uso 2 — arbitrar as escolhas técnicas da dissertação

Toda comparação de modelo precisa de um árbitro. Sem gabarito, escolher entre alternativas
vira questão de gosto. Com ele, vira medição:

| Decisão a tomar | Sem gabarito | Com gabarito |
|---|---|---|
| FinBERT-PT-BR × BERTimbau × Albertina | Opinião | Acurácia, F1, κ + IC por *bootstrap* |
| Encoder × comitê de dois modelos | Impossível decidir | Mensurável |
| Encoder × LLM generativo | Impossível decidir | Mensurável |
| Encoder × dicionário léxico | Impossível decidir | Mensurável |

Quatro das frentes técnicas planejadas — comparação de encoders, comitê, LLM e dicionário —
**dependem inteiramente do gabarito**. Sem ele, nenhuma pode ser concluída.

## 2.4 Uso 3 — diagnosticar **onde** o modelo erra, o que vira conserto

O gabarito não produz só um número; produz uma matriz de confusão:

| Humano ↓ / Modelo → | Negative | Neutral | Positive |
|---|---|---|---|
| Negative (80) | 60 | 11 | 9 |
| **Neutral (124)** | **32** | 66 | **26** |
| Positive (96) | 21 | 27 | 48 |

**58 dos 124 casos neutros (46,8%) foram empurrados para os extremos.** A classe neutra é onde
o modelo quebra.

Esse diagnóstico tem confirmação externa: Błoch, Santana e Amantino (2026), que usaram o mesmo
modelo, caracterizam-no como *"fortemente influenciado pela presença de termos negativos ou
positivos"* — ou seja, opera por **léxico**, não por **contexto**. Uma manchete neutra que
contenha termos carregados (*"Petrobras avalia corte de investimentos"*) é puxada para o
extremo.

> **Daí sai uma solução concreta:** combinar o FinBERT-PT-BR com um modelo **contextual** num
> comitê, exatamente como aqueles autores fizeram. O gabarito não disse apenas "58%" — disse
> **o que consertar e por quê**.

## 2.5 Uso 4 — corrigir o viés do índice de sentimento (o uso mais "prático")

**Este é o melhor argumento para responder ao Prof. Emerson**, porque mostra os 300 rótulos
agindo sobre os 8 anos inteiros da série.

O nosso Índice de Sentimento da Mídia é, na essência, uma função das **proporções de classes**:

$$\text{ISM}_t = \frac{\text{Pos}_t - \text{Neg}_t}{\text{Pos}_t + \text{Neu}_t + \text{Neg}_t}$$

Se o classificador erra de forma **sistemática** — e a matriz acima mostra que erra, empurrando
neutros para os extremos —, então as proporções estão viesadas, e **o ISM está viesado todos
os dias, ao longo de toda a série**. Esse ISM entra no GARCH e no XGBoost. O viés se propaga
até o resultado final.

**A matriz de confusão do gabarito permite corrigir isso.** É um problema conhecido em
aprendizado de máquina — chamado **quantificação** ou estimação de prevalência —, e a correção
é direta: se **M** é a matriz de confusão normalizada estimada no gabarito, e **p̂** é o vetor
de proporções observadas no corpus completo, a proporção verdadeira **p** resolve

$$\mathbf{M}^{\top}\,\mathbf{p} = \hat{\mathbf{p}}
\qquad\Longrightarrow\qquad
\mathbf{p} = (\mathbf{M}^{\top})^{-1}\,\hat{\mathbf{p}}$$

*(É o método "Adjusted Classify and Count"; a variante por máxima verossimilhança é o algoritmo
EM de Saerens, Latinne e Decaestecker.)*

**Em uma frase, para a mentoria:**

> *"Os 300 rótulos não treinam o modelo — eles **calibram o índice**. A matriz de confusão
> medida neles permite corrigir, dia a dia, a proporção de notícias positivas, neutras e
> negativas estimada nas ~205 mil notícias. É um conjunto pequeno que ajusta a escala de uma
> série de oito anos."*

**Duas condições, que devemos declarar:**

1. O gabarito precisa ser representativo da população, ou reponderável. **Já é**: a amostra é
   estratificada e a coluna `peso_amostral` existe. O relatório de validação já reporta as duas
   acurácias — bruta (58,00%) e reponderada à população (57,65%).
2. A matriz de confusão precisa ser razoavelmente estável ao longo do período. Isso é
   **testável** com o próprio gabarito, particionando por subperíodo — e é exatamente o
   diagnóstico de *concept drift* já planejado.

## 2.6 Uso 5 — quantificar a atenuação e **defender** o resultado

Existe um resultado clássico de econometria: quando um regressor é medido com erro, o
coeficiente estimado é **atenuado em direção a zero**. Como o ISM é construído a partir de um
classificador com κ = 0,371, ele **é** um regressor com erro de medida.

**Consequência prática e favorável:** o efeito do sentimento sobre a volatilidade que
estimamos é um **piso**, não uma estimativa central. O efeito verdadeiro é maior.

> Isso muda a frase que levamos à banca. Em vez de:
> *"o sentimento explica pouco da volatilidade"*
> passa a ser:
> *"o sentimento explica ao menos X da volatilidade, e essa é uma estimativa conservadora,
> porque o índice é medido com erro conhecido e quantificado — κ = 0,371 contra gabarito
> humano."*
>
> **Sem o gabarito, essa defesa não existe**, porque não haveria como saber que há erro de
> medida, nem de que tamanho.

## 2.7 Uso 6 — o rótulo de relevância é uma segunda base, e mais viável

A coluna `Relevante_PETR4` (111 Sim / 189 Não) é **binária**, e classificação binária com 300
exemplos é substancialmente mais tratável do que três classes.

Ela sustenta uma pergunta que nenhum trabalho da literatura faz: **os índices de sentimento
agregam todas as notícias coletadas, sem filtrar relevância por ativo.** Se 63% das notícias
que entram no índice não dizem respeito à empresa, o índice mede ruído de mercado, não sinal do
ativo — e isso pode explicar parte da fraqueza do sinal de direção.

> ⚠️ **Reporto um resultado negativo, para não vender o que não se sustenta.** Testei se as
> notícias marcadas como relevantes produzem mais movimento de preço em D+1. **Não produzem**:
> mediana de 1,01% para as relevantes contra 1,05% para as não relevantes, Mann-Whitney
> p = 0,76.
>
> Há duas ressalvas que atenuam, mas não anulam, esse resultado: **(a)** as "não relevantes"
> também passaram pelo filtro da nossa taxonomia de 152 termos — são notícias de
> petróleo e energia, não ruído aleatório, de modo que o contraste é conservador; e **(b)** D+1
> é uma janela curta, e a literatura sugere que o efeito do sentimento é lento (o estudo
> comparável com a PRIO3 só encontra efeito após 5 dias). **O teste precisa ser refeito em
> horizontes mais longos antes de se concluir qualquer coisa.**

## 2.8 Uso 7 — o gabarito como contribuição publicável

Não existe, em português, um equivalente ao *Financial PhraseBank*. Santos **não publicou** os
503 textos rotulados. Teles e Figueiredo (2025), diante da ausência de um conjunto brasileiro,
recorreram a três conjuntos **em inglês**.

Um conjunto-ouro público de sentimento financeiro em português, **ancorado em um ativo real**,
com dupla anotação e α reportado, seria citável independentemente dos resultados de previsão. É
o tipo de contribuição que sobrevive à dissertação.

## 2.9 Um achado que emergiu ao responder esta pergunta

Ao cruzar o gabarito com os preços, apareceu um sinal que aponta para o eixo certo da
dissertação. Magnitude do retorno em D+1, só nas notícias relevantes:

| Tom (humano) | n | Mediana \|retorno\| | Média \|retorno\| |
|---|---|---|---|
| **Negativo** | 38 | **1,12%** | **1,64%** |
| Neutro | 25 | 1,26% | 1,36% |
| **Positivo** | 48 | **0,88%** | **1,26%** |

Notícias de tom negativo são seguidas de movimentos **~30% maiores em média** que as de tom
positivo.

> ⚠️ **Kruskal-Wallis p = 0,443 — não é significativo com n = 111.** Não é resultado, é
> **indício**, e como tal deve ser apresentado.
>
> Mas é um indício na direção certa, e coerente com tudo o mais: **o sentimento não diz para
> onde o preço vai (direção ≈ acaso, 46,7%), mas parece dizer o quanto ele se move
> (volatilidade).** É exatamente a tese central da dissertação, agora visível já no dado bruto
> do gabarito, antes de qualquer modelagem.

---

# Parte 3 — como conduzir a conversa em 10/08

## 3.1 Roteiro sugerido

**1. Começar reconhecendo o que procede (2 min).**
Não abrir defendendo. Abrir com: *"o senhor tem razão, e eu testei — a coluna de direção
esperada acertou 46,7%, abaixo do acaso. E os dados de confiança do anotador mostram que o
déficit está exatamente onde o senhor apontou."* Isso estabelece que a crítica foi levada a
sério e verificada, não contornada.

**2. Mostrar que a rubrica já separa as tarefas (3 min).**
As quatro colunas, e o quadro de qual competência cada uma exige. A objeção se aplica
integralmente a **uma** delas.

**3. Apresentar o problema maior, que ninguém tinha levantado (3 min).**
Anotador único → sem α → os 58% não medem o modelo. É mais grave que a questão da
qualificação, e é nossa a responsabilidade de ter identificado.

**4. Propor a solução de custo baixo (4 min).**
Especialista como **árbitro de ~55 casos**, não anotador de 300. Coluna de direção **aposentada
e substituída pelo mercado**. Expertise codificada no guia.

**5. Responder à segunda pergunta com o Uso 4 (5 min).**
*"Não é base de treino, é instrumento de calibração"* — e a correção de viés do ISM, que faz
300 rótulos agirem sobre 8 anos de série.

**6. Fechar com o indício de volatilidade (2 min).**
O dado bruto do gabarito já aponta para o eixo da dissertação. Com a ressalva de que não é
significativo ainda.

## 3.2 Perguntas prováveis e respostas preparadas

| Pergunta | Resposta |
|---|---|
| *"Mas 46,7% não prova que um especialista faria melhor?"* | Não prova nem o contrário — o IC vai de 33,7% a 60,0%, n = 60. O que o teste mostra é que a pergunta **é testável**. Proponho aplicar o mesmo teste a quem quer que faça a próxima rodada, inclusive um especialista. Se ele bater 60%, temos a resposta. |
| *"Então a rotulagem foi perdida?"* | Não. Os 300 itens já produziram a única medição do modelo no nosso domínio (0,58 / κ 0,371), o diagnóstico da classe neutra, e a matriz que permite corrigir o viés do ISM. O que precisa ser refeito é a **segunda anotação**, não a primeira. |
| *"Por que não rotular mais, já que 300 é pouco?"* | Porque o problema não é volume, é **estrutura**. Dobrar para 600 com anotador único mantém o mesmo defeito e dobra o custo. A prioridade é a **segunda opinião** em 100–150 dos que já existem. |
| *"E se eu discordar de que 300 bastam?"* | Para **treinar**, 300 não bastam — e é por isso que não treinamos com eles. Para **medir** com IC aceitável, 300 bastam: o IC 95% da acurácia fica em torno de ±5,6 pontos, o que é suficiente para separar modelos que diferem em 10 pontos ou mais. |
| *"Como sei que os 300 representam as 205 mil?"* | Amostragem estratificada por categoria e ano, com `peso_amostral` calculado. Reportamos as duas acurácias — bruta e reponderada à população — e elas diferem em apenas 0,35 ponto, o que indica que a estratificação está funcionando. |

## 3.3 Uma ressalva a levar espontaneamente

A rodada 2 (400 manchetes, 33 rotuladas antes da suspensão) usou **amostragem por incerteza** —
o guia declara: *"são os casos em que o modelo tem MENOS confiança (onde ele mais erra)"*.

Isso é correto para **melhorar** o modelo, mas **inválido para medi-lo**: a amostra é
deliberadamente enviesada para os casos difíceis, e misturá-la com a rodada 1 rebaixaria
artificialmente a acurácia estimada.

> **As duas rodadas têm funções diferentes e não podem ser somadas.**
> Rodada 1 (300, estratificada, com pesos) → **medir**.
> Rodada 2 (400, por incerteza) → **treinar/melhorar**.
>
> Levar isso espontaneamente demonstra domínio do próprio instrumento — e evita um erro que
> seria difícil de desfazer depois.

---

## Referências citadas

ARTSTEIN, R.; POESIO, M. Inter-coder agreement for computational linguistics. **Computational
Linguistics**, v. 34, n. 4, p. 555-596, 2008.

BŁOCH, A.; SANTANA, C.; AMANTINO, M. Os jesuítas e a Era do Algoritmo: uma introdução à análise
de sentimentos da correspondência colonial ultramarina portuguesa. **Estudos Ibero-Americanos**,
v. 52, n. 1, p. 1-23, 2026.

BOLLEN, J.; MAO, H.; ZENG, X. Twitter mood predicts the stock market. **Journal of
Computational Science**, v. 2, n. 1, p. 1-8, 2011.

HOVY, E.; LAVID, J. Towards a 'science' of corpus annotation: a new methodological challenge for
corpus linguistics. **International Journal of Translation**, v. 22, n. 1, p. 13-36, 2010.

KRIPPENDORFF, K. **Content analysis**: an introduction to its methodology. 4. ed. Thousand Oaks:
Sage, 2018.

SANTOS, L. L. **FinBERT-PT-BR**: análise de sentimentos de textos em português referentes ao
mercado financeiro. 2022. TCC (Engenharia de Computação) — Escola Politécnica, USP, São Paulo.

SANTOS, L. L.; BIANCHI, R. A. C.; COSTA, A. H. R. FinBERT-PT-BR: análise de sentimentos de
textos em português do mercado financeiro. In: **BWAIF**, 2., 2023. Anais [...]. Porto Alegre:
SBC, 2023. p. 144-155.

TELES, L. E. P.; FIGUEIREDO, C. M. S. Comparing LLMs for sentiment analysis in financial market
news. **arXiv:2510.15929**, 2025.

---

## Anexo — arquivos desta análise

| Arquivo | Conteúdo |
|---|---|
| `src/sentimento/validar_rotulos_contra_mercado.py` | Script auditável dos três testes |
| `Mestrado_PETR4/validacao_rotulos_contra_mercado.json` | Resultados numéricos |
| `Mestrado_PETR4/conjunto_ouro/conjunto_ouro_para_rotular.xlsx` | Gabarito rodada 1 (300, estratificada) |
| `Mestrado_PETR4/conjunto_ouro/rotulagem_ampliacao.xlsx` | Rodada 2 (400 por incerteza, 33 feitas) |
| `Mestrado_PETR4/conjunto_ouro/relatorio_validacao_ouro.txt` | Acurácia, κ e matriz de confusão |
