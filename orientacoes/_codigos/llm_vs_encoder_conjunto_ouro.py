# -*- coding: utf-8 -*-
# =============================================================================
#  LLM generativo × encoder especializado, em PORTUGUÊS financeiro — gap G6
#  Preenche a lacuna deixada por Teles e Figueiredo (2025)
# =============================================================================
#
#  ⚠️  ORIGEM: código próprio. Teles e Figueiredo (2025) não publicaram código.
#
#  O QUE ESTE EXPERIMENTO FAZ DE DIFERENTE DAQUELE TRABALHO
#  ┌────────────────────┬──────────────────────────┬───────────────────────────┐
#  │ Aspecto            │ Teles e Figueiredo (2025)│ Este experimento          │
#  ├────────────────────┼──────────────────────────┼───────────────────────────┤
#  │ Idioma             │ Inglês                   │ PORTUGUÊS                 │
#  │ Corpus             │ 3 conjuntos genéricos    │ Conjunto-ouro PETR4       │
#  │ Encoder de domínio │ AUSENTE                  │ FinBERT-PT-BR incluído    │
#  │ Prompt             │ 1 frase genérica         │ Instrução LITERAL de      │
#  │                    │                          │ Santos (rentabilidade)    │
#  │ Determinismo       │ não discutido            │ temperatura 0 + n repet.  │
#  │ Significância      │ ausente                  │ bootstrap + IC + teste Z  │
#  └────────────────────┴──────────────────────────┴───────────────────────────┘
#
#  POR QUE VALE A PENA (3 resultados possíveis, TODOS publicáveis)
#    • LLM ganha    → evidência para migrar; achado inédito em PT-BR
#    • Encoder ganha→ justificativa EMPÍRICA para mantê-lo (hoje não temos)
#    • Empatam      → o argumento passa a ser custo, reprodutibilidade e
#                     determinismo, que favorecem o encoder
#
#  NÃO CONSOME ROTULAGEM NOVA — usa o conjunto-ouro de 300 manchetes.
#  Compatível com a suspensão da rotulagem (mentoria 29/07/2026).
#
#  RESSALVA A DECLARAR NA DISSERTAÇÃO: Abílio, Coelho e Silva (2024) documentam
#  que modelos generativos alteraram valores monetários e percentuais em texto
#  financeiro. Aqui a tarefa é classificação (não geração), o que mitiga o
#  risco — mas a ressalva deve constar.
# =============================================================================
from __future__ import annotations

import argparse
import json
import os
import re
import time
from collections import Counter
from datetime import date
from pathlib import Path

import pandas as pd
from sklearn.metrics import (accuracy_score, classification_report,
                             cohen_kappa_score, confusion_matrix, f1_score)

CLASSES = ["Negative", "Neutral", "Positive"]

# ─── O PROMPT ────────────────────────────────────────────────────────────────
# Instrução LITERAL de Santos (2022, Seção 4.2.3), a mesma dada aos anotadores
# humanos do FinBERT-PT-BR. Usar exatamente esta redação é o que torna a
# comparação justa: o LLM recebe a mesma definição operacional que o gabarito.
INSTRUCAO_SANTOS = (
    "Classifique a notícia considerando se o texto implicaria em uma "
    "rentabilidade Positiva, Negativa ou Neutra. Responda com uma única "
    "palavra: Positiva, Negativa ou Neutra."
)

PROMPT = """Você é um analista do mercado financeiro brasileiro.

{instrucao}

Manchete: "{titulo}"

Resposta:"""

MAPA_RESPOSTA = {
    "positiva": "Positive", "positivo": "Positive", "positive": "Positive",
    "negativa": "Negative", "negativo": "Negative", "negative": "Negative",
    "neutra": "Neutral", "neutro": "Neutral", "neutral": "Neutral",
}


def normalizar_resposta(txt: str) -> str | None:
    """Extrai a classe da resposta livre do modelo. None se não reconhecer."""
    t = re.sub(r"[^a-zç]", " ", str(txt).strip().lower())
    for token in t.split():
        if token in MAPA_RESPOSTA:
            return MAPA_RESPOSTA[token]
    return None


# ─── Provedores ──────────────────────────────────────────────────────────────
def classificar_anthropic(titulos, modelo="claude-sonnet-5", temperatura=0.0):
    """Requer ANTHROPIC_API_KEY e `pip install anthropic`."""
    from anthropic import Anthropic
    cli = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    saidas = []
    for i, t in enumerate(titulos, 1):
        r = cli.messages.create(
            model=modelo, max_tokens=8, temperature=temperatura,
            messages=[{"role": "user",
                       "content": PROMPT.format(instrucao=INSTRUCAO_SANTOS, titulo=t)}],
        )
        saidas.append(r.content[0].text)
        if i % 25 == 0:
            print(f"    {i}/{len(titulos)}")
        time.sleep(0.1)   # cortesia com o rate limit
    return saidas


def classificar_gemini(titulos, modelo="gemini-2.0-flash", temperatura=0.0):
    """Requer GOOGLE_API_KEY e `pip install google-generativeai`.

    Gemini 2.0-flash foi o modelo mais consistente em Teles e Figueiredo (2025)
    — acurácia acima de 70% nos três conjuntos. É o candidato natural para a
    replicação em português.
    """
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    m = genai.GenerativeModel(modelo)
    cfg = genai.types.GenerationConfig(temperature=temperatura, max_output_tokens=8)
    saidas = []
    for i, t in enumerate(titulos, 1):
        r = m.generate_content(
            PROMPT.format(instrucao=INSTRUCAO_SANTOS, titulo=t),
            generation_config=cfg)
        saidas.append(r.text)
        if i % 25 == 0:
            print(f"    {i}/{len(titulos)}")
        time.sleep(0.1)
    return saidas


