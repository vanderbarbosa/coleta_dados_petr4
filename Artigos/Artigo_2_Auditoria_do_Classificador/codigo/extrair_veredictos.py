# -*- coding: utf-8 -*-
# ==============================================================================
#   E2 v2 — Veredictos de especialistas, com controle de precisão
#
#   A versão 1 produziu 488 casos, mas a auditoria manual encontrou erros
#   graves de extração:
#     - "XP atualiza Top Picks no lugar de Petrobras"  -> é REMOÇÃO, não compra
#     - "Santander TIRA Petrobras da carteira e recomenda 8 ações para comprar"
#     - "Credit Suisse tem aposta acima da média para BR DISTRIBUIDORA"
#
#   Correções desta versão:
#     1. a Petrobras precisa estar no TÍTULO, não só no resumo;
#     2. o veredicto precisa estar PERTO da menção à Petrobras (janela de
#        caracteres), para não capturar parecer sobre outra empresa;
#     3. verbos de REMOÇÃO na janela invertem ou anulam o veredicto;
#     4. tudo que sobra vai para planilha de AUDITORIA MANUAL — nenhum número
#        é reportado sem conferência humana.
#
#   Saídas: _v2_para_auditoria.csv   (com coluna em branco para o revisor)
#           _v2_resultado.json
# ==============================================================================
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
BASE = RAIZ / "Mestrado_PETR4" / "noticias_com_sentimento.csv"

JANELA = 110          # caracteres de cada lado da menção à Petrobras

# Matérias-resumo ("radar do dia", "destaques do mercado") juntam várias
# empresas na mesma manchete; o parecer citado costuma ser sobre OUTRA empresa.
# Ex.: "Petrobras deve vender Braskem; Fitch eleva rating da USIMINAS e mais..."
RESUMO_DIARIO = (r"no radar|radar do|destaques do mercado|e mais notícias|"
                 r"principais notícias|resumo do dia|o que move|giro do mercado|"
                 r"agenda do dia|veja os destaques|newsletter")

PETRO = r"petrobras|petrobrás|petr4|petr3"

CASAS = (r"fitch|moody'?s|standard\s*&\s*poor|\bs&p\b|xp investimentos|\bxp\b|btg|"
         r"bradesco bbi|bb investimentos|itaú bba|itau bba|santander|safra|genial|"
         r"suno|levante|eleven|ativa investimentos|guide|órama|orama|nord research|"
         r"empiricus|morgan stanley|goldman sachs|jpmorgan|j\.p\.\s*morgan|\bubs\b|"
         r"citi|bank of america|credit suisse|jefferies|scotiabank|\bhsbc\b|"
         r"planner|analistas?|casa de análise|corretora")

# ── remoção / exclusão: mata ou inverte o veredicto ──────────────────────────
REMOCAO = (r"\b(tira|tirou|retira|retirou|remove|removeu|exclui|excluiu|"
           r"deixa de|deixou de|sai d|saiu d|fora d[ae]|no lugar d[ae]|"
           r"substitu\w+|troca\w*|corta|cortou|retirada)\b")

POSITIVO = [
    r"(é|são|foi|foram|está|estão)\s+(muito\s+|bastante\s+)?positiv",
    r"positiv[oa]s?\s+para",
    r"(elev|aument|sub[iu])\w*\s+(o\s+|a\s+|para\s+|as\s+)?(preço[- ]alvo|recomendaç|rating|estimativ|projeç)",
    r"recomendaç\w+\s+(de\s+|para\s+)?[«\"']?\s*compra",
    r"recomend\w+\s+(a\s+)?compra",
    r"\boutperform\b|acima da média do mercado|desempenho acima",
    r"(está|estão|segue|seguem|continua\w*)\s+(com\s+um\s+|como\s+)?(atraent|atrativ|barat)",
    r"bom ponto de entrada|top ?pick|ação preferida|preferid[ao]",
    r"surpres[ao] positiv|acima d[oa] (esperado|expectativa|projeç|consenso)",
    r"potencial de alta|espaço para alta|upside",
]
NEGATIVO = [
    r"(é|são|foi|foram|está|estão)\s+(muito\s+|bastante\s+)?negativ",
    r"negativ[oa]s?\s+para",
    r"(reduz|reduziu|cort|rebaix|diminu)\w*\s+(o\s+|a\s+|para\s+|as\s+)?(preço[- ]alvo|recomendaç|rating|estimativ|projeç)",
    r"recomendaç\w+\s+(de\s+|para\s+)?[«\"']?\s*venda",
    r"\bunderperform\b|abaixo da média do mercado|desempenho abaixo",
    r"surpres[ao] negativ|abaixo d[oa] (esperado|expectativa|projeç|consenso)|decepcion",
    r"potencial de queda|espaço para queda|downside",
]
NEUTRO = [
    r"\bmarket ?perform\b|em linha com a média|desempenho em linha",
    r"recomendaç\w+\s+(de\s+|para\s+)?[«\"']?\s*(neutr|manutenção)",
]


