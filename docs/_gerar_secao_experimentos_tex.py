# -*- coding: utf-8 -*-
# Gera a subseção LaTeX com (a) a suíte de experimentos de data fusion e (b) as
# técnicas de alto desempenho replicadas da literatura. Lê os CSVs reais.
from pathlib import Path
import json
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DS = RAIZ / "datasets_refino"
TEX = RAIZ / "Exame_qualificacao" / "PesquisaMestrado_Qualificacao" / "capitulos" / "4d-experimentos-suite.tex"
DATA = "2026-07-04"

_j = json.loads((DS / f"resultados_experimentos_datafusion_{DATA}.json").read_text(encoding="utf-8"))
N_TESTE = _j["n_teste"]
res = pd.read_csv(DS / f"resultados_experimentos_datafusion_{DATA}.csv").sort_values("acuracia_teste", ascending=False)
baseline = res["baseline_maj"].iloc[0]
best = res.iloc[0]

def esc(s): return str(s).replace("_", "\\_").replace("%", "\\%")

linhas = []
for _, r in res.iterrows():
    sup = "sim" if r["supera_baseline"] else "não"
    row = (f"{esc(r['modelo'])} & {esc(r['atributos'])} & {r['n_features']} & "
           f"{r['acuracia_teste']:.2f} & {r['auc']:.3f} & {r['mcc']:.3f} & {sup} \\\\")
    if r["modelo"] == best["modelo"] and r["atributos"] == best["atributos"]:
        row = "\\textbf{" + row.replace(" \\\\", "} \\\\").replace("&", "} & \\textbf{")
        row = row.replace("\\textbf{\\textbf{", "\\textbf{")
    linhas.append(row)

tec = pd.read_csv(DS / "05_tecnicas_alto_desempenho_rsl_v1.csv")
tec_rows = []
for _, r in tec.iterrows():
    tec_rows.append(f"{esc(r['Estudo'])} & {esc(r['Tecnica_de_alto_desempenho'])[:90]} & {esc(r['Como_replicamos_no_data_fusion'])[:80]} \\\\")

tex = r"""% Gerado por docs/_gerar_secao_experimentos_tex.py — dados reais (rodada """ + DATA + r""").
\subsection{Rodada de refinamento: suíte de experimentos de fusão de dados}
\label{sec:suite_experimentos}

Em atenção às ponderações da banca no seminário, conduziu-se uma rodada sistemática de
experimentos de fusão de dados, com o objetivo de verificar se a replicação das técnicas de
maior desempenho identificadas na revisão sistemática elevaria a acurácia direcional. As
técnicas transpostas para o presente modelo, e a forma de sua adoção, são sintetizadas na
Tabela~\ref{tab:tecnicas_replicadas}.

\begin{table}[htpb]
\centering
\caption{Técnicas de alto desempenho da literatura e sua replicação no modelo de fusão de dados desta pesquisa.}
\label{tab:tecnicas_replicadas}
\resizebox{\textwidth}{!}{%
\begin{tabular}{p{3.0cm} p{6.5cm} p{6.0cm}}
\hline
\textbf{Estudo} & \textbf{Técnica de alto desempenho} & \textbf{Replicação nesta pesquisa} \\ \hline
""" + "\n".join(tec_rows) + r"""
\hline
\end{tabular}%
}
\vspace{0.2cm}
{\small \\ Fonte: Elaborado pelo autor a partir da revisão sistemática (Cap.~\ref{chap:referencial_teorico}).}
\end{table}

Os experimentos combinaram cinco algoritmos --- regressão logística, máquina de vetores de
suporte com núcleo radial, floresta aleatória \cite{ballings_evaluating_2015}, \textit{XGBoost}
e um \textit{ensemble} por empilhamento (\textit{stacking}) na linha de \citeonline{barak_fusion_2017}
--- com três conjuntos de atributos: apenas os três atributos-base (retorno, volatilidade e
sentimento defasados), o acréscimo do sentimento por categoria temática \cite{nguyen_sentiment_2015}
e o conjunto completo de atributos defasados. Todos os modelos foram avaliados sob a mesma divisão
cronológica (60/15/25), com até """ + f"{int(res['n_features'].max())}" + r""" atributos e limiar de
decisão calibrado na validação \cite{nobre_combining_2019}, totalizando """ + f"{res.shape[0]}" + r"""
configurações submetidas a teste de significância binomial \cite{oliveira_impact_2017}. A
Tabela~\ref{tab:suite_experimentos} reúne todos os resultados.

\begin{table}[htpb]
\centering
\caption{Suíte de experimentos de fusão de dados para a previsão da direção da PETR4 (conjunto de teste, """ + f"{N_TESTE}" + r""" pregões). Baseline de classe majoritária: """ + f"{baseline:.2f}" + r"""\%. Em negrito, a melhor configuração.}
\label{tab:suite_experimentos}
\begin{tabular}{l l c c c c c}
\hline
\textbf{Modelo} & \textbf{Atributos} & \textbf{\#} & \textbf{Acur.\ (\%)} & \textbf{AUC} & \textbf{MCC} & \textbf{$>$ base} \\ \hline
""" + "\n".join(linhas) + r"""
\hline
\end{tabular}
\vspace{0.2cm}
{\small \\ Fonte: Elaborado pelo autor (rodada de refinamento """ + DATA + r"""; \texttt{src/modelagem/13\_experimentos\_datafusion.py}).}
\end{table}

A melhor configuração foi o \textit{XGBoost} sobre os três atributos-base, com acurácia de
""" + f"{best['acuracia_teste']:.2f}".replace(".", ",") + r"""\% no conjunto de teste, superando o
\textit{baseline} de classe majoritária (""" + f"{baseline:.2f}".replace(".", ",") + r"""\%) e sendo
estatisticamente superior ao acaso (teste binomial, $p = """ + f"{best['p_binomial_vs_50']:.3f}".replace(".", ",") + r"""$).
Três leituras honestas emergem do quadro completo. Primeiro, o ganho é \textbf{modesto}: a acurácia
oscila em torno de cinquenta e três a cinquenta e quatro por cento, e a AUC permanece próxima de
0,51, o que é coerente com a Hipótese de Mercados Eficientes para a direção diária de um ativo
líquido. Segundo, o \textit{stacking} e o conjunto completo de atributos \textbf{não} superaram as
configurações mais simples --- o desempenho superior de oitenta por cento reportado por
\citeonline{barak_fusion_2017} refere-se a outro mercado (Teerã) e a outra tarefa (retorno/risco),
não sendo transponível para a direção diária da PETR4; e o conjunto completo de atributos incorreu
em sobreajuste, com queda de desempenho fora da amostra. Terceiro, e mais relevante, a rodada
\textbf{confirma} o resultado central da dissertação: a fusão do sentimento eleva a acurácia frente
ao modelo de apenas preços, porém o ganho direcional é marginal, ao passo que a contribuição do
sentimento à \textbf{volatilidade} permanece o achado forte e estatisticamente robusto (Seção
sobre a causalidade de Granger). Cada configuração testada foi persistida como um conjunto de dados
independente (nomeado por data, modelo e atributos), permitindo auditoria e comparação integral.
"""

TEX.write_text(tex, encoding="utf-8")
print("✓ Gerado:", TEX)
print(f"  melhor: {best['modelo']}/{best['atributos']} = {best['acuracia_teste']}% (baseline {baseline}%)")
