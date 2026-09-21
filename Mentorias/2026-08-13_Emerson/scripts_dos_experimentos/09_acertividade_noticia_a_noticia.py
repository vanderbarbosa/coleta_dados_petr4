# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — O sentimento acertou o pregão seguinte? (auditoria direta)
# =============================================================================
#
#  ------------------------------------------------------------------
#  A LACUNA QUE ESTE SCRIPT PREENCHE
#  ------------------------------------------------------------------
#  A dissertação já mede o desempenho do sistema por vias INDIRETAS: um
#  classificador treinado sobre o índice diário agregado, testes de causalidade
#  de Granger, regressão quantílica. Todas legítimas, e todas mediadas por um
#  modelo estatístico interposto entre a notícia e o resultado.
#
#  Falta a verificação mais simples e mais auditável de todas, que qualquer
#  leitor pode conferir na planilha: NOTÍCIA POR NOTÍCIA, o sentimento apontou
#  para o lado certo do pregão seguinte?
#
#  É uma pergunta descritiva, não preditiva. Ela não substitui os modelos --- ela
#  os ancora. Sem essa tabela, o leitor precisa aceitar a palavra do XGBoost.
#
#  ------------------------------------------------------------------
#  O CUIDADO DECISIVO: QUAL PREGÃO A NOTÍCIA PODE AFETAR
#  ------------------------------------------------------------------
#  Uma notícia das 10h de terça pode mover o preço na própria terça. Uma notícia
#  das 18h de terça só pode mover na quarta. Confundir os dois casos produziria
#  um resultado inflado, porque parte do "acerto" seria apenas a notícia
#  DESCREVENDO um movimento que já ocorreu.
#
#  Definem-se, por isso, dois horizontes:
#
#    P0 — primeiro pregão cujo fechamento ocorre APÓS a publicação
#         Para notícia intradiária é o mesmo dia. Mistura reação e antecipação:
#         serve de diagnóstico, NÃO de evidência preditiva.
#
#    P1 — o pregão seguinte a P0
#         Estritamente posterior à notícia em todos os casos. É a evidência.
#
#  O corte das 17h já consta da coluna `Data_Ajustada`, mas ela desloca um dia
#  de CALENDÁRIO e não trata fins de semana e feriados. O mapeamento para o
#  pregão efetivo é refeito aqui.
#
#  ------------------------------------------------------------------
#  O CUIDADO ESTATÍSTICO: NOTÍCIAS NÃO SÃO INDEPENDENTES
#  ------------------------------------------------------------------
#  Num dia agitado saem 200 notícias, todas apontando para o mesmo pregão. Uma
#  taxa de acerto calculada por notícia contaria esse único evento 200 vezes.
#  Reporta-se, por isso, também a taxa por PREGÃO, com voto majoritário --- e é
#  essa que sustenta o teste de significância.
#
#  Uso:
#      python src/modelagem/09_acertividade_noticia_a_noticia.py
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
PROP_TREINO = 0.60          # fração usada só para calibrar limiares


# ─────────────────────────────────────────────────────────────────────────────
def carregar_pregoes(caminho: Path) -> pd.DataFrame:
    p = pd.read_csv(caminho, skiprows=[1])
    p["Date"] = pd.to_datetime(p["Date"], errors="coerce")
    for c in ("High", "Low", "Close"):
        p[c] = pd.to_numeric(p[c], errors="coerce")
    p = p.dropna(subset=["Date", "High", "Low", "Close"]) \
         .sort_values("Date").reset_index(drop=True)

    p["ret"] = np.log(p["Close"]).diff()
    p["vol"] = p["ret"].abs()
    # resultado do PREGÃO SEGUINTE ao pregão da linha
    p["ret_p1"] = p["ret"].shift(-1)
    p["vol_p1"] = p["vol"].shift(-1)
    p["idx"] = np.arange(len(p))
    return p


