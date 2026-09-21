# 02 · Błoch, Santana e Amantino (2026) — Máquina de Comitê

> **O único dos sete trabalhos citantes que efetivamente EXECUTOU o FinBERT-PT-BR.**
> O domínio é História Digital, não finanças — mas o método é o mais diretamente reaproveitável
> de toda a lista, e a caracterização que fazem do modelo **explica a nossa matriz de confusão**.
>
> Fonte: leitura integral do PDF (23 páginas), obtido em acesso aberto na PUCRS.

---

## 1. Ficha bibliográfica

| Campo | Valor |
|---|---|
| **Referência** | BŁOCH, A.; SANTANA, C.; AMANTINO, M. Os jesuítas e a Era do Algoritmo: uma introdução à análise de sentimentos da correspondência colonial ultramarina portuguesa. **Estudos Ibero-Americanos**, Porto Alegre, v. 52, n. 1, p. 1-23, jan.-dez. 2026. |
| **DOI** | 10.15448/1980-864x.2026.1.46315 |
| **Veículo** | Estudos Ibero-Americanos (PUCRS) — **acesso aberto** |
| **Data** | 13/04/2026 |
| **Área** | História Digital / Humanidades Digitais |
| **Código-fonte** | ❌ Não publicado |
| **Arquivo local** | `../_bloch2026.pdf` · `../_bloch2026.txt` |

---

## 2. Objetivo e pergunta de pesquisa

Investigar o impacto das tecnologias digitais no ofício do historiador, tomando como caso a
**presença da Companhia de Jesus nos registros do Arquivo Histórico Ultramarino entre 1642 e
1822**. A análise de sentimentos entra como *exemplo* de algoritmo que ilustra o quanto **a
qualidade dos dados condiciona o desempenho da IA**.

**Pergunta operacional:** como o sentimento expresso na correspondência colonial sobre os
jesuítas varia conforme (a) o tipo documental e (b) o período histórico?

**Enquadramento metodológico declarado.** Os autores se apoiam em Schmidt (2016) para dizer que
historiadores digitais não devem se restringir a usar algoritmos para validar afirmações, mas
ser *"usuários criativos desses algoritmos"*. E reconhecem, com Barnes (2013), que
*"o big data nem sempre oferece informações historicamente relevantes e, muitas vezes, apenas
produz ruído"*.

---

## 3. Dados

| Item | Valor |
|---|---|
| **Fonte** | Arquivo Histórico Ultramarino — Brasil e África Ocidental |
| **Período** | 1642–1822 (180 anos) |
| **Total de documentos classificados** | **1.467** |
| **Tipologia adotada** | Dias (2012) e Bellotto (2004) |

Categorização documental — a mesma peça pode entrar em mais de uma categoria:

| Grupo | N | Tipos documentais |
|---|---|---|
| **Bottom-up** (ascendente) | 410 | representação, requerimento, carta, parecer, consulta — enviados por vassalos, súditos e autoridades subalternas |
| **Top-down** (descendente) | 444 | alvará, aviso, carta régia, decreto, ofício régio, provisão régia — emanam do monarca |
| **Horizontal** (informativa) | 613 | provisão, certidão, despacho, ofício, auto, mandado, escrito, informação |

> 💡 **Transponível para nós.** A ideia de **estratificar o corpus por tipo de documento antes
> de agregar o sentimento** é análoga à nossa taxonomia de 7 categorias de notícia
> (`src/comum/taxonomia.py`) — e à nossa ablação por categoria. Eles mostram que o sentimento
> agregado esconde dinâmicas que só aparecem na estratificação. É argumento de apoio para o
> nosso gap **G10** (filtro de relevância) e para a ablação de categorias que já temos.

---

## 4. Tecnologias, bibliotecas e encoders

| Componente | Papel |
|---|---|
| **`lucas-leme/FinBERT-PT-BR`** (SANTOS; BIANCHI; COSTA, 2023) | Membro 1 do comitê — modelo **treinado em base financeira** |
| **`pysentimiento`** (PÉREZ et al., 2021) | Membro 2 — modelo **de base geral em português** |
| **Moderador por voto** | Agrega as saídas parciais dos membros |

