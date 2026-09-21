# O que fazer com este levantamento — diagnóstico e plano

## 1. A pergunta que o Prof. Emerson quer ver respondida

*"Abrir o leque para tentar encontrar algo que nos dê uma melhor performance."*

A resposta, depois do levantamento, é que **existe desempenho melhor documentado na literatura, e
as razões pelas quais não o alcançamos são identificáveis e, em parte, corrigíveis**. Não se trata
de trocar de codificador.

## 2. Trocar de codificador resolveria?

**Não, e agora há evidência quantitativa disso.**

| Modelo | Situação | Macro-F1 |
|---|---|---|
| FinBERT inglês, sem ajuste | manchetes setoriais | **0,555** |
| **FinBERT-PT-BR, sem ajuste** | **manchetes da PETR4** | **0,579** |
| FinBERT inglês, ajustado com 1.500 manchetes | manchetes setoriais | 0,707 |

O modelo em inglês — treinado sobre 4,9 bilhões de tokens, com 4,5 milhões de downloads mensais e
publicação em periódico de primeira linha — obtém **0,555** quando aplicado sem ajuste a manchetes
de um setor específico. O nosso obtém **0,579**, ligeiramente superior.

**Conclusão: o teto de 0,58 não é um problema do português, nem do FinBERT-PT-BR, nem de escolha de
arquitetura. É o comportamento esperado de qualquer codificador financeiro aplicado sem supervisão
a um subdomínio.** Isso encerra, com evidência externa, a linha de investigação que já havíamos
encerrado com evidência interna após nove experimentos.

**O que a mesma tabela mostra que funciona:** 1.500 manchetes rotuladas do subdomínio levam de
0,555 a 0,707. O nosso G3 usou cerca de 350 e piorou. A explicação mais simples é o **volume**.

## 3. Por que eles superam o HAR e nós não

Quatro diferenças, em ordem de impacto provável:

| # | Diferença | Deles | Nosso | Corrigível? |
|---|---|---|---|---|
| 1 | Medida de volatilidade | Variância realizada de 5 min | Parkinson diário | Depende de dados intradiários |
| 2 | Número de ativos | 404 | 1 | **Sim** |
| 3 | Método de combinação | Subconjuntos completos, LASSO adaptativo | MQO com um regressor | **Sim, imediato** |
| 4 | Fontes de sinal | Notícias, Google Trends, Wikipédia, Twitter | Notícias | Parcialmente |

**A leitura honesta:** o nosso resultado negativo é compatível com **falta de poder estatístico** —
variável dependente ruidosa, um único ativo, combinação ingênua. Isso **não autoriza** afirmar que o
sentimento supera o HAR na PETR4. Autoriza reformular a limitação com precisão, e indicar o que
seria necessário para decidir a questão.

## 4. O que o levantamento CONFIRMA da nossa dissertação

Nem tudo cobra; parte valida.

| Nosso achado | Confirmação externa |
|---|---|
| **Efeito de cauda** (Pearson acha, Spearman não) | Halousková e Lyócsa (2025): maior ganho **nos dias de variação extrema**, 14,99% contra 12,74% na média, sobre 404 ativos |
| **Coeficiente do sentimento ≈ $-0{,}29$** | Mino e Williamson (2025): $-0{,}2275$ ($p = 0{,}0016$) no S&P 500, com o mesmo GARCH(1,1)-*t* |
| **90% dos erros envolvem a classe Neutra** | Huang, Wang e Yang (2023) apontam a resolução do neutro como o diferencial do modelo bem treinado |
| **LLM perde para o codificador** (G6: 0,480 contra 0,580) | Classificação de risco ESG em 10-K: FinBERT com 83% supera todos os LLMs testados |
| **Degradação por transferência de domínio** (0,760 para 0,580) | FinBERT inglês cai a 0,555 em manchetes setoriais |

**Cinco achados da dissertação com respaldo externo independente.** Isso deve ser dito no Capítulo 4
e no Capítulo 5, porque converte resultados que hoje parecem idiossincráticos em resultados
alinhados ao estado da arte internacional.

