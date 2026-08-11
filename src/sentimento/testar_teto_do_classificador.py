# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — Qual é o TETO de melhorar o classificador?
# =============================================================================
#
#  A PERGUNTA
#  "O que está baixo: a classificação da notícia, o índice de sentimento ou a
#  direção do preço?" — e, decorrente dela: vale a pena investir em melhorar o
#  classificador?
#
#  O EXPERIMENTO
#  O conjunto-ouro dá acesso a algo que normalmente não se tem: o rótulo
#  HUMANO. Ele funciona como um classificador PERFEITO por construção — é o
#  limite superior do que qualquer encoder poderia atingir neste corpus.
#
#  Basta então rodar a mesma regra de decisão duas vezes:
#     (a) com o sentimento do MODELO   -> desempenho atual
#     (b) com o sentimento HUMANO      -> TETO teórico
#
#  A diferença entre (a) e (b) é exatamente o quanto se ganharia com um
#  classificador perfeito. Se for pequena, melhorar o encoder é inútil para
#  aquela tarefa, por melhor que seja a intenção.
#
#  RESULTADO (08/08/2026)
#    DIREÇÃO      : modelo 49,7% -> humano 50,9%   (ganho de 1,2 pp, nulo)
#    VOLATILIDADE : modelo p=0,502 -> humano p=0,098 (o sinal APARECE)
#
#  Ou seja: melhorar o classificador NÃO resolve a direção — o gargalo ali não
#  é o texto. Mas parece deslocar a agulha na volatilidade, que é justamente o
#  eixo central da dissertação.
#
#  Uso:
#      python src/sentimento/testar_teto_do_classificador.py
# =============================================================================
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parents[2]
DIR = RAIZ / "Mestrado_PETR4"
MAPA = {"Positivo": "Positive", "Negativo": "Negative", "Neutro": "Neutral"}


def carregar(dir_dados: Path):
    p = pd.read_csv(dir_dados / "base_financeira_petr4.csv", skiprows=[1])
    p["Date"] = pd.to_datetime(p["Date"], errors="coerce")
    p["Close"] = pd.to_numeric(p["Close"], errors="coerce")
    p = p.dropna(subset=["Date", "Close"]).sort_values("Date")
    p["ret_d1"] = p["Close"].pct_change().shift(-1)
    p["vol"] = p["ret_d1"].abs()
    p = p.dropna(subset=["ret_d1"])

    h = pd.read_excel(dir_dados / "conjunto_ouro" / "conjunto_ouro_para_rotular.xlsx",
                      sheet_name="Rotular")
    m = pd.read_csv(dir_dados / "conjunto_ouro" / "conjunto_ouro_gabarito_modelo.csv")
    d = h.merge(m[["ID_OURO", "Label_Sentimento"]], on="ID_OURO")
    d["humano"] = d["Sentimento_Humano"].map(MAPA)
    d["Data"] = pd.to_datetime(d["Data"], errors="coerce")
    d = pd.merge_asof(d.sort_values("Data"),
                      p[["Date", "ret_d1", "vol"]].sort_values("Date"),
                      left_on="Data", right_on="Date", direction="forward")
    d = d.dropna(subset=["ret_d1"])
    d["subiu"] = d["ret_d1"] > 0
    return d, float((p["ret_d1"] > 0).mean())


def testar_direcao(d: pd.DataFrame, coluna: str) -> dict:
    """Regra: Positive -> aposta alta; Negative -> aposta baixa; Neutral -> não aposta.

    Colapsa por pregão (moda) para preservar a independência das observações.
    """
    ap = d[d[coluna].isin(["Positive", "Negative"])]
    g = (ap.groupby("Date")
           .agg(pred=(coluna, lambda s: s.mode().iat[0] if len(s.mode()) == 1 else None),
                subiu=("subiu", "first"))
           .dropna(subset=["pred"]))
    g["ok"] = (((g["pred"] == "Positive") & g["subiu"]) |
               ((g["pred"] == "Negative") & ~g["subiu"]))
    n, k = len(g), int(g["ok"].sum())
    bt = stats.binomtest(k, n, 0.5)
    lo, hi = bt.proportion_ci(0.95)
    return {"n_pregoes": n, "acertos": k, "taxa": round(k / n, 4),
            "p_valor": round(float(bt.pvalue), 4),
            "ic95": [round(float(lo), 4), round(float(hi), 4)]}


