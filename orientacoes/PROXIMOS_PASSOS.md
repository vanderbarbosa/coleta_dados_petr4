# Próximos passos

**Elaborado em:** 08/08/2026 · **Mentoria:** 10/08/2026 (em 2 dias) · **Defesa:** mar/2027

---

## O que mudou e por que a ordem importa

O achado do bug de caixa alta e da unidade de texto errada **reposicionou tudo**. Todos os
números medidos — acurácia 0,580, viés de 87% do ISM, matriz de confusão, teste do teto — vêm
de um corpus com **10,5% mal tokenizado** e com a **unidade de texto errada**.

Não são inválidos. São **piso**. Mas isso significa que **refazer a medição vem antes de tudo**:
qualquer análise nova construída sobre os números atuais teria de ser refeita depois.

> **O gargalo único é o PyTorch local inoperante.** Enquanto ele não for contornado, nada
> avança. A solução não é depurá-lo — é o Colab.

---

## Fase 0 — desbloquear (hoje, ~1 hora)

**Notebook pronto:** [`notebooks/revalidacao_encoder_colab.ipynb`](../notebooks/revalidacao_encoder_colab.ipynb)

Autônomo: os 300 exemplos do conjunto-ouro vão embutidos em base64. Não precisa subir arquivo
nem montar o Drive. Só abrir no Colab, ativar GPU (T4) e executar.

Roda três experimentos, em ordem de prioridade:

| # | Experimento | Hipótese | Tempo |
|---|---|---|---|
| 1 | **Caixa alta normalizada** | Cobertura do vocabulário sobe de 22,2% para 77,6%; as 36 manchetes do Petronoticias devem sair de acc 0,528 / κ 0,195 | ~3 min |
| 2 | **Granularidade** `Título` × `Título+Resumo` | `Título+Resumo` tem mediana 42 palavras, contra os 39 do treino de Santos e os 13 atuais | ~5 min |
| 3 | **Comitê** FinBERT + pysentimiento (G7) | O modelo é léxico; o contextual complementa. 90% dos erros envolvem o neutro | ~5 min |

**Saída:** `revalidacao_resultados.csv` e `revalidacao_predicoes.csv`, para trazer de volta a
`Mestrado_PETR4/`.

> ⚠️ **Antes de reportar qualquer ganho:** rodar
> `_codigos/reconstrucao_santos_bootstrap.py` sobre as predições. Com n = 300, diferenças
> menores que ~5 pontos percentuais provavelmente não são significativas.

---

## Fase 1 — antes da mentoria de 10/08 (2 dias)

Os entregáveis das sete tarefas **já estão prontos**. O que falta é incorporar o que apareceu
depois.

| # | Ação | Custo |
|---|---|---|
| 1.1 | **Rodar o notebook** (Fase 0) | 1 h |
| 1.2 | **Reenviar o e-mail** para `lucaslssantos99@gmail.com`, sem o pedido nº 2 | 15 min |
| 1.3 | **Acrescentar 2 slides** à pauta: o bug de caixa alta e o dataset encontrado | 1 h |
| 1.4 | Se o notebook confirmar ganho: **atualizar os números** nos documentos | 1 h |

### A pauta da mentoria, revisada

1. **Abrir pela auditoria, não pelo resultado.** *"Localizei o dataset original e, ao comparar
   com o nosso corpus, encontrei duas incompatibilidades que corrigi."* Isso enquadra a
   conversa como rigor, não como conserto de erro.
2. **O bug de caixa alta** — 21.619 notícias, mecanismo comprovado no vocabulário, correção
   pronta e medida.
3. **A unidade de texto** — 13 palavras contra 39; `Título+Resumo` dá 42.
4. **As duas perguntas dele**, já respondidas: os quatro rótulos e o uso prático (calibração
   do ISM).
5. **O teste do teto** — melhorar o classificador é inútil para direção (+1,2 pp) e promissor
   para volatilidade.
6. **O pedido:** aproximação com o Prof. Barddal sobre *concept drift*.

---

## Fase 2 — depois da mentoria (agosto a outubro/2026)

**Só começar depois que a Fase 0 tiver confirmado ou descartado os ganhos.**

