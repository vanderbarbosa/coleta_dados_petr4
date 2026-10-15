# Mentoria de 12 de outubro de 2026 — Prof. Julio

> **Nota de data:** esta mentoria foi marcada para 12/10/2026; a preparação
> ficou pronta em 15/10/2026, três dias depois. Se a reunião foi adiada, está
> tudo aqui; se já aconteceu de outra forma, me avise para eu ajustar.

## O que foi pedido

1. Determinar o número médio de ações por investidor (ações em circulação ÷
   número de investidores).
2. Calcular o valor médio investido por investidor (número médio de ações ×
   preço da ação).
3. Comparando duas técnicas, que valor percentual de ganho justificaria o
   esforço computacional extra de uma delas?
4. O artigo precisa ter a ver com o objetivo da pesquisa — verificar se a
   análise de sentimento afeta a volatilidade e a direção do preço — e testar
   um encoder do Google para séries temporais, comparando com o Prophet.

## Itens 1 e 2 — feitos, com fórmula, nada hardcoded

Planilha: **`01_Valor_Medio_Investido.xlsx`**, duas abas (Top 10 em destaque,
e os 62 papéis já mapeados na pesquisa). Fonte: o Formulário de Referência da
CVM (acionistas e ações em circulação) × o preço de fechamento mais recente
coletado (15/09/2026).

| Papel | Ações por investidor | Valor médio investido |
|---|---|---|
| BBAS3 (menor) | 1.833 | R$ 40.390 |
| PETR4 | 6.665 | R$ 336.098 |
| BPAC11 (maior) | 28.719 | R$ 1.728.873 |

**Leia com cuidado — é média, não o investidor típico.** A distribuição é
muito desigual: poucos acionistas grandes (controlador, fundos, BNDESPAR)
puxam a média para cima. O BPAC11 e a SBSP3 saem com mais de R$1,5 milhão de
"valor médio investido" porque têm poucos acionistas e um controlador grande
— não porque o investidor pessoa física típico tenha isso investido. Esta
base não tem como calcular a mediana (só temos o total de ações e o total de
acionistas, não a distribuição entre eles) — se precisar da mediana de
verdade, teria que vir do arquivo `posicao_acionaria` da CVM, que lista os
grandes acionistas nominalmente, e ainda assim não cobre o pequeno investidor
individual.

**Seis papéis não entraram no item 2** por não termos preço coletado:
EMBR3, BRFS3, MRFG3, ELET3 (virou AXIA3), AZUL4, GOLL4. Aparecem na aba
"Todos os papéis" só com o item 1.

## Item 3 — quanto de ganho justifica o esforço computacional

**Não existe um número universal — mas existe um piso que vale para ESTA
pesquisa, calculado a partir do nosso próprio tamanho de amostra.**

A resposta tem duas camadas, e a primeira manda na segunda:

### Camada 1 — o piso estatístico (sem isto, nem vale comparar)

Com os tamanhos de teste que usamos (579 a 653 pregões), o erro-padrão de uma
taxa de acerto é de ~2,0 pontos percentuais. Isso dá um **intervalo de 95% de
±~4 pontos percentuais** — ou seja: **uma diferença menor que ~4 pontos de
acurácia (ou ~0,04 de AUC) não pode nem ser distinguida de acaso**, com esse
tamanho de amostra. Não é opinião — é a mesma conta que já apareceu nos
nossos próprios resultados: o intervalo de confiança do ganho de AUC do texto
sobre o mercado deu [-0,032, +0,015] (`CVM/dados/diagnostico_ml.json`), bem
nessa faixa.

**Regra prática:** se a técnica mais cara ganhar menos que ~3-4 pontos
percentuais (de acurácia ou AUC) sobre a mais simples, **não dá nem para
afirmar que o ganho é real** — gastar GPU, Colab, ou qualquer esforço a mais
nisso é apostar, não é evidência.

### Camada 2 — o piso de relevância (depois de passar na camada 1)

