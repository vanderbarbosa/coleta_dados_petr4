---
name: comparativo-top10-ibovespa
description: o resultado nulo de direção (preço × preço+CVM) generalizado para as 10 maiores ações do Ibovespa — 60 testes, 9 com p<0,05 bruto, ZERO sobrevive a Bonferroni
metadata:
  type: project
---

**30/09 a 02/10/2026.** Mentoria do Prof. Julio: refazer, PAPEL POR PAPEL, a
comparação de direção (só preço × preço+CVM completo × preço+só Fato
Relevante × FR-vs-todos) para as 10 principais ações da bolsa, mais
investidores por ação e preço atual de cada uma. Ver [[escopo-e-ml-de-verdade]]
para o protocolo original (só PETR4) e [[distribuicao-capital-cvm-fre]] para
os investidores.

**Como os "10 principais" foram definidos — critério objetivo, não palpite:**
peso teórico OFICIAL do Ibovespa, consultado direto no endpoint da B3
(`sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay`, JSON,
data-base 02/10/2026), **restrito aos papéis que JÁ estão na pesquisa** — já
têm comunicado da CVM coletado/classificado e preço coletado. Por essa regra
ficaram de fora nomes grandes do índice sem dado coletado: WEGE3, AXIA3
(ex-Eletrobras, trocou de ticker), EMBJ3 (Embraer), CPLE3, ENEV3. **Os 10
usados:** VALE3, ITUB4, PETR4, SBSP3, BBDC4, B3SA3, ITSA4, BPAC11, BBAS3,
ABEV3. Carteira salva em `CVM/dados/ibovespa_carteira_teorica.csv`
(gitignored).

**Execução:** `CVM/22_comparativo_top10_acoes.py` generaliza o `20_preco_e_
cvm_sem_noticia.py` (mesmo protocolo Cap.3: GARCH(1,1) PRÓPRIO de cada papel,
SVM-RBF/XGBoost 300/depth3/lr0,05, split cronológico 60/15/25, McNemar) para
rodar nos 10 de uma vez → `dados/comparativo_top10_acoes.json`. **Notícia de
jornal (itens 3 e 7) continua bloqueada para os 10** — mesma razão do PETR4:
falta o corpus de notícias classificado nesta máquina.

**O resultado, e é o achado: o nulo de PETR4 se generaliza, de forma mais
forte.** 60 testes binomiais no total (10 papéis × 3 braços × 2 modelos). Ao
acaso, a 5%, esperam-se ~3 falsos positivos; apareceram 9. **Corrigindo por
Bonferroni (limiar 0,05/60 = 0,000833), ZERO sobrevive.** Maioria dos 9 "quase
significativos" é pior que o palpite fixo, não melhor (ex.: ITUB4 e SBSP3 só
com preço, XGBoost, caem abaixo da majoritária com p<0,05 — o modelo erra
mais que o acaso deveria permitir, não acerta mais). A única exceção acima da
majoritária foi ABEV3 preço+CVM(só FR) XGBoost, 55,44% vs 50,09%, p=0,0100 —
mas não passa em 0,000833, e o papel tem só 11 eventos de Fato Relevante em 9
anos: amostra pequena demais para confiar.

**Entrega:** `Mentorias/2026-09-16_Emerson_e_Julio/
18_Comparativo_Top10_Acoes.xlsx`, 11 abas (Visão Geral + 1 por papel), cada
aba com peso Ibovespa, preço atual, investidores, ações/investidor, a tabela
de direção e o McNemar — e a coluna "Sobrevive Bonferroni?" usando o limiar
dos 60 testes do conjunto todo, não 6 por aba (armadilha a evitar: corrigir
aba por aba mascararia a múltipla comparação real).

**Why:** responde ao pedido de 30/09 na íntegra, e é a validação externa mais
forte da pesquisa até aqui — o resultado nulo de direção não é peculiaridade
da PETR4, é um padrão em 10 dos papéis mais líquidos e mais pesados do
índice.

**How to apply:** ao relatar para a banca, citar os 60 testes e o Bonferroni
juntos — nunca o p de um papel isolado. Se pedirem os 5 que faltaram
(WEGE3/AXIA3/EMBJ3/CPLE3/ENEV3), é coleta nova de CVM+preço para eles, não
está feito. Relacionado: [[volatilidade-so-a-combinacao]],
[[como-ler-os-numeros]].
