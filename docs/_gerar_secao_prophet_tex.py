# -*- coding: utf-8 -*-
# Gera a subseção LaTeX do contraponto com o Prophet (série temporal) nas 10
# maiores ações do Ibovespa. Lê os números reais de
# CVM/dados/prophet_vs_garch_svm_xgboost.json — nada é digitado à mão.
# Pedido do Prof. Julio na mentoria de 16/10/2026.
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
JSON = RAIZ / "CVM" / "dados" / "prophet_vs_garch_svm_xgboost.json"
TEX = RAIZ / "Exame_qualificacao" / "PesquisaMestrado_Qualificacao" / "capitulos" / "4p-prophet-series-temporais.tex"
DATA = "2026-10-18"

d = json.loads(JSON.read_text(encoding="utf-8"))
P = d["papeis"]
TICKERS = list(P.keys())


def num(x, casas=2, sinal=False):
    s = f"{x:+.{casas}f}" if sinal else f"{x:.{casas}f}"
    return s.replace(".", "{,}")


# ── tabela 1: direção ────────────────────────────────────────────────────────
lin_dir = []
for tk in TICKERS:
    p = P[tk]["direcao"]
    melhor = p["melhor_classico"]
    acc_c = p["arms"][melhor]["acuracia"] * 100
    acc_p = p["arms"]["Prophet (preço)"]["acuracia"] * 100
    maj = p["majoritaria"] * 100
    alta_p = p["arms"]["Prophet (preço)"]["pct_previu_alta"]
    lin_dir.append(f"{tk} & ${num(maj)}\\%$ & ${num(acc_c)}\\%$ & ${num(acc_p)}\\%$ & ${num(alta_p, 1)}\\%$ \\\\")

# ── tabela 2: volatilidade e preço, contra a régua ancorada ──────────────────
lin_cont = []
for tk in TICKERS:
    vol = P[tk]["volatilidade"]["arms"]["Prophet (volatilidade)"]["r2os_vs_ancorada"]
    pre = P[tk]["preco"]["arms"]["Prophet (preço)"]["r2os_vs_ancorada"]
    diaria = P[tk]["preco"]["arms"]["Ingênua diária (fechamento de ontem)"]["r2os_vs_ancorada"]
    lin_cont.append(f"{tk} & ${num(vol, 1, True)}\\%$ & ${num(pre, 1, True)}\\%$ & ${num(diaria, 1, True)}\\%$ \\\\")

n_vol_pior = sum(P[tk]["volatilidade"]["arms"]["Prophet (volatilidade)"]["r2os_vs_ancorada"] < 0 for tk in TICKERS)
n_pre_pior = sum(P[tk]["preco"]["arms"]["Prophet (preço)"]["r2os_vs_ancorada"] < 0 for tk in TICKERS)
n_dir_pior = sum(P[tk]["direcao"]["arms"]["Prophet (preço)"]["acuracia"]
                 < P[tk]["direcao"]["arms"][P[tk]["direcao"]["melhor_classico"]]["acuracia"] for tk in TICKERS)
n_cvm_ajuda = sum(P[tk]["direcao"]["arms"]["Prophet (preço+CVM)"]["acuracia"]
                  > P[tk]["direcao"]["arms"]["Prophet (preço)"]["acuracia"] for tk in TICKERS)
n = len(TICKERS)
n_teste = P[TICKERS[0]]["direcao"]["n_teste"]