**Sobre o `pysentimiento`.** É um *toolkit* multilíngue de PLN social. O modelo de sentimento em
português é `pysentimiento/bertweet-pt-sentiment` (**46.843 downloads/mês**, verificado em
04/08/2026), construído sobre o **BERTabaporu**. Uso:

```python
from pysentimiento import create_analyzer
analisador = create_analyzer(task="sentiment", lang="pt")
analisador.predict("A Petrobras anunciou dividendos extraordinários")
# → AnalyzerOutput(output=POS, probas={POS: 0.9, NEU: 0.07, NEG: 0.03})
```

Rótulos: `POS`, `NEU`, `NEG` — **ordem diferente da do FinBERT-PT-BR**, atenção ao mapear.

---

## 5. Método passo a passo

### 5.1 A escolha da abordagem autossupervisionada

Os autores classificam as abordagens de análise de sentimento em três categorias — **baseada em
regras**, **aprendizado de máquina** (supervisionado, semissupervisionado, não supervisionado e
autossupervisionado) e **híbrida** — e justificam a escolha:

> *"Neste trabalho, optamos por utilizar uma abordagem autossupervisionada, tendo em vista que
> os textos na nossa base não estão classificados, **para evitar o trabalho de criar uma base de
> treino classificada**."*

> 💡 **Esta frase é, em uma linha, o argumento que precisamos para a mentoria de 10/08.** Diante
> da ausência de gabarito, eles não pararam a pesquisa — **mudaram de paradigma**. É exatamente
> o que propomos com os gaps G3 (MLM, *self-supervised*) e G7 (comitê, sem rótulo).

### 5.2 A Máquina de Comitê

```
              ┌────────────────────┐
   texto  ───▶│  FinBERT-PT-BR     │──▶ sentimento parcial 1  ┐
         │    └────────────────────┘                          │
         │    ┌────────────────────┐                          ├──▶ MODERADOR ──▶ saída
         └───▶│  pysentimiento (PT)│──▶ sentimento parcial 2  ┘   (voto simples)
              └────────────────────┘
```

**Critério de seleção dos membros, literal:**

> *"Para que a abordagem de comitê produza resultados promissores, é essencial a seleção de
> modelos de análise de sentimentos que tenham **características distintas e complementares**.
> Os modelos que selecionamos se enquadram nesse requisito, pois um deles — treinado em uma base
> financeira (Santos; Bianchi; Costa, 2023) — mostra resultados **fortemente influenciados pela
> presença de termos negativos ou positivos**, enquanto o segundo — treinado em uma base mais
> geral com conteúdo em português (Pérez et al., 2021) — **analisa mais o contexto em que os
> termos aparecem**."*

**Moderação:** voto simples — a classe identificada pela maioria dos modelos. Com dois membros,
isso implica uma regra de desempate que o artigo não detalha explicitamente (ver Seção 8.4).

### 5.3 Validação

> *"Em conjunto, os dois modelos apresentam uma boa capacidade de identificação de sentimentos,
> o que pode ser verificado nos experimentos em que comparamos, **para um subconjunto de textos,
> a classificação do comitê com a de um historiador**."*

**É o mesmo desenho do nosso conjunto-ouro:** classificação automática × especialista humano,
num subconjunto. A diferença é que eles validaram um **comitê** e nós validamos um **modelo
isolado**. O artigo não publica as métricas dessa validação — é uma fragilidade (ver Seção 8.3).

---

## 6. Resultados

Os resultados são apresentados de forma **qualitativa e gráfica** (Figuras 6 a 9), sem tabela de
métricas. Os achados substantivos:

| Achado | Detalhe |
|---|---|
| **Predominância de neutro e negativo** | Documentos neutros chegam a ~4.000; negativos, a ~175 |
| **Explicação do neutro** | *"a natureza burocrática intrínseca à correspondência ultramarina impõe uma estrutura formal, caracterizada pela ausência de linguagem cotidiana e vulgar"* |
| ***Bottom-up*** | Tom predominantemente neutro, mas com negativos **persistentes** ao longo dos séculos XVII e XVIII — críticas contínuas aos jesuítas, antes e depois da expulsão |
| **Pico documental** | 1720–1760: produção **mais que dobrou** (15,82 documentos/ano contra média histórica de ~9) |
| **Ápice absoluto** | **1759–1761** (expulsão dos jesuítas): média de **99,33 documentos/ano**; só em 1760, 109 documentos |