| # | Ação | Depende de | Custo |
|---|---|---|---|
| 2.1 | **Reprocessar o corpus completo** com títulos normalizados e a melhor granularidade | Fase 0 | 6–8 h |
| 2.2 | **Recalibrar o ISM** com a nova matriz de confusão | 2.1 | 30 min |
| 2.3 | **Refazer GARCH, XGBoost e volatilidade** com o ISM novo | 2.2 | 1 dia |
| 2.4 | **Adaptação de domínio (G3)** — MLM sobre as 205 mil notícias, agora com o texto corrigido | 2.1 | Colab, 6–10 h |
| 2.5 | **Ajuste fino com os 503 textos de Santos** — 11 épocas, *gradual unfreezing*, lr 5e-6 | 2.4 | Colab, 2 h |
| 2.6 | **LLM × encoder (G6)** — usar a instrução literal de Santos | — | 4 h |
| 2.7 | **SHAP (G13)** — contribuição marginal do sentimento na volatilidade | 2.3 | 4 h |

> **O item 2.5 é novo e só ficou possível esta semana.** Com os 503 textos rotulados por três
> pessoas (α = 0,88), há finalmente base de treino de qualidade — sem depender da rotulagem
> suspensa.

---

## Fase 3 — a que está atrasada (a partir de setembro/2026)

**É preciso dizer isto com clareza: há muito diagnóstico acumulado e pouca escrita.**

Os gaps G1 e G2 estão marcados como *"editorial, custo zero"* desde o levantamento — e não
foram escritos. O risco real deste projeto, hoje, não é técnico: é acumular análise e chegar a
março de 2027 sem texto.

| # | O que escrever | Onde |
|---|---|---|
| 3.1 | **Reposicionar a volatilidade** como contribuição principal e a direção como resultado negativo reportado | Cap. de resultados |
| 3.2 | **Transferência de domínio** — por que 0,76 vira 0,58 | Cap. de resultados |
| 3.3 | **Lacuna de literatura** — 177 mil downloads/mês e adoção acadêmica aplicada quase nula | Introdução |
| 3.4 | **Limitações** — *concept drift*, gabarito de anotador único, caixa alta | Cap. de método |
| 3.5 | **Método** — licença, ficha técnica, o mapeamento de rótulos, a decisão de granularidade | Cap. de método |
| 3.6 | Incorporar as **4 referências de relação muito alta** + as 3 da monografia | Referencial |

**Sugestão de disciplina:** reservar um dia fixo por semana só para escrever, sem rodar código.
O material para os itens 3.1 a 3.5 já está inteiro nos documentos da pasta `orientacoes/` — é
transposição, não pesquisa nova.

---

## Fase 4 — quando a rotulagem for liberada

| # | Ação |
|---|---|
| 4.1 | **Dupla anotação** de 100–150 das 300 já rotuladas, com Krippendorff's alpha |
| 4.2 | **Especialista como árbitro** dos ~55 casos relevantes com confiança média/baixa |
| 4.3 | Migrar da planilha para o **`doccano`** |
| 4.4 | Publicar o conjunto-ouro com DOI (Zenodo) — contribuição de artefato |

---

## O que NÃO fazer

| Item | Por quê |
|---|---|
| Depurar o PyTorch local | O Colab resolve, e é onde o pipeline já roda |
| Ampliar o gabarito para 600 no protocolo atual | Dobra o custo mantendo o defeito estrutural |
| Novos diagnósticos antes da Fase 0 | Seriam refeitos depois com os números corrigidos |
| Prometer melhora na previsão de **direção** | O teste do teto mostra que não vai acontecer (+1,2 pp) |
| Trocar de encoder | Os testes anteriores foram inconclusivos por protocolo; e o caminho é adaptar, não trocar |
| Estender a estratégia de carteira de Santos, ou índice × macroeconomia | Fora do escopo; matéria de doutorado |

---

## Resumo em uma frase

> **Rodar o notebook hoje, levar o achado do bug para a mentoria de 10/08, reprocessar o corpus
> na semana seguinte — e a partir de setembro escrever, porque é isso que está atrasado.**
