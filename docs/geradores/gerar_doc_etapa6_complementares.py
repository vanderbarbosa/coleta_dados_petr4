# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Gerador da Documentação (ETAPA 6: Análises complementares)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Documento ABNT que consolida quatro análises que fecham lacunas da banca:
#   (A) ISM ponderado; (B) baseline e significância estatística; (C) causalidade
#   de Granger (Lead-Lag); (D) avaliação da previsão de volatilidade do GARCH.
#   Lê os resultados reais gerados por src/modelagem/06_analises_complementares.
#   Saída: docs/saida/Documentacao_Etapa6_Analises_Complementares_PETR4.docx
# ==============================================================================

import sys, json
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src" / "comum"))
import abnt_docx as abnt

PASTA = RAIZ / "Mestrado_PETR4"
SAIDA = RAIZ / "docs" / "saida" / "Documentacao_Etapa6_Analises_Complementares_PETR4.docx"

ism = pd.read_csv(PASTA / "resultados_ism_ponderado_petr4.csv")
gr = pd.read_csv(PASTA / "resultados_granger_petr4.csv")
with open(PASTA / "resultados_significancia_petr4.json", encoding="utf-8") as f:
    sig = json.load(f)
with open(PASTA / "resultados_volatilidade_petr4.json", encoding="utf-8") as f:
    vol = json.load(f)

def acc_de(var):
    return float(ism.loc[ism.Variante_ISM == var, "Acc_teste"].iloc[0])

a_sem = acc_de("(sem sentimento)"); a_simp = acc_de("ISM_simples")
a_conf = acc_de("ISM_confianca"); a_saldo = acc_de("ISM_saldo")

doc = abnt.novo_documento()
abnt.capa(
    doc,
    "Análises Complementares de Robustez e Significância",
    "Etapa 6 — ISM ponderado, significância estatística, causalidade de Granger e avaliação da volatilidade",
    "Vanderlei Barbosa da Silva",
    "Orientador: Prof. Dr. Julio Cesar Nievola",
    "Pontifícia Universidade Católica do Paraná — Mestrado em Informática",
    descricao=("Documento técnico-metodológico da dissertação “O Impacto do Sentimento de Notícias "
               "Financeiras na Previsão de Direção e Volatilidade do Ativo PETR4”. Reúne análises de "
               "robustez que respondem a exigências de rigor da banca: ponderação do índice de "
               "sentimento, comparação com linhas de base, testes de significância, causalidade "
               "preditiva (Lead-Lag) e avaliação direta da previsão de volatilidade."),
)

# 1
abnt.secao(doc, "1", "Apresentação")
abnt.paragrafo(doc,
 "Esta etapa complementa a modelagem (Etapas 4 e 4b) com quatro análises voltadas ao rigor e ao "
 "fechamento de lacunas: (i) a ponderação do Índice de Sentimento da Mídia (ISM); (ii) a comparação "
 "do modelo com linhas de base e a verificação de SIGNIFICÂNCIA estatística; (iii) o teste de "
 "CAUSALIDADE preditiva de Granger, que fundamenta empiricamente a hipótese Lead-Lag; e (iv) a "
 "avaliação direta da qualidade da previsão de VOLATILIDADE — a segunda dimensão do objeto desta "
 "dissertação. Todos os números provêm de execução reproduzível sobre os dados reais.")

# 2 — ISM ponderado
abnt.secao(doc, "2", "Ponderação do Índice de Sentimento da Mídia (ISM)")
abnt.paragrafo(doc,
 "O ISM diário pode ser construído de diferentes formas. Avaliaram-se três variantes, todas "
 "agregando as notícias de cada pregão (com alinhamento Lead-Lag das 17h):")
abnt.lista(doc, [
 "**ISM simples (atual):** média aritmética dos índices de sentimento das notícias do dia (cada índice é polaridade × confiança).",
 "**ISM ponderado por confiança:** média da polaridade ponderada pela confiança do classificador — notícias classificadas com maior certeza pesam mais.",
 "**ISM de saldo (voto):** diferença entre o número de notícias positivas e negativas, dividida pelo total — ignora a confiança, contando apenas “votos”.",
])
abnt.paragrafo(doc,
 f"A Tabela 1 apresenta o efeito de cada variante na previsão de direção (acurácia de teste, mesmo "
 f"protocolo cronológico). O resultado é esclarecedor: a inclusão do sentimento eleva a acurácia de "
 f"{a_sem:.2f}% (sem sentimento) para {a_simp:.2f}% (ISM simples), e a ponderação por confiança "
 f"produz o MELHOR desempenho ({a_conf:.2f}%). Já a variante de saldo, que ignora a confiança, "
 f"praticamente ANULA o ganho ({a_saldo:.2f}%), retornando ao patamar do acaso.")