def janelas_petro(texto: str) -> list[str]:
    """Trechos ao redor de cada menção à Petrobras."""
    t = texto.lower()
    return [t[max(0, m.start() - JANELA): m.end() + JANELA]
            for m in re.finditer(PETRO, t)]


def _acha(j: str, pads: list[str]) -> str | None:
    for p in pads:
        m = re.search(p, j)
        if m:
            return m.group(0)[:70]
    return None


def classificar(titulo: str, resumo: str) -> tuple[str, str, str]:
    """(rótulo, evidência, observação). Só olha janelas ao redor da Petrobras."""
    texto = f"{titulo} || {resumo}"
    js = janelas_petro(texto)
    if not js:
        return "SemVeredicto", "", "sem menção"

    achados: list[tuple[str, str, bool]] = []
    for j in js:
        remocao = bool(re.search(REMOCAO, j))
        for rot, pads in (("Positive", POSITIVO), ("Negative", NEGATIVO),
                          ("Neutral", NEUTRO)):
            ev = _acha(j, pads)
            if ev:
                achados.append((rot, ev, remocao))
                break

    if not achados:
        return "SemVeredicto", "", ""

    # havendo verbo de remoção junto a um veredicto, o caso é duvidoso:
    # "tira Petrobras da carteira e recomenda comprar" não é parecer positivo
    if any(r for _, _, r in achados):
        rot, ev, _ = achados[0]
        return "Duvidoso", ev, "verbo de remoção na janela"

    # ressalva explícita ("eleva preço-alvo, MAS não recomenda compra")
    if re.search(r"mas\s+(não|nao|ainda não)", texto.lower()):
        return "Ambiguo", achados[0][1], "ressalva com 'mas não'"

    rots = {r for r, _, _ in achados}
    if len(rots) > 1:
        return "Ambiguo", achados[0][1], "sinais contrários"
    return achados[0][0], achados[0][1], ""


def casa(texto: str) -> str:
    m = re.search(CASAS, texto.lower())
    return m.group(0) if m else ""


