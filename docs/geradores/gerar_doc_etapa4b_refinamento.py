# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Gerador da Documentação (ETAPA 4b: Refinamento dos modelos)
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Documento ABNT que detalha as bases de treino/validação/teste, a engenharia
#   de atributos, o protocolo experimental e a JORNADA de refinamento (E0..E8)
#   com os resultados reais de cada experimento — incluindo a conclusão honesta
#   sobre sobreajuste e parcimônia.
#   Saída: docs/saida/Documentacao_Etapa4b_Refinamento_PETR4.docx
# ==============================================================================

import sys, json
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src" / "comum"))
import abnt_docx as abnt

PASTA = RAIZ / "Mestrado_PETR4"
SAIDA = RAIZ / "docs" / "saida" / "Documentacao_Etapa4b_Refinamento_PETR4.docx"

# ── Carrega resultados reais do experimento ───────────────────────────────────
res = pd.read_csv(PASTA / "resultados_refinamento_petr4.csv")
with open(PASTA / "meta_refinamento_petr4.json", encoding="utf-8") as f:
    meta = json.load(f)

# Estatísticas das três bases (a partir da matriz enriquecida)
dfm = pd.read_csv(PASTA / "base_master_enriquecida_petr4.csv", parse_dates=["Date"])
n = len(dfm); i_tr, i_va = int(n * 0.60), int(n * 0.75)
tr, va, te = dfm.iloc[:i_tr], dfm.iloc[i_tr:i_va], dfm.iloc[i_va:]
def info(d):
    return (str(d["Date"].min().date()), str(d["Date"].max().date()),
            len(d), f"{d['Alvo'].mean()*100:.1f}%")

baseline = res.loc[res.Experimento == "E0", "Acc_teste"].iloc[0]
melhor_teste = res["Acc_teste"].apply(lambda x: float(x) if x != "—" else -1).max()

# ── Documento ─────────────────────────────────────────────────────────────────
doc = abnt.novo_documento()
abnt.capa(
    doc,
    "Refinamento e Avaliação do Desempenho Preditivo da PETR4",
    "Etapa 4b — Bases de treino/validação/teste, engenharia de atributos e jornada experimental",
    "Vanderlei Barbosa da Silva",
    "Orientador: Prof. Dr. Julio Cesar Nievola",
    "Pontifícia Universidade Católica do Paraná — Mestrado em Informática",
    descricao=("Documento técnico-metodológico da dissertação “O Impacto do Sentimento de Notícias "
               "Financeiras na Previsão de Direção e Volatilidade do Ativo PETR4”. Aprofunda a "
               "modelagem da Etapa 4 com um estudo controlado de refinamento, detalhando as bases de "
               "dados, a engenharia de atributos e o resultado de cada experimento."),
)

# 1
abnt.secao(doc, "1", "Objetivo do refinamento")
abnt.paragrafo(doc,
 "A Etapa 4 estabeleceu que a fusão de preços, volatilidade e sentimento (Data Fusion) supera, de "
 "forma modesta, o modelo baseado apenas em preços. Esta etapa investiga, de modo controlado e "
 "reproduzível, se é possível ELEVAR o desempenho preditivo fora da amostra por meio de quatro "
 "estratégias: (i) enriquecimento de atributos; (ii) seleção de variáveis; (iii) modelos "
 "alternativos; e (iv) ajuste de hiperparâmetros e do limiar de decisão. O critério de êxito é "
 "rigoroso: melhora da acurácia no conjunto de TESTE (dados nunca vistos), e não na validação.")

# 2 — Bases
abnt.secao(doc, "2", "Bases de treino, validação e teste")
abnt.paragrafo(doc,
 "Para impedir o vazamento de informação futura, a divisão é estritamente CRONOLÓGICA, na proporção "
 "60/15/25 (treino/validação/teste). O treino ajusta os parâmetros; a validação serve à SELEÇÃO de "
 "atributos, modelos e hiperparâmetros; o teste é consultado UMA ÚNICA VEZ, ao final, para a medida "
 "de desempenho não enviesada. A Tabela 1 descreve as três partições.")
