---
name: restringir-a-dias-de-evento-nao-ajuda
description: 29/10/2026 — avaliar só nos pregões com comunicado PIORA (agrupado: −4,5 a −5,8pp só preço, p<0,05); o limite não é o modelo, é a raridade do evento (1% a 28% dos pregões)
metadata:
  type: project
---

**29/10/2026.** Hipótese do Vanderlei, razoável: como em 60,4% dos pregões
não há comunicado e a coluna de sentimento vira zero de preenchimento, medir
sobre todos os dias dilui o sinal. Restringindo aos dias com comunicado, os
índices deveriam subir.

**Não subiram. Desceram.** `CVM/25_dias_com_evento.py`, 10 papéis, mesmos 579
pregões de teste, mesmo protocolo.

**Por papel, nada é mensurável.** Os pregões com comunicado vão de 5 (ABEV3,
0,9% — excluída, abaixo do mínimo de 30 que fixei ANTES de rodar) a 165
(PETR4, 28,5%). A meia-largura do IC95% fica entre **±7,6 e ±17,1 pontos**
— e o efeito procurado é de 2 a 3 pontos. Instrumento sem precisão para a
pergunta. Piorou em 8 dos 9 avaliáveis; 0 braços significativos em qualquer
papel.

**Agrupando os 10 (n=5.790 total, 670 com evento, IC ±3,8) — aí mede:**

| arranjo | todos | só com comunicado |
|---|---|---|
| SVM só preço | −1,43pp (p=0,030) | **−4,48pp (p=0,022)** |
| XGBoost só preço | −1,61pp (p=0,015) | **−5,82pp (p=0,003)** |
| SVM preço+sent (A) | −1,57pp | −2,69pp (p=0,164) |
| XGBoost preço+sent (A) | −1,54pp | −3,43pp (p=0,081) |
| SVM preço+sent (B) | −1,54pp | −3,13pp (p=0,104) |
| XGBoost preço+sent (B) | −0,64pp | −1,34pp (p=0,486) |

Todos abaixo do palpite fixo, e nos dias de comunicado o déficit é MAIOR.
Os dois de preço puro chegam a ser significativamente piores.

**Testei a objeção óbvia** (o modelo geral aprendeu num mundo com 60% de dias
mudos): treinei um **especialista só com dias de evento**. Piorou em 6 dos 7
papéis com treino suficiente; em BBDC4 e BPAC11 nem deu para treinar (<100
dias de evento no treino).

**PADRÃO NÃO CONFIRMADO, registrado como conjectura:** nos dias com
comunicado, os braços COM sentimento erram menos (−1,3 a −3,4) que os de
preço puro (−4,5 e −5,8). Pode ser que o sentimento atue como atenuação de
erro, não como fonte de acerto. **Não testei pareado** — não afirmar.

**A LIÇÃO, e é a que vale:** o limite não é o modelo nem a representação do
sentimento — é a **raridade do fenômeno**. Comunicado após o fechamento
ocorre em 1% a 28% dos pregões. O caminho é **base maior** (mais ativos,
horizonte mais longo), não modelo mais elaborado. Coerente com o efeito de
cauda já documentado em [[efeito-de-cauda-auditoria-noticia]].

**ARMADILHA EVITADA, anotar para sempre:** ao trocar de subconjunto, o
ADVERSÁRIO muda — a classe majoritária dos dias com evento não é a do total.
Cada subconjunto foi julgado contra a SUA própria majoritária. E o n menor
alarga o IC: o mesmo ganho em pontos vale menos como evidência. Reportar
sempre os dois efeitos.

**DIVERGÊNCIA DE FÓRMULA ENCONTRADA E RESOLVIDA.** A dissertação (Cap. 3) e o
ramo de notícias usam `polaridade × confiança` (neutro → zero exato). O ramo
da CVM (scripts 18 a 24) usa `p_pos − p_neg` (neutro conserva a inclinação).
Importa porque **70% dos comunicados da PETR4 são neutros**. Em vez de
escolher no escuro, rodei as DUAS como variantes (linhas A e B) e medi: o
desvio-padrão agregado por pregão é 0,319 (A) contra 0,344 (B) — parecido, e
a escolha não altera conclusão alguma. O Cap. 3 agora documenta as duas.

**QUARTA TENTATIVA, também negativa — só dias com TOM declarado**
(`CVM/26_so_dias_com_tom.py`, 29/10). Proposta: descartar os pregões cujos
comunicados são todos neutros, treinando e projetando só onde há tom. Medi
ANTES e registrei a expectativa: PETR4 cai de 165 para **56** pregões de
teste, IC de ±7,6 para **±13,1**. Resultado pior que o previsto: **8 dos 10
papéis não puderam ser avaliados** (ITUB4 com 3 pregões, ABEV3 com 1); só
PETR4 (56) e VALE3 (49) sobreviveram, agrupadas em n=105, IC ±9,6. Melhor
braço +5,71pp (p=0,282) — dentro da margem, 1 de 8 braços. Treinar SÓ com
dias de tom piorou muito (−10,5 e −11,4pp, p=0,040 e 0,024) por perda de
dados de treino. **Limiar de Bonferroni da família acumulada: 132 testes →
0,000379.** Ressalva central: o filtro usa o rótulo do FinBERT, aferido em
**58% de acurácia** contra o conjunto-ouro — filtro ruidoso.

**O PADRÃO DAS QUATRO TENTATIVAS, e é a lição que fica:** cada filtro troca
sinal por tamanho de amostra, e a amostra já era o gargalo. Não é falta de
engenho na especificação — é limite de informação da base.

**Escrito na dissertação:** Cap. 3 ganhou a subseção **"A cadeia de
componentes"** (tabela de o que cada peça consome e entrega — era o que
faltava para o Vanderlei conseguir explicar, ver
[[entregar-pouco-e-compreensivel]]) e a subsubseção das duas formas do
índice; Cap. 4 ganhou a seção **4q**. Validador passa.

**Entregue:** `Mentorias/2026-10-29_Emerson_e_Julio/`.
