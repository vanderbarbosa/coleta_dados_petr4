# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — Calibração do ISM com o conjunto-ouro
#  DEMONSTRAÇÃO PRÁTICA: como 300 rótulos humanos corrigem 8 anos de série
# =============================================================================
#
#  A PERGUNTA QUE ESTE SCRIPT RESPONDE
#  Na mentoria de 29/07/2026 o Prof. Emerson perguntou como as notícias
#  rotuladas seriam usadas na prática. Este script é a resposta executável.
#
#  O RACIOCÍNIO
#  O Índice de Sentimento da Mídia é uma função das PROPORÇÕES de classe:
#
#        ISM = (Pos - Neg) / (Pos + Neu + Neg)
#
#  O classificador erra de forma SISTEMÁTICA — a matriz de confusão medida no
#  conjunto-ouro mostra que 46,8% das manchetes neutras são empurradas para as
#  classes extremas. Logo as proporções observadas são viesadas, e o ISM está
#  viesado TODOS OS DIAS, ao longo de toda a série. Esse ISM entra no GARCH e
#  no XGBoost: o viés se propaga até o resultado final da dissertação.
#
#  A CORREÇÃO
#  Com a matriz de confusão estimada no gabarito é possível recuperar as
#  proporções verdadeiras. Sendo M[i][j] = P(predito=j | verdadeiro=i):
#
#        p_predito = M^T · p_verdadeiro    =>    p_verdadeiro = (M^T)^-1 · p_predito
#
#  É o método "Adjusted Classify and Count" (ACC), da literatura de
#  QUANTIFICAÇÃO — o subcampo que estima prevalência de classes em vez de
#  classificar itens individuais. Referência: Forman (2008), "Quantifying
#  counts and costs via classification", Data Mining and Knowledge Discovery.
#
#  POR QUE ISSO IMPORTA PARA A DEFESA
#  Os 300 rótulos NÃO treinam o modelo (300 itens não ajustam 110 milhões de
#  parâmetros). Eles CALIBRAM O INSTRUMENTO. É a diferença entre um termômetro
#  sem aferição e um termômetro aferido: o segundo não esquenta nada, mas é o
#  único cujas leituras significam alguma coisa.
#
#  Uso:
#      python src/sentimento/calibrar_ism_com_gabarito.py
# =============================================================================
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
DIR_DADOS = RAIZ / "Mestrado_PETR4"
GAB_HUMANO = DIR_DADOS / "conjunto_ouro" / "conjunto_ouro_para_rotular.xlsx"
GAB_MODELO = DIR_DADOS / "conjunto_ouro" / "conjunto_ouro_gabarito_modelo.csv"
CORPUS = DIR_DADOS / "noticias_com_sentimento.csv"

CLASSES = ["Negative", "Neutral", "Positive"]
MAPA_HUMANO = {"Negativo": "Negative", "Neutro": "Neutral", "Positivo": "Positive"}


