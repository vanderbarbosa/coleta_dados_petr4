---
name: resumos-pesquisas-finbert
description: Pasta orientacoes/resumos_pesquisas/ — 7 fichas completas + scripts prontos p/ os gaps; o código do FinBERT-PT-BR nunca foi publicado
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-05T00:28:29.342Z
---

Em `coleta_dados_petr4/orientacoes/` há duas pastas montadas em ago/2026 a pedido do orientador:

- **`resumos_pesquisas/`** — 7 fichas (~2.350 linhas), uma por pesquisa, com o mesmo esqueleto: ficha bibliográfica · objetivo · dados · tecnologias/encoders · método com TODOS os hiperparâmetros · resultados · código · leitura crítica (o que aproveitar / não aproveitar / gaps).
- **`_codigos/`** — 6 scripts próprios (um por gap, todos com sintaxe validada) + 8 arquivos originais do repositório `jp-alves/prio3-sentiment`.

**Why:** é o material de estudo para separar o que dá para reaproveitar; e os scripts são a implementação direta dos gaps G3, G4, G6, G7 e G12.

**How to apply:** ler `resumos_pesquisas/00_INDICE.md` primeiro — traz o mapa de leitura e o quadro comparativo geral. Executar os scripts na ordem de `_codigos/README.md`.

**Achados desta rodada:**
- **O código de treinamento do FinBERT-PT-BR NUNCA foi publicado** — verificado no GitHub pessoal do Lucas Leme (22 repos), na org `turing-usp` (81 repos) e no HuggingFace (10 arquivos, só pesos). As reconstruções em `_codigos/` são próprias, escritas a partir dos hiperparâmetros do artigo e da monografia; **nunca apresentar como replicação exata**.
- Santos usou **Kedro** para orquestrar o pipeline e **wandb** para rastrear experimentos — dois itens que não temos.
- **`jp-alves/prio3-sentiment`** (GitHub, 2025) é quase a nossa pesquisa com PRIO3 no lugar de PETR4: notícias de petróleo + FinBERT-PT-BR + estudo de evento + Granger. **Não é acadêmico e não cita Santos** — usar só como referência de implementação, nunca como citação. Achados deles CONVERGEM com os nossos: impacto intradiário ≈ 0, efeito só após 5+ dias. Validação externa do nosso resultado de direção.
- **Abílio et al. (2024) publicou tudo sob MIT**: `github.com/rsabilio/NerEval-BrazilianCorporateTranscripts` — corpus BraFiNER (earnings calls de bancos) + usa **`doccano`** para anotação, que é a ferramenta certa p/ substituir a planilha Excel quando a rotulagem voltar.
- Teles e Figueiredo (2025): os modelos *zero-shot* **colapsam a classe Neutra** (recall 0,02–0,09). Nosso FinBERT erra o neutro na direção oposta (empurra p/ os extremos, 46,8%). **A classe neutra é problema estrutural da área**, não falha nossa — bom argumento de banca.
- Excluídos por baixa relação: Alves et al. (2024) e Tanaka et al. (2026), com a razão registrada no índice.

Ver [[gaps-pesquisa-petr4]], [[mentoria-emerson-agosto2026]] e [[encoders-sentimento-ptbr]].
