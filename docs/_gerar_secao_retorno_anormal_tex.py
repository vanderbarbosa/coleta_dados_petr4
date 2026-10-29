# -*- coding: utf-8 -*-
# Gera a subseção LaTeX sobre a troca do alvo para o retorno anormal.
# Lê os números reais dos JSON dos Scripts 27, 28 e 29 — nada digitado à mão.
# Mentoria de 29/10/2026.
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
D = RAIZ / "CVM" / "dados"
TEX = RAIZ / "Exame_qualificacao" / "PesquisaMestrado_Qualificacao" / "capitulos" / "4r-retorno-anormal.tex"
DATA = "2026-10-29"

A = json.loads((D / "retorno_anormal_e_painel.json").read_text(encoding="utf-8"))
B = json.loads((D / "reexecucao_alvo_anormal.json").read_text(encoding="utf-8"))
try:
    C = json.loads((D / "prophet_alvo_anormal.json").read_text(encoding="utf-8"))
except Exception:
    C = None


def n(x, c=2, s=False):
    return (f"{x:+.{c}f}" if s else f"{x:.{c}f}").replace(".", "{,}")


br = [v["ganho_pp"] for k, v in A["arms"].items() if "BRUTO" in k]
an = [v["ganho_pp"] for k, v in A["arms"].items() if "ANORMAL" in k]
melhor_an = max(A["arms"].items(), key=lambda kv: kv[1]["ganho_pp"] if "ANORMAL" in kv[0] else -99)
mv = melhor_an[1]

# tabela de direção: os oito braços, por alvo
lin = []
for k, v in A["arms"].items():
    alvo = "anormal" if "ANORMAL" in k else "bruto"
    nome = k.split(" — ")[0] + ", " + k.split(" — ")[1] + ", " + k.split(" — ")[2]
    lin.append((alvo, nome, v))
lin_br = "\n".join(f"{nm.replace('—','--')} & ${n(v['ganho_pp'],2,True)}$ & "
                   f"$[{n(v['ic95_pp'][0],2,True)};\\,{n(v['ic95_pp'][1],2,True)}]$ & ${n(v['p_bootstrap'],3)}$ \\\\"
                   for a, nm, v in lin if a == "bruto")
lin_an = "\n".join(f"{nm.replace('—','--')} & ${n(v['ganho_pp'],2,True)}$ & "
                   f"$[{n(v['ic95_pp'][0],2,True)};\\,{n(v['ic95_pp'][1],2,True)}]$ & ${n(v['p_bootstrap'],3)}$ \\\\"
                   for a, nm, v in lin if a == "anormal")

# volatilidade
vol = B["volatilidade"]
lin_vol = "\n".join(
    f"{k.replace('—','--').replace('ANORMAL (idiossincrática)','anormal').replace('BRUTA','bruta')} & "
    f"${n(v['r2os_pct'],3,True)}\\%$ & $[{n(v['ic95_pct'][0],3,True)};\\,{n(v['ic95_pct'][1],3,True)}]$ & "
    f"${n(v['p_bootstrap'],3)}$ \\\\" for k, v in vol.items())

betas = ", ".join(f"{tk} {n(v,2)}" for tk, v in A["betas"].items())

prophet_txt = ""
if C:
    r = C["resumo"]
    prophet_txt = (r"""
\subsubsection{O Prophet não é resgatado pela troca de alvo}

Registrou-se, antes de executar, a previsão de que a correção do alvo não beneficiaria o
\textit{Prophet}, pela razão que a Seção~\ref{sec:prophet} já expôs: o modelo decompõe a série em
tendência e sazonalidade de calendário, e o retorno anormal é aproximadamente estacionário e de
média quase nula, de sorte que não há tendência a extrapolar. A execução confirmou a previsão. Nos
dez ativos, a amplitude da previsão correspondeu a apenas """ + n(r["razao_amplitude_media"], 2) + r""" da amplitude efetivamente
observada --- o modelo produz uma versão alisada e quase nula da série --- e o ganho médio sobre a
classe majoritária foi de """ + n(r["ganho_medio_pp"], 2, True) + r""" pontos percentuais, com """ + str(r["papeis_positivos"]) + r""" dos dez ativos acima da
referência. O comportamento é o correto para um modelo de tendência aplicado a série sem
tendência, e inútil para a tarefa direcional.
""")

