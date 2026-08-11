# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — Validação dos rótulos humanos contra o MERCADO
# =============================================================================
#
#  MOTIVAÇÃO
#  Na mentoria de 29/07/2026 o Prof. Emerson levantou que a rotulagem, para ser
#  útil e válida, precisaria ser feita por especialistas em finanças.
#
#  Este script transforma essa questão — que até aqui era de opinião — em
#  hipótese testável. A ideia é simples: o gabarito humano registra, na coluna
#  `Direcao_Esperada_PETR4`, uma APOSTA sobre o efeito da notícia no preço.
#  O mercado já respondeu a essa aposta. Basta confrontar.
#
#  A vantagem decisiva: o retorno realizado é um "rótulo" que NÃO precisa de
#  anotador nenhum. Ele existe, é público e é indiscutível.
#
#  TRÊS TESTES
#    1. A direção esperada pelo humano acerta o retorno realizado em D+1?
#       → mede a competência do anotador na tarefa que exige finanças
#    2. Notícias marcadas como relevantes geram mais volatilidade?
#       → mede o conteúdo econômico do rótulo de relevância
#    3. O tom (sentimento) se associa à magnitude do retorno?
#       → mede o conteúdo econômico do rótulo de sentimento
#
#  CUIDADO METODOLÓGICO IMPLEMENTADO
#  Várias notícias podem cair no mesmo pregão, o que quebraria a independência
#  das observações. O script COLAPSA por pregão (voto majoritário) antes de
#  testar, e reporta quantos pregões distintos sobraram.
#
#  Uso:
#      python src/sentimento/validar_rotulos_contra_mercado.py
# =============================================================================
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parents[2]
GABARITO = RAIZ / "Mestrado_PETR4" / "conjunto_ouro" / "conjunto_ouro_para_rotular.xlsx"
PRECOS = RAIZ / "Mestrado_PETR4" / "base_financeira_petr4.csv"
SAIDA = RAIZ / "Mestrado_PETR4" / "validacao_rotulos_contra_mercado.json"


def carregar_precos(caminho: Path) -> pd.DataFrame:
    """Lê a base do yfinance (2ª linha é o ticker repetido) e calcula D+1."""
    p = pd.read_csv(caminho, skiprows=[1])
    p["Date"] = pd.to_datetime(p["Date"], errors="coerce")
    p["Close"] = pd.to_numeric(p["Close"], errors="coerce")
    p = p.dropna(subset=["Date", "Close"]).sort_values("Date").reset_index(drop=True)
    # retorno do PREGÃO SEGUINTE: a notícia de hoje afeta o fechamento de amanhã
    p["ret_d1"] = p["Close"].pct_change().shift(-1)
    p["vol_abs_d1"] = p["ret_d1"].abs()
    return p.dropna(subset=["ret_d1"])


def casar_noticia_pregao(g: pd.DataFrame, p: pd.DataFrame) -> pd.DataFrame:
    """Casa cada notícia com o primeiro pregão >= data da notícia.

    `direction='forward'` garante que notícia de fim de semana ou feriado seja
    atribuída ao pregão seguinte, e nunca ao anterior — o que vazaria futuro.
    """
    return pd.merge_asof(
        g.sort_values("Data"),
        p[["Date", "ret_d1", "vol_abs_d1"]].sort_values("Date"),
        left_on="Data", right_on="Date", direction="forward",
    ).dropna(subset=["ret_d1"])


def voto_majoritario(s: pd.Series):
    """Direção do dia. Devolve None em caso de empate (dia descartado)."""
    v = s.value_counts()
    if len(v) == 1:
        return v.index[0]
    return v.index[0] if v.iloc[0] > v.iloc[1] else None


def teste_direcao(m: pd.DataFrame) -> dict:
    """TESTE 1 — a aposta direcional do humano bate o acaso?"""
    d = m[m["Direcao_Esperada_PETR4"].isin(["Alta", "Baixa"])]
    # colapsa por pregão para preservar independência
    agg = (d.groupby("Date")
             .agg(direcao=("Direcao_Esperada_PETR4", voto_majoritario),
                  ret=("ret_d1", "first"))
             .dropna(subset=["direcao"]))
    agg["acertou"] = (((agg["direcao"] == "Alta") & (agg["ret"] > 0)) |
                      ((agg["direcao"] == "Baixa") & (agg["ret"] < 0)))
    n, k = len(agg), int(agg["acertou"].sum())
    bt = stats.binomtest(k, n, 0.5)
    lo, hi = bt.proportion_ci(0.95)

    por_classe = {}
    for cls in ("Alta", "Baixa"):
        sub = agg[agg["direcao"] == cls]
        if len(sub):
            por_classe[cls] = {"n": int(len(sub)),
                               "acertos": int(sub["acertou"].sum()),
                               "taxa": round(float(sub["acertou"].mean()), 4)}

    return {
        "n_pregoes": n, "acertos": k, "taxa_acerto": round(k / n, 4),
        "p_valor_binomial": round(float(bt.pvalue), 4),
        "ic95": [round(float(lo), 4), round(float(hi), 4)],
        "por_classe": por_classe,
    }