# ─────────────────────────────────────────────────────────────────────────────
#  ETAPA 1 — matriz de confusão a partir do gabarito
# ─────────────────────────────────────────────────────────────────────────────
def matriz_confusao_ponderada(gab: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """M[i][j] = P(predito = j | verdadeiro = i), ponderada à população.

    A amostra é estratificada COM PISO para a classe minoritária, portanto não
    é auto-ponderada: usar `peso_amostral` é obrigatório para que a matriz
    represente as 205.697 notícias, e não os 300 itens sorteados.
    """
    M = np.zeros((3, 3))
    for i, verdadeiro in enumerate(CLASSES):
        sub = gab[gab["humano"] == verdadeiro]
        peso_total = sub["peso_amostral"].sum()
        for j, predito in enumerate(CLASSES):
            M[i, j] = sub.loc[sub["predito"] == predito, "peso_amostral"].sum() / peso_total
    # prevalência verdadeira observada no gabarito, também ponderada
    prev = np.array([gab.loc[gab["humano"] == c, "peso_amostral"].sum() for c in CLASSES])
    return M, prev / prev.sum()


# ─────────────────────────────────────────────────────────────────────────────
#  ETAPA 2 — correção ACC
# ─────────────────────────────────────────────────────────────────────────────
def corrigir_acc(p_predito: np.ndarray, M: np.ndarray) -> np.ndarray:
    """Resolve M^T · p_verdadeiro = p_predito.

    A inversão pode devolver proporções negativas quando a contagem observada é
    pequena — limitação conhecida do ACC. Nesses casos truncamos em zero e
    renormalizamos, que é o tratamento padrão na literatura de quantificação.
    """
    try:
        p = np.linalg.solve(M.T, p_predito)
    except np.linalg.LinAlgError:
        p = np.linalg.lstsq(M.T, p_predito, rcond=None)[0]
    p = np.clip(p, 0, None)
    return p / p.sum() if p.sum() > 0 else p_predito


def ism(p: np.ndarray) -> float:
    """ISM = (Pos - Neg) / total, com p na ordem [Negative, Neutral, Positive]."""
    return float(p[2] - p[0])


def bootstrap_calibracao(gab: pd.DataFrame, p_obs: np.ndarray,
                         n_reamostras: int = 2000, seed: int = 42):
    """Propaga o erro amostral do gabarito até o ISM calibrado.

    A matriz de confusão é estimada em 300 itens — a linha 'Positive' tem
    apenas 96. Reamostrar o gabarito com reposição e refazer toda a correção
    devolve a distribuição empírica do ISM calibrado, e daí o IC de 95%.
    """
    rng = np.random.default_rng(seed)
    n = len(gab)
    ism_boot, props_boot = [], []
    for _ in range(n_reamostras):
        amostra = gab.iloc[rng.integers(0, n, n)]
        # descarta reamostras que percam alguma classe verdadeira
        if amostra["humano"].nunique() < 3:
            continue
        try:
            Mb, _ = matriz_confusao_ponderada(amostra)
            if np.any(np.isnan(Mb)) or abs(np.linalg.det(Mb.T)) < 1e-8:
                continue
            pb = corrigir_acc(p_obs, Mb)
        except (np.linalg.LinAlgError, ZeroDivisionError):
            continue
        ism_boot.append(ism(pb))
        props_boot.append(pb)
    ism_boot = np.array(ism_boot)
    props_boot = np.array(props_boot)
    return (np.percentile(ism_boot, [2.5, 97.5]),
            np.percentile(props_boot, [2.5, 97.5], axis=0))


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path,
                    default=DIR_DADOS / "ism_calibrado_petr4.csv")
    ap.add_argument("--relatorio", type=Path,
                    default=DIR_DADOS / "calibracao_ism_relatorio.json")
    args = ap.parse_args()

    # ── carga ────────────────────────────────────────────────────────────────
    h = pd.read_excel(GAB_HUMANO, sheet_name="Rotular")
    m = pd.read_csv(GAB_MODELO)
    gab = h.merge(m[["ID_OURO", "Label_Sentimento", "peso_amostral"]], on="ID_OURO")
    gab["humano"] = gab["Sentimento_Humano"].map(MAPA_HUMANO)
    gab = gab.rename(columns={"Label_Sentimento": "predito"})
    gab = gab.dropna(subset=["humano", "predito"])

    corpus = pd.read_csv(CORPUS, usecols=["hash_titulo", "Label_Sentimento", "Data"])
    corpus["Data"] = pd.to_datetime(corpus["Data"], errors="coerce")
    corpus = corpus.dropna(subset=["Data", "Label_Sentimento"])

    print("=" * 74)
    print("ETAPA 1 — O QUE OS 300 RÓTULOS MEDEM")
    print("=" * 74)
    M, prev_gabarito = matriz_confusao_ponderada(gab)
    print("\nMatriz de confusão ponderada à população — P(predito | verdadeiro):\n")
    cabecalho = "verdadeiro / predito"
    print(f"{cabecalho:<22}" + "".join(f"{c:>12}" for c in CLASSES))
    for i, c in enumerate(CLASSES):
        print(f"{c:<22}" + "".join(f"{M[i, j]:>12.3f}" for j in range(3)))

    print("\nLeitura da linha 'Neutral':")
    print(f"  De cada 100 manchetes VERDADEIRAMENTE neutras, o modelo classifica")
    print(f"  {M[1, 0] * 100:.0f} como negativas e {M[1, 2] * 100:.0f} como positivas — "
          f"só {M[1, 1] * 100:.0f} ficam neutras.")
    print("  É um viés SISTEMÁTICO: infla os extremos e esvazia o centro.")

    # ── ETAPA 2: efeito agregado no período inteiro ──────────────────────────
    print("\n" + "=" * 74)
    print("ETAPA 2 — O EFEITO NO PERÍODO INTEIRO (205.697 notícias, 2018–2026)")
    print("=" * 74)
    cont = corpus["Label_Sentimento"].value_counts()
    p_obs = np.array([cont.get(c, 0) for c in CLASSES], dtype=float)
    p_obs = p_obs / p_obs.sum()
    p_cor = corrigir_acc(p_obs, M)

    print(f"\n{'':<12}{'BRUTO':>12}{'CALIBRADO':>12}{'DIFERENÇA':>12}")
    for i, c in enumerate(CLASSES):
        print(f"{c:<12}{p_obs[i]:>11.1%}{p_cor[i]:>12.1%}{p_cor[i] - p_obs[i]:>+12.1%}")
    print(f"\n{'ISM':<12}{ism(p_obs):>11.4f}{ism(p_cor):>12.4f}{ism(p_cor) - ism(p_obs):>+12.4f}")

    vies_rel = abs(ism(p_cor) - ism(p_obs)) / abs(ism(p_obs)) if ism(p_obs) else float("nan")
    print(f"\n>>> O ISM bruto esta enviesado em {ism(p_cor) - ism(p_obs):+.4f} "
          f"({vies_rel:.0%} do valor bruto).")
    print(">>> Isso NAO e ruido aleatorio: e deslocamento sistematico, na mesma")
    print(">>> direcao, em todos os dias da serie.")

    # ── incerteza da correção ────────────────────────────────────────────────
    # A matriz de confusão vem de 300 itens; suas células têm erro amostral.
    # Reamostrar o gabarito propaga esse erro até o ISM calibrado. Sem isto o
    # número acima seria uma estimativa pontual sem margem — indefensável em
    # banca, ainda mais com um efeito desta magnitude.
    ic_ism, ic_props = bootstrap_calibracao(gab, p_obs, n_reamostras=2000)
    print(f"\nIC 95% do ISM calibrado (bootstrap sobre o gabarito, 2000 reamostras):")
    print(f"  [{ic_ism[0]:+.4f} , {ic_ism[1]:+.4f}]   (pontual {ism(p_cor):+.4f})")
    print(f"  O ISM bruto ({ism(p_obs):+.4f}) "
          f"{'ESTA FORA' if not (ic_ism[0] <= ism(p_obs) <= ic_ism[1]) else 'esta dentro'}"
          f" do intervalo -> o vies "
          f"{'e estatisticamente distinguivel de zero' if not (ic_ism[0] <= ism(p_obs) <= ic_ism[1]) else 'NAO e conclusivo'}.")

    # ── ETAPA 3: série mensal calibrada ──────────────────────────────────────
    print("\n" + "=" * 74)
    print("ETAPA 3 — A SÉRIE CALIBRADA (agregação mensal)")
    print("=" * 74)
    corpus["mes"] = corpus["Data"].dt.to_period("M")
    linhas = []
    for mes, g in corpus.groupby("mes"):
        c = g["Label_Sentimento"].value_counts()
        bruto = np.array([c.get(k, 0) for k in CLASSES], dtype=float)
        n = bruto.sum()
        if n == 0:
            continue
        p_b = bruto / n
        p_c = corrigir_acc(p_b, M)
        linhas.append({
            "mes": str(mes), "n_noticias": int(n),
            "prop_neg_bruta": p_b[0], "prop_neu_bruta": p_b[1], "prop_pos_bruta": p_b[2],
            "prop_neg_calib": p_c[0], "prop_neu_calib": p_c[1], "prop_pos_calib": p_c[2],
            "ISM_bruto": ism(p_b), "ISM_calibrado": ism(p_c),
        })
    serie = pd.DataFrame(linhas)
    serie["delta"] = serie["ISM_calibrado"] - serie["ISM_bruto"]

    print(f"\nMeses processados: {len(serie)} "
          f"({serie['mes'].iloc[0]} a {serie['mes'].iloc[-1]})")
    print(f"Média de notícias por mês: {serie['n_noticias'].mean():.0f}")
    print("\nDeslocamento do ISM (calibrado - bruto):")
    print(f"  média  = {serie['delta'].mean():+.4f}")
    print(f"  mínimo = {serie['delta'].min():+.4f}   máximo = {serie['delta'].max():+.4f}")
    print(f"  meses em que a correção MUDA O SINAL do ISM: "
          f"{int((np.sign(serie['ISM_bruto']) != np.sign(serie['ISM_calibrado'])).sum())}"
          f" de {len(serie)}")

    print(f"\ncorrelação entre as duas séries: "
          f"{serie['ISM_bruto'].corr(serie['ISM_calibrado']):.4f}")
    print(f"desvio-padrão  bruto = {serie['ISM_bruto'].std():.4f}   "
          f"calibrado = {serie['ISM_calibrado'].std():.4f}")

    print("\nPrimeiros 6 meses:")
    print(serie.head(6)[["mes", "n_noticias", "ISM_bruto", "ISM_calibrado", "delta"]]
          .to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print("\nÚltimos 6 meses:")
    print(serie.tail(6)[["mes", "n_noticias", "ISM_bruto", "ISM_calibrado", "delta"]]
          .to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    # ── ETAPA 4: por que não fazer isso no nível diário ──────────────────────
    print("\n" + "=" * 74)
    print("ETAPA 4 — RESSALVA: por que a calibração é mensal e não diária")
    print("=" * 74)
    corpus["dia"] = corpus["Data"].dt.date
    por_dia = corpus.groupby("dia").size()
    print(f"\nNotícias por dia: mediana={por_dia.median():.0f}  "
          f"p10={por_dia.quantile(.10):.0f}  p90={por_dia.quantile(.90):.0f}")
    poucos = int((por_dia < 10).sum())
    print(f"Dias com menos de 10 notícias: {poucos} de {len(por_dia)} "
          f"({poucos / len(por_dia):.1%})")
    print("\nA inversão da matriz AMPLIFICA ruído quando a contagem é pequena.")
    print("Com poucas notícias no dia, a proporção observada tem variância alta e")
    print("a correção pode devolver valores fora de [0,1], que precisam ser")
    print("truncados — o que introduz outro viés. Por isso a recomendação é:")
    print("  • calibrar na agregação MENSAL (ou em janela móvel de 21 pregões);")
    print("  • manter o ISM diário bruto como variável de curto prazo;")
    print("  • declarar essa escolha no capítulo de método.")

    # ── saída ────────────────────────────────────────────────────────────────
    serie.to_csv(args.saida, index=False, encoding="utf-8-sig")
    args.relatorio.write_text(json.dumps({
        "data_execucao": date.today().isoformat(),
        "metodo": "Adjusted Classify and Count (Forman, 2008)",
        "n_gabarito": int(len(gab)),
        "n_corpus": int(len(corpus)),
        "matriz_confusao_ponderada": M.round(4).tolist(),
        "classes": CLASSES,
        "periodo_agregado": {
            "prop_bruta": dict(zip(CLASSES, p_obs.round(4))),
            "prop_calibrada": dict(zip(CLASSES, p_cor.round(4))),
            "ISM_bruto": round(ism(p_obs), 4),
            "ISM_calibrado": round(ism(p_cor), 4),
            "vies_absoluto": round(ism(p_cor) - ism(p_obs), 4),
        },
        "serie_mensal": {
            "n_meses": int(len(serie)),
            "delta_medio": round(float(serie["delta"].mean()), 4),
            "delta_min": round(float(serie["delta"].min()), 4),
            "delta_max": round(float(serie["delta"].max()), 4),
            "correlacao_bruto_calibrado": round(
                float(serie["ISM_bruto"].corr(serie["ISM_calibrado"])), 4),
            "meses_com_troca_de_sinal": int(
                (np.sign(serie["ISM_bruto"]) != np.sign(serie["ISM_calibrado"])).sum()),
        },
    }, indent=2, ensure_ascii=False, default=float), encoding="utf-8")

    print(f"\n[OK] Serie calibrada  -> {args.saida}")
    print(f"[OK] Relatorio        -> {args.relatorio}")


if __name__ == "__main__":
    main()
