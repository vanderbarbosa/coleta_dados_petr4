# Demonstração prática do uso dos rótulos + situação do código-fonte

**Mestrando:** Vanderlei Barbosa da Silva · **Elaborado em:** 08/08/2026
**Complementa:** `RESPOSTA_DUAS_PERGUNTAS_EMERSON.md`

> **Duas coisas pedidas**
> 1. Mostrar **na prática**, e não em tese, como as notícias rotuladas seriam usadas.
> 2. Obter o **código-fonte** da pesquisa de referência — direto do autor, ou pelos trabalhos
>    que a citam/usam.

---

# Parte 1 — A demonstração prática, rodada nos seus dados

Dois scripts novos, executáveis e auditáveis:

| Script | O que faz |
|---|---|
| [`src/sentimento/calibrar_ism_com_gabarito.py`](../src/sentimento/calibrar_ism_com_gabarito.py) | Usa os 300 rótulos para corrigir o ISM das 205.697 notícias |
| [`src/sentimento/avaliar_ganho_calibracao.py`](../src/sentimento/avaliar_ganho_calibracao.py) | Testa se a correção **de fato** melhora a previsão |

Saídas: `Mestrado_PETR4/ism_calibrado_petr4.csv`, `calibracao_ism_relatorio.json`,
`ganho_calibracao_ism.json`.

## 1.1 O que os 300 rótulos revelam

Matriz de confusão, **ponderada à população** pelo `peso_amostral` — que soma exatamente
205.697, confirmando que a amostra estratificada representa o corpus inteiro:

**P(o modelo classifica como… | a manchete é de fato…)**

| verdadeiro ↓ / predito → | Negative | Neutral | Positive |
|---|---|---|---|
| **Negative** | **0,824** | 0,127 | 0,049 |
| **Neutral** | **0,327** | 0,568 | 0,104 |
| **Positive** | **0,336** | 0,363 | **0,301** |

Duas leituras que mudam o entendimento do pipeline:

1. **De cada 100 manchetes verdadeiramente neutras, 33 são classificadas como negativas.**
2. **Pior: de cada 100 manchetes verdadeiramente positivas, apenas 30 são classificadas como
   positivas — e 34 vão para "negativa".** O modelo erra o positivo mais do que acerta, e o erro
   vai desproporcionalmente para o extremo oposto.

> Isto não é ruído aleatório. É um **viés sistemático e direcionado**: o modelo puxa tudo para
> "negativo". E age nas 205.697 notícias, todos os dias, durante oito anos.

## 1.2 O efeito no período inteiro

| | ISM bruto | ISM calibrado | Diferença |
|---|---|---|---|
| Proporção **Negative** | 48,5% | **31,2%** | −17,3 pp |
| Proporção **Neutral** | 37,5% | **41,9%** | +4,4 pp |
| Proporção **Positive** | 14,0% | **26,8%** | +12,9 pp |
| **ISM** | **−0,3450** | **−0,0439** | **+0,3011** |

**O viés é de 87% do valor bruto.**

E, com *bootstrap* de 2.000 reamostras sobre o gabarito para propagar o erro amostral da matriz:

> **IC 95% do ISM calibrado: [−0,2250 ; +0,1857]**
> O ISM bruto (−0,3450) **está fora do intervalo** → o viés é estatisticamente distinguível de
> zero.

**Tradução para a banca:** o corpus de notícias sobre a Petrobras **não é predominantemente
negativo**. Ele é aproximadamente neutro. A negatividade que aparece no nosso índice é
**artefato do classificador**, não propriedade dos dados.

## 1.3 A série mensal corrigida

96 meses, de 2018-01 a 2025-12, média de 2.143 notícias/mês:

| | Valor |
|---|---|
| Deslocamento médio | **+0,3184** |
| Deslocamento mínimo / máximo | +0,0778 / +0,6411 |
| **Meses em que a correção troca o SINAL do ISM** | **49 de 96 (51%)** |
| Correlação entre as duas séries | **0,9730** |
| Desvio-padrão bruto → calibrado | 0,0645 → **0,1670** (2,6×) |

Amostra concreta:

