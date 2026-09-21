# -*- coding: utf-8 -*-
# ==============================================================================
#   CONFRONTO DE FONTES — notícia de portal, comunicado da CVM, e os dois juntos
#
#   A pergunta: qual fonte de texto prevê melhor o pregão seguinte?
#
#   REGRAS DO CONFRONTO, para que ele seja honesto:
#
#   1. MESMA JANELA. Conta o que foi publicado entre o fechamento de um pregão
#      e a abertura do seguinte — a "noite". Os dois braços enxergam
#      exatamente o mesmo intervalo.
#
#   2. MESMOS DIAS. Notícia de portal existe quase toda noite; comunicado da
#      CVM, não. Comparar a acurácia de um em 2.000 dias com a do outro em 900
#      não diz nada. O confronto principal roda na INTERSEÇÃO.
#
#   3. MESMA REGRA. Saldo de sentimento positivo prevê ALTA, negativo prevê
#      BAIXA, empate não prevê nada. Vale para as três fontes.
#
#   4. MESMO ADVERSÁRIO. Tudo é comparado contra a classe majoritária — quem
#      não lê nada e sempre chuta o lado mais frequente.
#
#   Dois alvos, e o segundo nunca foi testado nesta pesquisa:
#      DIREÇÃO  — o preço sobe ou desce?
#      VOLUME   — o giro fica acima ou abaixo do normal recente?
#
#   Saída: CVM/dados/confronto_fontes.json
# ==============================================================================
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
RAIZ = AQUI.parent

TICKER = "PETR4"
FECHA, ABRE = 17, 10          # pregão da B3
JANELA_VOL = 5                # dias para a média de volume de referência


def sinal(pos: int, neg: int) -> str | None:
    """Saldo de sentimento -> previsão de direção."""
    if pos > neg:
        return "ALTA"
    if neg > pos:
        return "BAIXA"
    return None


def avalia(df: pd.DataFrame, col_prev: str, col_real: str, rot: str) -> dict | None:
    s = df[df[col_prev].notna()]
    if len(s) < 40:
        return None
    acerto = (s[col_prev] == s[col_real])
    acc = acerto.mean()
    maj = s[col_real].value_counts(normalize=True).iloc[0]
    p = stats.binomtest(int(acerto.sum()), len(s), 0.5).pvalue
    from sklearn.metrics import cohen_kappa_score, matthews_corrcoef
    return {"rotulo": rot, "n": int(len(s)), "acuracia": round(float(acc), 4),
            "majoritaria": round(float(maj), 4),
            "ganho_pp": round(float((acc - maj) * 100), 2),
            "p_vs_acaso": float(p),
            "kappa": round(float(cohen_kappa_score(s[col_real], s[col_prev])), 4),
            "mcc": round(float(matthews_corrcoef(s[col_real], s[col_prev])), 4)}


def imprime(m):
    if m is None:
        return
    ok = "  *" if m["p_vs_acaso"] < 0.05 else ""
    print(f"  {m['rotulo']:<34} {m['n']:>5,} {m['acuracia']:>8.1%} "
          f"{m['majoritaria']:>8.1%} {m['ganho_pp']:>+7.2f} {m['p_vs_acaso']:>9.4f}{ok}")


