---
name: cvm-estudo-de-evento
description: "linha CVM (Emerson, ago/2026) — 16.437 eventos oficiais em 54 papéis da B3; direção nula, magnitude 1,325, e o efeito de cauda demonstrado sem modelo de sentimento"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-27T19:13:35.173Z
---

Pedido do Prof. Emerson na mentoria de 26/08/2026: coletar publicações da CVM, classificar
com o FinBERT-PT-BR, avaliar o impacto nos principais ativos da B3 e, eventualmente,
retreinar o encoder. Etapas de coleta e estudo de evento concluídas em 27/08/2026.

**Fonte:** `dados.cvm.gov.br/dados/CIA_ABERTA/DOC/IPE/DADOS/ipe_cia_aberta_{ano}.zip` —
dados abertos oficiais, 2003–2026, sem raspagem. Colhidos 89.902 comunicados de 2018 a
2026, dos quais **23.009 Fatos Relevantes**; 62 companhias mapeadas para papéis da B3;
20.421 textos prontos para classificar (campo `Assunto`, ~47 caracteres).

**Por que a fonte é superior ao corpus de notícias:** a relevância vem por lei (Res. CVM 44
obriga divulgar todo fato capaz de influir na cotação) — e o filtro de relevância foi o
único dos nove experimentos que funcionou (ver [[filtro-relevancia-primeiro-ganho]]); o
poder estatístico sobe de 1 para 54 papéis, que era a nossa fraqueza contra Halousková (ver
[[onde-a-literatura-nos-supera]]); e a atribuição à empresa é exata, por CNPJ.

**Resultados do estudo de evento (modelo de mercado, 16.437 eventos):**
- **Direção: nada.** CAR médio dos Fatos Relevantes de +0,006% a −0,046%, valores-p de
  0,64 a 0,99. Nem o fato que o regulador chama de relevante prevê alta ou baixa.
- **Magnitude: 1,325** em [0,+1] (p = 1,2e-53) — o preço sacode 32,5% mais que o normal.
- **A lei acerta:** Fato Relevante 1,325 contra Comunicado ao Mercado 1,181, diferença
  +0,144 (p = 4,4e-10).
- **Efeito de cauda:** mediana **0,967** — o Fato Relevante TÍPICO mexe MENOS que um dia
  comum — contra percentil 99 de 7,712. Na PETR4 (537 casos): mediana 0,860, p99 10,113.

**A tese sai generalizada:** não é o sentimento que só importa nos extremos, é a notícia —
mesmo a legalmente relevante — e isso foi demonstrado **sem usar modelo de sentimento
nenhum** (ver [[efeito-de-cauda-auditoria-noticia]]).

**Limitação principal:** a base traz data, não hora; não se sabe se o comunicado saiu antes
ou depois do pregão. A hora existe no PDF do `Link_Download`. E os maiores choques
individuais não são atribuíveis ao comunicado — o maior da PETR4 é de 06/03/2020, semana da
pandemia; o modelo desconta o Ibovespa, não o barril.

**Pendente:** classificar os 20.421 textos e o retreino do encoder — ambos **no Colab**,
porque o torch segue quebrado localmente (ver [[ambiente-torch-quebrado]]). Sobre o
retreino, registrado que o G3 já falhou (ver [[g3-adaptacao-esquecimento]]); a proposta é
refazer avaliando pelos **embeddings**, não pela cabeça de sentimento (ver
[[revisao-ponderacao-confianca]]).

Código em `coleta_dados_petr4/CVM/`: `01_coletar_ipe.py`, `02_coletar_precos.py`,
`03_estudo_de_evento.py`. Documento: `01_RESULTADO_CVM.docx`. O yfinance exige sessão com
`verify=False` nesta rede (proxy interceptador), como já fazia o coletor do projeto.
