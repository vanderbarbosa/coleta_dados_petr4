---
name: piso-estatistico-custo-computacional
description: quanto de ganho percentual justifica uma técnica computacionalmente mais cara — ~4 pontos (nosso tamanho de amostra) é o piso estatístico; ~2-5 pontos / R²-OS+5% é o piso de relevância já usado na pesquisa
metadata:
  type: project
---

**12-15/10/2026.** Pedido do Prof. Julio: comparando duas técnicas, uma mais
cara computacionalmente, que valor percentual de ganho justifica o esforço
extra? Não existe número universal — mas existe um piso calculável para ESTA
pesquisa, com os tamanhos de amostra que usamos.

**Camada 1 — piso estatístico.** Com teste de 579 a 653 pregões (os tamanhos
usuais desta pesquisa), o erro-padrão de uma taxa de acerto é ~2,0 pontos
percentuais, e o IC95% é de **~±4 pontos**. Qualquer ganho menor que isso não
pode ser distinguido de acaso com esta amostra — bate com o IC real já medido
no diagnóstico (texto sobre mercado: [-0,032, +0,015] de AUC, ver
`CVM/dados/diagnostico_ml.json`).

**Camada 2 — piso de relevância**, só depois de passar a camada 1 (idealmente
via McNemar, corrigido por Bonferroni se houver mais de uma comparação — ver
[[comparativo-top10-ibovespa]]): usar a régua que a própria pesquisa já
adotou — **+2,4 pp** foi o ganho de direção já considerado digno de reportar
(Tabela 4.3), e **R²-OS > +5%** é a meta de volatilidade (ver
[[como-ler-os-numeros]]). Recomendação: só valorizar o esforço extra se o
ganho passar as duas camadas.

**Aplicação retroativa:** é exatamente por isso que o embedding de 768
dimensões da CVM (caro, precisa GPU) nunca se justificou nesta pesquisa — não
passa no McNemar e às vezes piora (ver [[escopo-e-ml-de-verdade]]).

**Entregue em:** `Mentorias/2026-10-12_Julio/00_LEIA-ME.md` (item 3),
junto com os itens 1 e 2 (ações/investidor e valor médio investido, em
`01_Valor_Medio_Investido.xlsx`) e a confirmação do item 4 (o sentimento move
volatilidade medida, não direção — consistente com todo o resto da pesquisa).

**Pendente, não executado:** pedido de testar um "encoder do Google para
séries temporais" comparado com Prophet. Nenhum dos dois foi testado antes
neste projeto (procurei — Prophet não aparece em nenhum script ou memória).
Fica em aberto até o Vanderlei confirmar: (a) qual encoder do Google —
provável TimesFM, do Google Research, mas não confirmado; (b) se é para
rodar os dois agora, ou se o Prophet já tinha resultado em algum lugar que
eu não achei.

**Why:** responde ao pedido de 12/10/2026 (mentoria pode ter sido adiada —
preparado em 15/10, três dias depois da data marcada).

**How to apply:** ao comparar qualquer técnica nova contra uma mais simples
nesta pesquisa, citar as duas camadas juntas — nunca só o p-valor, nunca só
o tamanho do ganho isolado.
