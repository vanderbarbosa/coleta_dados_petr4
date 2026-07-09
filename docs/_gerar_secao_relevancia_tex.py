# -*- coding: utf-8 -*-
# Gera a subseção LaTeX do experimento de FILTRO DE RELEVÂNCIA (dados reais).
from pathlib import Path
import pandas as pd
RAIZ = Path(__file__).resolve().parents[1]
DS = RAIZ / "datasets_refino"
TEX = RAIZ / "Exame_qualificacao" / "PesquisaMestrado_Qualificacao" / "capitulos" / "4e-filtro-relevancia.tex"
DATA = "2026-07-05"
res = pd.read_csv(DS / f"resultados_relevancia_{DATA}.csv")
NOME = {"todas_apos17h": "Todas (após 17h)", "relevante_direta": "Relevantes (menção direta)",
        "categoria_CAT1_CAT2": "Categorias CAT1+CAT2"}
base = res["baseline_maj"].iloc[0]

def v(nome, col):
    return res.loc[res["variante"] == nome, col].iloc[0]

linhas = []
for _, r in res.iterrows():
    sup = "sim" if r["supera_baseline"] else "não"
    linhas.append(f"{NOME.get(r['variante'], r['variante'])} & {r['cobertura_dias_com_noticia']:.2f} & "
                  f"{r['acuracia_teste']:.2f} & {r['auc']:.3f} & {r['p_granger_sent_para_vol_min']:.4f} & {sup} \\\\")

tex = r"""% Gerado por docs/_gerar_secao_relevancia_tex.py — dados reais (""" + DATA + r""").
\subsection{Filtro de relevância: reordenando o \textit{pipeline}}
\label{sec:filtro_relevancia}

Uma hipótese levantada na análise dos resultados é a de que a baixa acurácia direcional
decorreria da ausência de um passo de \textbf{filtragem de relevância}: o índice de sentimento
diário é hoje a média do sentimento de \emph{todas} as notícias coletadas no dia, o que poderia
diluir o sinal com notícias apenas tangencialmente ligadas à Petrobras. Para testar essa hipótese
de forma controlada, reordenou-se o \textit{pipeline} na sequência sugerida --- coleta, seleção das
notícias publicadas após o fechamento (17h), \textbf{filtro de relevância} e, só então, predição ---
e reconstruiu-se o sinal de sentimento sob três critérios: todas as notícias após as 17h; apenas as
que mencionam diretamente a empresa ou a \textit{commodity} (Petrobras, PETR4, petróleo, Brent, WTI,
OPEP, entre outros termos); e apenas as duas categorias mais diretas (Empresa e Mercado de Petróleo).
Das """ + f"{int(v('todas_apos17h','n_teste'))}" + r""" observações de teste, o filtro de menção direta
retém cerca de 23\% das notícias após as 17h. O modelo \textit{XGBoost} foi re-treinado, validado e
testado para cada critério, sob divisão cronológica 60/15/25 no período 2018--2025. A
Tabela~\ref{tab:filtro_relevancia} apresenta os resultados.

\begin{table}[htpb]
\centering
\caption{Efeito do filtro de relevância sobre a previsão da direção da PETR4 (\textit{XGBoost}, teste cronológico). \textit{Baseline} de classe majoritária: """ + f"{base:.2f}" + r"""\%.}
\label{tab:filtro_relevancia}
\begin{tabular}{l c c c c c}
\hline
\textbf{Sinal de sentimento} & \textbf{Cobertura} & \textbf{Acur.\ (\%)} & \textbf{AUC} & \textbf{$p$ Granger} & \textbf{$>$ base} \\ \hline
""" + "\n".join(linhas) + r"""
\hline
\end{tabular}
\vspace{0.2cm}
{\small \\ Fonte: Elaborado pelo autor (\texttt{datasets\_refino/gerar\_pipeline\_relevancia.py}, """ + DATA + r"""). Cobertura = fração de pregões com ao menos uma notícia; $p$ Granger = menor $p$-valor da causalidade sentimento~$\rightarrow$~volatilidade nas defasagens de 1 a 5 dias.}
\end{table}

O resultado é esclarecedor e, embora contrarie a intuição inicial, reforça a tese central. A
filtragem de relevância \textbf{não elevou a acurácia direcional}: o sinal de menção direta produziu
exatamente a mesma acurácia de teste (""" + f"{v('relevante_direta','acuracia_teste'):.2f}".replace(".", ",") + r"""\%)
do sinal sem filtro, com melhora apenas marginal na ordenação (AUC de
""" + f"{v('todas_apos17h','auc'):.3f}".replace(".", ",") + r""" para """ + f"{v('relevante_direta','auc'):.3f}".replace(".", ",") + r"""),
ao passo que o filtro por categoria chegou a reduzir a acurácia. Três fatores explicam o achado.
Primeiro, a cobertura permanece próxima de cem por cento --- mesmo após a filtragem, quase todos os
pregões mantêm ao menos uma notícia relevante, de modo que a \emph{média} diária pouco se altera.
Segundo, o corpus já nasce filtrado pela taxonomia de 152 termos, o que limita o ganho de uma segunda
filtragem. Terceiro, e mais importante, o gargalo da previsão de direção não é o ruído do sentimento,
mas a própria \textbf{eficiência do mercado}: a direção diária de um ativo líquido é quase um passeio
aleatório, e nenhuma depuração do sinal textual a torna previsível. É digno de nota, contudo, que a
relação \textbf{sentimento~$\rightarrow$~volatilidade} permanece estatisticamente significativa sob
todos os critérios (teste de Granger, $p < 0{,}02$ em todos os casos), o que confirma, mais uma vez,
que o sentimento informa o risco muito mais do que a direção. Do ponto de vista prático, o conjunto
filtrado é menor, mais limpo e mais interpretável, sendo preferível para a linha de estudo de eventos
e de volatilidade, ainda que não eleve a acurácia direcional.

\subsection{Direções para elevar a acurácia e a acertividade}
\label{sec:direcoes_melhoria}

A partir dos experimentos, delineiam-se caminhos promissores, priorizados pela razão entre ganho
esperado e custo. (i) \textbf{Deslocar o alvo para a volatilidade}: como o sentimento a antecede de
forma robusta, prever a \emph{magnitude} da volatilidade (e não apenas a direção) é a via de maior
retorno científico. (ii) \textbf{Rótulo com zona morta}: descartar do treino os dias de variação
próxima de zero, prevendo apenas movimentos economicamente relevantes, reduz o ruído do alvo. (iii)
\textbf{Modelo em dois estágios}: primeiro identificar os dias de \emph{choque informacional} (os
cerca de 15\% que coincidem com rupturas de estresse no GARCH) e, só neles, aplicar o preditor
direcional. (iv) \textbf{Sentimento direcionado ao ativo} (\textit{aspect-based}): distinguir o que é
bom \emph{para a Petrobras} do que é bom para o mercado em geral --- a leitura econômica setorial
(Kilian; Hamilton) como atributo explícito. (v) \textbf{Ponderar a notícia pela reação de mercado}
(saliência) em vez de filtro binário. (vi) \textbf{Encoder mais forte} (Albertina PT-BR), pendente de
rotulagem do conjunto-ouro e de \textit{hardware}. (vii) \textbf{Maior frequência} (intradiário),
na linha de \citeonline{gros-klusmann_when_2011} e \citeonline{carta_multi-dqn_2021}, em que a
previsibilidade é reconhecidamente maior.
"""
TEX.write_text(tex, encoding="utf-8")
print("✓", TEX.name, "| baseline", base, "| relevante acc", v("relevante_direta", "acuracia_teste"))
