# Análise de Gaps — Cobertura das 24 Ponderações da Banca

**Dissertação:** O Impacto do Sentimento de Notícias Financeiras na Previsão de Direção e Volatilidade do Ativo PETR4
**Autor:** Vanderlei Barbosa da Silva · **Orientador:** Prof. Dr. Julio Cesar Nievola
**Qualificação:** 09/06/2026 (nota C) · **Defesa prevista:** mar/2027
**Banca:** Nievola (orientador), Emerson Cabrera Paraiso, Rayson Bartoski Laroca dos Santos

Legenda: ✅ resolvido · 🟡 parcial · ⬜ pendente (nível de redação da dissertação)

---

## Críticos (4)

| # | Ponderação | Status | Onde / como |
|---|---|---|---|
| 01 | Timestamps ausentes (datas aleatórias invalidavam a causalidade) | ✅ | Coleta WordPress: 205.716 notícias com **hora exata** (Brasília + UTC) e Lead-Lag 17h. **Etapa 1 e 2** |
| 02 | Linguagem promocional ("validado matematicamente", "rigor absoluto") | ✅ | Tom acadêmico sem marketing em todos os docs; resultados honestos (53–55%, ganhos modestos, achados negativos reportados) |
| 03 | Afirmações não sustentadas sobre BERTimbau desambiguar ironia/jargão | ✅ | **Etapa 3 §2–2.2**: FinBERT-PT-BR = BERTimbau + *fine-tuning* financeiro (Santos et al., 2023); 6 critérios; tabela comparativa |
| 04 | Slides respondiam as QP antes de validar | ✅ | Validação antes da afirmação; **Etapa 6** acrescenta testes de significância (binomial p=0,024; McNemar p=0,053) |

## Importante / Ajuste (20)

| # | Ponderação | Status | Onde / como |
|---|---|---|---|
| 05 | Definir "sentimento" operacionalmente; justificar/remover "Big Data" | 🟡 | Definição operacional em **Etapa 3 §1**. *Pendente:* revisar uso de "Big Data" no texto da dissertação |
| 06 | Citar TODOS os 25 estudos da RSL (rastreabilidade) | ⬜ | Nível de redação — exige o `.docx`/`.tex` da dissertação |
| 07 | Janela temporal da RSL + justificar recorte Brasil | ⬜ | Nível de redação (capítulo de RSL) |
| 08 | Figura geral da arquitetura do pipeline | 🟡 | Animação "Jornada" no site + Quadros nos docs. *Sugerido:* figura estática única no corpo da dissertação |
| 09 | Separar Metodologia de Método | ⬜ | Nível de estrutura da dissertação |
| 10 | Validação dos tópicos LDA | ✅ | LDA **removido**; substituído pela taxonomia supervisionada de 7 categorias/152 termos (**Etapa 1**) |
| 11 | Justificar cada escolha (GARCH(1,1), XGBoost, AUC-ROC, limiares) | ✅ | **Etapa 4 §5 (Tabela 3)** + **Etapa 6** (significância, baselines, limiar 0,5) |
| 12 | Documentar extração do sentimento (modelo HF, zero-shot, softmax) | ✅ | **Etapa 3 §2–3** (modelo exato, head 3 classes, softmax, índice contínuo) |
| 13 | Fonte única (Valor Econômico → viés) | ✅ | 5 portais (InfoMoney, Exame, MoneyTimes, Petronotícias, Poder360) |
| 14 | Walk-forward / sem vazamento | ✅ | Split cronológico 60/15/25; **Etapa 4 §6** e **Etapa 4b** (walk-forward) |
| 15 | Documento muito curto (34p → meta 80–100p) | 🟡 | 7 documentos técnicos ABNT já produzidos como anexos/base; *pendente* integrar ao corpo principal |
| 16–19 | Formatação LaTeX / acrônimos / idioma / palavras coladas | ⬜ | Nível de redação |
| 20 | Justificar objetivos específicos | ⬜ | Nível de redação |
| 21 | Exemplos didáticos | ✅ | Exemplos trabalhados: agregação de dia conflitante (**Etapa 3 §6**), matriz Data Fusion (**Etapa 4**), inferência (**Etapa 5**) |
| 22 | Justificar Data Fusion (Barak et al., 2017) | 🟡 | **Etapa 4 §4** formaliza o Data Fusion. *Pendente:* inserir a citação de Barak et al. (2017) |
| 23 | Seção de Limitações | ✅ | Limitações em cada etapa; **Etapa 4b §6–7** (sobreajuste, parcimônia, honestidade) |
| 24 | Reformular slides | ⬜ | Nível de apresentação |

---

## Novos reforços já entregues (além do que a banca pediu)

- **ISM ponderado** (Etapa 6 §2): ponderar por confiança é a melhor construção (54,93%); o sinal está na intensidade, não na contagem.
- **Significância estatística** (Etapa 6 §3): Data Fusion supera o acaso com p=0,024.
- **Causalidade de Granger** (Etapa 6 §4): sentimento → retorno em t+1 (p=0,025) e sentimento → volatilidade fortíssima em todas as defasagens (p≈0,000) — fundamento empírico do Lead-Lag.
- **Avaliação da volatilidade** (Etapa 6 §5): GARCH com correlação 0,41 e Mincer-Zarnowitz b=0,69 contra a volatilidade realizada — atende a metade "volatilidade" do título.
- **Conjunto-ouro de sentimento** (validação por kappa de Cohen) pronto para rotulagem.

---

## Sugestões de adições (o que ainda pode reforçar a defesa)

Itens **empíricos** (posso implementar com os dados atuais):

1. **Significância econômica / backtest com custos** — verificar se a vantagem de ~54,5% gera retorno acima do *buy-and-hold* líquido de custos de transação. Responde "o resultado tem valor prático?".
2. **Robustez por subperíodo** — acurácia em janelas (2020 COVID, 2022 eleição, 2024–25) para mostrar estabilidade/instabilidade do sinal.
3. **Figura única da arquitetura** (item 08) — diagrama estático do pipeline para o corpo da dissertação.
4. **Validação humana do sentimento** — rotular o conjunto-ouro e rodar `avaliar_conjunto_ouro` para obter acurácia + kappa reais (item 03/12).
5. **Curva ROC e matriz de confusão** do Data Fusion como figuras formais.

Itens de **redação** (dependem do `.docx`/`.tex` da dissertação, ainda não disponível aqui):

6. Citar os 25 estudos da RSL (06); janela temporal e recorte Brasil (07); separar Metodologia/Método (09); justificar objetivos (20); citação Barak et al. 2017 (22); revisar "Big Data" (05); formatação/acrônimos/idioma (16–19); reformular slides (24).

7. **Seções textuais a redigir:** Ameaças à validade (consolidada); Ética e Termos de Uso da coleta (scraping); Reprodutibilidade (sementes, versões de bibliotecas).
