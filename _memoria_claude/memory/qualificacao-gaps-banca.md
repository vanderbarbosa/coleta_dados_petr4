---
name: qualificacao-gaps-banca
description: As 24 ponderações da banca de qualificação (nota C) que devem ser corrigidas até a defesa final (mar/2027)
metadata: 
  node_type: memory
  type: project
  originSessionId: f1c998e8-b9fc-44e5-a002-9f71b5ff48ec
---

Exame de qualificação de Vanderlei (PUCPR/PPGIa) em **09/06/2026, nota C**. Defesa final prevista para **março/2027**. Banca: Julio Cesar Nievola (orientador), Emerson Cabrera Paraiso e Rayson Bartoski Laroca dos Santos (avaliadores). Materiais em `Exame_qualificacao/` (questionamentos Emerson .docx, plano de correção .docx, PDF da dissertação com marcações do Rayson, pptx da apresentação, mp4 da defesa). 29 PDFs do referencial em `Referencial_Teorico/`.

**24 ponderações em 3 ondas.** CRÍTICOS (4): (01) timestamps ausentes — as 9.079 notícias antigas tinham datas aleatórias → invalidava tudo; (02) linguagem promocional ("validado matematicamente", "rigor absoluto"); (03) afirmações não sustentadas sobre BERTimbau desambiguar ironia/jargão sem fine-tuning financeiro; (04) slides respondiam as questões de pesquisa antes de validar.

**O que NOSSO trabalho já resolveu:** item 01 (timestamps) — coleta WordPress com 205.716 notícias e hora exata + Lead-Lag 17h. Item 13 (fonte única Valor Econômico → viés) — agora 5 portais. Item 11/d (walk-forward/sem leakage) — split treino/validação/teste implementado.

**Pendências-chave (IMPORTANTE/AJUSTE):** (03/12) documentar tecnicamente extração do sentimento (modelo HF exato, zero-shot vs fine-tuned, softmax) e considerar **FinBERT-PT-BR** ou fine-tuning financeiro + validação com gold standard/kappa; (05) definir "sentimento" operacionalmente e justificar/remover "Big Data"; (06) citar TODOS os 25 estudos da tabela nas referências (rastreabilidade); (07) janela temporal da RSL + justificar recorte Brasil; (08) figura geral da arquitetura do pipeline; (09) separar Metodologia de Método; (10) validação dos tópicos LDA; (11) justificar cada escolha (GARCH(1,1), XGBoost, AUC-ROC, limiares de sentimento); (15) documento muito curto (34p → meta 80-100p); (16-19) formatação LaTeX/acrônimos/idioma/palavras coladas; (20) justificar objetivos específicos; (21) exemplos didáticos; (22) justificar Data Fusion (Barak et al. 2017); (23) seção de Limitações; (24) reformular slides.

**Visão futura do usuário (pós-pipeline):** site/app profissional e acessível com: consulta de notícias (filtro por grupo/data), consulta de preços (data/ano/mês), avaliar se uma mensagem é relevante para o preço e prever direção (sobe/cai/neutro), demonstração prática com dados reais, gráficos/tabelas interativos, explicação completa da pesquisa para a defesa — sem nada inventado. Objetivo final: fechar todos os gaps da banca e deixar a pesquisa **pronta para Doutorado**. Ver [[projeto-petr4-dissertacao]].