| mês | notícias | ISM bruto | ISM calibrado | Δ |
|---|---|---|---|---|
| 2018-01 | 1.396 | **−0,2794** | **+0,1030** | +0,3824 |
| 2018-05 | 2.267 | −0,4883 | −0,3964 | +0,0919 |
| 2025-10 | 3.203 | **−0,3197** | **+0,0008** | +0,3205 |
| 2025-12 | 2.456 | **−0,2952** | **+0,1026** | +0,3978 |

> **Em janeiro de 2018 e em dezembro de 2025, o índice bruto diz "pessimismo" e o calibrado diz
> "otimismo".** Em metade da série, a conclusão qualitativa se inverte.

**Isto é, concretamente, a resposta ao Prof. Emerson:** 300 manchetes rotuladas por uma pessoa
recalibram a escala de uma série de oito anos e 205 mil notícias. Não treinam nada — **aferem**.

## 1.4 O teste honesto: isso melhora a previsão?

Seria fácil parar no item anterior. Mas a pergunta seguinte — a que o Prof. Emerson faria — é se
a correção **melhora o resultado da dissertação**. Testei:

| Alvo | ISM bruto | ISM calibrado | Melhorou? |
|---|---|---|---|
| Volatilidade do mês **seguinte** | r = −0,118 (p = 0,26) | r = −0,051 (p = 0,62) | **Não** |
| Volatilidade **contemporânea** | **r = −0,309 (p = 0,002)** | r = −0,273 (p = 0,007) | **Não** |
| Retorno do mês seguinte | r = +0,036 (p = 0,73) | r = −0,002 (p = 0,99) | **Não** |

> ### **A calibração NÃO melhora o poder preditivo.** Reporto isso porque esconder seria pior.

**E a explicação é o achado de verdade.** A correlação entre a série bruta e a calibrada é
**0,973** — elas têm quase a mesma forma; o que muda é o **nível**. E correlação é **invariante
a deslocamento de nível**: ele é absorvido pelo intercepto de qualquer regressão.

Portanto, com precisão:

| A calibração **conserta** | A calibração **não conserta** |
|---|---|
| A **leitura** do índice — o corpus é neutro, não negativo | O **poder preditivo** em modelo linear |
| O **sinal** do ISM em 49 de 96 meses | A correlação com volatilidade ou retorno |
| Qualquer **regra de limiar** ("ISM < −0,30 → regime de estresse") | Os coeficientes de regressão que usam só variação |
| A **classificação de regimes** (otimista/pessimista) | |
| A **validação qualitativa contra eventos econômicos** | |

**Onde buscar melhora de índice, então:** no **classificador**, não na agregação. É o comitê de
modelos (G7) e a adaptação de domínio (G3). Corrigir a agregação conserta a interpretação;
melhorar o classificador é o que muda o resultado.

## 1.5 Dois achados laterais que valem a mentoria

**(a) A relação contemporânea é significativa; a preditiva não é.**
r = −0,309 com p = 0,002 no mesmo mês, contra r = −0,118 e p = 0,26 no mês seguinte. Sentimento
negativo **coincide** com volatilidade alta, mas não a **antecipa** — pelo menos não em janela
mensal. É coerente com tudo o mais que encontramos, e é um resultado honesto a reportar.

**(b) A calibração precisa ser mensal, não diária.**
A inversão da matriz amplifica ruído quando a contagem é pequena. Mediana de 73 notícias/dia,
mas 82 dias (2,8%) têm menos de 10. Recomendação implementada no script: **calibrar na agregação
mensal** (ou janela móvel de 21 pregões), manter o ISM diário bruto como variável de curto
prazo, e declarar a escolha no capítulo de método.

## 1.6 As três ressalvas que precisam acompanhar esse resultado

Com um efeito desta magnitude, omitir as limitações seria indefensável:

1. **A "verdade" do gabarito é o julgamento de uma pessoa.** A matriz de confusão mede a
   discordância entre o modelo e **um anotador não calibrado**, não entre o modelo e a verdade.
   Com dupla anotação e α de Krippendorff, a matriz mudaria — e a correção também.
2. **A linha "Positive" tem só 96 itens.** É a linha com maior erro amostral, e é justamente a
   que produz a maior correção. O IC de 95% do ISM calibrado é largo — de −0,225 a +0,186 —
   e reflete isso.