> 💡 **Paralelo direto com o nosso trabalho.** Eles cruzam o volume e o sentimento documental
> com **eventos históricos datados** (bula papal de 1639, rebeliões de 1640, expulsão de 1759) —
> exatamente o que fazemos com a guerra da Ucrânia e o que Santos fez com os oito eventos
> econômicos. **A validação qualitativa contra eventos é um padrão consolidado da área**, e vale
> citar os três trabalhos juntos ao justificar a nossa.

---

## 7. Código

❌ **Não publicado.** Não há repositório declarado no artigo.

O comitê, porém, é trivial de reconstruir a partir da descrição. Script gravado em
[`../_codigos/comite_sentimento_petr4.py`](../_codigos/comite_sentimento_petr4.py), já adaptado
ao nosso conjunto-ouro. Núcleo:

```python
from transformers import pipeline
from pysentimiento import create_analyzer

finbert = pipeline("text-classification", model="lucas-leme/FinBERT-PT-BR",
                   truncation=True, max_length=512)
geral = create_analyzer(task="sentiment", lang="pt")

def comite(texto, regra="abstencao"):
    """Combina um modelo léxico-financeiro e um modelo contextual geral."""
    a = MAPA_FINBERT[finbert(texto)[0]["label"]]     # POSITIVE/NEGATIVE/NEUTRAL
    b = MAPA_PYSENT[geral.predict(texto).output]     # POS/NEU/NEG
    if a == b:
        return a
    if regra == "abstencao":
        return "Neutral"        # discordância → neutro (conservador)
    ...
```

Três regras de moderação implementadas no script, para comparação:

| Regra | Comportamento na discordância |
|---|---|
| `voto` | Com 2 membros, empate → devolve o do FinBERT (modelo de domínio) |
| `abstencao` | Devolve **Neutro** — conservadora, tende a corrigir o excesso de extremos |
| `media_prob` | Soma as distribuições de probabilidade e devolve o *argmax* |

---

## 8. Leitura crítica

### 8.1 O achado mais valioso: por que o nosso κ é 0,371

A caracterização dos autores é um **achado independente que explica o nosso resultado**:

> FinBERT-PT-BR → *"fortemente influenciado pela **presença de termos** negativos ou positivos"*
> pysentimiento → *"analisa mais o **contexto** em que os termos aparecem"*

Confrontando com a nossa matriz de confusão (`conjunto_ouro/relatorio_validacao_ouro.txt`):

| Humano ↓ / Modelo → | Negative | Neutral | Positive | Total |
|---|---|---|---|---|
| **Negative** | 60 | 11 | 9 | 80 |
| **Neutral** | **32** | 66 | **26** | 124 |
| **Positive** | 21 | 27 | 48 | 96 |

**A classe Neutra é a mais confundida: 58 dos 124 casos neutros (46,8%) foram empurrados para
os extremos.** É precisamente a assinatura de um modelo dominado por léxico. Uma manchete
neutra que contenha termos carregados — *"Petrobras avalia corte de investimentos"*,
*"Petrobras estuda venda de refinaria"* — é puxada para o extremo mesmo quando o enunciado é
puramente informativo.

> **Passamos de "o modelo acerta 58%" para "o modelo acerta 58% porque opera por léxico e não
> por contexto, o que degrada especialmente a classe neutra — e há caracterização independente
> na literatura que sustenta esse diagnóstico".** A segunda formulação é infinitamente mais
> forte em banca.

### 8.2 O que aproveitar

