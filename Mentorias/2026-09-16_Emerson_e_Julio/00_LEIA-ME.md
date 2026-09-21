# Mentoria de 16 de setembro de 2026 — Profs. Emerson e Julio

## O que foi pedido

Uma **engenharia reversa**: temos a publicação e temos o que o preço fez depois.
Confrontar as duas coisas.

Com um recorte importante, sugerido pelos professores: **usar só o que foi
publicado após o fechamento do pregão**, e olhar o **pregão seguinte**.

Em duas rodadas — primeiro com a classificação que já vem na publicação, depois
com a nossa.

E uma sugestão do Prof. Emerson: comparar a volatilidade do dia seguinte com a
**média da semana anterior**, e não com uma média distante.

## O que foi feito, em linguagem simples

### O recorte da noite é a melhor parte do desenho

> É como trancar todo mundo fora do estádio, pôr a notícia no telão, e só então
> abrir os portões. **Ninguém pôde reagir antes.**

Para fazer esse recorte precisávamos da hora exata. **A CVM não publica a hora nos
dados abertos** — e recuperá-la virou a principal contribuição da pesquisa. Como
isso foi feito está em `Artigos/Artigo_1_O_Relogio_da_CVM/03_COMO_OBTIVEMOS_A_HORA.md`.

### A sugestão do Prof. Emerson estava certa, e é mais exigente

Volatilidade é grudenta: depois de uma semana agitada vem outra agitada. **Bater a
média da própria semana anterior é muito mais difícil** que bater uma média de
cem dias atrás.

### Uma correção que evitou dois números errados

A razão entre o dia e a média da semana **já vale mais que 1,00 sem evento
algum** — porque um dia pode ser cinco vezes mais agitado que a média, mas nunca
cinco vezes menos. Medimos esse piso em 105.896 pregões sem comunicado.

Sem esse controle teríamos anunciado **+21,9%** de volatilidade e **+44,6%** de
volume. Os números corretos são **+9,6%** e **+16,5%**.

## Os resultados

| Pergunta | Resposta |
|---|---|
| A publicação move o preço? | **Sim — o risco, não a direção** |
| Move sempre? | **Não. 59% não movem nada** |
| Dá para saber o lado? | Só com a nossa leitura, e só no Fato Relevante |
| A lei acerta? | **Sim. Fato Relevante mexe 2,6× mais que Comunicado** |

## A terceira parte: combinar as duas fontes

Esta parte ficou por último porque o desenho teve de ser refeito.

**A primeira regra falhou.** Somar o sentimento da noite — mais positivas que
negativas, aposta em alta — **previu BAIXA em 99% das noites.** O programa que lê
os textos enxerga quase tudo como negativo, então o saldo nunca vira positivo.
Uma regra que diz a mesma coisa 99% das vezes não é previsão, é constante.

**A correção** foi mudar a pergunta: em vez de *"teve notícia boa?"*, perguntar
*"esta noite foi pior que o habitual desta ação?"*, comparando com a média dos 60
pregões anteriores. Isso sozinho valeu seis pontos percentuais.

**O resultado**, nos 1.163 dias em que as duas fontes existem:

| Fonte | Acertou | Quem não lê nada | Vale? |
|---|---|---|---|
| só o jornal | 53,8% | 52,1% | **sim** |
| só o comunicado da CVM | 50,8% | 51,7% | não |
| os dois juntos | 53,7% | 52,1% | **sim** |

**O jornal prevê melhor que o comunicado oficial.** O motivo é de linguagem: o
comunicado descreve o fato em termos administrativos; o jornal já traz a
interpretação.

**E nas 402 noites de Fato Relevante:**

| Fonte | Acertou | Quem não lê nada | Ganho |
|---|---|---|---|
| só o jornal | 54,7% | 51,4% | +3,31 pts (não passa) |
| **os dois juntos** | **55,2%** | 51,5% | **+3,73 pts** ✓ |

**É o melhor resultado de direção de toda a pesquisa.** E o jornal sozinho não
passa no teste — só a combinação passa.

### A hipótese que isso levanta, e que NÃO está provada

Se o comunicado não prevê nada sozinho mas a combinação só funciona nas noites em
que ele existe, então ele **não serve como texto — serve como aviso de qual noite
importa**.

| Tipo de noite | Vantagem do jornal |
|---|---|
| sem comunicado | +0,25 pontos |
| com Comunicado ao Mercado | +0,91 pontos |
| com Fato Relevante | **+3,31 pontos** |

A vantagem triplica. **Mas a diferença não passa no teste** (p = 0,57). Seriam
precisas ~15.200 noites; temos 393. **Fica como hipótese, não como achado.**

---

## O que está nesta pasta

| Arquivo | O que é |
|---|---|
| `01_Plano.docx` | o plano, escrito antes de rodar, com as previsões registradas |
| `02_Resultados.docx` | as duas primeiras partes: impacto e classificação |
| `03_Explicacao_completa.docx` | tudo em linguagem comum, do zero |
| `04_Painel_resultados.xlsx` | planilha das duas primeiras partes |
| **`05_Combinar_as_fontes_COMPLETO.docx`** | **a terceira parte, detalhada** |
| **`06_Combinar_as_fontes_RESUMIDO.docx`** | **a terceira parte, em cinco minutos** |
| **`07_Combinar_as_fontes.xlsx`** | **planilha da terceira parte, para projetar** |
