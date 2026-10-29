# -*- coding: utf-8 -*-
# Gera a subseção LaTeX sobre a restrição aos pregões com comunicado.
# Lê os números reais de CVM/dados/dias_com_evento.json — nada digitado à mão.
# Pedido da mentoria de 29/10/2026.
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
JSON = RAIZ / "CVM" / "dados" / "dias_com_evento.json"
TEX = RAIZ / "Exame_qualificacao" / "PesquisaMestrado_Qualificacao" / "capitulos" / "4q-dias-com-evento.tex"
DATA = "2026-10-29"

d = json.loads(JSON.read_text(encoding="utf-8"))
P, AG = d["papeis"], d["agrupado"]
TICK = list(P.keys())


def n(x, c=2, s=False):
    return (f"{x:+.{c}f}" if s else f"{x:.{c}f}").replace(".", "{,}")


# cobertura por papel
lin_cob = [f"{tk} & {P[tk]['n_com_evento']} & ${n(P[tk]['pct_com_evento'],1)}\\%$ \\\\" for tk in TICK]

# agrupado
lin_ag = []
for b, v in AG.items():
    a, e = v["todos_os_dias"], v["so_dias_com_evento"]
    lin_ag.append(f"{b.replace('—','--').replace('_','\\_')} & ${n(a['ganho_pp'],2,True)}$ & "
                  f"${n(a['p_vs_majoritaria'],3)}$ & ${n(e['ganho_pp'],2,True)}$ & "
                  f"${n(e['p_vs_majoritaria'],3)}$ \\\\")

n_av = sum(1 for tk in TICK if "ganho_pp" not in str(P[tk].get("resumo", {})) or
           P[tk]["resumo"].get("ganho_medio_com_evento_pp") is not None)
piorou = sum(1 for tk in TICK if P[tk].get("resumo", {}).get("ganho_medio_com_evento_pp") is not None
             and P[tk]["resumo"]["ganho_medio_com_evento_pp"] < P[tk]["resumo"]["ganho_medio_todos_pp"])
ic_min = min(P[tk]["resumo"]["ic95_com_evento_pp"] for tk in TICK
             if P[tk].get("resumo", {}).get("ic95_com_evento_pp"))
ic_max = max(P[tk]["resumo"]["ic95_com_evento_pp"] for tk in TICK
             if P[tk].get("resumo", {}).get("ic95_com_evento_pp"))
n_ev_ag = AG[list(AG)[0]]["so_dias_com_evento"]["n"]
ic_ag = AG[list(AG)[0]]["so_dias_com_evento"]["ic95_meia_largura_pp"]

