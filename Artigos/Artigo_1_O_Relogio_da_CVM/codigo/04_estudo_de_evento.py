# -*- coding: utf-8 -*-
# ==============================================================================
#   RODADA A — a publicação divulgada APÓS O FECHAMENTO move o pregão seguinte?
#   Usando APENAS a classificação que já vem da CVM (Fato Relevante / Comunicado).
#
#   O DESENHO, pedido pelos orientadores:
#     documento entregue depois que o mercado fechou  ->  observa-se o PRÓXIMO
#     pregão. Ninguém pôde negociar sobre aquela informação antes da abertura.
#
#   A MEDIDA DE VOLATILIDADE, sugerida pelo Prof. Emerson:
#     comparar a volatilidade do pregão seguinte com a MÉDIA DOS DIAS
#     ANTERIORES (uma semana, por exemplo), e não com uma média distante.
#
#     Por que isso é mais exigente: volatilidade é grudenta. Depois de uma
#     semana agitada vem outra agitada. Se a notícia bate a média da PRÓPRIA
#     semana anterior, ela acrescentou algo ao regime que já estava em curso.
#
#     Cuidado que tomamos: a linha de base PULA os dois pregões imediatamente
#     anteriores ([-6,-2] e não [-5,-1]). Se houver vazamento de informação na
#     véspera, incluí-la inflaria a base e esconderia o efeito.
#
#   Saída: CVM/dados/rodada_A.json e rodada_A_casos.csv
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

HORA_CORTE = 17          # entregue às 17h ou depois = após o fechamento
BASES = {"1 semana (-6 a -2)": (-6, -2),
         "2 semanas (-11 a -2)": (-11, -2),
         "1 mês (-23 a -2)": (-23, -2),
         "distante (-120 a -21)": (-120, -21)}
MIN_BASE = 4             # mínimo de pregões válidos na linha de base


def pregao_que_reage(data_ev, pregoes) -> int | None:
    """Índice do pregão que reage a um documento entregue após o fechamento.

    Se a entrega caiu num pregão, o mercado responde no SEGUINTE.
    Se caiu em dia sem negociação (fim de semana, feriado), responde no
    primeiro pregão que vier.
    """
    i = pregoes.searchsorted(data_ev, side="left")
    if i >= len(pregoes):
        return None
    if pregoes[i] == data_ev:      # a entrega caiu num pregão -> reage no próximo
        i += 1
    return i if i < len(pregoes) else None