abnt.tabela_abnt(doc, "1", "Efeito da construção do ISM na previsão de direção (teste)",
 ["Construção do ISM", "Acurácia teste (%)", "AUC teste"],
 [[r["Variante_ISM"], f'{r["Acc_teste"]:.2f}', f'{r["AUC_teste"]:.4f}'] for _, r in ism.iterrows()])
abnt.paragrafo(doc,
 "A interpretação é direta e teoricamente relevante: o sinal preditivo está na INTENSIDADE do "
 "sentimento (a confiança do modelo), e não na mera contagem de notícias positivas versus negativas. "
 "Ponderar pela confiança — dar mais peso às notícias inequívocas — é, portanto, a construção "
 "recomendada, ainda que o ganho sobre o ISM simples seja modesto (as três variantes correlacionam-se "
 "acima de 0,99). Esse achado reforça a escolha de um classificador que fornece um escore de "
 "confiança calibrado (FinBERT-PT-BR), e não apenas um rótulo.")

# 3 — Baseline e significância
abnt.secao(doc, "3", "Linhas de base e significância estatística")
abnt.paragrafo(doc,
 "Para que a acurácia tenha sentido, ela precisa ser confrontada com referências ingênuas e ter sua "
 "significância testada — exigência de rigor da banca. Adotam-se duas linhas de base: a CLASSE "
 "MAJORITÁRIA (prever sempre a direção mais frequente no treino) e o modelo de APENAS PREÇOS.")
abnt.tabela_abnt(doc, "2", "Desempenho frente às linhas de base (conjunto de teste)",
 ["Preditor", "Acurácia teste (%)"],
 [["Classe majoritária (sempre alta)", f'{sig["acc_classe_majoritaria"]:.2f}'],
  ["Apenas preços (retorno + volatilidade)", f'{sig["acc_apenas_precos"]:.2f}'],
  ["Data Fusion (preços + sentimento)", f'{sig["acc_data_fusion"]:.2f}']])
abnt.paragrafo(doc,
 f"Sobre {sig['n_teste']} pregões de teste, o Data Fusion acertou {sig['acertos_fusion']}, "
 f"superando tanto a classe majoritária ({sig['acc_classe_majoritaria']:.2f}%) quanto o modelo de "
 f"apenas preços ({sig['acc_apenas_precos']:.2f}%). Dois testes formais foram aplicados:")
abnt.lista(doc, [
 f"**Teste binomial (vs. acaso de 50%):** p = {sig['p_binomial_vs_50']:.4f}. Como p < 0,05, "
 "rejeita-se a hipótese de que o acerto do Data Fusion seja fruto do acaso: o modelo é "
 "estatisticamente superior ao palpite aleatório.",
 f"**Teste de McNemar (Data Fusion vs. apenas preços):** p = {sig['p_mcnemar_fusion_vs_precos']:.4f}. "
 f"Dos pregões discordantes, o Data Fusion acertou {sig['mcnemar_fusion_acerta_precos_erra']} casos "
 f"em que o modelo de preços errou, contra {sig['mcnemar_precos_acerta_fusion_erra']} no sentido "
 "oposto. O valor de p situa-se no limiar de 5%, indicando vantagem do sentimento de magnitude "
 "modesta e significância marginal — resultado reportado com transparência, sem superestimação.",
])

# 4 — Granger
abnt.secao(doc, "4", "Causalidade de Granger: fundamento empírico do Lead-Lag")
abnt.paragrafo(doc,
 "A exigência da banca quanto ao horário exato das notícias visava possibilitar o teste da relação "
 "Lead-Lag (a notícia ANTECEDE o movimento de mercado). Operacionaliza-se essa relação pelo teste de "
 "causalidade de Granger, que verifica se os valores passados do sentimento ajudam a prever o "
 "retorno e a volatilidade, além do que a própria série já prevê. A Tabela 3 traz os p-valores por "
 "defasagem.")
abnt.tabela_abnt(doc, "3", "Causalidade de Granger do sentimento (p-valores)",
 ["Defasagem (dias)", "Sentimento → Retorno", "Sentimento → Volatilidade"],
 [[str(int(r["Defasagem_dias"])), f'{r["p_sent_para_retorno"]:.4f}', f'{r["p_sent_para_volatilidade"]:.4f}']
  for _, r in gr.iterrows()])