3. **O ACC pressupõe matriz estável no período.** Se houver *concept drift* (gap G4), a matriz
   de 2018 não vale para 2026. Isso é testável particionando o gabarito por subperíodo — mas com
   ~33 itens por ano, o poder é baixo. O caminho viável é dividir em dois blocos.

---

# Parte 2 — O código-fonte

## 2.1 O código do FinBERT-PT-BR não existe publicamente. Confirmado.

Verifiquei por quatro caminhos independentes, em 08/08/2026:

| Onde | Resultado |
|---|---|
| GitHub pessoal `lucas-leme` (22 repositórios) | ❌ Nenhum repositório de PLN financeiro |
| Organização `turing-usp` (81 repositórios) | ❌ Nenhum repositório do FinBERT-PT-BR |
| Repositório HuggingFace (10 arquivos) | ❌ Só pesos e *tokenizer*; sem `training_args.bin`, sem dados |
| Busca de código no GitHub (autenticada) | 92 resultados — **todos de terceiros que consomem o modelo**, nenhum que o treine |

**Não há como replicar o treinamento exatamente.** Mas a busca rendeu bem mais do que a
ausência: rendeu **cinco pipelines de terceiros que usam o modelo em produção** e — o mais
valioso — **hiperparâmetros reais de quem já fez ajuste fino a partir dele**.

## 2.2 O achado mais útil: hiperparâmetros de um ajuste fino bem-sucedido

Existem modelos derivados do FinBERT-PT-BR publicados no HuggingFace, com `base_model:
lucas-leme/FinBERT-PT-BR`. O *model card* de `Asthem/FinBERT-PT-BR-news`, gerado
automaticamente pelo `Trainer`, expõe a configuração usada:

```
learning_rate:     2e-05
train_batch_size:  8
eval_batch_size:   8
seed:              42
optimizer:         AdamW  (betas 0.9/0.999, eps 1e-08)
lr_scheduler_type: linear
num_epochs:        10          ← dez épocas

Transformers 4.53.0 · PyTorch 2.6.0+cu124 · Datasets 3.6.0 · Tokenizers 0.21.2
```

> 💡 **Corroboração independente do nosso diagnóstico.** Um terceiro que ajustou com sucesso a
> partir do FinBERT-PT-BR usou **10 épocas**; Santos usou **11**. **Nós usamos 3.** É evidência
> externa — vinda de quem executou, não de quem escreveu o artigo — de que o nosso protocolo de
> comparação de encoders estava subtreinado.

Outros derivados: `Asthem/FinBERT-PT-BR-wiki`, `-geofis`, variantes `_tax0.45`, e
`g-assismoraes/FinBERT-PT-BR-geofis`.

## 2.3 Os cinco pipelines de terceiros coletados

Baixados em [`_codigos/terceiros/`](_codigos/terceiros/):

| Repositório | O que tem de aproveitável | Valor |
|---|---|---|
| **`IagoErrera/scrap-fin`** | `create_index.py` — constrói índice de sentimento com FinBERT-PT-BR. **Faz *chunking* com sobreposição** (400 tokens, 50 de overlap) e voto majoritário entre trechos, para processar **texto completo** e não só manchete. Coleta com **Scrapy** (Estadão, Folha, G1) — mesma arquitetura de Santos. | **Alto** |
| **`JoseOtavioJunqueira/Analise-de-Sentimento-IC`** (ICMC/USP, *push* em 20/07/2026) | Pipeline completo: coleta → sentimento → decisão → *backtest* → Streamlit. Decisão por **Random Forest / Regressão Logística / Q-Learning**. Documentação em `COMO_DECIDE_COMPRA_VENDA.md` e template de `RELATORIO_EXPERIMENTOS.md`. | **Alto** |
| **`MarcoAfB/soybean-price-forecasting-lstm-llm`** | Previsão de preço de *commodity* com LSTM + LLM. Estrutura `src/acquisition/news/` com *scrapers* por portal e `docs/reproduction.md`. Estruturalmente próximo do nosso. | Médio |
| **`ajdavidl/corpus-atas-copom`** | Corpus das atas do COPOM + `scripts/sentiment-analysis.py`. **Conecta com Reichert e Perlin (2025)**, que validaram o dicionário deles sobre comunicados do COPOM. | Médio |
| **`jp-alves/prio3-sentiment`** (já coletado antes) | Pipeline PRIO3 completo — o mais parecido com o nosso. | **Alto** |