tex = r"""% Gerado por docs/_gerar_secao_prophet_tex.py --- dados reais (""" + DATA + r""").
% Fonte: CVM/dados/prophet_vs_garch_svm_xgboost.json
% Script: CVM/23_prophet_vs_garch_svm_xgboost.py
\subsection{Um contraponto de série temporal: o Prophet}
\label{sec:prophet}

As seções anteriores avaliaram o sentimento dentro de um arranjo fixo de modelagem --- fusão
precoce de atributos defasados, classificadores de margem e de \textit{boosting} para a direção,
e o modelo HAR de \citeonline{corsi_simple_2009} para a volatilidade. Cabe perguntar se esse
arranjo, construído sob medida para o problema, é de fato necessário, ou se um previsor de uso
geral, de configuração trivial, alcançaria resultado equivalente a custo menor. O
\textit{Prophet}, de \citeonline{taylor_forecasting_2018}, oferece esse contraponto: decompõe uma
série em tendência, sazonalidade e regressoras externas, e foi concebido justamente para que
analistas sem formação em séries temporais obtenham previsões razoáveis sem ajuste fino.

Registre-se, antes de tudo, uma distinção de natureza. O \textit{Prophet} não processa texto e não
substitui o codificador de linguagem: ele projeta valores numéricos ao longo do tempo. O sentimento
que aqui lhe serve de regressora é o mesmo produzido pelo FinBERT-PT-BR sobre os comunicados
oficiais, descrito na Seção~\ref{sec:metodologia_ism}. O que se compara, portanto, não são dois
classificadores de sentimento, mas dois arranjos de previsão que consomem o mesmo insumo textual.

\subsubsection{Desenho}

O experimento cobre as dez ações de maior peso na carteira teórica do Ibovespa que já integram a
base de comunicados desta pesquisa, com """ + str(n_teste) + r""" pregões de teste por ativo sob a
mesma divisão cronológica de sessenta, quinze e vinte e cinco por cento empregada em todo o
capítulo. Três alvos foram examinados: a direção do pregão seguinte, a volatilidade condicional
estimada por GARCH(1,1) e o preço de fechamento.

Uma decisão de desenho merece registro, por ter alterado materialmente a leitura dos resultados. Em
uma primeira execução, o \textit{Prophet} foi ajustado uma única vez sobre treino e validação e
instado a prever o período de teste inteiro de uma só vez --- quase dois anos de horizonte sem
reancoragem. O componente de tendência divergiu, e os erros resultantes excederam em duas ordens de
grandeza os de qualquer referência, configurando resultado degenerado e não informativo. Adotou-se,
em substituição, reajuste a cada vinte e um pregões sobre janela expansiva, de modo que nenhuma
previsão se afasta mais de um mês da última observação disponível.

Essa escolha impõe, contudo, uma assimetria de informação que seria desleal ignorar: as referências
usuais desta pesquisa --- o HAR e a previsão ingênua de persistência --- dispõem do valor observado
na véspera em cada pregão do teste, ao passo que o \textit{Prophet}, no vigésimo primeiro dia de um
bloco, ainda opera sobre o que se conhecia três semanas antes. Introduziu-se, por isso, uma
\textbf{referência ancorada}: a persistência do último valor anterior ao bloco, mantido por todo o
bloco. Ela recebe exatamente a mesma informação que o \textit{Prophet} e constitui a comparação
metodologicamente correta. A referência de atualização diária é reportada à parte, por medir coisa
distinta --- o valor da reancoragem frequente, e não a qualidade do modelo.

\subsubsection{Resultados}

A Tabela~\ref{tab:prophet_direcao} apresenta a direção. A coluna do melhor modelo clássico recolhe,
para cada ativo, o maior acerto entre a máquina de vetores de suporte e o \textit{boosting} sobre
atributos de preço.

\begin{table}[htpb]
\centering
\caption{Acerto direcional no pregão seguinte: melhor modelo clássico contra o \textit{Prophet}, nas dez maiores ações do Ibovespa.}
\label{tab:prophet_direcao}
\begin{tabular}{l c c c c}
\hline
\textbf{Ativo} & \textbf{Classe majoritária} & \textbf{Melhor clássico} & \textbf{Prophet} & \textbf{Prophet prevê alta em} \\ \hline
""" + "\n".join(lin_dir) + r"""
\hline
\end{tabular}
\vspace{0.2cm}
{\small \\ Fonte: Elaborado pelo autor (\texttt{CVM/23\_prophet\_vs\_garch\_svm\_xgboost.py}, """ + DATA + r"""). A última coluna é diagnóstico de degeneração: um previsor que aponte sempre o mesmo lado reproduz a classe majoritária sem conter informação.}
\end{table}

O \textit{Prophet} ficou abaixo do melhor modelo clássico em """ + str(n_dir_pior) + r""" dos """ + str(n) + r""" ativos.
Mais relevante que a comparação entre ambos, contudo, é a constatação já estabelecida nas seções
anteriores e aqui reiterada por outra via: nenhum dos dois arranjos se distingue de forma confiável
do palpite da classe majoritária. O acréscimo do sentimento dos comunicados como regressora elevou o
acerto do \textit{Prophet} em """ + str(n_cvm_ajuda) + r""" dos """ + str(n) + r""" ativos, variação compatível com oscilação amostral.

A Tabela~\ref{tab:prophet_continuos} traz os dois alvos contínuos, medidos pelo $R^2$ fora da
amostra contra a referência ancorada.

\begin{table}[htpb]
\centering
\caption{Ganho de erro quadrático fora da amostra sobre a referência ancorada, que dispõe da mesma informação do \textit{Prophet}. Valores negativos indicam desempenho pior que simplesmente manter o último valor conhecido.}
\label{tab:prophet_continuos}
\begin{tabular}{l c c c}
\hline
\textbf{Ativo} & \textbf{Prophet (volatilidade)} & \textbf{Prophet (preço)} & \textbf{Persistência diária (preço)} \\ \hline
""" + "\n".join(lin_cont) + r"""
\hline
\end{tabular}
\vspace{0.2cm}
{\small \\ Fonte: Elaborado pelo autor (\texttt{CVM/23\_prophet\_vs\_garch\_svm\_xgboost.py}, """ + DATA + r"""). A última coluna mede o valor da reancoragem diária, não a qualidade de um modelo.}
\end{table}

O resultado é inequívoco e negativo. Em """ + str(n_vol_pior) + r""" dos """ + str(n) + r""" ativos na volatilidade e em """ + str(n_pre_pior) + r""" dos """ + str(n) + r"""
no preço, o \textit{Prophet} produziu erro maior que o de simplesmente manter o último valor
conhecido, dispondo ambos da mesma informação. A extrapolação de tendência, que confere ao modelo
sua utilidade em séries de negócio com sazonalidade estável, torna-se passivo em séries de preço de
ativo, cuja trajetória se aproxima de um passeio aleatório: a inclinação estimada sobre o passado
recente frequentemente já se inverteu antes de o bloco de previsão se encerrar.

\subsubsection{Implicação para a escolha de método}

A última coluna da Tabela~\ref{tab:prophet_continuos} quantifica, nesta base, algo que a literatura
de previsão financeira sustenta e que convém explicitar: a frequência com que o previsor se
reancora ao dado observado pesa mais que a sofisticação de sua estrutura interna. Reduzir o
intervalo de reajuste do \textit{Prophet} de vinte e um pregões para um multiplicaria por cerca de
vinte e uma vezes o custo de processamento --- cada reajuste consome aproximadamente um segundo e
três décimos --- sem garantia de superar uma referência de custo nulo.

O contraponto, portanto, não enfraquece o arranjo adotado nesta dissertação; delimita-o. O HAR e os
classificadores sobre atributos defasados não são preferidos por elegância, mas porque operam
sobre a informação da véspera e não dependem de extrapolar tendência. E a conclusão central do
capítulo permanece intacta sob um método de previsão inteiramente distinto, o que lhe acrescenta
robustez: o sentimento informa o risco, não a direção.
"""

TEX.write_text(tex, encoding="utf-8")
print(f"gerado: {TEX}")
print(f"  direção: Prophet pior em {n_dir_pior}/{n} | volatilidade pior em {n_vol_pior}/{n} | preço pior em {n_pre_pior}/{n}")