def mapear_para_pregao(noticias: pd.DataFrame, p: pd.DataFrame) -> pd.DataFrame:
    """Casa cada notícia com P0, o primeiro pregão que pode reagir a ela.

    `direction='forward'` garante que notícia de sexta à noite, de sábado ou de
    feriado caia no pregão SEGUINTE, e nunca no anterior --- o que seria
    vazamento de informação futura.
    """
    n = noticias.sort_values("data_efetiva")
    return pd.merge_asof(
        n, p[["Date", "idx", "ret", "vol", "ret_p1", "vol_p1"]].sort_values("Date"),
        left_on="data_efetiva", right_on="Date", direction="forward",
    ).dropna(subset=["idx"])


def taxa(acertos: int, n: int, base: float) -> dict:
    """Taxa de acerto com teste binomial contra uma referência declarada."""
    bt = stats.binomtest(acertos, n, base)
    lo, hi = bt.proportion_ci(0.95)
    return {"n": int(n), "acertos": int(acertos), "taxa": round(acertos / n, 4),
            "referencia": round(base, 4), "p_valor": round(float(bt.pvalue), 4),
            "ic95": [round(float(lo), 4), round(float(hi), 4)]}


def moda_ou_nada(s: pd.Series):
    """Voto majoritário do pregão; devolve None se houver empate."""
    v = s.value_counts()
    if len(v) == 1:
        return v.index[0]
    return v.index[0] if v.iloc[0] > v.iloc[1] else None


# ─────────────────────────────────────────────────────────────────────────────
def matriz_direcao(d: pd.DataFrame, col_ret: str, rotulo: str) -> list[dict]:
    """Para cada classe de sentimento: com que frequência o pregão subiu?"""
    print(f"\n  --- {rotulo} ---")
    print(f"  {'sentimento':12s}{'noticias':>10s}{'subiu':>9s}{'caiu':>9s}"
          f"{'ret medio':>12s}{'|ret| med':>12s}")
    linhas = []
    for cls in ("Positive", "Neutral", "Negative"):
        g = d[d["Label_Sentimento"] == cls].dropna(subset=[col_ret])
        if not len(g):
            continue
        subiu = float((g[col_ret] > 0).mean())
        rm = float(g[col_ret].mean())
        vm = float(g[col_ret].abs().mean())
        print(f"  {cls:12s}{len(g):>10,}{subiu:>9.1%}{1 - subiu:>9.1%}"
              f"{rm:>+12.4%}{vm:>12.4%}")
        linhas.append({"horizonte": rotulo, "sentimento": cls, "n": int(len(g)),
                       "pct_subiu": round(subiu, 4),
                       "retorno_medio": round(rm, 6),
                       "volatilidade_media": round(vm, 6)})
    return linhas


