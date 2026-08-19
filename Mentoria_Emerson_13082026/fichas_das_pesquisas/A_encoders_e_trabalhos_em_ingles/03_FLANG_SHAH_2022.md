# FLANG e FLUE (Shah et al., 2022) — o sucessor técnico e o primeiro *benchmark*

## 1. Ficha bibliográfica

| Campo | Conteúdo |
|---|---|
| **Referência** | SHAH, R. S. et al. **When FLUE meets FLANG: benchmarks and large pretrained language model for financial domain.** In: PROCEEDINGS OF THE 2022 CONFERENCE ON EMPIRICAL METHODS IN NATURAL LANGUAGE PROCESSING (EMNLP), 2022. arXiv:2211.00083. |
| **Instituições** | Georgia Tech e Stanford |
| **Veículo** | **EMNLP 2022** — conferência de primeira linha em processamento de linguagem natural |
| **Repositório** | `github.com/SALT-NLP/FLANG` |

## 2. As duas contribuições

### FLUE — o *benchmark*

**FLUE é o primeiro conjunto aberto e abrangente de referências para compreensão de linguagem
financeira em inglês.** Reúne cinco tarefas:

1. Análise de sentimento financeiro
2. Classificação de manchetes de notícias
3. Reconhecimento de entidades nomeadas
4. Detecção de limites estruturais
5. Resposta a perguntas

**Por que isso importa para nós.** O português **não possui** equivalente ao FLUE. Não há um
conjunto de tarefas padronizado sobre o qual comparar codificadores financeiros em português. Essa
ausência é, ela própria, uma lacuna de pesquisa de porte — e uma que poderia ser preenchida por um
trabalho de doutorado, na linha que o Vanderlei já cogita.

### FLANG — o modelo

Diferentemente dos dois FinBERT, o FLANG não parte do BERT: **baseia-se no ELECTRA**. E introduz
uma técnica que merece atenção:

- **Mascaramento preferencial** — em vez de ocultar palavras ao acaso, como faz o BERT, o FLANG
  ocultapreferencialmente **palavras-chave e expressões do domínio financeiro**.
- Emprega ainda objetivo de fronteira de constituinte (*span boundary objective*) e objetivo de
  preenchimento (*in-filling*).

**Resultado declarado:** o FLANG supera os modelos da literatura anterior em variadas tarefas.

## 3. A ligação direta com o nosso experimento G3

Esta é a parte relevante para a dissertação.

O nosso experimento G3 aplicou **modelagem de linguagem mascarada padrão** — mascaramento
**aleatório** a 15%, conforme Devlin et al. (2019) — sobre as 205.697 notícias. O resultado foi:
perplexidade reduzida em 49%, mas **F1 degradado em 0,056 ($p = 0{,}022$)**, com esquecimento
catastrófico concentrado na classe Positiva.

Shah et al. (2022) sustentam que **o mascaramento aleatório é subótimo para o domínio financeiro**,
precisamente porque desperdiça a maior parte do orçamento de treinamento em palavras irrelevantes.
A alternativa que propõem — mascarar preferencialmente os termos financeiros — é uma explicação
plausível para o nosso fracasso, e converte o G3 de "resultado negativo" em "resultado negativo com
hipótese explicativa identificada na literatura".

**Isso deve entrar na Seção 4.i da dissertação**, tanto na discussão do resultado quanto nos
trabalhos futuros: a adaptação de domínio pode ter falhado não por ser inadequada, mas por ter sido
executada com a técnica de mascaramento errada.

## 4. Leitura crítica

**O que aproveitar:**
- A hipótese do mascaramento preferencial como explicação para o G3 — barata de escrever, valiosa
  de ter.
- A constatação de que não existe FLUE em português, como lacuna a declarar.

**O que não aproveitar:**
- O modelo em si é em inglês e baseado em ELECTRA. Reimplementar mascaramento preferencial em
  português exigiria construir a lista de termos do domínio (que já temos, parcialmente: a taxonomia
  de 152 termos) e refazer o pré-treinamento — trabalho de porte, com o agravante de que o ambiente
  local está com o PyTorch quebrado.

**Nível de esforço para testar a hipótese:** alto. Exigiria Colab com GPU e uma nova rodada de
adaptação. **Não é prioridade** diante das ações de custo baixo identificadas na ficha 04. Registre-se
como trabalho futuro fundamentado.
