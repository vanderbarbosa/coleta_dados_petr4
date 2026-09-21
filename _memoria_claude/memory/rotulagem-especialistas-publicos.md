---
name: rotulagem-especialistas-publicos
description: "nova linha pedida por Emerson e Julio (ago/2026) — colher rótulos de análises públicas; o especialista vira RÉGUA, e validar rótulo pelo preço é armadilha"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-26T23:23:27.107Z
---

Em reunião de agosto de 2026, os Profs. Emerson Paraiso e Julio Nievola pediram uma
via alternativa de rotulagem: localizar sites e blogs de especialistas em mercado
financeiro ou na Petrobras, verificar se classificam as notícias publicadas, e depois
conferir nos preços se a previsão do especialista se confirmou.

**Viável.** Precedente: Chen, De, Hu e Hwang (2014), *Review of Financial Studies*
27(5):1367-1403 — opiniões de especialistas no Seeking Alpha antecipam retorno e
surpresa de resultado. PDF aberto em bhwang.com.

Fontes com acesso testado em 26/08/2026: InfoMoney e Money Times publicam **carteiras
recomendadas mensais** com contagem explícita de quantas corretoras recomendam PETR4
(artigo de 05/01/2021 recuperado); TradingView tem ideias com rótulo "viés de
alta/baixa" datado desde ~2020; Seeking Alpha bloqueia (403). InfoMoney e Money Times
**já são raspados** pelos coletores do projeto.

**A armadilha, e é o ponto central:** o pedido encadeia três coisas distintas — (a) o
especialista classifica uma NOTÍCIA, (b) o especialista PREVÊ alta/baixa, (c) confere-se
no preço. **O item (c) valida (b) e NÃO valida (a).** Validar rótulo pelo preço julgaria
bons rótulos com uma régua que já provamos ser cara ou coroa: a rotulagem humana de
direção acertou 46,7% (ver [[conjunto-ouro-quatro-rotulos]]) e o sinal do pregão de
reação colapsa no dia seguinte (ver [[efeito-de-cauda-auditoria-noticia]]).

**O reenquadramento que dá valor:** usar o especialista como **RÉGUA**, não só como
fonte de rótulo. Se analistas profissionais acertam X% da direção da PETR4 no mesmo
período em que o modelo acerta 54,5%, tem-se a resposta direta à crítica de que 54,5%
é pouco — hoje respondida indiretamente pelo ganho de 4,4 p.p. (ver
[[onde-a-literatura-nos-supera]]).

**Ação de maior retorno, ainda pendente:** perguntar à biblioteca da PUCPR se a
instituição assina **Economatica** ou **Refinitiv Eikon**. Havendo assinatura, obtém-se
a série histórica de consenso estruturada, sem raspagem e sem discussão de termos de
uso. Eikon é a base usada por Hashami e Maldonado (ver [[resumos-pesquisas-finbert]]).

Protocolo completo em `coleta_dados_petr4/Rotulagem_Especialistas/01_PROTOCOLO.docx`:
três experimentos (E1 régua, E2 rótulo sem preço, E3 estudo de evento), com riscos.
Isto **não reabre** a rotulagem manual suspensa (ver [[mentoria-emerson-agosto2026]]):
lá se produziriam rótulos, aqui se colhem rótulos que já existem publicados.
