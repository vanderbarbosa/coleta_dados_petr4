# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — O ISM filtrado melhora a PREVISÃO de volatilidade?
# =============================================================================
#
#  ------------------------------------------------------------------
#  POR QUE ESTE TESTE, E NÃO O DA DIREÇÃO
#  ------------------------------------------------------------------
#  O Script 07 mostrou que o filtro de relevância NÃO muda a previsão de
#  direção — as acurácias ficaram idênticas, no acaso. Isso já era esperado:
#  o teste de teto havia mostrado que nem um classificador perfeito melhoraria
#  a direção. O gargalo ali não é o texto.
#
#  Só que o eixo central da dissertação é a VOLATILIDADE, e é justamente ali
#  que o filtro mostrou ganho de correlação (0,1385 -> 0,1704). Falta a
#  pergunta que importa: correlação dentro da amostra vira PREVISÃO fora dela?
#
#  ------------------------------------------------------------------
#  COMO SE MEDE VOLATILIDADE AQUI
#  ------------------------------------------------------------------
#  Volatilidade não é observável: é preciso estimá-la. O retorno ao quadrado é
#  o estimador ingênuo, e é muito ruidoso. Usa-se aqui o estimador de
#  PARKINSON (1980), que aproveita a máxima e a mínima do dia em vez de apenas
#  o fechamento. Como o preço passeia entre as duas pontas ao longo do pregão,
#  a amplitude carrega mais informação que os extremos isolados — na prática,
#  Parkinson é cerca de cinco vezes mais eficiente.
#
#  ------------------------------------------------------------------
#  O MODELO DE REFERÊNCIA: HAR
#  ------------------------------------------------------------------
#  O HAR (CORSI, 2009) prevê a volatilidade de amanhã a partir da média dela
#  ontem, na última semana e no último mês. A intuição é que o mercado tem
#  agentes de horizontes diferentes — o operador de curtíssimo prazo, o gestor
#  semanal, o institucional mensal — e cada um reage a uma dessas médias.
#  É simples e notoriamente difícil de superar, o que o torna um adversário
#  honesto: se o sentimento acrescenta algo, tem de acrescentar SOBRE isso.
#
#  Três especificações, comparadas fora da amostra:
#      BASE — só HAR (sem sentimento nenhum)
#      +A   — HAR + ISM de TODAS as notícias
#      +B   — HAR + ISM filtrado (CAT1 + CAT2)
#
#  ------------------------------------------------------------------
#  COMO A COMPARAÇÃO É FEITA COM HONESTIDADE
#  ------------------------------------------------------------------
#  1. Janela EXPANSIVA: para prever o dia t, o modelo é reestimado usando
#     apenas os dias anteriores a t. Nunca vê o futuro.
#  2. Duas funções de perda: EQM sobre o log e QLIKE. A QLIKE é a métrica
#     usual em volatilidade porque pune de forma assimétrica — errar para
#     baixo num dia turbulento custa mais do que errar para cima num dia calmo.
#  3. Teste de DIEBOLD-MARIANO (1995): responde se a diferença de erro entre
#     dois modelos é real ou cabe dentro do acaso amostral. Usa erro-padrão
#     robusto a autocorrelação (Newey-West), porque erros de previsão de dias
#     seguidos são correlacionados.
#
#  Uso:
#      python src/modelagem/08_previsao_volatilidade_ism_filtrado.py
# =============================================================================
from __future__ import annotations

import argparse
import json
import warnings
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parents[2]
DIR = RAIZ / "Mestrado_PETR4"

PROP_TREINO_INICIAL = 0.60      # a janela expansiva começa com 60% da série
CAT_FILTRO = ["CAT1_Empresa", "CAT2_Mercado_Petroleo"]


# ─────────────────────────────────────────────────────────────────────────────
def volatilidade_parkinson(alta: pd.Series, baixa: pd.Series) -> pd.Series:
    """Estimador de Parkinson (1980) da volatilidade diária.

    sigma = sqrt( (ln(High/Low))^2 / (4 ln 2) )

    O fator 4·ln2 vem da esperança do quadrado da amplitude de um movimento
    browniano; é o que torna o estimador não enviesado sob essa hipótese.
    """
    return np.sqrt((np.log(alta / baixa) ** 2) / (4 * np.log(2)))