def regra_direcional(d: pd.DataFrame, col_ret: str, base: float,
                     rotulo: str) -> dict:
    """Regra: Positive -> aposta alta, Negative -> aposta baixa, Neutral -> passa.

    Reporta por notícia (informativo) e por pregão (é o que vale para o teste).
    """
    ap = d[d["Label_Sentimento"].isin(["Positive", "Negative"])].dropna(subset=[col_ret])

    ok = (((ap["Label_Sentimento"] == "Positive") & (ap[col_ret] > 0)) |
          ((ap["Label_Sentimento"] == "Negative") & (ap[col_ret] <= 0)))
    por_noticia = taxa(int(ok.sum()), len(ap), base)

    g = (ap.groupby("idx")
           .agg(pred=("Label_Sentimento", moda_ou_nada), ret=(col_ret, "first"))
           .dropna(subset=["pred", "ret"]))
    okp = (((g["pred"] == "Positive") & (g["ret"] > 0)) |
           ((g["pred"] == "Negative") & (g["ret"] <= 0)))
    por_pregao = taxa(int(okp.sum()), len(g), base)

    print(f"\n  --- {rotulo} ---")
    print(f"  por noticia : {por_noticia['taxa']:.2%} de {por_noticia['n']:,} "
          f"(referencia {base:.2%})")
    print(f"  por pregao  : {por_pregao['taxa']:.2%} de {por_pregao['n']:,}  "
          f"p={por_pregao['p_valor']:.4f}  "
          f"IC95=[{por_pregao['ic95'][0]:.2%},{por_pregao['ic95'][1]:.2%}]  "
          f"-> {'SIGNIFICATIVO' if por_pregao['p_valor'] < 0.05 else 'nao significativo'}")
    return {"horizonte": rotulo, "por_noticia": por_noticia, "por_pregao": por_pregao}


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=DIR / "acertividade_noticia.json")
    args = ap.parse_args()

    p = carregar_pregoes(DIR / "base_financeira_petr4.csv")
    base_alta = float((p["ret"] > 0).mean())

    n = pd.read_csv(DIR / "noticias_com_sentimento.csv",
                    usecols=["Data_Coleta", "Data_Ajustada", "categoria",
                             "Label_Sentimento", "Score_Confianca",
                             "Indice_Sentimento"])
    n["data_efetiva"] = pd.to_datetime(n["Data_Ajustada"], errors="coerce")
    n["hora"] = pd.to_datetime(n["Data_Coleta"], errors="coerce").dt.hour
    n["apos_fechamento"] = n["hora"] >= 17
    n = n.dropna(subset=["data_efetiva", "Label_Sentimento"])

    d = mapear_para_pregao(n, p)

    print("=" * 78)
    print("AUDITORIA DIRETA: O SENTIMENTO ACERTOU O PREGAO?")
    print("=" * 78)
    print(f"  noticias casadas com pregao ..... {len(d):,}")
    print(f"  pregoes distintos alcancados .... {d['idx'].nunique():,}")
    print(f"  publicadas apos as 17h .......... {int(d['apos_fechamento'].sum()):,} "
          f"({d['apos_fechamento'].mean():.0%})")
    print(f"  PETR4 subiu em .................. {base_alta:.2%} dos pregoes da serie")

    res = {"data_execucao": date.today().isoformat(),
           "n_noticias": int(len(d)), "n_pregoes": int(d["idx"].nunique()),
           "base_alta_mercado": round(base_alta, 4)}

    # ── 1. matriz descritiva ────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("1. O QUE ACONTECEU DEPOIS DE CADA TIPO DE NOTICIA")
    print("=" * 78)
    res["matriz"] = (matriz_direcao(d, "ret", "P0 — pregao que reage (reacao + antecipacao)")
                     + matriz_direcao(d, "ret_p1", "P1 — pregao seguinte (estritamente preditivo)"))

    # ── 2. a regra direcional acerta? ───────────────────────────────────────
    print("\n" + "=" * 78)
    print("2. A REGRA DIRECIONAL BATE O MERCADO?")
    print("=" * 78)
    print("  Regra: Positive -> aposta alta | Negative -> aposta baixa | Neutral -> passa")
    res["regra_direcional"] = [
        regra_direcional(d, "ret", base_alta, "P0 — pregao que reage"),
        regra_direcional(d, "ret_p1", base_alta, "P1 — pregao seguinte"),
    ]

    # ── 3. recortes: onde a regra funciona melhor? ──────────────────────────
    print("\n" + "=" * 78)
    print("3. EXISTE ALGUM RECORTE EM QUE A REGRA FUNCIONA? (horizonte P1)")
    print("=" * 78)
    ap_ = d[d["Label_Sentimento"].isin(["Positive", "Negative"])].dropna(subset=["ret_p1"])
    ap_ = ap_.assign(ok=(((ap_["Label_Sentimento"] == "Positive") & (ap_["ret_p1"] > 0)) |
                         ((ap_["Label_Sentimento"] == "Negative") & (ap_["ret_p1"] <= 0))))

    res["recortes"] = []
    faixas = [("categoria", ap_["categoria"]),
              ("publicacao", np.where(ap_["apos_fechamento"], "apos 17h", "ate 17h")),
              ("confianca", pd.qcut(ap_["Score_Confianca"], 4,
                                    labels=["Q1 baixa", "Q2", "Q3", "Q4 alta"]))]
    for nome, chave in faixas:
        print(f"\n  por {nome}:")
        print(f"  {'faixa':26s}{'noticias':>10s}{'acerto':>9s}{'vs base':>10s}")
        for v, g in ap_.groupby(chave, observed=True):
            t = float(g["ok"].mean())
            print(f"  {str(v):26s}{len(g):>10,}{t:>9.2%}{t - base_alta:>+10.2%}")
            res["recortes"].append({"dimensao": nome, "faixa": str(v),
                                    "n": int(len(g)), "taxa": round(t, 4),
                                    "vs_base": round(t - base_alta, 4)})

    #  A confiança do modelo é informativa? Se fosse, o acerto cresceria do Q1
    #  para o Q4. Testa-se a tendência sobre PREGÕES, não sobre notícias.
    q = pd.qcut(ap_["Score_Confianca"], 4, labels=False)
    porq = (ap_.assign(q=q).groupby(["idx", "q"], observed=True)["ok"]
                .mean().reset_index())
    rho, pv_rho = stats.spearmanr(porq["q"], porq["ok"])
    print(f"\n  tendencia acerto x confianca (Spearman, por pregao x quartil): "
          f"rho={rho:+.4f}  p={pv_rho:.4f}")
    print("  rho negativo significa que o modelo erra MAIS justamente quando "
          "esta mais confiante.")
    res["tendencia_confianca"] = {"spearman_rho": round(float(rho), 4),
                                  "p_valor": round(float(pv_rho), 6),
                                  "significativo": bool(pv_rho < 0.05)}

    # ── 4. volatilidade: a notícia antecipa o sacolejo? ─────────────────────
    print("\n" + "=" * 78)
    print("4. VOLATILIDADE: A NOTICIA ANTECIPA O TAMANHO DO MOVIMENTO?")
    print("=" * 78)
    print("  Hipotese: apos noticia NEGATIVA o pregao seguinte oscila MAIS\n")
    neg = d.loc[d["Label_Sentimento"] == "Negative", "vol_p1"].dropna()
    pos = d.loc[d["Label_Sentimento"] == "Positive", "vol_p1"].dropna()
    neu = d.loc[d["Label_Sentimento"] == "Neutral", "vol_p1"].dropna()
    print(f"  apos Negative : mediana {neg.median():.4%}  (n={len(neg):,})")
    print(f"  apos Neutral  : mediana {neu.median():.4%}  (n={len(neu):,})")
    print(f"  apos Positive : mediana {pos.median():.4%}  (n={len(pos):,})")

    #  ATENÇÃO — pseudorreplicação. As 205 mil notícias distribuem-se por apenas
    #  1.989 pregões, de modo que a mesma volatilidade é contada dezenas de
    #  vezes. Um teste sobre a tabela de notícias declararia significância a
    #  partir de diferenças ínfimas. O teste válido é o de PREGÃO: colapsa-se o
    #  dia pelo sentimento majoritário e comparam-se dias, não notícias.
    diario = (d.groupby("idx")
                .agg(pred=("Label_Sentimento", moda_ou_nada),
                     ism=("Indice_Sentimento", "mean"), vol=("vol_p1", "first"))
                .dropna(subset=["pred", "vol"]))
    contagem = diario["pred"].value_counts().to_dict()

    print(f"\n  Colapsando por pregao (voto majoritario) --- o teste valido:")
    print(f"  {'sentimento do dia':22s}{'pregoes':>9s}{'mediana |ret| D+1':>20s}")
    for rot in ("Negative", "Neutral", "Positive"):
        s = diario.loc[diario["pred"] == rot, "vol"]
        print(f"  {rot:22s}{len(s):>9,}"
              f"{(f'{s.median():.4%}' if len(s) else '---'):>20s}")

    negd = diario.loc[diario["pred"] == "Negative", "vol"]
    neud = diario.loc[diario["pred"] == "Neutral", "vol"]
    res["volatilidade_por_classe"] = {
        "por_noticia": {
            "mediana_apos_negative": round(float(neg.median()), 6),
            "mediana_apos_neutral": round(float(neu.median()), 6),
            "mediana_apos_positive": round(float(pos.median()), 6),
            "aviso": "pseudorreplicacao: 205.697 noticias em 1.989 pregoes; "
                     "nao usar para inferencia"},
        "contagem_pregoes_por_classe": {k: int(v) for k, v in contagem.items()}}

    #  Não existe um único pregão de maioria Positiva. A comparação canônica
    #  Negativo x Positivo é, portanto, IMPOSSÍVEL neste corpus --- fato que é
    #  ele próprio a evidência mais crua do viés do classificador. Restam dois
    #  contrastes viáveis, ambos por grau de pessimismo e não por classe.
    print("\n  Nao ha pregao algum de maioria Positiva. A comparacao canonica e")
    print("  impossivel; testam-se entao GRAUS de pessimismo.\n")

    u1, p1 = stats.mannwhitneyu(negd, neud, alternative="greater")
    print(f"  (a) dias Negativos x dias Neutros: p={p1:.4f}  "
          f"razao={negd.median() / neud.median():.3f}x  -> "
          f"{'SIGNIFICATIVO' if p1 < 0.05 else 'NAO significativo'}")

    t = diario["ism"].quantile([1 / 3, 2 / 3]).to_list()
    pess = diario.loc[diario["ism"] <= t[0], "vol"]     # terço mais pessimista
    otim = diario.loc[diario["ism"] >= t[1], "vol"]     # terço menos pessimista
    u2, p2 = stats.mannwhitneyu(pess, otim, alternative="greater")
    razao = float(pess.median() / otim.median())
    print(f"  (b) terco mais pessimista x terco menos pessimista do ISM:")
    print(f"      {len(pess):,} x {len(otim):,} pregoes  |  "
          f"{pess.median():.4%} x {otim.median():.4%}")
    print(f"      p={p2:.6f}  razao={razao:.3f}x  "
          f"({(razao - 1) * 100:+.1f}% de volatilidade a mais)  -> "
          f"{'SIGNIFICATIVO' if p2 < 0.05 else 'NAO significativo'}")

    res["volatilidade_por_classe"]["contraste_negativo_neutro"] = {
        "n_negativo": int(len(negd)), "n_neutro": int(len(neud)),
        "mediana_negativo": round(float(negd.median()), 6),
        "mediana_neutro": round(float(neud.median()), 6),
        "razao": round(float(negd.median() / neud.median()), 4),
        "mann_whitney_p": round(float(p1), 6), "significativo": bool(p1 < 0.05)}
    #  ── reconciliação com a correlação já reportada ─────────────────────────
    #
    #  A correlação linear entre o ISM e a volatilidade é significativa
    #  ($r \approx -0,14$, $p \approx 0$), mas o contraste de medianas acima não
    #  é. Não há contradição: as duas medidas respondem a perguntas distintas.
    #  A correlação é sensível às caudas --- basta um punhado de dias de crise,
    #  com ISM muito baixo e volatilidade muito alta, para produzi-la. A mediana
    #  descreve o dia TÍPICO, e ali o efeito quase desaparece. Reportar as duas
    #  lado a lado evita que o leitor tome uma pela outra.
    print("\n  Reconciliacao com a correlacao reportada na Secao do filtro:")
    rp, ppv = stats.pearsonr(diario["ism"], diario["vol"])
    rs, spv = stats.spearmanr(diario["ism"], diario["vol"])
    print(f"    Pearson  (sensivel a cauda) r={rp:+.4f}  p={ppv:.6f}")
    print(f"    Spearman (so ordenacao)     r={rs:+.4f}  p={spv:.6f}")
    print(f"    media    do terco pessimista x otimista: "
          f"{pess.mean():.4%} x {otim.mean():.4%}  "
          f"(razao {pess.mean() / otim.mean():.3f}x)")
    print(f"    mediana  do terco pessimista x otimista: "
          f"{pess.median():.4%} x {otim.median():.4%}  (razao {razao:.3f}x)")
    print("    A razao entre MEDIAS supera a razao entre MEDIANAS: o efeito")
    print("    concentra-se nos dias extremos, nao no dia tipico.")
    res["reconciliacao"] = {
        "pearson_r": round(float(rp), 4), "pearson_p": round(float(ppv), 8),
        "spearman_r": round(float(rs), 4), "spearman_p": round(float(spv), 8),
        "razao_medias": round(float(pess.mean() / otim.mean()), 4),
        "razao_medianas": round(razao, 4),
        "leitura": "o efeito e de cauda: aparece na correlacao e nas medias, "
                   "some na mediana; o dia tipico nao se distingue"}

    res["volatilidade_por_classe"]["contraste_tercos_ism"] = {
        "n_pessimista": int(len(pess)), "n_otimista": int(len(otim)),
        "mediana_pessimista": round(float(pess.median()), 6),
        "mediana_otimista": round(float(otim.median()), 6),
        "razao": round(razao, 4),
        "mann_whitney_p": round(float(p2), 8), "significativo": bool(p2 < 0.05)}

    # ── 5. a chamada de volatilidade acerta? ────────────────────────────────
    #
    #  Transforma-se a associação em DECISÃO: prever se o pregão seguinte será
    #  de volatilidade acima ou abaixo da mediana histórica. Os limiares vêm
    #  apenas do trecho de treino, de modo que a avaliação não usa o futuro.
    print("\n" + "=" * 78)
    print("5. A CHAMADA DE VOLATILIDADE ACERTA? (decisao binaria, fora da amostra)")
    print("=" * 78)

    dia = (d.groupby("idx")
             .agg(ism=("Indice_Sentimento", "mean"), n_not=("idx", "size"))
             .join(p.set_index("idx")[["vol_p1"]]).dropna().sort_index())
    corte = int(len(dia) * PROP_TREINO)
    tr, te = dia.iloc[:corte], dia.iloc[corte:]

    #  diagnóstico do viés: se o ISM quase nunca for positivo, "mais pessimista"
    #  e "mais extremo" selecionam o mesmo conjunto de dias, e os dois sinais
    #  abaixo produzirão resultados idênticos --- o que é achado, não erro
    pct_neg = float((dia["ism"] < 0).mean())
    print(f"  dias com ISM negativo: {pct_neg:.1%} "
          f"(mediana do ISM diario: {dia['ism'].median():+.4f})")

    lim_vol = tr["vol_p1"].median()          # o que se considera "dia agitado"
    alvo = (te["vol_p1"] > lim_vol).astype(int)
    base_vol = float(alvo.mean())
    print(f"  limiar de dia agitado (mediana do treino): {lim_vol:.4%}")
    print(f"  pregoes de teste: {len(te):,} | agitados: {base_vol:.1%}\n")
    print(f"  {'sinal usado':32s}{'acerto':>9s}{'precisao':>10s}{'cobertura':>11s}{'p':>9s}")

    res["chamada_volatilidade"] = []
    for nome, serie_tr, serie_te, q in [
        ("ISM pessimista (30% menores)", tr["ism"], te["ism"], 0.30),
        ("ISM extremo (|ISM| 30% maiores)", tr["ism"].abs(), te["ism"].abs(), 0.70),
        ("volume de noticias (30% maiores)", tr["n_not"], te["n_not"], 0.70),
    ]:
        lim = serie_tr.quantile(q)
        sinal = (serie_te <= lim).astype(int) if q < 0.5 else (serie_te >= lim).astype(int)
        acerto = float((sinal == alvo).mean())
        marcados = int(sinal.sum())
        prec = float(alvo[sinal == 1].mean()) if marcados else float("nan")
        cob = float(sinal[alvo == 1].mean())
        # o sinal acerta mais que marcar ao acaso na mesma proporção?
        pv2 = stats.binomtest(int(alvo[sinal == 1].sum()), marcados, base_vol).pvalue \
            if marcados else 1.0
        print(f"  {nome:32s}{acerto:>9.1%}{prec:>10.1%}{cob:>11.1%}{pv2:>9.4f}"
              f"   {'SIG' if pv2 < 0.05 else ''}")
        res["chamada_volatilidade"].append(
            {"sinal": nome, "n_marcados": marcados, "acuracia": round(acerto, 4),
             "precisao": round(prec, 4), "cobertura": round(cob, 4),
             "base": round(base_vol, 4), "p_valor": round(float(pv2), 6),
             "significativo": bool(pv2 < 0.05)})

    args.saida.write_text(json.dumps(res, indent=2, ensure_ascii=False, default=float),
                          encoding="utf-8")
    print(f"\n[OK] Salvo em {args.saida}")


if __name__ == "__main__":
    main()
