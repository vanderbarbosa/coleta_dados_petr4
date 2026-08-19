# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — Notícia macro vence notícia da empresa? E em que prazo?
# =============================================================================
#
#  ------------------------------------------------------------------
#  DE ONDE VEM A HIPÓTESE
#  ------------------------------------------------------------------
#  BODILSEN e LUNDE (2025), no Journal of Applied Econometrics, testaram
#  exatamente o que a Seção 4.k desta dissertação testou --- acrescentar
#  sentimento de notícias a um modelo HAR de volatilidade --- e chegaram a
#  duas conclusões que aqui não foram investigadas:
#
#    1. O sentimento de notícia ESPECÍFICA DA EMPRESA não acrescenta nada
#       ao que a própria volatilidade passada já captura.
#    2. O sentimento de notícia MACROECONÔMICA melhora de forma significativa,
#       e a melhora é substancialmente maior em HORIZONTES LONGOS.
#
#  Ora, o índice desta pesquisa mistura tudo, e o recorte que adotamos como
#  padrão --- empresa mais mercado de petróleo --- é justamente o mais próximo
#  do "específico da empresa". E toda a avaliação foi feita a um dia de
#  distância. Se Bodilsen e Lunde estiverem certos, testamos a pior
#  combinação possível: a fatia errada do corpus, no prazo errado.
#
#  ------------------------------------------------------------------
#  O QUE ESTE SCRIPT FAZ
#  ------------------------------------------------------------------
#  Cruza cinco recortes do corpus com três horizontes de previsão:
#
#    EMPRESA   CAT1 + CAT6         (empresa e governança)
#    PETROLEO  CAT2                (mercado da commodity)
#    MACRO     CAT3 + CAT5 + CAT7  (geopolítica, sanções, macro de energia)
#    EMP+PETR  CAT1 + CAT2         (o recorte adotado na Seção 4.k)
#    TODAS     o corpus inteiro
#
#    horizontes: 1 dia, 5 dias (uma semana) e 22 dias (um mês)
#
#  Para cada célula, mede-se se o acréscimo do sentimento ao HAR reduz o erro
#  de previsão fora da amostra, com teste de Diebold-Mariano.
#
#  Uso:
#      python src/modelagem/10_macro_vs_empresa_horizontes.py
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
PROP_TREINO = 0.60

RECORTES = {
    "EMPRESA":  ["CAT1_Empresa", "CAT6_Governanca"],
    "PETROLEO": ["CAT2_Mercado_Petroleo"],
    "MACRO":    ["CAT3_Geopolitica", "CAT5_Sancoes_Navegacao", "CAT7_Macro_Energia"],
    "EMP+PETR": ["CAT1_Empresa", "CAT2_Mercado_Petroleo"],
    "TODAS":    None,
}
HORIZONTES = [1, 5, 22]


# ─────────────────────────────────────────────────────────────────────────────
def volatilidade_parkinson(alta: pd.Series, baixa: pd.Series) -> pd.Series:
    """Estimador de Parkinson (1980): usa a amplitude do pregão, não o fechamento."""
    return np.sqrt((np.log(alta / baixa) ** 2) / (4 * np.log(2)))


def montar_base(precos: pd.DataFrame, indices: dict[str, pd.Series]) -> pd.DataFrame:
    d = precos.copy()
    d["vol"] = volatilidade_parkinson(d["High"], d["Low"])
    d = d[d["vol"] > 0].copy()
    d["lvol"] = np.log(d["vol"])

    # componentes HAR, todos defasados
    d["har_d"] = d["lvol"].shift(1)
    d["har_s"] = d["lvol"].rolling(5).mean().shift(1)
    d["har_m"] = d["lvol"].rolling(22).mean().shift(1)

    # alvos: média do log da volatilidade nos próximos h pregões
    for h in HORIZONTES:
        d[f"alvo_{h}"] = (d["lvol"].rolling(h).mean().shift(-(h - 1))
                          if h > 1 else d["lvol"])

    d["dia"] = d["Date"].dt.date
    for nome, s in indices.items():
        d = d.merge(s.rename(nome), left_on="dia", right_index=True, how="left")
        d[f"{nome}_ont"] = d[nome].shift(1)

    cols = ["har_d", "har_s", "har_m"] + [f"{n}_ont" for n in indices]
    return d.dropna(subset=cols).reset_index(drop=True)


def prever_expansivo(base: pd.DataFrame, alvo: str, colunas: list[str],
                     inicio: int) -> tuple[np.ndarray, np.ndarray]:
    """Previsão de um passo, reestimando por mínimos quadrados a cada pregão."""
    sub = base.dropna(subset=[alvo]).reset_index(drop=True)
    n = len(sub)
    if inicio >= n:
        return np.array([]), np.array([])
    y = sub[alvo].to_numpy()
    X = np.column_stack([np.ones(n)] + [sub[c].to_numpy() for c in colunas])
    pred = np.empty(n - inicio)
    for k, t in enumerate(range(inicio, n)):
        beta, *_ = np.linalg.lstsq(X[:t], y[:t], rcond=None)   # só o passado
        pred[k] = X[t] @ beta
    return y[inicio:], pred