def main() -> None:
    print("=" * 84)
    print(f"  CONFRONTO DE FONTES — {TICKER}")
    print("=" * 84)

    # ── preços ───────────────────────────────────────────────────────────────
    px = pd.read_csv(DADOS / "ohlcv_b3.csv", parse_dates=["Data"])
    px = px[px["Ticker"] == TICKER].sort_values("Data").reset_index(drop=True)
    px["vol_ref"] = px["Volume"].shift(1).rolling(JANELA_VOL).mean()
    px["dir_real"] = np.where(px["Retorno"] > 0, "ALTA", "BAIXA")
    px["vol_real"] = np.where(px["Volume"] > px["vol_ref"], "ACIMA", "ABAIXO")
    pregoes = px["Data"].tolist()

    def noite_de(i):
        """A janela que antecede o pregão i: do fechamento anterior à abertura."""
        if i == 0:
            return None, None
        ini = pregoes[i - 1].replace(hour=FECHA, minute=0)
        fim = pregoes[i].replace(hour=ABRE, minute=0)
        return ini, fim

    # ── notícias de portal ───────────────────────────────────────────────────
    nw = pd.read_csv(RAIZ / "Mestrado_PETR4" / "noticias_com_sentimento.csv",
                     low_memory=False)
    nw["dt"] = pd.to_datetime(nw["data_gmt"], errors="coerce")
    nw = nw[nw["dt"].notna()][["dt", "Label_Sentimento"]]
    print(f"\n  notícias de portal ....... {len(nw):,}")

    # ── comunicados da CVM ───────────────────────────────────────────────────
    base = pd.read_csv(DADOS / "cvm_para_classificar.csv", dtype=str)
    base["numSequencia"] = base["Link_Download"].str.extract(r"numSequencia=(\d+)")
    hora = pd.read_csv(DADOS / "cvm_hora_entrega.csv", dtype=str).drop_duplicates("numSequencia")
    cls = pd.read_csv(DADOS / "cvm_classificado.csv", dtype=str).drop_duplicates("Protocolo_Entrega")
    cv = (base.merge(hora, on="numSequencia")
              .merge(cls[["Protocolo_Entrega", "Rotulo"]], on="Protocolo_Entrega"))
    cv = cv[cv["Ticker"] == TICKER].copy()
    cv["dt"] = pd.to_datetime(cv["Data_Entrega_oficial"] + " " + cv["Hora_Entrega_oficial"],
                              format="%d/%m/%Y %H:%M:%S", errors="coerce")
    cv["Rotulo"] = cv["Rotulo"].str.capitalize()
    cv = cv[cv["dt"].notna()][["dt", "Rotulo", "Categoria"]]
    print(f"  comunicados da CVM ....... {len(cv):,}")

    # ── conta o que caiu em cada noite ───────────────────────────────────────
    linhas = []
    for i in range(JANELA_VOL + 2, len(px)):
        ini, fim = noite_de(i)
        if ini is None or pd.isna(px["vol_ref"].iloc[i]):
            continue
        jn = nw[(nw["dt"] > ini) & (nw["dt"] <= fim)]
        jc = cv[(cv["dt"] > ini) & (cv["dt"] <= fim)]
        linhas.append({
            "data": px["Data"].iloc[i],
            "dir_real": px["dir_real"].iloc[i],
            "vol_real": px["vol_real"].iloc[i],
            "n_pos": int((jn["Label_Sentimento"] == "Positive").sum()),
            "n_neg": int((jn["Label_Sentimento"] == "Negative").sum()),
            "n_tot": int(len(jn)),
            "c_pos": int((jc["Rotulo"] == "Positive").sum()),
            "c_neg": int((jc["Rotulo"] == "Negative").sum()),
            "c_tot": int(len(jc)),
            "c_fr": int((jc["Categoria"] == "Fato Relevante").sum()),
        })
    d = pd.DataFrame(linhas)

    # previsões de direção, pela mesma regra nas três fontes
    d["prev_news"] = [sinal(p, n) for p, n in zip(d["n_pos"], d["n_neg"])]
    d["prev_cvm"] = [sinal(p, n) for p, n in zip(d["c_pos"], d["c_neg"])]
    d["prev_ambos"] = [sinal(a + c, b + e) for a, b, c, e in
                       zip(d["n_pos"], d["n_neg"], d["c_pos"], d["c_neg"])]

    print(f"\n  pregões analisados ....... {len(d):,}")
    print(f"  com notícia na noite ..... {(d['n_tot'] > 0).sum():,}"
          f"  ({(d['n_tot'] > 0).mean():.1%})")
    print(f"  com comunicado da CVM .... {(d['c_tot'] > 0).sum():,}"
          f"  ({(d['c_tot'] > 0).mean():.1%})")
    print(f"  com os DOIS .............. {((d['n_tot'] > 0) & (d['c_tot'] > 0)).sum():,}")

    res = {"ticker": TICKER, "n_pregoes": int(len(d)),
           "cobertura": {"noticia": int((d["n_tot"] > 0).sum()),
                         "cvm": int((d["c_tot"] > 0).sum()),
                         "ambos": int(((d["n_tot"] > 0) & (d["c_tot"] > 0)).sum())},
           "direcao": {}, "volume": {}}

    cab = (f"\n  {'fonte':<34} {'dias':>5} {'acertou':>8} {'palpite':>8} "
           f"{'ganho':>7} {'p vs acaso':>9}")

    # ── ALVO 1: DIREÇÃO ──────────────────────────────────────────────────────
    print("\n" + "=" * 84)
    print("  ALVO 1 — o preço SOBE ou DESCE no pregão seguinte?")
    print("=" * 84)

    print("\n  (a) cada fonte no terreno em que ela consegue opinar")
    print(cab)
    print("  " + "-" * 80)
    for rot, col in (("notícia de portal", "prev_news"),
                     ("comunicado da CVM", "prev_cvm"),
                     ("os dois somados", "prev_ambos")):
        m = avalia(d, col, "dir_real", rot)
        imprime(m)
        if m:
            res["direcao"][f"todos_{col}"] = m

    # o confronto que vale: só os dias em que AMBOS existem
    inter = d[(d["n_tot"] > 0) & (d["c_tot"] > 0)]
    print(f"\n  (b) O CONFRONTO JUSTO — só os {len(inter):,} dias em que existem as duas fontes")
    print(cab)
    print("  " + "-" * 80)
    for rot, col in (("notícia de portal", "prev_news"),
                     ("comunicado da CVM", "prev_cvm"),
                     ("os dois somados", "prev_ambos")):
        m = avalia(inter, col, "dir_real", rot)
        imprime(m)
        if m:
            res["direcao"][f"inter_{col}"] = m

    # e só quando houve FATO RELEVANTE, que é o evento forte
    forte = d[(d["n_tot"] > 0) & (d["c_fr"] > 0)]
    if len(forte) >= 40:
        print(f"\n  (c) só as noites com FATO RELEVANTE ({len(forte):,} dias)")
        print(cab)
        print("  " + "-" * 80)
        for rot, col in (("notícia de portal", "prev_news"),
                         ("comunicado da CVM", "prev_cvm"),
                         ("os dois somados", "prev_ambos")):
            m = avalia(forte, col, "dir_real", rot)
            imprime(m)
            if m:
                res["direcao"][f"fatorel_{col}"] = m

    # ── ALVO 2: VOLUME ───────────────────────────────────────────────────────
    print("\n" + "=" * 84)
    print("  ALVO 2 — o VOLUME fica acima ou abaixo da média recente?")
    print("  Aqui a previsão não vem do sentimento, e sim da QUANTIDADE de texto:")
    print("  noite movimentada de publicações -> giro acima do normal.")
    print("=" * 84)

    # limiar: a mediana histórica de cada contagem
    lim_n = d.loc[d["n_tot"] > 0, "n_tot"].median()
    lim_c = 0                      # houve ou não houve comunicado
    d["volprev_news"] = np.where(d["n_tot"] > lim_n, "ACIMA", "ABAIXO")
    d["volprev_cvm"] = np.where(d["c_tot"] > lim_c, "ACIMA", "ABAIXO")
    d["volprev_ambos"] = np.where((d["n_tot"] > lim_n) | (d["c_tot"] > lim_c),
                                  "ACIMA", "ABAIXO")
    print(f"\n  regra: mais de {lim_n:.0f} notícias na noite, ou qualquer comunicado da CVM")
    print(cab)
    print("  " + "-" * 80)
    for rot, col in (("volume de notícias", "volprev_news"),
                     ("houve comunicado da CVM", "volprev_cvm"),
                     ("os dois somados", "volprev_ambos")):
        m = avalia(d, col, "vol_real", rot)
        imprime(m)
        if m:
            res["volume"][col] = m

    # ── o ganho de juntar as fontes é real? teste pareado ────────────────────
    print("\n" + "=" * 84)
    print("  JUNTAR AS FONTES ACRESCENTA? (teste de McNemar, mesmos dias)")
    print("=" * 84)
    for alvo, real, a, b, rot in (
            ("direção", "dir_real", "prev_news", "prev_ambos", "notícia sozinha x as duas"),
            ("volume", "vol_real", "volprev_news", "volprev_ambos", "notícia sozinha x as duas")):
        s = d[d[a].notna() & d[b].notna()]
        aa = (s[a] == s[real])
        bb = (s[b] == s[real])
        n01 = int((~aa & bb).sum())     # só o combinado acertou
        n10 = int((aa & ~bb).sum())     # só a notícia acertou
        if n01 + n10 == 0:
            continue
        p = stats.binomtest(n01, n01 + n10, 0.5).pvalue
        print(f"\n  {alvo.upper()} — {rot}  (n = {len(s):,})")
        print(f"    só o combinado acertou ... {n01}")
        print(f"    só a notícia acertou ..... {n10}")
        print(f"    valor-p .................. {p:.4f}"
              f"{'  *' if p < 0.05 else '   (empate técnico)'}")
        res.setdefault("mcnemar", {})[alvo] = {
            "so_combinado": n01, "so_noticia": n10, "p": float(p), "n": int(len(s))}

    d.to_csv(DADOS / "confronto_fontes_dias.csv", index=False, encoding="utf-8-sig")
    (DADOS / "confronto_fontes.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  gravados: confronto_fontes_dias.csv e confronto_fontes.json")


if __name__ == "__main__":
    main()