p_ret1 = float(gr.loc[gr.Defasagem_dias == 1, "p_sent_para_retorno"].iloc[0])
abnt.paragrafo(doc,
 f"Dois achados se destacam. Para o RETORNO, há causalidade significativa na defasagem de 1 dia "
 f"(p = {p_ret1:.4f} < 0,05), que se DISSIPA nas defasagens seguintes — padrão coerente com a "
 "hipótese Lead-Lag e com a quase-eficiência do mercado: a informação da notícia é incorporada "
 "rapidamente ao preço. Para a VOLATILIDADE, a causalidade é fortíssima e PERSISTENTE em todas as "
 "defasagens (p ≈ 0,000), evidência de que o sentimento das notícias antecede a turbulência do "
 "mercado de forma muito mais robusta do que antecede a direção. Esse resultado sustenta "
 "empiricamente a relevância da segunda dimensão do título da dissertação — a volatilidade.")

# 5 — Volatilidade
abnt.secao(doc, "5", "Avaliação direta da previsão de volatilidade (GARCH)")
abnt.paragrafo(doc,
 "Como o objeto da pesquisa inclui a VOLATILIDADE, avalia-se diretamente a qualidade da previsão do "
 "GARCH(1,1), confrontando a volatilidade condicional prevista com a volatilidade realizada "
 "(aproximada pelo valor absoluto do retorno diário). Empregam-se métricas usuais da literatura: "
 "erro absoluto médio (MAE), raiz do erro quadrático médio (RMSE), a função de perda QLIKE e a "
 "regressão de Mincer-Zarnowitz (realizada = a + b × prevista).")
abnt.tabela_abnt(doc, "4", "Qualidade da previsão de volatilidade do GARCH(1,1)",
 ["Métrica", "Valor", "Leitura"],
 [["Correlação (prev. × real.)", f'{vol["correlacao_prev_real"]:.3f}', "Associação positiva moderada"],
  ["MAE", f'{vol["MAE"]:.3f}', "Erro médio em pontos percentuais de |retorno|"],
  ["RMSE", f'{vol["RMSE"]:.3f}', "Penaliza mais os grandes erros"],
  ["QLIKE", f'{vol["QLIKE"]:.3f}', "Perda assimétrica padrão para volatilidade"],
  ["Mincer-Zarnowitz b", f'{vol["MZ_coef_b"]:.3f}', "Ideal = 1; <1 indica leve sobre-reação do modelo"],
  ["Mincer-Zarnowitz R²", f'{vol["MZ_R2"]:.3f}', "Fração da variação realizada explicada"]])
abnt.paragrafo(doc,
 f"A previsão de volatilidade do GARCH apresenta correlação positiva moderada com a realizada "
 f"(r = {vol['correlacao_prev_real']:.3f}) e um coeficiente de Mincer-Zarnowitz de "
 f"{vol['MZ_coef_b']:.3f} (próximo, porém abaixo, do valor ideal 1, indicando leve viés). O R² "
 f"modesto ({vol['MZ_R2']:.3f}) é esperado quando se usa |retorno| diário como proxy — um estimador "
 "ruidoso da volatilidade latente. Em conjunto com a forte causalidade de Granger do sentimento "
 "sobre a volatilidade (Seção 4), conclui-se que o canal de VOLATILIDADE é, nesta pesquisa, onde o "
 "sentimento exerce influência mais nítida e estável — direção promissora para o aprofundamento no "
 "doutorado.")

# 6 — Síntese
abnt.secao(doc, "6", "Síntese das contribuições desta etapa")
abnt.lista(doc, [
 f"A ponderação do ISM por confiança é a melhor construção ({a_conf:.2f}%); o sinal está na intensidade, não na contagem de votos.",
 f"O Data Fusion supera o acaso com significância estatística (binomial p = {sig['p_binomial_vs_50']:.4f}) e supera as linhas de base ingênuas.",
 "O sentimento Granger-causa o retorno em t+1 (efeito curto, coerente com eficiência) e a volatilidade de forma forte e persistente — fundamento empírico do Lead-Lag.",
 "A previsão de volatilidade do GARCH é informativa, ainda que limitada pela proxy diária; a volatilidade é o canal mais promissor do sentimento.",
])

abnt.referencias(doc, "7", [
 "GRANGER, C. W. J. Investigating causal relations by econometric models and cross-spectral methods. Econometrica, v. 37, n. 3, p. 424-438, 1969.",
 "MINCER, J.; ZARNOWITZ, V. The evaluation of economic forecasts. In: Economic forecasts and expectations. NBER, 1969.",
 "PATTON, A. J. Volatility forecast comparison using imperfect volatility proxies. Journal of Econometrics, v. 160, n. 1, p. 246-256, 2011.",
 "DIEBOLD, F. X.; MARIANO, R. S. Comparing predictive accuracy. Journal of Business & Economic Statistics, v. 13, n. 3, p. 253-263, 1995.",
])

doc.save(SAIDA)
print(f"[OK] Documento ABNT gerado: {SAIDA}")
