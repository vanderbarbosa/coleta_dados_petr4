# FinBERT (Yang, Uy e Huang, 2020) — o maior corpus, publicado em periódico A1

## 1. Ficha bibliográfica

| Campo | Conteúdo |
|---|---|
| **Referência (preprint)** | YANG, Y.; UY, M. C. S.; HUANG, A. **FinBERT: a pretrained language model for financial communications.** arXiv:2006.08097, 2020. |
| **Referência (periódico)** | HUANG, A. H.; WANG, H.; YANG, Y. **FinBERT: a large language model for extracting information from financial text.** *Contemporary Accounting Research*, v. 40, n. 2, 2023. DOI 10.1111/1911-3846.12832. |
| **Instituição** | HKUST — Hong Kong University of Science and Technology |
| **Repositório** | `github.com/yya518/FinBERT` |
| **Downloads** | `yiyanghkust/finbert-tone`: **704.839 por mês** · 223 curtidas (13/08/2026) |
| **Código** | Público, com quatro modelos no Hugging Face |

**Por que a publicação em periódico importa.** A *Contemporary Accounting Research* é um dos
periódicos de maior prestígio da área contábil. Enquanto o FinBERT de Araci permanece como
*preprint* de dissertação, este passou por revisão por pares em veículo de primeira linha. Para a
dissertação, isso o torna a referência preferível quando se quer sustentar afirmações sobre o
desempenho de codificadores financeiros.

## 2. Corpus de pré-treinamento — 4,9 bilhões de tokens

| Fonte | Volume |
|---|---|
| Relatórios corporativos (10-K e 10-Q) | 2,5 bilhões de tokens |
| Transcrições de teleconferências de resultados | 1,3 bilhão de tokens |
| Relatórios de analistas | 1,1 bilhão de tokens |
| **Total** | **4,9 bilhões de tokens** |

Compare-se com o corpus de adaptação de Santos et al. (2023): 1,4 milhão de **textos**. Ainda que
as unidades sejam distintas — tokens contra textos —, a ordem de grandeza da diferença é de
milhares de vezes. **Este é o dado mais eloquente do levantamento sobre por que o recurso em
inglês é mais forte que o em português: não é o idioma, é o volume.**

## 3. A família de quatro modelos

| Modelo | Identificador | Tarefa | Supervisão |
|---|---|---|---|
| Pré-treinado | `yiyanghkust/finbert-pretrain` | Base, sem cabeça de tarefa | — |
| Tom/sentimento | `yiyanghkust/finbert-tone` | Positivo, negativo, neutro | **10.000 sentenças anotadas** de relatórios de analistas |
| ESG | `yiyanghkust/finbert-esg` | Classificação ambiental, social e de governança | 2.000 sentenças [via resumo] |
| Declarações prospectivas | `yiyanghkust/finbert-fls` | Identifica afirmações sobre o futuro | não declarado no repositório |

**O modelo `finbert-fls` merece atenção.** Ele separa o que é **relato do passado** do que é
**projeção de futuro**. Aplicado ao nosso corpus, permitiria testar a hipótese de que apenas as
notícias prospectivas carregam sinal preditivo — o que é economicamente plausível e dialoga
diretamente com o achado da Seção 4.l, segundo o qual o nosso sentimento acompanha o mercado em
vez de antecedê-lo. É a ideia mais promissora que este levantamento produziu.

## 4. Resultados declarados [via resumo]

- **Sentimento:** supera de forma substancial o dicionário de Loughran e McDonald e também *naïve
  Bayes*, máquinas de vetores de suporte, florestas aleatórias, redes convolucionais e LSTM.
- **Mecanismo do ganho:** o artigo atribui a vantagem à capacidade de identificar sentenças
  positivas ou negativas que os demais algoritmos **rotulam erroneamente como neutras**, graças ao
  uso de informação contextual.
- **ESG:** 89,5% de acurácia na rotulagem de discussões ambientais, sociais e de governança.

**O segundo item é diretamente relevante para nós.** A Seção 4 da dissertação documentou que 90%
dos erros do FinBERT-PT-BR envolvem a classe Neutra. Huang, Wang e Yang (2023) identificam
exatamente esse ponto como o **diferencial** do modelo bem treinado. Ou seja: o nosso modo de falha
predominante é precisamente aquilo que a versão em inglês, com corpus mil vezes maior, resolve.
Trata-se de uma evidência externa forte de que o problema do neutro é de **volume de dados**, e
não de arquitetura ou de idioma.

## 5. Ligação com a nossa pesquisa

Este trabalho fornece três elementos que a dissertação pode usar de imediato:

1. **Uma referência revisada por pares** para afirmações sobre codificadores financeiros, em
   substituição ao *preprint* de Araci.
2. **A explicação externa para o nosso erro na classe Neutra**, transformando o que hoje é um
   diagnóstico interno em achado alinhado à literatura.
3. **O modelo `finbert-fls`**, que abre uma linha experimental nova e barata.

## 6. Leitura crítica

**O que aproveitar:** os três elementos acima, e a comparação de volume de corpus como argumento
central do capítulo de limitações.

**O que não aproveitar:** o modelo é treinado em inglês sobre documentos corporativos dos Estados
Unidos. Não se aplica ao nosso corpus sem tradução, e a tradução automática introduz um erro de
medida que precisaria ser quantificado antes de qualquer conclusão.

**O que verificar antes de citar:** o artigo da *Contemporary Accounting Research* não pôde ser
lido na íntegra (HTTP 403). Os números de 89,5% e as comparações com Loughran-McDonald vêm de
fontes secundárias e **devem ser conferidos no texto original** antes de entrarem na dissertação.