def main() -> None:
    print("=" * 78)
    print("RODADA A — SÓ COM A CLASSIFICAÇÃO DA CVM")
    print("=" * 78)

    px = pd.read_csv(DADOS / "ohlcv_b3.csv", parse_dates=["Data"])
    px = px.sort_values(["Ticker", "Data"])

    base = pd.read_csv(DADOS / "cvm_para_classificar.csv", dtype=str)
    base["numSequencia"] = base["Link_Download"].str.extract(r"numSequencia=(\d+)")
    hora = pd.read_csv(DADOS / "cvm_hora_entrega.csv", dtype=str)
    hora = hora.drop_duplicates("numSequencia")

    ev = base.merge(hora, on="numSequencia", how="inner")
    ev["dh"] = pd.to_datetime(ev["Data_Entrega_oficial"] + " " + ev["Hora_Entrega_oficial"],
                              format="%d/%m/%Y %H:%M:%S", errors="coerce")
    ev = ev[ev["dh"].notna()]
    print(f"\n  documentos com hora oficial ......... {len(ev):,}")

    ev = ev[ev["dh"].dt.hour >= HORA_CORTE]
    print(f"  APÓS O FECHAMENTO (>= {HORA_CORTE}h) ......... {len(ev):,}")

    ev = ev[ev["Ticker"].isin(px["Ticker"].unique())]
    print(f"  com preço disponível ................ {len(ev):,}")
    print(f"  categorias: " + ", ".join(
        f"{k} {v:,}" for k, v in ev["Categoria"].value_counts().items()))

    # ── mede cada evento ─────────────────────────────────────────────────────
    linhas = []
    for tk, g in ev.groupby("Ticker"):
        p = px[px["Ticker"] == tk].reset_index(drop=True)
        datas = p["Data"].values
        park = p["Parkinson"].values
        vol = p["Volume"].values.astype(float)
        gap = p["Gap"].values
        intra = p["Intradia"].values
        ret = p["Retorno"].values

        for _, r in g.iterrows():
            i = pregao_que_reage(np.datetime64(r["dh"].normalize()), datas)
            if i is None or i < 130 or i >= len(p) - 1:
                continue
            reg = {"Protocolo_Entrega": r["Protocolo_Entrega"],
                   "Ticker": tk, "Empresa": r["Nome_Companhia"],
                   "Categoria": r["Categoria"], "Assunto": r["Assunto"],
                   "Entrega": r["dh"], "Pregao_reacao": p["Data"].iloc[i],
                   "Parkinson_d1": park[i], "Volume_d1": vol[i],
                   "Gap_d1": gap[i], "Intradia_d1": intra[i], "Retorno_d1": ret[i]}
            for nome, (a, b) in BASES.items():
                jan_p = park[i + a:i + b + 1]
                jan_v = vol[i + a:i + b + 1]
                jan_p = jan_p[np.isfinite(jan_p) & (jan_p > 0)]
                jan_v = jan_v[np.isfinite(jan_v) & (jan_v > 0)]
                reg[f"razaoVol_{nome}"] = (park[i] / jan_p.mean()
                                           if len(jan_p) >= MIN_BASE else np.nan)
                reg[f"razaoVolume_{nome}"] = (vol[i] / jan_v.mean()
                                              if len(jan_v) >= MIN_BASE else np.nan)
            linhas.append(reg)

    d = pd.DataFrame(linhas)
    print(f"  eventos medidos ..................... {len(d):,}")

    fr = d[d["Categoria"] == "Fato Relevante"]
    cm = d[d["Categoria"] == "Comunicado ao Mercado"]

    res = {"n": int(len(d)), "n_fr": int(len(fr)), "n_cm": int(len(cm)),
           "hora_corte": HORA_CORTE, "volatilidade": {}, "volume": {}}

    # ── A.1 volatilidade contra a média dos dias anteriores ──────────────────
    print("\n" + "=" * 78)
    print("  A.1  VOLATILIDADE DO PREGÃO SEGUINTE contra a MÉDIA DOS DIAS ANTERIORES")
    print("  1,00 = igual à média recente. Acima de 1 = a notícia acrescentou.")
    print("=" * 78)
    print(f"  {'linha de base':<24} {'grupo':<22} {'n':>6} {'razão':>7} {'valor-p':>10}")
    print("  " + "-" * 74)
    for nome in BASES:
        for rot, sub in (("Fato Relevante", fr), ("Comunicado ao Mercado", cm)):
            v = sub[f"razaoVol_{nome}"].dropna()
            if len(v) < 30:
                continue
            t, p = stats.ttest_1samp(v, 1.0)
            print(f"  {nome:<24} {rot:<22} {len(v):>6,} {v.mean():>7.3f} {p:>10.2e}"
                  f"{'  *' if p < 0.05 else ''}")
            res["volatilidade"].setdefault(nome, {})[rot] = {
                "n": int(len(v)), "razao": round(float(v.mean()), 4),
                "mediana": round(float(v.median()), 4), "p": float(p)}
        print()

    # ── A.2 volume ───────────────────────────────────────────────────────────
    print("=" * 78)
    print("  A.2  VOLUME NEGOCIADO no pregão seguinte, mesma comparação")
    print("=" * 78)
    print(f"  {'linha de base':<24} {'grupo':<22} {'n':>6} {'razão':>7} {'valor-p':>10}")
    print("  " + "-" * 74)
    for nome in BASES:
        for rot, sub in (("Fato Relevante", fr), ("Comunicado ao Mercado", cm)):
            v = sub[f"razaoVolume_{nome}"].dropna()
            if len(v) < 30:
                continue
            t, p = stats.ttest_1samp(v, 1.0)
            print(f"  {nome:<24} {rot:<22} {len(v):>6,} {v.mean():>7.3f} {p:>10.2e}"
                  f"{'  *' if p < 0.05 else ''}")
            res["volume"].setdefault(nome, {})[rot] = {
                "n": int(len(v)), "razao": round(float(v.mean()), 4),
                "mediana": round(float(v.median()), 4), "p": float(p)}
        print()

    # ── A.3 direção: tem de dar zero ─────────────────────────────────────────
    print("=" * 78)
    print("  A.3  DIREÇÃO — registrada a previsão: deve dar ZERO, por construção")
    print("=" * 78)
    for rot, col in (("gap de abertura", "Gap_d1"),
                     ("intradiário", "Intradia_d1"),
                     ("pregão inteiro", "Retorno_d1")):
        v = fr[col].dropna()
        t, p = stats.ttest_1samp(v, 0.0)
        acima = (v > 0).mean()
        print(f"  {rot:<18} média {v.mean()*100:+7.4f}%   p={p:>6.3f}   "
              f"subiu em {acima:.1%} dos casos")
        res.setdefault("direcao", {})[rot] = {
            "media_pct": round(float(v.mean() * 100), 4), "p": float(p),
            "prop_alta": round(float(acima), 4)}

    print("\n  COMO LER: o rótulo da CVM não distingue notícia boa de ruim.")
    print("  Altas e baixas se cancelam. Um resultado nulo aqui é o esperado,")
    print("  e é a demonstração de que a Rodada B (com sinal) é necessária.")

    # ── A.4 CONTROLE — o pregão SEM notícia nenhuma ──────────────────────────
    # Sem isto os números anteriores enganam: a razão entre um dia e a média da
    # semana anterior tem média MAIOR que 1 mesmo sem evento algum, porque a
    # distribuição é assimétrica à direita. O piso não é 1,00 — é o que um
    # pregão qualquer entrega. É contra ele que o excesso deve ser medido.
    print("")
    print("=" * 78)
    print("  A.4  CONTROLE — comparação com pregões SEM comunicado")
    print("=" * 78)

    chave = set(zip(d["Ticker"], pd.to_datetime(d["Pregao_reacao"])))
    ini, fim = pd.to_datetime(d["Pregao_reacao"]).min(), pd.to_datetime(d["Pregao_reacao"]).max()
    ctl = []
    for tk, g in px[px["Ticker"].isin(d["Ticker"].unique())].groupby("Ticker"):
        g = g.reset_index(drop=True)
        pk, vl = g["Parkinson"].values, g["Volume"].values.astype(float)
        gp, itr, rt = g["Gap"].values, g["Intradia"].values, g["Retorno"].values
        for i in range(130, len(g) - 1):
            dia = g["Data"].iloc[i]
            if dia < ini or dia > fim:
                continue
            jp, jv = pk[i - 6:i - 1], vl[i - 6:i - 1]
            jp = jp[np.isfinite(jp) & (jp > 0)]
            jv = jv[np.isfinite(jv) & (jv > 0)]
            if len(jp) < MIN_BASE or len(jv) < MIN_BASE or not np.isfinite(pk[i]) or pk[i] <= 0:
                continue
            ctl.append({"ev": (tk, dia) in chave, "rv": pk[i] / jp.mean(),
                        "rq": vl[i] / jv.mean(), "gap": gp[i], "intra": itr[i],
                        "ret": rt[i]})
    c = pd.DataFrame(ctl)
    sem, com = c[~c["ev"]], c[c["ev"]]
    print(f"  pregões sem comunicado: {len(sem):,}   com comunicado: {len(com):,}\n")
    print(f"  {'medida':<26} {'SEM':>9} {'COM':>9} {'excesso':>9} {'valor-p':>11}")
    print("  " + "-" * 70)
    for rot, col in (("volatilidade (Parkinson)", "rv"), ("volume negociado", "rq"),
                     ("gap de abertura (%)", "gap"), ("intradiário (%)", "intra"),
                     ("pregão inteiro (%)", "ret")):
        x, y = sem[col].dropna(), com[col].dropna()
        t_, p_ = stats.ttest_ind(y, x, equal_var=False)
        if col in ("rv", "rq"):
            exc = f"{y.mean()/x.mean():.1%}"
            print(f"  {rot:<26} {x.mean():>9.3f} {y.mean():>9.3f} {exc:>9} {p_:>11.2e}"
                  f"{'  *' if p_ < 0.05 else ''}")
        else:
            print(f"  {rot:<26} {x.mean()*100:>9.4f} {y.mean()*100:>9.4f} "
                  f"{(y.mean()-x.mean())*100:>+9.4f} {p_:>11.3f}"
                  f"{'  *' if p_ < 0.05 else ''}")
        res.setdefault("controle", {})[rot] = {
            "sem": round(float(x.mean()), 5), "com": round(float(y.mean()), 5),
            "p": float(p_)}

    print("")
    print('  ATENÇÃO: o piso NÃO é 1,00. Um pregão qualquer já rende razão acima')
    print("  de 1 por assimetria da distribuição. O excesso real é medido contra a")
    print("  coluna SEM — e é menor que o que a seção A.1 sugeria isoladamente.")

    d.to_csv(DADOS / "rodada_A_casos.csv", index=False, encoding="utf-8-sig")
    (DADOS / "rodada_A.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  gravados: rodada_A_casos.csv ({len(d):,} linhas) e rodada_A.json")


if __name__ == "__main__":
    main()
