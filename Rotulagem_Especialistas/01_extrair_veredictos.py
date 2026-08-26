# -*- coding: utf-8 -*-
# ==============================================================================
#   E2 — Rótulo do especialista, extraído do nosso próprio corpus
#
#   Pedido dos Profs. Emerson Paraiso e Julio Nievola: encontrar especialistas
#   que publiquem se a notícia é boa ou ruim para a Petrobras, e usar isso como
#   validação do nosso classificador.
#
#   Achado que dispensou a coleta externa: esses veredictos JÁ ESTÃO no nosso
#   corpus. Casas de análise e agências de risco publicam o parecer, e a
#   imprensa reproduz na própria manchete — "Guide: reajuste do GLP é positivo
#   para a Petrobras".
#
#   O preço NÃO é usado como critério de qualidade do rótulo (ver Seção 3 do
#   protocolo). Aqui se mede concordância entre dois leitores: o especialista
#   humano e o FinBERT-PT-BR.
#
#   Saídas: _veredictos_especialistas.csv  e  _resultado_concordancia.json
# ==============================================================================
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
DADOS = RAIZ / "datasets_refino"

# corpus completo, já com o rótulo do FinBERT-PT-BR em cada linha
BASE = RAIZ / "Mestrado_PETR4" / "noticias_com_sentimento.csv"

# ── quem é especialista ──────────────────────────────────────────────────────
CASAS = (r"fitch|moody'?s|standard\s*&\s*poor|\bs&p\b|xp investimentos|\bxp\b|btg|"
         r"bradesco bbi|bb investimentos|itaú bba|itau bba|santander|safra|genial|"
         r"suno|levante|eleven|ativa investimentos|guide|órama|orama|nord research|"
         r"empiricus|morgan stanley|goldman sachs|jpmorgan|j\.p\.\s*morgan|\bubs\b|"
         r"citi|bank of america|credit suisse|jefferies|scotiabank|\bhsbc\b|"
         r"analistas?|casa de análise|corretora")

PETRO = r"petrobras|petrobrás|petr4|petr3"

# ── o veredicto, por polaridade ──────────────────────────────────────────────
# Ordem importa: procura-se primeiro o enunciado explícito, depois o indireto.
POSITIVO = [
    r"(é|são|foi|foram)\s+(muito\s+)?positiv",
    r"positiv[oa]s?\s+para\s+(a\s+|as\s+|o\s+)?(petrobras|petrobrás|petr4|petr3|companhia|empresa|estatal|papel|ação|ações)",
    r"(elev|aument|sub)\w+\s+(o\s+|a\s+|para\s+)?(preço[- ]alvo|recomendação|rating)",
    r"recomendaç\w+\s+(de\s+|para\s+)?[«\"']?\s*compra",
    r"recomend\w+\s+(a\s+)?compra",
    r"para\s+[«\"']?compra[»\"']?",
    r"\boutperform\b|acima da média do mercado",
    r"(está|estão|segue|seguem)\s+(com\s+um\s+)?(bom|ótim|atraent|atrativ)",
    r"bom ponto de entrada|top ?pick|ação preferida|preferida d\w+ analistas",
    r"surpres[ao] positiv|acima d[oa] (esperado|expectativa|projeç)",
    r"(vê|veem|enxerg\w+)\s+\w*\s*(oportunidade|potencial de alta|espaço para alta)",
]
NEGATIVO = [
    r"(é|são|foi|foram)\s+(muito\s+)?negativ",
    r"negativ[oa]s?\s+para\s+(a\s+|as\s+|o\s+)?(petrobras|petrobrás|petr4|petr3|companhia|empresa|estatal|papel|ação|ações|crédito)",
    r"(reduz|cort|rebaix|diminu)\w+\s+(o\s+|a\s+|para\s+)?(preço[- ]alvo|recomendação|rating)",
    r"recomendaç\w+\s+(de\s+|para\s+)?[«\"']?\s*venda",
    r"deixa de recomendar|deixou de recomendar",
    r"\bunderperform\b|abaixo da média do mercado",
    r"surpres[ao] negativ|abaixo d[oa] (esperado|expectativa|projeç)|decepcion",
    r"(vê|veem|enxerg\w+)\s+\w*\s*(risco|pressão|deterioraç)",
]
NEUTRO = [
    r"\bmarket ?perform\b|em linha com a média",
    r"recomendaç\w+\s+(de\s+|para\s+)?[«\"']?\s*(neutr|manutenção)",
    r"mant[ée]m\s+(a\s+)?recomendaç\w+\s+neutr",
]


def _bate(texto: str, padroes: list[str]) -> list[str]:
    return [p for p in padroes if re.search(p, texto)]


def classificar(texto: str) -> tuple[str, str]:
    """Devolve (rótulo, evidência). 'Ambíguo' quando há sinais contrários."""
    t = texto.lower()
    pos, neg, neu = _bate(t, POSITIVO), _bate(t, NEGATIVO), _bate(t, NEUTRO)
    if pos and neg:
        return "Ambiguo", "sinais contrários"
    if pos:
        return "Positive", re.search(pos[0], t).group(0)[:60]
    if neg:
        return "Negative", re.search(neg[0], t).group(0)[:60]
    if neu:
        return "Neutral", re.search(neu[0], t).group(0)[:60]
    return "SemVeredicto", ""


def qual_casa(texto: str) -> str:
    m = re.search(CASAS, texto.lower())
    return m.group(0) if m else ""