### O que aproveitar de imediato

**(a) `chunking` com sobreposição — do `scrap-fin`.** Resolve o problema de classificar textos
longos com um modelo de 512 tokens, e é exatamente o que falta para o gap **G9** (granularidade:
manchete × subtítulo × corpo):

```python
def get_chuncks(text, max_tokens=400, overlap=50):
    tokens = tokenizer.tokenize(text)
    chunks, start = [], 0
    while start < len(tokens):
        chunk = tokens[start:start + max_tokens]
        chunks.append(tokenizer.convert_tokens_to_string(chunk))
        start = start + max_tokens - overlap
    return chunks
```

**(b) A confirmação de que ninguém treina o modelo.** O projeto do ICMC/USP declara
explicitamente, em `DADOS_E_TREINAMENTO.md`:

> *"Hoje a IA de sentimento é o FinBERT-PT-BR (Santos 2022): um modelo **já treinado** (…) No
> código nós **não treinamos** esse modelo — só **usamos** ele para classificar (inferência).
> Ou seja: **não há etapa de 'treinar a IA' no pipeline atual.**"*

> Isso é confirmação de terceiro, independente, de que **o uso padrão do FinBERT-PT-BR é como
> modelo de prateleira**. Reforça o argumento da lacuna: nós somos dos poucos que **validam** o
> modelo contra gabarito humano em vez de simplesmente aplicá-lo.

**(c) O template de relatório de experimentos** do projeto do ICMC — com seed, versões, métricas
financeiras (Sharpe, *max drawdown*, *win rate*) e comparação com Selic e ETF passivo. É um bom
padrão de reprodutibilidade para adotarmos.

## 2.4 O que fazer com isso

| # | Ação | Baseia-se em |
|---|---|---|
| 1 | **Refazer a comparação de encoders com 10–11 épocas**, não 3 | Asthem (10) + Santos (11) |
| 2 | Implementar ***chunking* com sobreposição** para testar granularidade | `scrap-fin` |
| 3 | Adotar o **template de relatório de experimentos** | ICMC/USP |
| 4 | Considerar **atas do COPOM** como variável de controle macro-textual | `corpus-atas-copom` + Reichert e Perlin |
| 5 | Ao reportar, escrever *"implementação própria do protocolo descrito por Santos"* — **nunca** "replicação" | Código original inexistente |

## 2.5 Uma tentativa que vale a pena e é barata

O código não está público, mas **o autor está acessível**. Lucas Leme Santos mantém perfil
público no LinkedIn e no GitHub, e o e-mail institucional consta do artigo
(`lucaslssantos99@usp.br`). A orientadora, Profa. Anna Helena Reali Costa, é professora da Poli
e igualmente acessível.

> Um e-mail cordial pedindo (a) o código de treinamento e (b) os 503 textos rotulados custa
> quinze minutos. A pior resposta possível é o silêncio, que é o estado atual. E se vier
> resposta positiva, **resolve de uma vez os gaps G3 e G5**.
>
> Sugiro mencionar que a dissertação usa o modelo, que já rendeu uma validação independente
> contra gabarito humano — o que é informação que interessa ao próprio autor.

---

## Anexo — arquivos gerados nesta rodada

| Arquivo | Conteúdo |
|---|---|
| `src/sentimento/calibrar_ism_com_gabarito.py` | Calibração do ISM por ACC + *bootstrap* |
| `src/sentimento/avaliar_ganho_calibracao.py` | Teste honesto do ganho preditivo |
| `Mestrado_PETR4/ism_calibrado_petr4.csv` | Série mensal, bruta e calibrada, 96 meses |
| `Mestrado_PETR4/calibracao_ism_relatorio.json` | Matriz de confusão, proporções, IC |
| `Mestrado_PETR4/ganho_calibracao_ism.json` | Correlações bruto × calibrado |
| `orientacoes/_codigos/terceiros/` | 15 arquivos de 4 repositórios de terceiros |

**Referência do método:** FORMAN, G. Quantifying counts and costs via classification.
**Data Mining and Knowledge Discovery**, v. 17, n. 2, p. 164-206, 2008.
