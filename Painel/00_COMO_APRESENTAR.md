# O painel — o que é e como mostrar

**Link:** https://claude.ai/code/artifact/43e567a3-c66a-4044-83e4-851e8db2f0a0

Abre em qualquer navegador, em qualquer máquina. Não precisa instalar nada, não
precisa do projeto baixado. **Teste o link antes da reunião.**

---

## O que o painel é

Uma página onde você **escolhe um comunicado real** entregue à CVM e vê, passo a
passo, o que aconteceu com o preço da ação no pregão seguinte.

Não é ilustração nem exemplo inventado. São **23 casos reais**, extraídos dos
11.161 que estudamos, com data, hora oficial, texto do comunicado e o que o preço
efetivamente fez.

---

## A estrutura da página, de cima para baixo

**1. Seletor de casos.** Botões agrupados por aquilo que cada caso demonstra. São
cinco grupos, e dois deles são incomuns de propósito:

| Grupo | Por que está ali |
|---|---|
| Choques grandes | o que todo mundo espera ver |
| Petrobras | o ativo da dissertação |
| **Nada aconteceu** | **são a maioria dos casos, e ninguém mostra** |
| O programa acertou | quando a nossa classificação funciona |
| **O programa errou** | **quando ela falha** |

**2. O cartão do caso.** Empresa, categoria, o texto literal do comunicado e a
hora oficial de entrega.

**3. A linha do tempo.** Três faixas: o pregão anterior fechando às 17h, a faixa
escura em que a bolsa está fechada e a notícia chega, e a abertura do dia
seguinte. **É a parte que explica por que só usamos notícia da noite.**

**4. As três réguas**, cada uma com gráfico:

- **O preço sacudiu?** Cinco barras cinza são os pregões da semana anterior, a
  barra clara é o dia da reação, a linha pontilhada é a média da semana.
- **Quanta gente negociou?** Mesma leitura, com volume.
- **Para que lado foi?** O caminho do preço: fechamento da véspera → abertura →
  fechamento. Dá para ver o salto da abertura separado do resto do dia.

**5. O que o programa disse.** Selo verde, vermelho ou cinza, com a explicação.

**6. O panorama.** Os números do conjunto inteiro: a barra de quantos mexeram, o
efeito médio contra o controle, a comparação entre as duas gavetas da CVM, e o
acerto do classificador.

---

## O roteiro de apresentação — sete minutos

### Minuto 1 — abra e explique o que é

> *"Este painel percorre um comunicado real entregue à CVM e mostra o que
> aconteceu com o preço no pregão seguinte. São 23 casos reais, escolhidos dos
> 11.161 que estudei."*

### Minuto 2 — clique em **OIBR3 07/11/2025**

É o caso-escola. Enquanto carrega:

> *"A Oi entregou este comunicado às 19h31, com a bolsa fechada — 'Manifestação
> sobre a Continuidade do Grupo Oi'. Ninguém pôde negociar até a abertura do dia
> seguinte."*

Aponte a linha do tempo, depois os números:

> *"No pregão seguinte a ação caiu 44%, com volatilidade quase cinco vezes a média
> da semana anterior e volume quase seis vezes."*

### Minuto 3 — **aqui está o truque da apresentação**

Clique em qualquer caso do grupo **"Nada aconteceu"**.

> *"Agora olhem este. Também é Fato Relevante. Também foi divulgado à noite. E o
> preço não fez nada — ficou até mais parado que uma semana comum."*

Pausa. Então:

> *"E este é o caso típico, não a exceção. **59% dos comunicados não movem o
> preço.** É o achado central do artigo."*

### Minuto 4 — clique em **PETR4 16/04/2021**, no grupo "O programa errou"

> *"Mostro também onde falhamos. Aqui o texto era sobre renúncia de conselheiro, o
> programa classificou como negativo, e a ação subiu 5,6%. Casos assim existem em
> quantidade parecida com os acertos."*

**Mostrar o erro por conta própria vale mais do que qualquer defesa.** Tira do
avaliador a chance de descobrir sozinho.

### Minutos 5 a 7 — desça até o panorama

Três tabelas, nesta ordem:

1. **A barra colorida** — quantos mexeram, quantos não
2. **"A lei acerta?"** — o Fato Relevante mexe 2,6 vezes mais que o Comunicado ao
   Mercado. *"A hierarquia da norma aparece no preço."*
3. **"O nosso programa acerta a direção?"** — e a ressalva: só funciona no Fato
   Relevante; no Comunicado, ganha zero.

---

## Três perguntas que podem vir, e as respostas

**"Esses casos foram escolhidos a dedo?"**
> "Foram escolhidos para cobrir o espectro, e isso inclui os casos em que nada
> aconteceu e aqueles em que o modelo errou. Os números do panorama, no fim da
> página, são do conjunto inteiro — 11.161 eventos."

**"A queda de 44% foi causada pelo comunicado?"**
> "Não posso afirmar causa. Posso afirmar que o comunicado saiu com o mercado
> fechado e que o movimento veio na abertura seguinte, e que comparei com 105.896
> pregões sem comunicado. É o mais perto de um experimento que se consegue com
> dado de mercado."

**"E a PETR4 de março de 2020, que caiu 35%?"**
> "Essa é justamente a que **não** se deve usar como exemplo. Foi a semana do
> início da pandemia e da guerra de preços do petróleo. O painel mostra o que
> aconteceu, não garante a causa — e nesse caso a causa foi outra."

---

## Antes de entrar na sala

- [ ] Abrir o link e conferir que carrega
- [ ] Clicar em dois ou três casos para garantir que a página responde
- [ ] Deixar **OIBR3 07/11/2025** já selecionado, para não procurar na hora
- [ ] Ter o `05_PAINEL_RESULTADOS.xlsx` aberto numa aba, como reserva caso a
      internet falhe