def diebold_mariano(p1: np.ndarray, p2: np.ndarray, defasagens: int = 22):
    """Negativo favorece o primeiro modelo. Erro-padrão robusto (Newey-West)."""
    d = p1 - p2
    n = len(d)
    m = d.mean()
    dc = d - m
    var = (dc @ dc) / n
    for lag in range(1, min(defasagens, n - 1) + 1):
        var += 2 * (1 - lag / (defasagens + 1)) * (dc[lag:] @ dc[:-lag]) / n
    if var <= 0:
        return float("nan"), float("nan")
    dm = m / np.sqrt(var / n)
    return float(dm), float(2 * (1 - stats.norm.cdf(abs(dm))))


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=DIR / "macro_vs_empresa.json")
    args = ap.parse_args()

    n = pd.read_csv(DIR / "noticias_com_sentimento.csv",
                    usecols=["Data_Ajustada", "categoria", "Indice_Sentimento"])
    n["dia"] = pd.to_datetime(n["Data_Ajustada"], errors="coerce")
    n = n.dropna(subset=["dia", "Indice_Sentimento"])

    p = pd.read_csv(DIR / "base_financeira_petr4.csv", skiprows=[1])
    p["Date"] = pd.to_datetime(p["Date"], errors="coerce")
    for c in ("High", "Low", "Close"):
        p[c] = pd.to_numeric(p[c], errors="coerce")
    p = p.dropna(subset=["Date", "High", "Low", "Close"]) \
         .sort_values("Date").reset_index(drop=True)

    print("=" * 78)
    print("NOTICIA MACRO x NOTICIA DA EMPRESA, EM TRES HORIZONTES")
    print("=" * 78)
    print("  Hipotese de Bodilsen e Lunde (2025, J. Applied Econometrics):")
    print("  noticia da empresa nao acrescenta ao HAR; noticia MACRO acrescenta,")
    print("  e o ganho e maior nos horizontes LONGOS.\n")

    indices = {}
    print(f"  {'recorte':12s}{'noticias':>11s}{'% corpus':>10s}{'dias':>8s}")
    for nome, cats in RECORTES.items():
        sub = n if cats is None else n[n["categoria"].isin(cats)]
        indices[nome] = sub.groupby(sub["dia"].dt.date)["Indice_Sentimento"].mean()
        print(f"  {nome:12s}{len(sub):>11,}{len(sub)/len(n):>9.0%}"
              f"{len(indices[nome]):>8,}")

    base = montar_base(p, indices)
    inicio = int(len(base) * PROP_TREINO)
    print(f"\n  pregoes: {len(base):,} | treino inicial: {inicio}")

    res = {"data_execucao": date.today().isoformat(), "n_pregoes": int(len(base)),
           "hipotese": "Bodilsen e Lunde (2025): macro acrescenta ao HAR, "
                       "empresa nao; ganho maior em horizonte longo",
           "resultados": []}

    for h in HORIZONTES:
        alvo = f"alvo_{h}"
        y, pred_base = prever_expansivo(base, alvo, ["har_d", "har_s", "har_m"], inicio)
        if not len(y):
            continue
        perda_base = (y - pred_base) ** 2

        print("\n" + "=" * 78)
        print(f"HORIZONTE DE {h} PREGAO(S)  --  {len(y)} previsoes fora da amostra")
        print("=" * 78)
        print(f"  HAR sozinho (referencia): EQM = {perda_base.mean():.6f}\n")
        print(f"  {'recorte':12s}{'EQM':>12s}{'ganho %':>10s}{'DM':>9s}{'p':>9s}")

        for nome in RECORTES:
            y2, pred = prever_expansivo(
                base, alvo, ["har_d", "har_s", "har_m", f"{nome}_ont"], inicio)
            perda = (y2 - pred) ** 2
            dm, pv = diebold_mariano(perda, perda_base)
            ganho = (perda_base.mean() - perda.mean()) / perda_base.mean() * 100
            marca = "  <-- SIGNIFICATIVO" if pv < 0.05 and ganho > 0 else ""
            print(f"  {nome:12s}{perda.mean():>12.6f}{ganho:>+10.2f}"
                  f"{dm:>9.3f}{pv:>9.4f}{marca}")
            res["resultados"].append({
                "horizonte": h, "recorte": nome,
                "eqm": round(float(perda.mean()), 8),
                "eqm_har": round(float(perda_base.mean()), 8),
                "ganho_pct": round(float(ganho), 4),
                "DM": round(dm, 4), "p_valor": round(pv, 6),
                "significativo": bool(pv < 0.05 and ganho > 0)})

    # ── síntese ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("SINTESE")
    print("=" * 78)
    sig = [r for r in res["resultados"] if r["significativo"]]
    if sig:
        print("  Combinacoes que superam o HAR de forma significativa:\n")
        for r in sorted(sig, key=lambda x: -x["ganho_pct"]):
            print(f"    {r['recorte']:10s} horizonte {r['horizonte']:2d} dia(s): "
                  f"{r['ganho_pct']:+.2f}% de EQM  (p={r['p_valor']:.4f})")
    else:
        print("  Nenhuma combinacao supera o HAR de forma significativa.")

    print("\n  Ganho medio por recorte, atraves dos horizontes:")
    df = pd.DataFrame(res["resultados"])
    for nome, g in df.groupby("recorte", sort=False):
        print(f"    {nome:12s}{g['ganho_pct'].mean():>+8.2f}%")
    print("\n  Ganho medio por horizonte, atraves dos recortes:")
    for h, g in df.groupby("horizonte"):
        print(f"    {h:2d} dia(s){g['ganho_pct'].mean():>+8.2f}%")

    args.saida.write_text(json.dumps(res, indent=2, ensure_ascii=False, default=float),
                          encoding="utf-8")
    print(f"\n[OK] Salvo em {args.saida}")


if __name__ == "__main__":
    main()