## 5. O que a nossa dissertação faz que os comparáveis NÃO fazem

Este ponto é para a defesa, e é legítimo.

| Nossa prática | Mino e Williamson (2025) | Halousková e Lyócsa (2025) |
|---|---|---|
| Avaliação fora da amostra com Diebold-Mariano | **Não fazem** — só ajuste dentro da amostra | Fazem (Model Confidence Set) |
| Estratificação por regime de volatilidade | **Não fazem** — declaram como limitação | Fazem |
| Validação contra padrão humano | Não fazem | Não fazem |
| Auditoria do artefato (caixa alta, sigmoide) | Não fazem | Não fazem |
| Relato de resultados negativos | Não há | Não há |

**Mino e Williamson (2025) param exatamente onde nós continuamos.** Se tivéssemos parado ali,
teríamos relatado sucesso — coeficiente significativo, sinal correto — e estaríamos errados, porque
a avaliação fora da amostra mostra que aquilo não se converte em ganho preditivo.

**Isso é uma contribuição metodológica, e deve ser enunciada como tal:** a dissertação avalia com
mais rigor do que trabalhos publicados na mesma linha, e é por isso que encontra um limite que eles
não encontram.

## 6. Plano de ação proposto

### Custo muito baixo — dias, sem dados novos

1. **Incorporar as cinco validações externas** da seção 4 ao Capítulo 4 e ao Capítulo 5.
2. **Reformular a limitação da Seção 4.k**: de "o sentimento não supera o HAR" para "não foi
   possível detectar superação com medida diária sobre um único ativo, ao passo que a literatura a
   detecta com medida intradiária sobre 404 ativos".
3. **Reformular a conclusão do G3** (Seção 4.i): de "a adaptação de domínio degrada" para "a
   adaptação com 350 exemplos degrada, ao passo que 1.500 exemplos rotulados elevam o F1 de 0,555
   para 0,707 na literatura" — e acrescentar a hipótese do mascaramento preferencial de
   Shah et al. (2022).
4. **Registrar a armadilha metodológica dos 95%** como contribuição crítica à leitura da
   literatura.

### Custo baixo — dias, só código

5. **Implementar regressão de subconjuntos completos e LASSO adaptativo** sobre os dados atuais.
   Testa a hipótese 3 da seção 3 e roda localmente.
6. **Testar o filtro de prospectividade**: refazer o índice apenas com notícias que projetam o
   futuro. Testa diretamente a explicação dada ao colapso entre $P_0$ e $P_1$, e segue a lição de
   que mexer no corpus funciona.

### Custo médio — semanas

7. **Replicar o *pipeline* para cinco a dez ativos líquidos da B3.** Atende à orientação do Prof.
   Emerson, ataca a limitação de poder estatístico e permite testar a predição de que o efeito de
   cauda cresce com a volatilidade do ativo.

### A decidir com os orientadores

8. **Retomar a rotulagem, com protocolo diferente.** Não ampliar volume — ampliar **redundância**:
   reanotar as mesmas 300 manchetes com 3 anotadores de formação em finanças, calcular concordância
   e publicar subconjuntos por nível de acordo, à maneira de Malo et al. (2014).

   **Ressalva obrigatória:** o teste de teto mostrou que classificador perfeito eleva a direção em
   apenas 1,2 ponto percentual. Refazer a rotulagem **não vai melhorar a previsão**. O valor é
   outro: permitir afirmar com rigor se o desempenho de 0,58 é limitação do modelo ou ruído do
   anotador — indeterminação que hoje é uma fragilidade real da dissertação.

## 7. Recomendação de prioridade

Se houver tempo para apenas três coisas: os itens **1 a 4** (escrita, custo quase nulo, ganho
argumentativo alto), o item **6** (prospectividade — a hipótese mais promissora do levantamento) e
o item **7** (múltiplos ativos — o que o Prof. Emerson pediu e o que mais aumenta o poder
estatístico).