| # | O que | Como | Gap |
|---|---|---|---|
| 1 | **A caracterização léxico × contexto** | Citar como explicação da nossa matriz de confusão | **G2** |
| 2 | **A arquitetura de comitê** | FinBERT-PT-BR + pysentimiento sobre o conjunto-ouro, 3 regras de moderação | **G7** |
| 3 | **A justificativa do paradigma autossupervisionado** | Argumento de por que avançar sem rótulo é escolha metodológica e não improviso | G3, G5 |
| 4 | **A estratificação por tipo documental** | Apoio à nossa ablação por categoria e ao filtro de relevância | **G10** |
| 5 | **A validação contra especialista num subconjunto** | Precedente metodológico citável para o conjunto-ouro | G5 |
| 6 | **A discussão sobre qualidade dos dados condicionar a IA** | Citação elegante, de fora da área, para justificar o gabarito humano | — |
| 7 | **A validação qualitativa contra eventos datados** | Somar a Santos como padrão consolidado da área | — |

### 8.3 Fragilidades do trabalho (e o que aprendemos com elas)

| Fragilidade | Lição para nós |
|---|---|
| **Não publica métricas da validação** — diz que comparou com um historiador, mas não informa acurácia, kappa nem tamanho do subconjunto | **Não repetir.** Nosso relatório de validação informa n, acurácia bruta, reponderada, kappa e matriz completa. Isso é um ponto forte nosso — vale destacá-lo. |
| **Não publica o código** | Publicar o nosso. |
| **Não detalha a regra de desempate** do voto com 2 membros | Implementar e **comparar as três regras**, o que transforma uma omissão deles numa contribuição nossa. |
| **Usa um modelo financeiro em texto do século XVIII** | Transferência de domínio ainda mais extrema que a nossa. Reforça que o problema de G2 é geral, e não idiossincrasia nossa. |

### 8.4 Melhoria que podemos entregar sobre o trabalho deles

Eles usaram comitê **sem medir o ganho** do comitê contra os membros isolados. Nós podemos
fazer o que faltou:

| Configuração | Métrica a reportar |
|---|---|
| FinBERT-PT-BR sozinho | acurácia, F1-macro, κ (já temos: 58,0% / 57,63% / 0,371) |
| pysentimiento sozinho | a medir |
| Comitê — voto | a medir |
| Comitê — abstenção | a medir |
| Comitê — média de probabilidades | a medir |

Com *bootstrap* e IC de 80% (script `reconstrucao_santos_bootstrap.py`), isso vira uma tabela
com significância — algo que **nem Błoch et al. nem Santos fizeram para comitês**.

**Hipótese testável a registrar antes de rodar:** se o diagnóstico léxico × contexto estiver
correto, a regra de **abstenção** deve produzir o maior ganho na classe **Neutra**, que é
justamente a mais confundida. Se isso se confirmar, temos um resultado explicativo, e não
apenas uma melhoria numérica.

### 8.5 Como citar

> *"A caracterização do FinBERT-PT-BR como modelo cuja saída é 'fortemente influenciada pela
> presença de termos negativos ou positivos', em contraste com modelos de propósito geral que
> 'analisam mais o contexto em que os termos aparecem' (BŁOCH; SANTANA; AMANTINO, 2026), é
> consistente com o padrão observado na nossa matriz de confusão, em que 46,8% das manchetes
> anotadas como neutras foram classificadas em uma das classes extremas."*

---

## Anexo — quadro-resumo

| | |
|---|---|
| **Objetivo** | Análise de sentimento de correspondência colonial portuguesa (1642–1822) |
| **Corpus** | 1.467 documentos do Arquivo Histórico Ultramarino, em 3 tipologias |
| **Encoders** | **FinBERT-PT-BR** + **pysentimiento (PT)** |
| **Arquitetura** | Máquina de Comitê com moderador por voto |
| **Paradigma** | **Autossupervisionado** — escolhido para evitar criar base rotulada |
| **Validação** | Comitê × historiador, em subconjunto (sem métricas publicadas) |
| **Resultados** | Qualitativos: predominância neutro/negativo; pico documental em 1759–61 (99,33 doc/ano) |
| **Código** | ❌ Não publicado · reconstrução em `../_codigos/comite_sentimento_petr4.py` |
| **Valor para nós** | **Máximo** — explica a nossa matriz de confusão e entrega o método do gap G7 |