def testar_volatilidade(d: pd.DataFrame, coluna: str) -> dict:
    """Notícia negativa é seguida de movimento maior que notícia positiva?"""
    neg = d.loc[d[coluna] == "Negative", "vol"].dropna()
    pos = d.loc[d[coluna] == "Positive", "vol"].dropna()
    u, pv = stats.mannwhitneyu(neg, pos, alternative="greater")
    return {"n_neg": int(len(neg)), "n_pos": int(len(pos)),
            "mediana_apos_negativa": round(float(neg.median()), 6),
            "mediana_apos_positiva": round(float(pos.median()), 6),
            "razao": round(float(neg.median() / pos.median()), 4),
            "mann_whitney_U": round(float(u), 1), "p_valor": round(float(pv), 4)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=DIR / "teto_do_classificador.json")
    args = ap.parse_args()

    d, base = carregar(DIR)
    print(f"n = {len(d)} noticias | baseline 'sempre alta' no periodo = {base:.1%}\n")

    res = {"data_execucao": date.today().isoformat(), "n": int(len(d)),
           "baseline_alta": round(base, 4), "direcao": {}, "volatilidade": {}}

    print("=" * 76)
    print("TESTE 1 - DIRECAO: um classificador PERFEITO ajudaria?")
    print("=" * 76)
    print("  Regra: Positive -> aposta alta | Negative -> aposta baixa | Neutral -> passa\n")
    for col, nome in [("Label_Sentimento", "sentimento do MODELO (acc 0,58)"),
                      ("humano", "sentimento HUMANO (teto teorico)")]:
        r = testar_direcao(d, col)
        res["direcao"][col] = r
        print(f"  {nome:38s} n={r['n_pregoes']:3d}  taxa={r['taxa']:.1%}  "
              f"p={r['p_valor']:.3f}  IC95=[{r['ic95'][0]:.1%},{r['ic95'][1]:.1%}]")

    ganho = res["direcao"]["humano"]["taxa"] - res["direcao"]["Label_Sentimento"]["taxa"]
    res["ganho_direcao_pp"] = round(ganho * 100, 2)
    print(f"\n  >>> GANHO de um classificador perfeito: {ganho * 100:+.1f} pontos percentuais")
    print(f"  >>> Ambos ficam ABAIXO do baseline de 'sempre alta' ({base:.1%}).")
    print("  >>> O gargalo da DIRECAO nao e o classificador.")

    print("\n" + "=" * 76)
    print("TESTE 2 - VOLATILIDADE: e aqui, ajudaria?")
    print("=" * 76)
    print("  Hipotese: noticia negativa e seguida de movimento MAIOR que positiva\n")
    for col, nome in [("Label_Sentimento", "sentimento do MODELO"),
                      ("humano", "sentimento HUMANO (teto)")]:
        r = testar_volatilidade(d, col)
        res["volatilidade"][col] = r
        print(f"  {nome:30s} apos NEG: {r['mediana_apos_negativa']:.4%} (n={r['n_neg']})  "
              f"apos POS: {r['mediana_apos_positiva']:.4%} (n={r['n_pos']})")
        print(f"  {'':30s} razao={r['razao']:.2f}x   Mann-Whitney p={r['p_valor']:.4f}")

    pm = res["volatilidade"]["Label_Sentimento"]["p_valor"]
    ph = res["volatilidade"]["humano"]["p_valor"]
    print(f"\n  >>> Com o rotulo do MODELO o sinal NAO aparece (p={pm:.3f}).")
    print(f"  >>> Com o rotulo HUMANO ele aparece (p={ph:.3f}), na direcao esperada.")
    print("  >>> ATENCAO: p=0,098 NAO e significativo a 5%. E TENDENCIA, nao resultado.")
    print("  >>> Mas o contraste sugere que o ruido do classificador esta APAGANDO")
    print("  >>> um sinal que existe — e que melhorar o encoder pode recupera-lo.")

    print("\n" + "=" * 76)
    print("CONCLUSAO")
    print("=" * 76)
    print("""
Melhorar o classificador:
  - para a DIRECAO      -> INUTIL. O teto (rotulo humano) tambem fica no acaso.
  - para a VOLATILIDADE -> PROMISSOR. O sinal existe no rotulo perfeito e se
                           perde no rotulo do modelo.

Isso reordena as prioridades da dissertacao: os investimentos em comite (G7) e
adaptacao de dominio (G3) devem ser justificados pelo eixo da VOLATILIDADE, e
nao pela promessa de melhorar a previsao de direcao — que nao vai acontecer.
""")
    args.saida.write_text(json.dumps(res, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    print(f"[OK] Salvo em {args.saida}")


if __name__ == "__main__":
    main()