def montar_base(precos: pd.DataFrame, ism_a: pd.Series, ism_b: pd.Series) -> pd.DataFrame:
    """Base HAR: volatilidade de ontem, da última semana e do último mês."""
    d = precos.copy()
    d["vol"] = volatilidade_parkinson(d["High"], d["Low"])
    d = d[d["vol"] > 0].copy()
    d["lvol"] = np.log(d["vol"])

    # componentes HAR — todos defasados, para nunca usar o dia que se quer prever
    d["har_d"] = d["lvol"].shift(1)
    d["har_s"] = d["lvol"].rolling(5).mean().shift(1)
    d["har_m"] = d["lvol"].rolling(22).mean().shift(1)

    d["dia"] = d["Date"].dt.date
    d = d.merge(ism_a.rename("ism_a"), left_on="dia", right_index=True, how="left")
    d = d.merge(ism_b.rename("ism_b"), left_on="dia", right_index=True, how="left")
    d["ism_a_ont"] = d["ism_a"].shift(1)
    d["ism_b_ont"] = d["ism_b"].shift(1)

    return d.dropna(subset=["lvol", "har_d", "har_s", "har_m",
                            "ism_a_ont", "ism_b_ont"]).reset_index(drop=True)


def prever_expansivo(base: pd.DataFrame, colunas: list[str]) -> np.ndarray:
    """Previsão de 1 passo à frente, reestimando por mínimos quadrados a cada dia.

    Retorna o vetor de previsões do log da volatilidade no período de teste.
    """
    n = len(base)
    inicio = int(n * PROP_TREINO_INICIAL)
    y = base["lvol"].to_numpy()
    X = np.column_stack([np.ones(n)] + [base[c].to_numpy() for c in colunas])

    previsoes = np.empty(n - inicio)
    for k, t in enumerate(range(inicio, n)):
        beta, *_ = np.linalg.lstsq(X[:t], y[:t], rcond=None)   # só o passado
        previsoes[k] = X[t] @ beta
    return previsoes