t0, t1, tn, tb = info(tr); v0, v1, vn, vb = info(va); e0, e1, en, eb = info(te)
abnt.tabela_abnt(doc, "1", "Composição das bases (divisão cronológica 60/15/25)",
 ["Partição", "Início", "Fim", "Pregões", "% de altas", "Papel"],
 [["Treino", t0, t1, str(tn), tb, "Ajuste dos parâmetros do modelo"],
  ["Validação", v0, v1, str(vn), vb, "Seleção de atributos, modelo e hiperparâmetros"],
  ["Teste", e0, e1, str(en), eb, "Avaliação final, única e não enviesada"]])
abnt.paragrafo(doc,
 f"Observa-se desde já um ponto metodologicamente crítico: a proporção de pregões de alta difere "
 f"entre validação ({vb}) e teste ({eb}). Essa MUDANÇA DE REGIME entre os períodos é determinante "
 "para interpretar os resultados adiante, pois penaliza modelos que se especializam no padrão da "
 "validação.")

# 3 — Engenharia de atributos
abnt.secao(doc, "3", "Engenharia de atributos")
abnt.paragrafo(doc,
 "Partindo dos três atributos do Data Fusion (retorno, volatilidade GARCH e sentimento agregado, "
 "todos defasados em t−1), construíram-se três famílias adicionais de variáveis, igualmente "
 "defasadas para preservar a causalidade temporal:")
abnt.lista(doc, [
 "**Sentimento por categoria (7 séries):** o índice de sentimento desagregado nas sete categorias temáticas (empresa, mercado de petróleo, geopolítica, infraestrutura, sanções, governança e macro/energia), permitindo ao modelo ponderar cada vetor isoladamente.",
 "**Intensidade e dispersão do noticiário:** volume diário de notícias (em escala logarítmica), sentimento líquido (positivas − negativas) e magnitude absoluta do sentimento, capturando o grau de atenção e de polarização da mídia.",
 "**Dinâmica temporal:** médias móveis de 3 e 5 dias do sentimento, desvio-padrão de 5 dias (instabilidade do humor de mercado) e média móvel de 5 dias da volatilidade, capturando tendências e regimes de curto prazo.",
])

# 4 — Protocolo
abnt.secao(doc, "4", "Protocolo experimental")
abnt.paragrafo(doc,
 "Cada experimento segue o mesmo rito: treina no treino, é selecionado/ajustado na validação e é "
 "avaliado uma única vez no teste. Os experimentos são incrementais (E0 a E8), de modo que o efeito "
 "de cada decisão seja isolável. A métrica primária é a acurácia; reporta-se também a AUC-ROC.")

# 5 — Resultados
abnt.secao(doc, "5", "Resultados por experimento")
abnt.paragrafo(doc,
 "A Tabela 2 apresenta o resultado real de cada experimento, na validação e no teste. A coluna de "
 "teste é a única que importa para o critério de êxito.")
linhas = []
for _, r in res.iterrows():
    linhas.append([str(r["Experimento"]), str(r["Descrição"]), str(r["Nº_features"]),
                   str(r["Acc_validação"]), str(r["Acc_teste"]), str(r["AUC_teste"])])
abnt.tabela_abnt(doc, "2", "Resultado de cada experimento de refinamento",
 ["Exp.", "Estratégia", "Nº atrib.", "Acc. validação (%)", "Acc. teste (%)", "AUC teste"], linhas)

# 6 — Análise honesta
abnt.secao(doc, "6", "Análise: o sobreajuste à validação")
abnt.paragrafo(doc,
 f"O resultado é tão instrutivo quanto contraintuitivo. O baseline parcimonioso (E0), com apenas "
 f"três atributos, obteve a MELHOR acurácia de teste de todo o estudo ({baseline:.2f}%). Cada "
 "tentativa de sofisticação — adicionar sentimento por categoria, volume, dinâmica temporal, "
 "selecionar atributos por importância, trocar de modelo, ajustar hiperparâmetros e calibrar o "
 "limiar — ELEVOU a acurácia na validação (chegando à casa dos 57–58%), mas DEGRADOU a acurácia no "
 "teste. Esse padrão é a assinatura clássica do sobreajuste: o procedimento de seleção encontra, na "
 "validação, regularidades que não se sustentam no período seguinte.")