def main() -> None:
    print("=" * 76)
    print("E2 — VEREDICTOS DE ESPECIALISTAS EXTRAÍDOS DO NOSSO CORPUS")
    print("=" * 76)

    d = pd.read_csv(BASE, low_memory=False)
    d = d.rename(columns={"Titulo": "Noticia", "Label_Sentimento": "Sentimento_Rotulo",
                          "Indice_Sentimento": "Sentimento_Indice",
                          "Data": "Data_Publicacao", "dominio": "Portal"})
    d["texto"] = d["Noticia"].fillna("") + " || " + d["Resumo"].fillna("")
    t = d["texto"].str.lower()

    m_petro = t.str.contains(PETRO, regex=True, na=False)
    m_casa = t.str.contains(CASAS, regex=True, na=False)
    pool = d[m_petro & m_casa].copy()

    print("")
    print("  corpus completo ........... {:,}".format(len(d)))
    print(f"  menciona Petrobras ........ {m_petro.sum():,}")
    print(f"  ... e uma casa/analista ... {len(pool):,}  <- conjunto candidato")

    pool[["Rotulo_Especialista", "Evidencia"]] = pool["texto"].apply(
        lambda x: pd.Series(classificar(x)))
    pool["Casa"] = pool["texto"].apply(qual_casa)

    print("\n  Veredictos extraídos:")
    for k, v in pool["Rotulo_Especialista"].value_counts().items():
        print(f"    {k:16s} {v:>5,}")

    # conjunto de trabalho: veredicto explícito, sem ambiguidade
    ok = pool[pool["Rotulo_Especialista"].isin(["Positive", "Negative", "Neutral"])].copy()
    ok = ok[ok["Sentimento_Rotulo"].notna()]

    print(f"\n  >>> CONJUNTO DE VALIDAÇÃO: {len(ok):,} notícias com veredicto de "
          f"especialista E rótulo do nosso modelo")

    # ── concordância ─────────────────────────────────────────────────────────
    ok["Acertou"] = ok["Rotulo_Especialista"] == ok["Sentimento_Rotulo"]
    acc = ok["Acertou"].mean()

    print("\n" + "-" * 76)
    print(f"  CONCORDÂNCIA FinBERT-PT-BR x ESPECIALISTA: {acc:.1%}")
    print("-" * 76)

    print("\n  Matriz (linha = especialista, coluna = nosso modelo):")
    mat = pd.crosstab(ok["Rotulo_Especialista"], ok["Sentimento_Rotulo"])
    print(mat.to_string().replace("\n", "\n    "))

    print("\n  Por classe do especialista:")
    linhas = []
    for cls in ["Positive", "Neutral", "Negative"]:
        sub = ok[ok["Rotulo_Especialista"] == cls]
        if len(sub):
            a = sub["Acertou"].mean()
            print(f"    {cls:10s} n={len(sub):>4}   concordância {a:>6.1%}")
            linhas.append({"classe": cls, "n": len(sub), "concordancia": round(a, 4)})

    # kappa de Cohen
    try:
        from sklearn.metrics import cohen_kappa_score, f1_score
        k = cohen_kappa_score(ok["Rotulo_Especialista"], ok["Sentimento_Rotulo"])
        f1 = f1_score(ok["Rotulo_Especialista"], ok["Sentimento_Rotulo"],
                      average="macro", zero_division=0)
        print(f"\n    kappa de Cohen ... {k:.4f}")
        print(f"    F1 macro ......... {f1:.4f}")
    except Exception:                                             # noqa: BLE001
        k = f1 = None

    # quanto o especialista é positivo, contra o nosso viés conhecido
    print("\n  DISTRIBUIÇÃO — especialista contra o nosso modelo (mesmas notícias):")
    for nome, col in [("especialista", "Rotulo_Especialista"),
                      ("nosso modelo", "Sentimento_Rotulo")]:
        p = ok[col].value_counts(normalize=True)
        print(f"    {nome:14s} pos {p.get('Positive',0):.1%} | "
              f"neu {p.get('Neutral',0):.1%} | neg {p.get('Negative',0):.1%}")

    cols = ["Data_Publicacao", "Data_Pregao_Atribuido", "Portal", "Casa", "Noticia",
            "Resumo", "Rotulo_Especialista", "Evidencia", "Sentimento_Rotulo",
            "Sentimento_Indice", "Acertou", "URL"]
    cols = [c for c in cols if c in ok.columns]
    ok[cols].sort_values("Data_Publicacao").to_csv(
        AQUI / "_veredictos_especialistas.csv", index=False, encoding="utf-8-sig")

    res = {
        "corpus_completo": int(len(d)),
        "menciona_petrobras": int(m_petro.sum()),
        "conjunto_candidato": int(len(pool)),
        "veredictos": pool["Rotulo_Especialista"].value_counts().to_dict(),
        "conjunto_validacao": int(len(ok)),
        "concordancia_global": round(float(acc), 4),
        "kappa_cohen": round(float(k), 4) if k is not None else None,
        "f1_macro": round(float(f1), 4) if f1 is not None else None,
        "por_classe": linhas,
        "matriz": mat.to_dict(),
        "dist_especialista": ok["Rotulo_Especialista"].value_counts(normalize=True).round(4).to_dict(),
        "dist_modelo": ok["Sentimento_Rotulo"].value_counts(normalize=True).round(4).to_dict(),
    }
    (AQUI / "_resultado_concordancia.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n  gravados: _veredictos_especialistas.csv e _resultado_concordancia.json")


if __name__ == "__main__":
    main()