Se o ganho passar no teste estatístico (idealmente McNemar, corrigido por
Bonferroni quando houver mais de uma comparação — ver
`comparativo-top10-ibovespa` na memória do projeto), a pergunta vira "esse
ganho é grande o bastante para merecer virar resultado da dissertação?" Aqui
não há fórmula, mas há um padrão que esta própria pesquisa já usa:

- O ganho que a dissertação já considerou digno de reportar na direção foi de
  **+2,4 pontos percentuais** (Tabela 4.3, Data Fusion contra a classe
  majoritária).
- Para volatilidade, a meta registrada foi **R²-OS acima de +5%**
  (ver [[como-ler-os-numeros]]).

**Recomendação concreta para decidir entre as duas técnicas:** só valorize o
esforço computacional extra se o ganho (a) passar no McNemar com correção
para o número de comparações feitas, **e** (b) for de pelo menos ~3 pontos
percentuais de acurácia/AUC, ou +5% de R²-OS na volatilidade — a mesma régua
que a pesquisa já usa em todo lugar, para não inventar um critério novo só
para esta comparação.

**Como isto se aplica à pesquisa até agora:** é exatamente por isso que o
embedding de 768 dimensões da CVM (técnica mais cara, precisa de GPU) **não
se justificou** — ele não passou no McNemar e às vezes até piorou (ver
`escopo-e-ml-de-verdade` na memória do projeto). A técnica simples (preço +
rótulo do FinBERT) já está no mesmo patamar, de graça.

## Item 4 — o artigo e o objetivo da pesquisa

Isso não é uma tarefa de cálculo — é um lembrete de escopo, e vale confirmar
onde a pesquisa já está, com números:

| A notícia/comunicado afeta... | O que já medimos | Onde |
|---|---|---|
| **Volatilidade (medição, não previsão)** | Fato Relevante: **+18,2%**; nas 10 principais ações, confirmado o nulo de direção mas não remedido a volatilidade | Artigo 1 |
| **Volatilidade (como previsão)** | O texto acrescenta no máximo +0,6 ponto de R²-OS sobre um modelo que já ganha +6,9% só com preço | `pesquisa_com_cvm.json` |
| **Direção** | NENHUMA combinação (PETR4 ou as 10 principais) bate o palpite fixo, mesmo corrigindo por 60 testes | `comparativo-top10-ibovespa` |

**Conclusão para levar ao orientador:** a pesquisa já responde exatamente a
pergunta que o item 4 pede — e a resposta, honesta, é que o sentimento
**move o tamanho do movimento** (volatilidade, medida, não prevista) mas
**não move a direção**, em nenhum desenho testado até agora. Qualquer artigo
escolhido deve se ancorar nessa distinção, não tentar escondê-la.

## O encoder do Google para séries temporais — preciso de uma decisão sua

Antes de rodar, duas coisas que só você (ou o professor) pode decidir, porque
são escolhas de desenho, não fatos a verificar:

1. **Qual encoder do Google, exatamente?** O mais conhecido hoje para
   previsão de séries temporais é o **TimesFM** (Time Series Foundation
   Model, Google Research) — é esse que o professor quer? Existem outros
   (Temporal Fusion Transformer não é do Google; TiDE é do Google também).
2. **Sobre o Prophet:** procurei no projeto inteiro e **nunca foi testado
   aqui antes** — não achei nenhum script, resultado ou nota de memória. Pelo
   jeito que a frase foi escrita ("comparar com o que já testamos (Prophet)")
   pode ser que o professor tenha pensado em outra reunião, ou queira que eu
   rode os DOIS agora (TimesFM e Prophet) como novo experimento, para
   comparar entre si. Qual dos dois é o caso?

Assim que confirmar, eu monto o experimento: qual alvo (direção, volatilidade
ou preço), qual papel, e deixo claro de antemão — como sempre nesta pesquisa
— o que espero encontrar antes de rodar.

## Arquivos desta pasta

| Arquivo | O que é |
|---|---|
| `01_Valor_Medio_Investido.xlsx` | itens 1 e 2, Top 10 e os 62 papéis |
| `_gerar_planilha_valor_investido.py` | gerador da planilha acima |