def diebold_mariano(perda1: np.ndarray, perda2: np.ndarray, defasagens: int = 10):
    """Teste DM: o modelo 1 erra menos que o modelo 2, ou é acaso?

    Estatística = média da diferença de perdas / erro-padrão Newey-West.
    Negativa favorece o modelo 1.
    """
    dif = perda1 - perda2
    n = len(dif)
    m = dif.mean()
    dc = dif - m
    gama0 = (dc @ dc) / n
    variancia = gama0
    for lag in range(1, defasagens + 1):
        g = (dc[lag:] @ dc[:-lag]) / n
        variancia += 2 * (1 - lag / (defasagens + 1)) * g       # janela de Bartlett
    if variancia <= 0:
        return float("nan"), float("nan"), float(m)
    dm = m / np.sqrt(variancia / n)
    pv = 2 * (1 - stats.norm.cdf(abs(dm)))
    return float(dm), float(pv), float(m)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=DIR / "previsao_volatilidade_ism.json")
    args = ap.parse_args()

    noticias = pd.read_csv(DIR / "noticias_com_sentimento.csv",
                           usecols=["categoria", "Data", "Indice_Sentimento"])
    noticias["Data"] = pd.to_datetime(noticias["Data"], errors="coerce")
    noticias = noticias.dropna(subset=["Data", "Indice_Sentimento"])

    precos = pd.read_csv(DIR / "base_financeira_petr4.csv", skiprows=[1])
    precos["Date"] = pd.to_datetime(precos["Date"], errors="coerce")
    for c in ("High", "Low", "Close"):
        precos[c] = pd.to_numeric(precos[c], errors="coerce")
    precos = precos.dropna(subset=["Date", "High", "Low", "Close"]) \
                   .sort_values("Date").reset_index(drop=True)

    def ism(cats=None):
        s = noticias if cats is None else noticias[noticias["categoria"].isin(cats)]
        return s.groupby(s["Data"].dt.date)["Indice_Sentimento"].mean()

    base = montar_base(precos, ism(), ism(CAT_FILTRO))
    inicio = int(len(base) * PROP_TREINO_INICIAL)
    y_teste = base["lvol"].to_numpy()[inicio:]

    print("=" * 78)
    print("PREVISAO DE VOLATILIDADE FORA DA AMOSTRA (janela expansiva, 1 passo)")
    print("=" * 78)
    print(f"  pregoes: {len(base):,} | treino inicial: {inicio} | teste: {len(y_teste)}")
    print(f"  volatilidade: estimador de Parkinson sobre High/Low\n")

    especificacoes = {
        "BASE (so HAR)":        ["har_d", "har_s", "har_m"],
        "+A (HAR + ISM todas)": ["har_d", "har_s", "har_m", "ism_a_ont"],
        "+B (HAR + ISM CAT1+CAT2)": ["har_d", "har_s", "har_m", "ism_b_ont"],
    }

    perdas, res = {}, {"data_execucao": date.today().isoformat(),
                       "n_pregoes": int(len(base)), "n_teste": int(len(y_teste)),
                       "estimador_volatilidade": "Parkinson (High/Low)",
                       "modelos": {}}

    print(f"  {'especificacao':28s}{'EQM (log)':>12s}{'QLIKE':>12s}{'R2 fora':>11s}")
    for nome, cols in especificacoes.items():
        pred = prever_expansivo(base, cols)
        eqm = (y_teste - pred) ** 2
        # QLIKE opera na variância, não no log: sigma2 = exp(2*lvol)
        v_real, v_prev = np.exp(2 * y_teste), np.exp(2 * pred)
        qlike = np.log(v_prev) + v_real / v_prev
        r2 = 1 - eqm.sum() / ((y_teste - y_teste.mean()) ** 2).sum()
        perdas[nome] = {"eqm": eqm, "qlike": qlike}
        res["modelos"][nome] = {"eqm": round(float(eqm.mean()), 6),
                                "qlike": round(float(qlike.mean()), 6),
                                "r2_fora_amostra": round(float(r2), 4)}
        print(f"  {nome:28s}{eqm.mean():>12.6f}{qlike.mean():>12.6f}{r2:>11.4f}")

    print("\n" + "=" * 78)
    print("TESTE DE DIEBOLD-MARIANO (negativo favorece o primeiro modelo)")
    print("=" * 78)
    contrastes = [("+B (HAR + ISM CAT1+CAT2)", "BASE (so HAR)",
                   "ISM filtrado acrescenta algo ao HAR?"),
                  ("+A (HAR + ISM todas)", "BASE (so HAR)",
                   "ISM completo acrescenta algo ao HAR?"),
                  ("+B (HAR + ISM CAT1+CAT2)", "+A (HAR + ISM todas)",
                   "ISM filtrado supera o ISM completo?")]
    res["diebold_mariano"] = []
    for m1, m2, rot in contrastes:
        print(f"\n  {rot}")
        linha = {"contraste": f"{m1} x {m2}", "descricao": rot}
        for metrica in ("eqm", "qlike"):
            dm, pv, dif = diebold_mariano(perdas[m1][metrica], perdas[m2][metrica])
            sig = "SIGNIFICATIVO" if pv < 0.05 else "nao significativo"
            melhor = m1.split()[0] if dif < 0 else m2.split()[0]
            print(f"    {metrica.upper():6s} DM={dm:+7.3f}  p={pv:.4f}  "
                  f"dif_media={dif:+.6f}  -> {sig} (favorece {melhor})")
            linha[metrica] = {"DM": round(dm, 4), "p_valor": round(pv, 4),
                              "dif_media_perda": round(dif, 8),
                              "significativo": bool(pv < 0.05)}
        res["diebold_mariano"].append(linha)

    # ── onde o sentimento ajuda: dias calmos ou dias turbulentos? ────────────
    #
    #  A média esconde regime. Prever bem um dia calmo é fácil e pouco útil; o
    #  que interessa a quem gere risco é o dia turbulento. Divide-se então o
    #  período de teste em quartis da volatilidade efetivamente observada e
    #  compara-se o erro dentro de cada faixa.
    print("\n" + "=" * 78)
    print("ONDE O SENTIMENTO AJUDA? (erro por quartil de volatilidade observada)")
    print("=" * 78)
    quartil = pd.qcut(y_teste, 4, labels=["Q1 calmo", "Q2", "Q3", "Q4 turbulento"])
    print(f"  {'faixa':16s}{'n':>5s}{'BASE':>11s}{'+A todas':>11s}"
          f"{'+B filtrado':>13s}{'ganho B':>10s}")
    res["por_quartil"] = []
    for q in quartil.categories:
        sel = np.asarray(quartil == q)
        b = perdas["BASE (so HAR)"]["eqm"][sel].mean()
        a = perdas["+A (HAR + ISM todas)"]["eqm"][sel].mean()
        f = perdas["+B (HAR + ISM CAT1+CAT2)"]["eqm"][sel].mean()
        print(f"  {q:16s}{int(sel.sum()):>5d}{b:>11.5f}{a:>11.5f}{f:>13.5f}"
              f"{b - f:>+10.5f}")
        res["por_quartil"].append({"faixa": str(q), "n": int(sel.sum()),
                                   "eqm_base": round(float(b), 6),
                                   "eqm_ism_todas": round(float(a), 6),
                                   "eqm_ism_filtrado": round(float(f), 6),
                                   "ganho_filtrado_sobre_base": round(float(b - f), 6)})

    # DM restrito ao quartil turbulento
    sel = np.asarray(quartil == quartil.categories[-1])
    dm, pv, dif = diebold_mariano(perdas["+B (HAR + ISM CAT1+CAT2)"]["eqm"][sel],
                                  perdas["BASE (so HAR)"]["eqm"][sel])
    print(f"\n  DM restrito ao quartil turbulento (+B x BASE): DM={dm:+.3f}  p={pv:.4f}"
          f"  -> {'SIGNIFICATIVO' if pv < 0.05 else 'nao significativo'}")
    res["dm_quartil_turbulento"] = {"DM": round(dm, 4), "p_valor": round(pv, 4),
                                    "dif_media_perda": round(dif, 8),
                                    "significativo": bool(pv < 0.05)}

    # ── o coeficiente do sentimento tem o sinal esperado? ────────────────────
    #
    #  Ajuste único sobre toda a série (leitura DENTRO da amostra, apenas
    #  descritiva). Espera-se coeficiente NEGATIVO: sentimento mais pessimista
    #  hoje, volatilidade maior amanhã.
    print("\n" + "=" * 78)
    print("SINAL DO COEFICIENTE DO SENTIMENTO (ajuste dentro da amostra)")
    print("=" * 78)
    res["coeficientes"] = {}
    for rot, col in [("ISM todas", "ism_a_ont"), ("ISM CAT1+CAT2", "ism_b_ont")]:
        X = np.column_stack([np.ones(len(base))] +
                            [base[c].to_numpy() for c in ("har_d", "har_s", "har_m", col)])
        y = base["lvol"].to_numpy()
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ beta
        s2 = resid @ resid / (len(y) - X.shape[1])
        ep = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
        t = beta[-1] / ep[-1]
        pv = 2 * (1 - stats.t.cdf(abs(t), len(y) - X.shape[1]))
        print(f"  {rot:16s} coef={beta[-1]:+.4f}  ep={ep[-1]:.4f}  "
              f"t={t:+.2f}  p={pv:.4f}  -> "
              f"{'SIGNIFICATIVO' if pv < 0.05 else 'nao significativo'}")
        res["coeficientes"][rot] = {"coeficiente": round(float(beta[-1]), 6),
                                    "erro_padrao": round(float(ep[-1]), 6),
                                    "t": round(float(t), 4), "p_valor": round(float(pv), 6),
                                    "significativo": bool(pv < 0.05)}

    args.saida.write_text(json.dumps(res, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    print(f"\n[OK] Salvo em {args.saida}")


if __name__ == "__main__":
    main()
