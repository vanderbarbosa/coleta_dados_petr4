---
name: numeros-altos-da-literatura
description: "Os 86,7% do Bollen são 13/15 pregões e foram REFUTADOS; os 71,2% do Schumaker medem reação em 20 min; o stacking do Barak já testamos e falhou"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-19T21:21:33.002Z
---

Verificado em 18/08/2026, a partir de uma pergunta do Vanderlei: *"a tabela mostra 80%+ em Barak e Bollen e 70%+ em Schumaker; por que sua avaliação não me mostra isso? Por que não posso usar para melhorar meus resultados?"* Pergunta legítima e a resposta **fortalece** a defesa.

## Por que eu não tinha trazido
Os três são **anteriores ao BERT** (2018): Bollen usou OpinionFinder+GPOMS (léxico), Schumaker saco-de-palavras+SVM, Barak ensembles sobre indicadores. Não aparecem numa busca por "quem cita o FinBERT" — que foi o recorte pedido pelo Emerson. **E já estavam na dissertação** (tabela `tab:comparacao` e Cap. 2).

## Bollen, Mao & Zeng (2011) — 86,7% = 13 acertos em 15 pregões
- Treino 28/02–28/11/2008; **teste 01–19/12/2008 = 15 pregões**. 13/15 = 86,7%
- Alvo é o **índice DJIA**, não ação individual (diversificação remove ruído idiossincrático)
- ⚠️ **REFUTADO:** Lachanski & Pav (2017), *Econ Journal Watch* 14(3):302–345, "Shy of the Character Limit". Estenderam a série para 2007 e **não acharam evidência fora da amostra**; atribuíram a **data snooping** e viés de comparações múltiplas (7 dimensões de humor × várias defasagens). Entrada bib: `lachanski_shy_2017`.
- 💡 **A ideia boa que quase ninguém cita:** das 7 dimensões de humor, **só "calma" previu**. A polaridade positivo/negativo — a nossa e a da maior parte da literatura — **NÃO previu**. Casa com [[diagnostico-erro-neutro]] (90% dos erros no Neutro; Pos×Neg = 0,783) e com a ideia de embeddings de [[revisao-ponderacao-confianca]]. **Representação em 3 classes pode ser o desenho errado.**

## Schumaker & Chen (2009) — 71,2% mede REAÇÃO, não previsão
- Prevê o preço **20 minutos após a notícia sair**; 5 semanas de dados; 9.211 artigos
- Os 71,18% são o **melhor entre vários esquemas** de particionamento ("stocks partitioned by Sectors were most predictable")
- **É o nosso P0, não o nosso P1.** Nossa Seção 4.l: P0 dá 55,0/53,2/51,6 (ordenado) e P1 colapsa para 52,5/52,4/51,5. Não há contradição com os 54,5% — são momentos diferentes.
- 💡 **Lição:** o sinal vive no curtíssimo prazo. Agora com **3 apoios independentes**: Schumaker (20 min), nosso P0×P1, e Halousková & Lyócsa (5 min, que superam o HAR). **Dados intradiários da PETR4 = maior potencial de melhoria da pesquisa.**

## Barak et al. (2017) — já replicado, falhou
Stacking na Tabela `tab:suite_experimentos`: **53,14% / 52,99% / 53,14%**, todos no baseline de classe majoritária (53,14%) ou abaixo. XGBoost simples com 3 atributos deu 54,52% e ganhou de todos. Mercado de Teerã, alvo retorno/risco, melhor entre configurações.

**Why:** a tabela `tab:comparacao` reportava os números crus sem essas ressalvas, o que deixava o Vanderlei na defensiva sem necessidade. Corrigido: tabela anotada + 4 parágrafos novos na Seção 4 detalhando cada caso.

**How to apply:** se a banca disser "mas Bollen conseguiu 86,7%", responder: *"são 13 acertos em 15 pregões, sobre um índice, e o resultado foi refutado por Lachanski e Pav (2017) como data snooping."* Reivindicar rigor, não acurácia.

⚠️ **Padrão a lembrar ao ler qualquer número alto da área:** conferir (a) tamanho do conjunto de teste, (b) se é o melhor entre configurações, (c) se é validação ou teste, (d) se a métrica é de regressão disfarçada de acurácia (ver armadilha dos 95% em [[encoders-ingles-levantamento]]), (e) se o alvo é índice ou ação individual, (f) se há refutação publicada.

Docx para leigos: `orientacoes/EXPLICACAO_SIMPLES_OS_80_PORCENTO.docx`.

Ver [[efeito-de-cauda-auditoria-noticia]], [[encoders-ingles-levantamento]], [[diagnostico-erro-neutro]] e [[revisao-ponderacao-confianca]].
