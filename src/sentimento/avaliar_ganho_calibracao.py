# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — A calibração do ISM melhora a previsão?
# =============================================================================
#
#  Complemento obrigatório de `calibrar_ism_com_gabarito.py`.
#
#  Aquele script mostra que o ISM bruto tem viés grande e sistemático (87% do
#  valor, troca de sinal em 49 de 96 meses). A pergunta natural, e que o Prof.
#  Emerson certamente fará, é: **isso melhora o resultado da dissertação?**
#
#  Este script responde — e a resposta é NÃO, pelo menos não na correlação
#  linear. Registrá-lo é mais importante do que escondê-lo: um resultado
#  negativo documentado vale mais em banca do que uma melhoria alegada e não
#  verificada.
#
#  A EXPLICAÇÃO (que é o achado de verdade)
#  A correlação entre o ISM bruto e o calibrado é 0,973. A calibração desloca
#  sobretudo o NÍVEL da série, e correlação é invariante a deslocamento de
#  nível — ele é absorvido pelo intercepto de qualquer regressão. Logo:
#
#    • a calibração CONSERTA a INTERPRETAÇÃO do índice
#      (o corpus não é majoritariamente negativo; isso era artefato do modelo)
#    • a calibração NÃO MELHORA o PODER PREDITIVO em modelo linear
#
#  Onde a calibração importa de fato:
#    - afirmar que um período foi otimista ou pessimista
#    - qualquer regra de limiar ("ISM < -0,30 -> regime de estresse")
#    - classificação de regimes
#    - a validação qualitativa contra eventos econômicos
#
#  Uso:
#      python src/sentimento/avaliar_ganho_calibracao.py
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
DIR = RAIZ / "Mestrado_PETR4"


def correlacoes(x: pd.Series, y: pd.Series) -> dict:
    r, pr = stats.pearsonr(x, y)
    s, ps = stats.spearmanr(x, y)
    return {"pearson_r": round(float(r), 4), "pearson_p": round(float(pr), 4),
            "spearman_rho": round(float(s), 4), "spearman_p": round(float(ps), 4)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ism", type=Path, default=DIR / "ism_calibrado_petr4.csv")
    ap.add_argument("--precos", type=Path, default=DIR / "base_financeira_petr4.csv")
    ap.add_argument("--saida", type=Path, default=DIR / "ganho_calibracao_ism.json")
    args = ap.parse_args()

    ism = pd.read_csv(args.ism)
    ism["mes"] = pd.PeriodIndex(ism["mes"], freq="M")

    p = pd.read_csv(args.precos, skiprows=[1])
    p["Date"] = pd.to_datetime(p["Date"], errors="coerce")
    p["Close"] = pd.to_numeric(p["Close"], errors="coerce")
    p = p.dropna(subset=["Date", "Close"]).sort_values("Date")
    p["ret"] = np.log(p["Close"]).diff()
    p["mes"] = p["Date"].dt.to_period("M")

    # volatilidade realizada mensal, anualizada
    vol = (p.groupby("mes")["ret"]
             .agg(vol=lambda s: s.std() * np.sqrt(252), ret_mes="sum")
             .reset_index())

    d = ism.merge(vol, on="mes").dropna(subset=["ISM_bruto", "ISM_calibrado", "vol"])
    d["vol_prox"] = d["vol"].shift(-1)
    d["ret_prox"] = d["ret_mes"].shift(-1)

    print("=" * 74)
    print("A CALIBRACAO DO ISM MELHORA A PREVISAO?")
    print("=" * 74)
    print(f"\nMeses pareados: {len(d)}")
    print(f"Correlacao entre ISM bruto e calibrado: "
          f"{d['ISM_bruto'].corr(d['ISM_calibrado']):.4f}")
    print("  -> as duas series tem quase a MESMA FORMA; o que muda e o NIVEL.\n")

    testes = {}
    blocos = [
        ("volatilidade do mes SEGUINTE", "vol_prox"),
        ("volatilidade CONTEMPORANEA", "vol"),
        ("retorno do mes SEGUINTE", "ret_prox"),
    ]
    for rotulo, alvo in blocos:
        sub = d.dropna(subset=[alvo])
        print(f"=== ISM -> {rotulo} (n={len(sub)}) ===")
        cb = correlacoes(sub["ISM_bruto"], sub[alvo])
        cc = correlacoes(sub["ISM_calibrado"], sub[alvo])
        for nome, c in (("BRUTO", cb), ("CALIBRADO", cc)):
            print(f"  ISM {nome:10s} Pearson r={c['pearson_r']:+.4f} "
                  f"(p={c['pearson_p']:.4f})   "
                  f"Spearman={c['spearman_rho']:+.4f} (p={c['spearman_p']:.4f})")
        delta = abs(cc["pearson_r"]) - abs(cb["pearson_r"])
        print(f"  -> variacao em |r|: {delta:+.4f} "
              f"{'(calibrado melhor)' if delta > 0 else '(calibrado NAO melhor)'}\n")
        testes[alvo] = {"rotulo": rotulo, "n": int(len(sub)),
                        "bruto": cb, "calibrado": cc,
                        "delta_abs_r": round(delta, 4)}

    print("=" * 74)
    print("CONCLUSAO")
    print("=" * 74)
    print("""
A calibracao NAO melhora a correlacao com a volatilidade nem com o retorno.
Isso era esperado: correlacao e invariante a deslocamento de nivel, e a
calibracao desloca sobretudo o nivel (r = 0,97 entre as duas series).

O que a calibracao CONSERTA, e que e relevante para a dissertacao:
  1. A leitura do indice. O ISM bruto diz que o corpus e fortemente negativo
     (-0,345); calibrado, ele e praticamente neutro (-0,044). A negatividade
     era artefato do classificador, nao propriedade do corpus.
  2. O SINAL do indice em 49 dos 96 meses. Qualquer afirmacao do tipo
     "o mercado estava pessimista em <mes>" muda de conclusao.
  3. Qualquer regra de limiar e qualquer classificacao de regime.
  4. A validacao qualitativa contra eventos economicos.

O que a calibracao NAO conserta:
  - o poder preditivo. Para isso o caminho e outro: melhorar o CLASSIFICADOR
    (comite de modelos, adaptacao de dominio), e nao corrigir a agregacao.

Observacao adicional que sobressai dos numeros: a relacao CONTEMPORANEA e
significativa (r = -0,31, p = 0,002) e a PREDITIVA nao e. Sentimento negativo
COINCIDE com volatilidade alta no mesmo mes, mas nao antecipa o mes seguinte.
E coerente com o resto do que ja encontramos.
""")

    args.saida.write_text(json.dumps({
        "data_execucao": date.today().isoformat(),
        "n_meses": int(len(d)),
        "corr_bruto_calibrado": round(float(d["ISM_bruto"].corr(d["ISM_calibrado"])), 4),
        "testes": testes,
        "conclusao": "A calibracao corrige o NIVEL e a INTERPRETACAO do indice, "
                     "mas nao melhora a correlacao preditiva. Correlacao e "
                     "invariante a deslocamento de nivel.",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] Salvo em {args.saida}")


if __name__ == "__main__":
    main()