abnt.paragrafo(doc,
 "Duas causas se somam. A primeira é estatística: com um sinal preditivo genuíno, porém fraco "
 "(coerente com a quase-eficiência do mercado), aumentar a capacidade do modelo serve principalmente "
 "para memorizar ruído. A segunda é a mudança de regime documentada na Seção 2 — a validação tem "
 "maior proporção de altas que o teste —, de modo que otimizar para a validação orienta o modelo na "
 "direção errada para o teste. A validação cruzada walk-forward (E8), que reestima o modelo ao longo "
 "do tempo, confirma um desempenho médio igualmente modesto, reforçando que o ganho aparente da "
 "sofisticação é ilusório.")

# 7 — Conclusão
abnt.secao(doc, "7", "Conclusão e implicações para a pesquisa")
abnt.lista(doc, [
 f"**A parcimônia vence.** O modelo Data Fusion de três atributos é o mais robusto fora da amostra ({baseline:.2f}% de acurácia de teste); a complexidade adicional não se traduz em ganho real.",
 "**O sinal do sentimento é real, porém modesto.** Ele contribui acima do acaso, mas em magnitude compatível com a eficiência informacional do mercado — resultado honesto, alinhado à literatura.",
 "**Rigor metodológico.** Avaliar apenas na validação teria levado à conclusão falsa de um modelo de ~58%; a separação estrita de um conjunto de teste, consultado uma única vez, evitou esse erro.",
 "**Não há inflação de resultados.** Reporta-se o melhor desempenho efetivamente generalizável, e não o número mais alto obtido em qualquer partição.",
])

# 8 — Trabalhos futuros
abnt.secao(doc, "8", "Direções para ganho efetivo (trabalhos futuros)")
abnt.paragrafo(doc,
 "O estudo delimita onde NÃO está o ganho (mais atributos e mais ajuste) e aponta caminhos mais "
 "promissores, a serem investigados:")
abnt.lista(doc, [
 "**Ajuste fino do FinBERT-PT-BR ao corpus da pesquisa**, com um conjunto-ouro rotulado, elevando a qualidade do próprio sinal de sentimento (a montante), em vez de sofisticar o classificador a jusante.",
 "**Modelagem sensível a regime** (por exemplo, detecção de mudança de regime de volatilidade), que enderece diretamente a heterogeneidade entre períodos observada na Seção 2.",
 "**Previsão de magnitude da volatilidade** (e não apenas a direção), em que o sentimento tende a ter poder explicativo maior e mais estável, conforme a literatura.",
 "**Janelas intradiárias**, aproveitando a marcação temporal precisa das notícias para medir a reação de mercado em horizontes curtos.",
])

abnt.referencias(doc, "9", [
 "CHEN, T.; GUESTRIN, C. XGBoost: a scalable tree boosting system. In: KDD, 2016. p. 785-794.",
 "HASTIE, T.; TIBSHIRANI, R.; FRIEDMAN, J. The elements of statistical learning. 2. ed. New York: Springer, 2009.",
 "FAMA, E. F. Efficient capital markets: a review of theory and empirical work. The Journal of Finance, v. 25, n. 2, p. 383-417, 1970.",
 "SANTOS, L. L.; BIANCHI, R. A. C.; COSTA, A. H. R. FinBERT-PT-BR: Análise de Sentimentos de Textos em Português do Mercado Financeiro. In: Anais do II BWAIF. Porto Alegre: SBC, 2023. p. 144-155.",
])

doc.save(SAIDA)
print(f"[OK] Documento ABNT gerado: {SAIDA}")
print(f"     Baseline (E0) teste = {baseline:.2f}%  |  melhor teste do estudo = {melhor_teste:.2f}%")