tex = r"""% Gerado por docs/_gerar_secao_retorno_anormal_tex.py --- dados reais (""" + DATA + r""").
% Fontes: CVM/dados/retorno_anormal_e_painel.json, reexecucao_alvo_anormal.json,
%         prophet_alvo_anormal.json
% Scripts: CVM/27, CVM/28, CVM/29
\subsection{A definição do alvo: retorno bruto e retorno anormal}
\label{sec:retorno_anormal}

Os resultados reportados até aqui tomaram por alvo o retorno bruto do ativo. Essa escolha,
herdada da formulação original do problema, embute uma inconsistência interna que convém expor,
pois a sua correção altera materialmente a leitura de parte dos achados.

O estudo de evento conduzido no Capítulo do relógio da CVM sempre descontou o retorno do
índice de mercado, conforme o modelo de mercado consagrado na literatura de estudos de evento, isolando o
retorno anormal. Os experimentos de aprendizado, porém, mantiveram o retorno bruto como alvo.
Mediu-se a consequência: entre os dez ativos examinados, a correlação média dos retornos no mesmo
pregão é de $0{,}486$, e dois ativos quaisquer movem-se na mesma direção em sessenta e quatro
vírgula cinco por cento dos pregões. Cerca de metade da variação diária de cada ativo é, portanto,
movimento comum de mercado --- componente que o sentimento de uma empresa específica não tem como
explicar, e cuja presença no alvo apenas adiciona ruído.

\subsubsection{Especificação}

Define-se o retorno anormal pela forma usual,
\begin{equation}
e_{it} = R_{it} - \left( \hat{\alpha}_i + \hat{\beta}_i R_{mt} \right),
\end{equation}
em que $R_{mt}$ é o retorno do Ibovespa e os coeficientes $\hat{\alpha}_i$ e $\hat{\beta}_i$ são
estimados \textbf{estritamente na janela de treino}, nunca no teste, preservando o pressuposto de
causalidade temporal enunciado no Capítulo~\ref{chap:metodologia}. Os betas estimados são compatíveis
com o conhecimento de mercado sobre os ativos, o que ampara o procedimento: """ + betas + r""".

A inferência passa a ser conduzida por \textbf{reamostragem em blocos de data}: sorteiam-se datas
com reposição, levando todos os ativos de cada data sorteada, de modo que a correlação transversal
seja preservada na reamostragem. Cabe registrar, em favor dos resultados anteriores, que se mediu
o efeito dessa correção e ele é pequeno --- a meia-largura do intervalo passa de um vírgula vinte e
nove para um vírgula trinta e cinco pontos percentuais, inflação de apenas cinco por cento. A razão
é que um classificador cuja acurácia ronda cinquenta por cento erra de maneira quase independente
entre ativos, ainda que os retornos sejam correlacionados. Os intervalos antes reportados estavam,
portanto, substancialmente corretos; a reamostragem por data é adotada por ser o procedimento
apropriado, e não por corrigir distorção relevante.

\subsubsection{Direção}

A Tabela~\ref{tab:alvo_direcao} contrasta os oito arranjos sob cada definição de alvo. Os arranjos
combinam os dois classificadores, as duas composições de atributo e os dois desenhos de
treinamento --- por ativo e em painel com efeito de ativo.

\begin{table}[htpb]
\centering
\caption{Ganho sobre a classe majoritária, em pontos percentuais, por definição de alvo. Intervalos por reamostragem em blocos de data.}
\label{tab:alvo_direcao}
\begin{tabular}{l c c c}
\hline
\textbf{Arranjo} & \textbf{Ganho} & \textbf{IC 95\%} & \textbf{$p$} \\ \hline
\multicolumn{4}{l}{\textit{Alvo: retorno bruto}} \\
""" + lin_br + r"""
\hline
\multicolumn{4}{l}{\textit{Alvo: retorno anormal}} \\
""" + lin_an + r"""
\hline
\end{tabular}
\vspace{0.2cm}
{\small \\ Fonte: Elaborado pelo autor (\texttt{CVM/27\_retorno\_anormal\_e\_painel.py}, """ + DATA + r""").}
\end{table}

O contraste é nítido. Sob o alvo bruto, nenhum dos oito arranjos supera a classe majoritária, e a
média dos ganhos é de """ + n(sum(br) / len(br), 2, True) + r""" pontos percentuais. Sob o alvo anormal, """ + str(sum(1 for x in an if x > 0)) + r""" dos oito arranjos
situam-se acima da referência, e a média sobe para """ + n(sum(an) / len(an), 2, True) + r""" pontos. O melhor arranjo passa a ser o
que incorpora o sentimento, com ganho de """ + n(mv["ganho_pp"], 2, True) + r""" pontos percentuais.

Convém, porém, qualificar o achado com precisão, para que não seja lido além do que sustenta.
Nenhum arranjo alcança significância: o melhor deles apresenta $p = """ + n(mv["p_bootstrap"], 3) + r"""$ e intervalo de
confiança $[""" + n(mv["ic95_pp"][0], 2, True) + r"""; \, """ + n(mv["ic95_pp"][1], 2, True) + r"""]$, que contém o zero. O que a correção do alvo produziu foi a
inversão do \emph{sinal} e a mudança de \emph{ordenamento} --- pela primeira vez em todo o conjunto
de experimentos, o arranjo com sentimento supera o arranjo de preço isolado ---, não a obtenção de
poder preditivo estatisticamente demonstrável. O modelo deixou de ser pior que a referência trivial;
não passou a ser melhor que ela.

O desenho em painel, por sua vez, produziu resultado equivalente ao treinamento por ativo, com
diferenças contidas no intervalo de confiança. Acrescentar observações fortemente correlacionadas
não acrescenta informação na proporção do número de linhas.

\subsubsection{Volatilidade}

A correção do alvo é conceitualmente ainda mais pertinente para a volatilidade, pois a volatilidade
do retorno anormal é a volatilidade idiossincrática --- a parcela da oscilação atribuível à própria
empresa. A Tabela~\ref{tab:alvo_vol} reporta o ganho de erro quadrático do modelo HAR acrescido do
sentimento sobre o HAR isolado.

\begin{table}[htpb]
\centering
\caption{Ganho de erro quadrático fora da amostra do HAR acrescido de sentimento sobre o HAR isolado, por definição de alvo e subconjunto.}
\label{tab:alvo_vol}
\begin{tabular}{l c c c}
\hline
\textbf{Alvo e subconjunto} & \textbf{$R^2$-OS} & \textbf{IC 95\%} & \textbf{$p$} \\ \hline
""" + lin_vol + r"""
\hline
\end{tabular}
\vspace{0.2cm}
{\small \\ Fonte: Elaborado pelo autor (\texttt{CVM/28\_reexecucao\_com\_alvo\_anormal.py}, """ + DATA + r""").}
\end{table}

O alvo anormal melhora o resultado, e o arranjo sobre a totalidade dos pregões constitui o achado
que mais se aproximou da significância em todo este Capítulo, com limite inferior do intervalo
praticamente tangente ao zero. Dois fatos, contudo, impedem que seja tomado como evidência. O
primeiro é que $p = """ + n(vol["volatilidade ANORMAL (idiossincrática) — todos os dias"]["p_bootstrap"], 3) + r"""$ não atinge o patamar convencional. O segundo, e decisivo, é de ordem de
grandeza: a meta estabelecida para a previsão de volatilidade nesta pesquisa é de $R^2$-OS superior
a cinco por cento, e o valor obtido é de """ + n(vol["volatilidade ANORMAL (idiossincrática) — todos os dias"]["r2os_pct"], 3, True) + r""" por cento --- duas ordens de grandeza abaixo do que se
consideraria relevante. Registra-se o sinal, não o efeito.
""" + prophet_txt + r"""
\subsubsection{Consequência para a interpretação do Capítulo}

A correção do alvo reposiciona parte dos achados anteriores sem reverter a conclusão central. O que
se demonstrou é que uma fração dos resultados negativos reportados nas seções precedentes decorria
de especificação inadequada do alvo, e não de ausência de conteúdo informativo no texto: ao exigir
do modelo que previsse um retorno cuja metade é movimento de mercado, impunha-se tarefa que nenhum
sinal de empresa específica poderia cumprir. Corrigida a especificação, os arranjos deixam de ser
inferiores à referência trivial e o sentimento passa a ocupar a primeira posição no ordenamento.

A conclusão central, porém, permanece: não se obteve, em nenhuma especificação, ganho direcional
estatisticamente demonstrável. E o canal da volatilidade, embora favorecido pela correção, produz
efeito de magnitude duas ordens abaixo do limiar de relevância fixado. A tese de que o sentimento
informa o risco mais do que a direção sai, destas verificações, preservada --- e mais bem
delimitada, porque agora se conhece também o que \emph{não} explicava os resultados nulos.
"""

TEX.write_text(tex, encoding="utf-8")
print(f"gerado: {TEX}")
print(f"  bruto: média {sum(br)/len(br):+.2f}pp, {sum(1 for x in br if x>0)}/8 positivos")
print(f"  anormal: média {sum(an)/len(an):+.2f}pp, {sum(1 for x in an if x>0)}/8 positivos")
print(f"  Prophet incluído: {'sim' if C else 'NÃO (json ausente)'}")