PROVEDORES = {"anthropic": classificar_anthropic, "gemini": classificar_gemini}


def classificar_finbert(titulos):
    """Linha de base: o encoder de domínio que já usamos."""
    from transformers import pipeline
    pipe = pipeline("text-classification", model="lucas-leme/FinBERT-PT-BR",
                    truncation=True, max_length=512)
    id2label = {int(k): v for k, v in pipe.model.config.id2label.items()}
    if id2label != {0: "POSITIVE", 1: "NEGATIVE", 2: "NEUTRAL"}:
        raise RuntimeError(f"Mapeamento de rótulos mudou! {id2label}")
    mapa = {"POSITIVE": "Positive", "NEGATIVE": "Negative", "NEUTRAL": "Neutral"}
    return [mapa[r["label"]] for r in pipe(list(titulos), batch_size=16)]


def avaliar(y_true, y_pred, nome):
    m = {
        "modelo": nome,
        "acuracia": round(float(accuracy_score(y_true, y_pred)), 4),
        "f1_macro": round(float(f1_score(y_true, y_pred, average="macro",
                                         labels=CLASSES, zero_division=0)), 4),
        "kappa": round(float(cohen_kappa_score(y_true, y_pred, labels=CLASSES)), 4),
        "matriz_confusao": confusion_matrix(y_true, y_pred, labels=CLASSES).tolist(),
    }
    print(f"\n── {nome} ──")
    print(classification_report(y_true, y_pred, labels=CLASSES,
                                digits=3, zero_division=0))
    return m


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gabarito", type=Path, required=True)
    p.add_argument("--col-texto", default="titulo")
    p.add_argument("--col-rotulo", default="rotulo_humano")
    p.add_argument("--provedor", default="anthropic", choices=sorted(PROVEDORES))
    p.add_argument("--modelo-llm", default=None)
    p.add_argument("--repeticoes", type=int, default=1,
                   help="Repetir para medir o não determinismo do LLM. "
                        "Teles e Figueiredo (2025) não fizeram isso — é uma "
                        "melhoria nossa. Sugerido: 3.")
    p.add_argument("--saida", type=Path,
                   default=Path("conjunto_ouro/resultado_llm_vs_encoder.json"))
    args = p.parse_args()

    df = pd.read_csv(args.gabarito).dropna(subset=[args.col_texto, args.col_rotulo])
    df = df[df[args.col_rotulo].isin(CLASSES)].reset_index(drop=True)
    titulos = df[args.col_texto].astype(str).tolist()
    y_true = df[args.col_rotulo].tolist()
    print(f"Conjunto-ouro: {len(titulos)} manchetes")
    print(f"Distribuição : {Counter(y_true)}\n")

    resultados = []

    print("Classificando com o encoder de domínio (FinBERT-PT-BR)...")
    pred_fin = classificar_finbert(titulos)
    resultados.append(avaliar(y_true, pred_fin, "FinBERT-PT-BR"))
    df["pred_finbert"] = pred_fin

    fn = PROVEDORES[args.provedor]
    kwargs = {"modelo": args.modelo_llm} if args.modelo_llm else {}
    predicoes_llm = []
    for rep in range(1, args.repeticoes + 1):
        print(f"\nClassificando com o LLM ({args.provedor}) — execução {rep}/"
              f"{args.repeticoes}, temperatura 0...")
        brutas = fn(titulos, **kwargs)
        pred = [normalizar_resposta(b) for b in brutas]
        nao_reconhecidas = sum(v is None for v in pred)
        if nao_reconhecidas:
            print(f"  ⚠️  {nao_reconhecidas} respostas não reconhecidas → Neutral")
        pred = [v or "Neutral" for v in pred]
        predicoes_llm.append(pred)
        resultados.append(avaliar(y_true, pred, f"LLM {args.provedor} (exec. {rep})"))
        df[f"pred_llm_{rep}"] = pred

    # Não determinismo: mesmo com temperatura 0, LLMs podem variar entre chamadas
    if args.repeticoes > 1:
        iguais = sum(len(set(v)) == 1 for v in zip(*predicoes_llm))
        estabilidade = iguais / len(titulos)
        print(f"\nEstabilidade do LLM entre {args.repeticoes} execuções: "
              f"{estabilidade:.1%} das manchetes com resposta idêntica")
    else:
        estabilidade = None
        print("\n⚠️  Com --repeticoes 1 não é possível medir o não determinismo. "
              "Sugerido: --repeticoes 3.")

    # CSV com as predições, insumo direto do bootstrap (G12)
    csv_pred = args.saida.with_suffix(".csv")
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_pred, index=False, encoding="utf-8-sig")

    args.saida.write_text(json.dumps({
        "data": date.today().isoformat(),
        "n": len(titulos),
        "provedor_llm": args.provedor,
        "modelo_llm": args.modelo_llm or "(padrão)",
        "temperatura": 0.0,
        "repeticoes": args.repeticoes,
        "estabilidade_llm": estabilidade,
        "prompt_instrucao": INSTRUCAO_SANTOS,
        "referencia": "Teles e Figueiredo (2025) — replicado em PT-BR, com "
                      "encoder de domínio incluído",
        "resultados": resultados,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n✓ Métricas em {args.saida}")
    print(f"✓ Predições em {csv_pred}")
    print("\nPRÓXIMO PASSO OBRIGATÓRIO — confirmar significância antes de "
          "reportar qualquer superioridade:")
    print(f"  python reconstrucao_santos_bootstrap.py --predicoes {csv_pred} \\")
    print(f"      --col-verdade {args.col_rotulo} --modelos pred_finbert pred_llm_1")


if __name__ == "__main__":
    main()