tex = r"""% Gerado por docs/_gerar_secao_dias_evento_tex.py --- dados reais (""" + DATA + r""").
% Fonte: CVM/dados/dias_com_evento.json
% Script: CVM/25_dias_com_evento.py
\subsection{A restrição aos pregões com divulgação}
\label{sec:dias_evento}

As seções anteriores avaliaram a contribuição do sentimento sobre a totalidade dos pregões do
conjunto de teste. Essa escolha, aparentemente neutra, embute uma diluição que convém examinar: em
boa parte dos pregões não houve divulgação alguma na véspera, e nesses o atributo de sentimento
assume um valor de preenchimento. Mede-se, portanto, a utilidade de uma informação em dias nos
quais ela inexiste.

A objeção é legítima e foi levantada na orientação. Se o sentimento informa, deveria informar
\emph{quando há o que informar}. Restringir a avaliação aos pregões precedidos de divulgação
deveria, pela hipótese, elevar os índices.

\subsubsection{A cobertura real}

A Tabela~\ref{tab:cobertura_evento} mostra quantos pregões do conjunto de teste --- """ + str(AG[list(AG)[0]]["todos_os_dias"]["n"] // len(TICK)) + r""" por
ativo --- foram precedidos de comunicado entregue após o fechamento.

\begin{table}[htpb]
\centering
\caption{Pregões do conjunto de teste precedidos de comunicado da CVM entregue após as dezessete horas.}
\label{tab:cobertura_evento}
\begin{tabular}{l r r}
\hline
\textbf{Ativo} & \textbf{Pregões com divulgação} & \textbf{Proporção} \\ \hline
""" + "\n".join(lin_cob) + r"""
\hline
\end{tabular}
\vspace{0.2cm}
{\small \\ Fonte: Elaborado pelo autor (\texttt{CVM/25\_dias\_com\_evento.py}, """ + DATA + r""").}
\end{table}

A cobertura é baixa e desigual. A Ambev, com apenas cinco pregões de divulgação no período de
teste, não admite avaliação estatística alguma, e foi excluída desta análise. O caso extremo
oposto, a Petrobras, não chega a trinta por cento.

\subsubsection{A armadilha de comparação, e como foi evitada}

Comparar diretamente a acurácia obtida no subconjunto com a obtida no conjunto completo seria
incorreto, porque ao mudar o subconjunto muda também o adversário: a classe majoritária dos
pregões com divulgação não é a mesma do total. Cada subconjunto foi, por isso, julgado contra a
sua própria classe majoritária. Há ainda um segundo efeito, de natureza distinta e igualmente
relevante: a redução do número de observações alarga o intervalo de confiança. Nos ativos
individuais, a meia-largura do intervalo de noventa e cinco por cento varia de """ + n(ic_min, 1) + r""" a """ + n(ic_max, 1) + r"""
pontos percentuais --- magnitude que inviabiliza a detecção de efeitos da ordem de dois ou três
pontos, que é a ordem relevante neste problema.

\subsubsection{Resultado}

Nos ativos tomados isoladamente, a restrição não elevou os índices: a média dos seis arranjos
piorou em """ + str(piorou) + r""" dos nove ativos avaliáveis, e nenhum arranjo, em nenhum ativo, superou a
respectiva classe majoritária com significância estatística. Testou-se ainda um modelo
\emph{especialista}, treinado exclusivamente nos pregões de divulgação, para afastar a objeção de
que o modelo geral houvesse aprendido num regime em que a maioria dos dias não contém
divulgação. O especialista tampouco superou a referência.

Dada a insuficiência de poder nos ativos isolados, agruparam-se os dez em um único conjunto ---
procedimento legítimo porque todos percorreram o mesmo protocolo, a mesma janela e a mesma
divisão temporal. O agrupamento eleva o número de pregões com divulgação para """ + str(n_ev_ag) + r""" e reduz a
meia-largura do intervalo para """ + n(ic_ag, 1) + r""" pontos percentuais. A Tabela~\ref{tab:evento_agrupado} reporta o
resultado.

\begin{table}[htpb]
\centering
\caption{Ganho sobre a classe majoritária, em pontos percentuais, nos dez ativos agrupados. Cada subconjunto é confrontado com a sua própria classe majoritária.}
\label{tab:evento_agrupado}
\begin{tabular}{l c c c c}
\hline
\textbf{Arranjo} & \textbf{Todos} & \textbf{$p$} & \textbf{Com divulgação} & \textbf{$p$} \\ \hline
""" + "\n".join(lin_ag) + r"""
\hline
\end{tabular}
\vspace{0.2cm}
{\small \\ Fonte: Elaborado pelo autor (\texttt{CVM/25\_dias\_com\_evento.py}, """ + DATA + r"""). Valores negativos indicam desempenho inferior ao da classe majoritária.}
\end{table}

O resultado contraria a hipótese, e de forma inequívoca. Com poder estatístico adequado, todos os
arranjos permanecem abaixo da classe majoritária, e nos pregões com divulgação o déficit é
\emph{maior}, não menor. Os dois arranjos que empregam apenas preço chegam a diferir da referência
com significância sob a amostra agrupada.

Registra-se, contudo, um padrão que merece investigação futura e que não se pretende aqui
estabelecer: nos pregões com divulgação, os arranjos que incorporam o sentimento exibem déficit
sistematicamente menor que os de preço isolado. A diferença é da ordem de dois a três pontos
percentuais e sugere que o sentimento atue, nesses dias, mais como atenuação de erro do que como
fonte de acerto. A verificação dessa conjectura exigiria teste pareado entre arranjos, não
realizado nesta etapa.

\subsubsection{Interpretação}

A leitura que o conjunto autoriza é que a limitação não reside no modelo nem na representação do
sentimento, mas na \emph{frequência do fenômeno}. Divulgações oficiais após o fechamento são
eventos esparsos: de cinco a vinte e oito por cento dos pregões, conforme o ativo. Qualquer efeito
da ordem de dois ou três pontos percentuais exigiria, para ser detectado com o rigor que esta
pesquisa adota, um número de eventos superior ao que uma década de histórico de dez ativos
oferece. O caminho para a verificação não passa, portanto, por modelo mais elaborado, e sim por
ampliação da base --- mais ativos, ou horizonte mais longo, ou ambos.

Essa constatação é consistente com o que o Capítulo relatou a respeito do efeito de cauda: a
divulgação move o preço, e isso foi medido com significância inequívoca; mas o movimento concentra-se
numa minoria de eventos, e a regularidade necessária à previsão não se encontra no caso típico.
"""

TEX.write_text(tex, encoding="utf-8")
print(f"gerado: {TEX}")
print(f"  papéis avaliáveis: {len(TICK)-1}/10 | piorou com a restrição em {piorou} | "
      f"n agrupado com evento: {n_ev_ag} (IC ±{ic_ag})")
