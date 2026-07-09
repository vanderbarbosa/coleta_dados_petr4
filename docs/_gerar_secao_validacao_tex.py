# -*- coding: utf-8 -*-
# Gera a subseção LaTeX da VALIDAÇÃO do sentimento (FinBERT vs conjunto-ouro humano).
# Recalcula a partir dos dados reais (planilha rotulada + gabarito do modelo).
from pathlib import Path
import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix, classification_report, accuracy_score

RAIZ = Path(__file__).resolve().parents[1]
OURO = RAIZ / "Mestrado_PETR4" / "conjunto_ouro"
TEX = RAIZ / "Exame_qualificacao" / "PesquisaMestrado_Qualificacao" / "capitulos" / "4g-validacao-sentimento.tex"
DATA = "2026-07-08"
MAPA = {"Positivo": "Positive", "Negativo": "Negative", "Neutro": "Neutral"}
ORDEM = ["Negative", "Neutral", "Positive"]
PT = {"Negative": "Negativo", "Neutral": "Neutro", "Positive": "Positivo"}

rot = pd.read_excel(OURO / "conjunto_ouro_para_rotular.xlsx", sheet_name="Rotular")
gab = pd.read_csv(OURO / "conjunto_ouro_gabarito_modelo.csv")
df = rot.merge(gab[["ID_OURO", "Label_Sentimento"]], on="ID_OURO", how="inner")
df = df[df["Sentimento_Humano"].notna()]
yh = df["Sentimento_Humano"].map(MAPA)
ym = df["Label_Sentimento"]
acc = accuracy_score(yh, ym)
kappa = cohen_kappa_score(yh, ym)
cm = confusion_matrix(yh, ym, labels=ORDEM)
rep = classification_report(yh, ym, labels=ORDEM, output_dict=True, zero_division=0)
rel = (df["Relevante_PETR4"].astype(str).str.strip() == "Sim").mean()
n = len(df)
kf = "razoável (\\textit{fair})" if kappa < 0.41 else ("moderada (\\textit{moderate})" if kappa < 0.61 else "substancial")

cm_rows = "\n".join(
    f"{PT[ORDEM[i]]} & " + " & ".join(str(cm[i][j]) for j in range(3)) + r" \\"
    for i in range(3))
f1_rows = "\n".join(
    f"{PT[c]} & {rep[c]['precision']:.3f} & {rep[c]['recall']:.3f} & {rep[c]['f1-score']:.3f} & {int(rep[c]['support'])} \\\\"
    for c in ORDEM)

tex = r"""% Gerado por docs/_gerar_secao_validacao_tex.py — dados reais (""" + DATA + r""").
\subsection{Validação do modelo de sentimento contra um conjunto-ouro humano}
\label{sec:validacao_sentimento}

Coerente com a estratégia de refinar o primeiro elo antes dos demais, e atendendo à exigência
da banca por uma medida de concordância que desconte o acaso, construiu-se um \textbf{conjunto-ouro}
de """ + f"{n}" + r""" manchetes, estratificado por categoria temática e rotulado manualmente, de forma
cega ao modelo, segundo uma rubrica explícita de sentimento financeiro. Comparou-se, então, o rótulo
do \mbox{FinBERT-PT-BR} ao rótulo humano. A Tabela~\ref{tab:validacao_sentimento} resume o desempenho.

\begin{table}[htpb]
\centering
\caption{Concordância entre o FinBERT-PT-BR e o rótulo humano no conjunto-ouro (""" + f"{n}" + r""" manchetes).}
\label{tab:validacao_sentimento}
\begin{tabular}{l r}
\hline
\textbf{Métrica} & \textbf{Valor} \\ \hline
Acurácia (concordância com o humano) & """ + f"{acc*100:.2f}".replace(".", ",") + r"""\% \\
Kappa de Cohen & """ + f"{kappa:.3f}".replace(".", ",") + r""" \\
F1 macro & """ + f"{rep['macro avg']['f1-score']*100:.1f}".replace(".", ",") + r"""\% \\ \hline
\end{tabular}
\end{table}

\begin{table}[htpb]
\centering
\caption{Desempenho por classe e matriz de confusão (linhas = rótulo humano; colunas = modelo).}
\label{tab:validacao_sentimento_classe}
\begin{minipage}{0.52\textwidth}\centering
\begin{tabular}{l c c c c}
\hline
\textbf{Classe} & \textbf{Prec.} & \textbf{Rev.} & \textbf{F1} & \textbf{N} \\ \hline
""" + f1_rows + r"""
\hline
\end{tabular}
\end{minipage}\hfill
\begin{minipage}{0.44\textwidth}\centering
\begin{tabular}{l c c c}
\hline
 & \textbf{Neg.} & \textbf{Neu.} & \textbf{Pos.} \\ \hline
""" + cm_rows + r"""
\hline
\end{tabular}
\end{minipage}
\vspace{0.2cm}
{\small \\ Fonte: Elaborado pelo autor (\texttt{src/sentimento/avaliar\_conjunto\_ouro\_petr4.py}, """ + DATA + r""").}
\end{table}

A concordância é de """ + f"{acc*100:.0f}".replace(".", ",") + r"""\%, com Kappa de Cohen de
""" + f"{kappa:.3f}".replace(".", ",") + r""", nível classificado como """ + kf + r""" na escala de
Landis e Koch. O resultado é, ao mesmo tempo, honesto e instrutivo. Por um lado, o modelo supera com
folga a concordância ao acaso e a classe majoritária, confirmando que ele captura sinal real de
sentimento em português financeiro. Por outro, a matriz de confusão revela uma tendência do
\mbox{FinBERT-PT-BR} a \textbf{superestimar a classe Negativa} (alta revocação, porém precisão modesta),
o que dilui a distinção entre neutro e negativo --- justamente as categorias mais frequentes no corpus.

Essa medição sustenta a decisão de refinar o sentimento como \emph{primeira} etapa: a qualidade do
sinal de entrada é apenas razoável, e há margem concreta de melhora, seja pela adoção de um codificador
mais forte (Albertina \mbox{PT-BR}, arquitetura DeBERTa) com \textit{fine-tuning} sobre este mesmo
conjunto-ouro, seja pela ampliação da base rotulada. Vale distinguir, contudo, dois limites de natureza
diferente: enquanto a acurácia do \emph{sentimento} é genuinamente aprimorável, o teto da acurácia da
\emph{direção} decorre da eficiência do mercado e não se dissolve com um sentimento melhor. Registra-se,
por fim, um achado descritivo relevante: dos """ + f"{n}" + r""" itens, apenas
""" + f"{rel*100:.0f}".replace(".", ",") + r"""\% foram julgados pelo rotulador como efetivamente
relevantes à PETR4, o que quantifica o grau de ruído temático do corpus e motiva, como trabalho futuro,
um classificador de relevância aprendido a partir desses rótulos humanos.
"""
TEX.write_text(tex, encoding="utf-8")
print(f"✓ {TEX.name} | acc={acc*100:.2f}% kappa={kappa:.3f} rel={rel*100:.0f}%")
