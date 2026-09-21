---
name: padrao-documentacao-dissertacao
description: "Padrão obrigatório para TODA documentação gerada para a dissertação (completude total, ABNT, nível doutorado)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f1c998e8-b9fc-44e5-a002-9f71b5ff48ec
---

Regras OBRIGATÓRIAS para todo documento Word gerado para a dissertação (cada etapa = um arquivo .docx separado, via `src/comum/abnt_docx.py`):

**Completude TOTAL — sem lacunas, sem "...":** Listar SEMPRE todos os itens por extenso. Erro cometido na Etapa 1 que NÃO pode repetir: tabelas mostraram só parte dos termos. Exigência do usuário: todos os 152 termos de cada categoria, todos os termos de filtragem (estrita e leve), todas as fontes, todas as bibliotecas. Usar o módulo único `src/comum/taxonomia.py` como fonte para garantir que nada falte.

**Conteúdo que cada documento deve cobrir:** método de captura/processamento; ferramentas e bibliotecas usadas; **justificativa de CADA biblioteca/ferramenta**; **motivo do DESCARTE de outras ferramentas**; quantidade de registros; tabelas; gráficos; informações estatísticas; **todas as dificuldades/problemas enfrentados e os recursos usados para obter êxito** (ex.: bloqueio 429 do GDELT, SSL do proxy, WinError 1114 do torch, env conda, CoW do pandas, rate limit do Yahoo).

**Tom do texto (conforme ponderações da banca — ver [[qualificacao-gaps-banca]]):** SEM linguagem promocional ("validado matematicamente", "rigor absoluto", "ratifica de forma brilhante", "elevando exponencialmente"); usar tom descritivo/condicional ("os resultados indicam", "sugere-se que", "os dados preliminares apontam"); didático (explicar GARCH, HME, Lead-Lag, Data Fusion com exemplos); definir termos operacionalmente (ex.: "sentimento" = escore de polaridade [−1,+1]); citar TODAS as referências usadas (autor-data, NBR 10520) e listá-las (NBR 6023); incluir figura da arquitetura; separar Metodologia de Método; justificar cada escolha e cada métrica; incluir seção de Limitações; garantir reprodutibilidade.

**Padrão de excelência para DOUTORADO** — objetivo é nota máxima e deixar a pesquisa pronta para doutorado. ABNT (Times 12, 1,5, margens 3/3/2/2, seções numeradas, tabelas abertas, quadros para código, figuras tituladas com Fonte). Convenção de nome: `Documentacao_EtapaN_<assunto>_PETR4.docx` em `docs/saida/`.
