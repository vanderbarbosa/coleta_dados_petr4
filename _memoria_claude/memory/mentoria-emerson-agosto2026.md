---
name: mentoria-emerson-agosto2026
description: Mentoria de 29/07/2026 com o Prof. Emerson — rotulagem manual suspensa e 7 tarefas de levantamento entregues em 10/08/2026
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-04T02:11:59.140Z
---

Na mentoria de **29/07/2026** o Prof. Emerson Paraiso mandou **PARAR a rotulagem manual** do conjunto-ouro, alegando que o rótulo de sentimento financeiro só faria sentido se feito por especialista em finanças. Passou 7 tarefas de levantamento (`coleta_dados_petr4/orientacoes/orientacoes.txt`) para a mentoria de **10/08/2026**.

**Why:** define o que pode e o que não pode avançar até nova ordem — nenhuma frente que dependa de rotulagem humana deve ser proposta.

**How to apply:** priorizar frentes *self-supervised* (MLM de domínio) e *zero-shot*/LLM, que não consomem rótulo. Ver [[encoders-sentimento-ptbr]].

**Contra-argumento apurado (levar à mentoria de 10/08):** Santos, o autor do FinBERT-PT-BR, **não** usou especialistas em finanças — usou 2 engenheiros e 1 linguista. O que salvou o gabarito dele foram 3 controles que **o nosso não tem**: definição operacional ancorada em rentabilidade, **dupla anotação com descarte de 49,7%** dos casos, e **Krippendorff's alpha** (0,88). Nosso conjunto-ouro tem 300 manchetes com **1 anotador só** → nenhuma métrica de concordância → os 58% de acurácia do FinBERT não medem o modelo, medem a distância até um anotador não calibrado. Ampliar p/ 600 não resolve; o certo é **dupla anotação de 100-150 das 300 já feitas**.

**Achados do levantamento** (`orientacoes/RESPOSTA_ORIENTACOES_2026-08-10.*`, `CITACOES_E_GAPS_2026-08-10.*`, `referencias_artigo_bwaif_24960.csv`, `citacoes_por_trabalho.csv`, `gaps_pesquisa.csv`):
- O link da tarefa 5 (SBC/BWAIF 24960) **é o próprio artigo do FinBERT-PT-BR** — tarefas 5 e 6 são o mesmo trabalho.
- **Lacuna de literatura:** dos 7 citantes verificados, **nenhum aplicou o FinBERT-PT-BR à tarefa financeira** para a qual foi feito; e **nenhum trabalho correlato prevê volatilidade**. Reposicionar a volatilidade como contribuição principal e a direção como resultado negativo reportado.
- Google Scholar diz 12 citações mas bloqueia por CAPTCHA; 7 verificadas via OpenAlex/Semantic Scholar. Falta fechar manualmente.
- **Imai et al. (2024)** sobre *concept drift* é de **Barddal e Britto Jr., do PPGIa/PUCPR** — usamos modelo congelado em 02/2024 sobre corpus 2018–2026; vale consultá-los.

**CORREÇÃO (após leitura integral dos textos, 03/08/2026):** a afirmação "nenhum dos 7 usou o modelo" estava **errada**. **Błoch, Santana e Amantino (2026)** *executaram* o FinBERT-PT-BR numa **máquina de comitê** com o `pysentimiento`, em correspondência colonial portuguesa (História Digital, não finanças). Eles caracterizam o FinBERT-PT-BR como *"fortemente influenciado pela presença de termos negativos ou positivos"* (léxico) contra o pysentimiento, que *"analisa mais o contexto"* — **isso explica a nossa matriz de confusão**, em que a classe Neutra é a mais confundida.

Ver [[gaps-pesquisa-petr4]] para os 13 gaps derivados deste levantamento.