def teste_relevancia(m: pd.DataFrame) -> dict:
    """TESTE 2 — notícia relevante move mais o preço?"""
    rel = m.loc[m["Relevante_PETR4"] == "Sim", "vol_abs_d1"].dropna()
    nao = m.loc[m["Relevante_PETR4"] == "Não", "vol_abs_d1"].dropna()
    u, pv = stats.mannwhitneyu(rel, nao, alternative="greater")
    return {
        "relevantes": {"n": int(len(rel)), "mediana": round(float(rel.median()), 6),
                       "media": round(float(rel.mean()), 6)},
        "nao_relevantes": {"n": int(len(nao)), "mediana": round(float(nao.median()), 6),
                           "media": round(float(nao.mean()), 6)},
        "mann_whitney_U": round(float(u), 1),
        "p_valor": round(float(pv), 4),
    }


def teste_sentimento_volatilidade(m: pd.DataFrame) -> dict:
    """TESTE 3 — o tom se associa à magnitude do retorno? (só relevantes)"""
    rr = m[m["Relevante_PETR4"] == "Sim"]
    por_classe = {
        cls: {"n": int(len(g)),
              "mediana_abs_ret": round(float(g["vol_abs_d1"].median()), 6),
              "media_abs_ret": round(float(g["vol_abs_d1"].mean()), 6)}
        for cls, g in rr.groupby("Sentimento_Humano")
    }
    grupos = [g["vol_abs_d1"].dropna().values for _, g in rr.groupby("Sentimento_Humano")]
    h, pv = stats.kruskal(*grupos) if len(grupos) > 1 else (np.nan, np.nan)
    return {"por_classe": por_classe,
            "kruskal_H": round(float(h), 4), "p_valor": round(float(pv), 4)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gabarito", type=Path, default=GABARITO)
    ap.add_argument("--precos", type=Path, default=PRECOS)
    ap.add_argument("--saida", type=Path, default=SAIDA)
    args = ap.parse_args()

    p = carregar_precos(args.precos)
    g = pd.read_excel(args.gabarito, sheet_name="Rotular")
    g["Data"] = pd.to_datetime(g["Data"], errors="coerce")
    g = g.dropna(subset=["Data"])

    m = casar_noticia_pregao(g, p)
    print(f"Notícias casadas com pregão: {len(m)} de {len(g)}")
    print(f"Pregões distintos          : {m['Date'].nunique()}")
    print(f"Referência de mercado      : PETR4 subiu em "
          f"{(p['ret_d1'] > 0).mean():.1%} dos pregões da série\n")

    t1 = teste_direcao(m)
    print("=== TESTE 1 — direção esperada pelo HUMANO × retorno realizado (D+1) ===")
    print(f"  n={t1['n_pregoes']} pregões · acertos={t1['acertos']} · "
          f"taxa={t1['taxa_acerto']:.1%} · p={t1['p_valor_binomial']:.4f}")
    print(f"  IC95% da taxa de acerto: "
          f"[{t1['ic95'][0]:.1%}, {t1['ic95'][1]:.1%}]")
    for cls, v in t1["por_classe"].items():
        print(f"    {cls:6s} n={v['n']:3d} acertos={v['acertos']:3d} "
              f"taxa={v['taxa']:.1%}")

    t2 = teste_relevancia(m)
    print("\n=== TESTE 2 — |retorno| D+1: relevantes × não relevantes ===")
    print(f"  relevantes     n={t2['relevantes']['n']:3d} "
          f"mediana={t2['relevantes']['mediana']:.4%}")
    print(f"  não relevantes n={t2['nao_relevantes']['n']:3d} "
          f"mediana={t2['nao_relevantes']['mediana']:.4%}")
    print(f"  Mann-Whitney unilateral: p={t2['p_valor']:.4f}")

    t3 = teste_sentimento_volatilidade(m)
    print("\n=== TESTE 3 — |retorno| D+1 por sentimento (só relevantes) ===")
    for cls, v in sorted(t3["por_classe"].items()):
        print(f"  {cls:9s} n={v['n']:3d} mediana={v['mediana_abs_ret']:.4%} "
              f"média={v['media_abs_ret']:.4%}")
    print(f"  Kruskal-Wallis: p={t3['p_valor']:.4f}")

    args.saida.write_text(json.dumps({
        "data_execucao": date.today().isoformat(),
        "n_noticias": int(len(m)),
        "n_pregoes_distintos": int(m["Date"].nunique()),
        "taxa_alta_mercado": round(float((p["ret_d1"] > 0).mean()), 4),
        "teste1_direcao_humana": t1,
        "teste2_relevancia_volatilidade": t2,
        "teste3_sentimento_volatilidade": t3,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[OK] Salvo em {args.saida}")

    print("\n" + "=" * 70)
    print("LEITURA - cuidados obrigatorios ao reportar:")
    print("  - O TESTE 1 tem n pequeno e IC largo. NAO prova que um")
    print("    especialista falharia; apenas que ESTE anotador nao bateu o acaso.")
    print("  - No TESTE 2, as 'nao relevantes' tambem passaram pelo filtro da")
    print("    taxonomia PETR4 - sao noticias de energia/petroleo, e nao ruido")
    print("    aleatorio. O contraste e, portanto, conservador.")
    print("  - D+1 e uma janela curta. Ver gap G1 sobre multiplos horizontes.")


if __name__ == "__main__":
    main()