def main() -> None:
    print("=" * 76)
    print("E2 v2 — VEREDICTOS COM CONTROLE DE PRECISÃO")
    print("=" * 76)

    d = pd.read_csv(BASE, low_memory=False)
    d = d.rename(columns={"Titulo": "Noticia", "Label_Sentimento": "Sentimento_Rotulo",
                          "Indice_Sentimento": "Sentimento_Indice",
                          "Data": "Data_Publicacao", "dominio": "Portal"})
    d["Noticia"] = d["Noticia"].fillna("")
    d["Resumo"] = d["Resumo"].fillna("")

    # FILTRO 1 — a notícia tem de ser SOBRE a Petrobras: menção no título
    no_titulo = d["Noticia"].str.lower().str.contains(PETRO, regex=True, na=False)
    # FILTRO 2 — alguma casa de análise citada
    tem_casa = (d["Noticia"] + " " + d["Resumo"]).str.lower().str.contains(
        CASAS, regex=True, na=False)

    # FILTRO 3 — fora as matérias-resumo, que misturam várias empresas
    e_resumo = d["Noticia"].str.lower().str.contains(RESUMO_DIARIO, regex=True, na=False)

    pool = d[no_titulo & tem_casa & ~e_resumo].copy()
    print("")
    print("  corpus ........................ {:,}".format(len(d)))
    print("  Petrobras NO TITULO ........... {:,}".format(no_titulo.sum()))
    print("  ... e casa de analise citada .. {:,}".format((no_titulo & tem_casa).sum()))
    print("  ... menos materias-resumo ..... {:,}   (descartadas {:,})".format(
        len(pool), (no_titulo & tem_casa & e_resumo).sum()))

    res = pool.apply(lambda r: pd.Series(classificar(r["Noticia"], r["Resumo"])),
                     axis=1)
    pool[["Rotulo_Especialista", "Evidencia", "Obs"]] = res
    pool["Casa"] = (pool["Noticia"] + " " + pool["Resumo"]).apply(casa)

    print("\n  Veredictos:")
    for k, v in pool["Rotulo_Especialista"].value_counts().items():
        print(f"    {k:16s} {v:>5,}")

    limpo = pool[pool["Rotulo_Especialista"].isin(
        ["Positive", "Negative", "Neutral"])].copy()
    limpo = limpo[limpo["Sentimento_Rotulo"].notna()]

    print(f"\n  >>> CONJUNTO LIMPO (pré-auditoria): {len(limpo):,}")

    limpo["Concorda"] = limpo["Rotulo_Especialista"] == limpo["Sentimento_Rotulo"]
    acc = limpo["Concorda"].mean()

    print("\n" + "-" * 76)
    print(f"  CONCORDÂNCIA (PRELIMINAR, PENDENTE DE AUDITORIA): {acc:.1%}")
    print("-" * 76)

    mat = pd.crosstab(limpo["Rotulo_Especialista"], limpo["Sentimento_Rotulo"])
    print("\n  Matriz (linha = especialista, coluna = nosso modelo):")
    print("    " + mat.to_string().replace("\n", "\n    "))

    linhas = []
    print("\n  Por classe do especialista:")
    for cls in ["Positive", "Neutral", "Negative"]:
        s = limpo[limpo["Rotulo_Especialista"] == cls]
        if len(s):
            print(f"    {cls:10s} n={len(s):>4}   concordância {s['Concorda'].mean():>6.1%}")
            linhas.append({"classe": cls, "n": int(len(s)),
                           "concordancia": round(float(s["Concorda"].mean()), 4)})

    try:
        from sklearn.metrics import cohen_kappa_score
        k = float(cohen_kappa_score(limpo["Rotulo_Especialista"],
                                    limpo["Sentimento_Rotulo"]))
        print(f"\n    kappa de Cohen ... {k:.4f}")
    except Exception:                                             # noqa: BLE001
        k = None

    print("\n  DISTRIBUIÇÃO nas mesmas notícias:")
    for nome, col in [("especialista", "Rotulo_Especialista"),
                      ("nosso modelo", "Sentimento_Rotulo")]:
        p = limpo[col].value_counts(normalize=True)
        print(f"    {nome:14s} pos {p.get('Positive',0):>5.1%} | "
              f"neu {p.get('Neutral',0):>5.1%} | neg {p.get('Negative',0):>5.1%}")

    # ── planilha de auditoria ────────────────────────────────────────────────
    aud = limpo.copy()
    aud["AUDITORIA_correto?"] = ""          # o revisor preenche: S / N
    aud["AUDITORIA_rotulo_certo"] = ""      # se N, qual seria
    cols = ["Data_Publicacao", "Portal", "Casa", "Noticia", "Resumo",
            "Rotulo_Especialista", "Evidencia", "Sentimento_Rotulo", "Concorda",
            "AUDITORIA_correto?", "AUDITORIA_rotulo_certo", "URL"]
    cols = [c for c in cols if c in aud.columns]
    aud[cols].sort_values("Data_Publicacao").to_csv(
        AQUI / "_v2_para_auditoria.csv", index=False, encoding="utf-8-sig")

    pool[pool["Rotulo_Especialista"].isin(["Duvidoso", "Ambiguo"])][
        [c for c in ["Data_Publicacao", "Noticia", "Rotulo_Especialista", "Evidencia",
                     "Obs"] if c in pool.columns]].to_csv(
        AQUI / "_v2_descartados.csv", index=False, encoding="utf-8-sig")

    (AQUI / "_v2_resultado.json").write_text(json.dumps({
        "corpus": int(len(d)),
        "petrobras_no_titulo": int(no_titulo.sum()),
        "com_casa_de_analise": int(len(pool)),
        "veredictos": {k: int(v) for k, v in
                       pool["Rotulo_Especialista"].value_counts().items()},
        "conjunto_limpo": int(len(limpo)),
        "concordancia_preliminar": round(float(acc), 4),
        "kappa_cohen": round(k, 4) if k is not None else None,
        "por_classe": linhas,
        "matriz": {str(i): {str(c): int(v) for c, v in r.items()}
                   for i, r in mat.iterrows()},
        "dist_especialista": limpo["Rotulo_Especialista"].value_counts(
            normalize=True).round(4).to_dict(),
        "dist_modelo": limpo["Sentimento_Rotulo"].value_counts(
            normalize=True).round(4).to_dict(),
        "AVISO": "Número preliminar. Exige auditoria manual de _v2_para_auditoria.csv "
                 "antes de ser reportado como resultado.",
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n  gravados: _v2_para_auditoria.csv, _v2_descartados.csv, _v2_resultado.json")
    print("\n  ATENÇÃO: o número acima é PRELIMINAR e exige auditoria manual.")


if __name__ == "__main__":
    main()
