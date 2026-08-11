# -*- coding: utf-8 -*-
# =============================================================================
#  DISSERTAÇÃO PETR4 — Recálculo do Índice de Sentimento com softmax
# =============================================================================
#
#  ------------------------------------------------------------------
#  O PROBLEMA, EM LINGUAGEM COMUM
#  ------------------------------------------------------------------
#  Quando o programa lê uma manchete, ele devolve duas coisas:
#     1. a nota    -> "positiva", "negativa" ou "neutra"
#     2. a certeza -> um número entre 0 e 1 dizendo o quanto ele confia
#
#  A NOTA está correta. A CERTEZA está numa escala errada.
#
#  Por quê: o arquivo de configuração do modelo publicado tem um campo escrito
#  errado ("problem_type": "multi_label_classification"). Por causa disso, a
#  biblioteca usa uma fórmula chamada SIGMOIDE para calcular a certeza, quando
#  deveria usar outra, chamada SOFTMAX.
#
#  A diferença prática:
#    - SOFTMAX  : as certezas das três notas SOMAM 1 (100%). É uma probabilidade
#                 de verdade: "70% positiva, 20% neutra, 10% negativa".
#    - SIGMOIDE : cada nota recebe um número independente, e eles NÃO somam 1.
#                 O número existe, mas não é uma probabilidade.
#
#  Medido no conjunto-ouro: a certeza média era 0,667 pela sigmoide e seria
#  0,755 pelo softmax. O máximo era 0,856 e seria 0,939. E os rótulos coincidem
#  em 100% dos casos - por isso acurácia, F1 e kappa continuam válidos.
#
#  ------------------------------------------------------------------
#  POR QUE ISSO IMPORTA PARA A DISSERTAÇÃO
#  ------------------------------------------------------------------
#  O Índice de Sentimento da Mídia (ISM) é calculado assim:
#
#       ISM = polaridade x certeza
#
#  onde polaridade é +1 (positiva), -1 (negativa) ou 0 (neutra). Ou seja: a
#  certeza entra DIRETAMENTE na conta. Se ela está fora de escala, o índice
#  está fora de escala - e é esse índice que alimenta o GARCH e o XGBoost.
#
#  O que muda e o que NÃO muda:
#    NÃO muda -> o sinal do índice (positivo continua positivo)
#    NÃO muda -> a ordem dos dias (o dia mais otimista continua o mais otimista)
#    MUDA     -> a MAGNITUDE, e portanto a escala da série inteira
#
#  ------------------------------------------------------------------
#  ATENÇÃO: ESTE SCRIPT PRECISA DE GPU
#  ------------------------------------------------------------------
#  Para recalcular a certeza é preciso rodar o modelo de novo nas 205.697
#  notícias. O PyTorch local está inoperante (erro de DLL), então rode no Google
#  Colab. Há um modo --simular que estima o efeito sem GPU, para inspeção.
#
#  Uso:
#      python src/sentimento/recalcular_ism_softmax.py --simular    (sem GPU)
#      python src/sentimento/recalcular_ism_softmax.py              (com GPU)
# =============================================================================
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
DIR = RAIZ / "Mestrado_PETR4"
MODELO = "lucas-leme/FinBERT-PT-BR"
CLASSES = ["Negative", "Neutral", "Positive"]
POLARIDADE = {"Positive": 1, "Negative": -1, "Neutral": 0}


# ─────────────────────────────────────────────────────────────────────────────
def classificar_com_softmax(textos, lote=64):
    """Roda o modelo e devolve a distribuição de probabilidade CORRETA.

    Em vez de usar a `pipeline` (que aplica sigmoide por causa do config
    errado), pegamos os números crus da última camada — os *logits* — e
    aplicamos o softmax nós mesmos.

    Gravamos também os logits: eles permitem refazer qualquer conta depois sem
    reprocessar as 205 mil notícias, e destravam o teste de reponderação por
    prior que ficou inconclusivo por falta deles.
    """
    import torch
    import torch.nn.functional as F
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODELO)
    mod = AutoModelForSequenceClassification.from_pretrained(MODELO)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    mod.to(dev).eval()

    # confere se a ordem dos rótulos continua a mesma. É contraintuitiva
    # (0=POSITIVE, 1=NEGATIVE, 2=NEUTRAL) e mudou de sentido daria erro mudo.
    id2label = {int(k): v for k, v in mod.config.id2label.items()}
    if id2label != {0: "POSITIVE", 1: "NEGATIVE", 2: "NEUTRAL"}:
        raise RuntimeError(f"A ordem dos rotulos mudou no modelo: {id2label}")
    ordem = ["Positive", "Negative", "Neutral"]      # posições 0, 1, 2

    todos_logits = []
    for i in range(0, len(textos), lote):
        enc = tok(list(textos[i:i + lote]), truncation=True, max_length=512,
                  padding=True, return_tensors="pt").to(dev)
        with torch.no_grad():
            todos_logits.append(mod(**enc).logits.cpu())
        if (i // lote) % 100 == 0:
            print(f"    {min(i + lote, len(textos)):,}/{len(textos):,}")

    logits = torch.cat(todos_logits)
    probs = F.softmax(logits, dim=-1).numpy()
    return probs, logits.numpy(), ordem


def montar_indice(probs, ordem):
    """ISM por notícia = polaridade x probabilidade da classe escolhida."""
    idx = probs.argmax(axis=1)
    rotulo = np.array([ordem[i] for i in idx])
    certeza = probs[np.arange(len(idx)), idx]
    polaridade = np.array([POLARIDADE[r] for r in rotulo])
    return rotulo, certeza, polaridade * certeza


# ─────────────────────────────────────────────────────────────────────────────
def modo_simulacao(df: pd.DataFrame) -> dict:
    """Estima o efeito SEM GPU, a partir do que já foi medido.

    Não substitui o recálculo. Serve para dimensionar a mudança antes de
    gastar tempo de GPU, e para o texto do capítulo de método.
    """
    print("=" * 74)
    print("MODO SIMULACAO — estimativa sem GPU")
    print("=" * 74)
    print("""
Medido no conjunto-ouro (200 manchetes, no Colab):
    certeza pela SIGMOIDE (o que temos): media 0,6665   maximo 0,8558
    certeza pelo SOFTMAX  (o correto)  : media 0,7553   maximo 0,9393
    coincidencia dos rotulos           : 100%
""")
    atual = df["Score_Confianca"]
    fator = 0.7553 / 0.6665      # razão medida entre as duas escalas
    print(f"Corpus completo ({len(df):,} noticias):")
    print(f"  certeza atual (sigmoide) : media={atual.mean():.4f}  "
          f"mediana={atual.median():.4f}  maximo={atual.max():.4f}")
    print(f"  fator de correcao medido : {fator:.4f}")
    print(f"  certeza estimada (softmax): media={atual.mean()*fator:.4f}")

    ism_atual = df["Indice_Sentimento"]
    print(f"\n  ISM por noticia — atual  : media={ism_atual.mean():+.4f}  "
          f"dp={ism_atual.std():.4f}")
    print(f"  ISM por noticia — estimado: media={ism_atual.mean()*fator:+.4f}  "
          f"dp={ism_atual.std()*fator:.4f}")
    print(f"\n  >>> A escala cresce cerca de {(fator-1):.1%}.")
    print("  >>> O SINAL e a ORDEM dos dias nao mudam; so a magnitude.")
    print("  >>> Modelos que usam apenas variacao (correlacao, regressao com")
    print("  >>> intercepto) sao pouco afetados. Regras de LIMIAR sao afetadas.")
    return {"modo": "simulacao", "fator_estimado": round(fator, 4),
            "certeza_media_atual": round(float(atual.mean()), 4),
            "certeza_media_estimada": round(float(atual.mean() * fator), 4)}


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entrada", type=Path, default=DIR / "noticias_com_sentimento.csv")
    ap.add_argument("--saida", type=Path, default=DIR / "noticias_sentimento_softmax.csv")
    ap.add_argument("--saida-indice", type=Path,
                    default=DIR / "indice_sentimento_petr4_softmax.csv")
    ap.add_argument("--relatorio", type=Path, default=DIR / "recalculo_ism_softmax.json")
    ap.add_argument("--simular", action="store_true",
                    help="Estima o efeito sem rodar o modelo (nao precisa de GPU)")
    ap.add_argument("--limite", type=int, default=None,
                    help="Processa só as N primeiras — para teste rápido")
    args = ap.parse_args()

    df = pd.read_csv(args.entrada)
    print(f"Corpus: {len(df):,} noticias de {args.entrada.name}\n")

    if args.simular:
        rel = modo_simulacao(df)
        args.relatorio.write_text(json.dumps(rel, indent=2, ensure_ascii=False),
                                  encoding="utf-8")
        print(f"\n[OK] Estimativa salva em {args.relatorio}")
        return

    if args.limite:
        df = df.head(args.limite)

    col_texto = next((c for c in ("Titulo", "titulo", "Título") if c in df.columns), None)
    if col_texto is None:
        raise SystemExit(f"Coluna de titulo nao encontrada: {list(df.columns)}")

    print("Reclassificando com softmax (isto leva tempo)...")
    probs, logits, ordem = classificar_com_softmax(df[col_texto].astype(str).tolist())
    rotulo, certeza, ism = montar_indice(probs, ordem)

    # ── comparação antes/depois ──────────────────────────────────────────────
    concorda = (rotulo == df["Label_Sentimento"].values).mean()
    print(f"\n=== CONFERENCIA ===")
    print(f"  rotulos identicos aos atuais: {concorda:.2%}")
    if concorda < 0.99:
        print("  *** ATENCAO: era esperado ~100%. Investigar antes de prosseguir. ***")

    print(f"\n=== CERTEZA ===")
    print(f"  antes (sigmoide): media={df['Score_Confianca'].mean():.4f}  "
          f"maximo={df['Score_Confianca'].max():.4f}")
    print(f"  agora (softmax) : media={certeza.mean():.4f}  maximo={certeza.max():.4f}")

    print(f"\n=== ISM POR NOTICIA ===")
    print(f"  antes: media={df['Indice_Sentimento'].mean():+.4f}  "
          f"dp={df['Indice_Sentimento'].std():.4f}")
    print(f"  agora: media={ism.mean():+.4f}  dp={ism.std():.4f}")
    corr = np.corrcoef(df["Indice_Sentimento"].values, ism)[0, 1]
    print(f"  correlacao entre as duas versoes: {corr:.4f}")
    print("  (perto de 1 significa que a FORMA da serie foi preservada;")
    print("   o que muda e a ESCALA)")

    # ── grava ────────────────────────────────────────────────────────────────
    df["Label_Sentimento_softmax"] = rotulo
    df["Score_Confianca_softmax"] = certeza
    df["Indice_Sentimento_softmax"] = ism
    for j, c in enumerate(ordem):                 # guarda a distribuição inteira
        df[f"prob_{c}"] = probs[:, j]
        df[f"logit_{c}"] = logits[:, j]
    df.to_csv(args.saida, index=False, encoding="utf-8-sig")

    # ── índice diário ────────────────────────────────────────────────────────
    col_data = next((c for c in ("Data", "Data_Ajustada", "data") if c in df.columns), None)
    if col_data:
        df["_d"] = pd.to_datetime(df[col_data], errors="coerce")
        diario = (df.dropna(subset=["_d"]).groupby(df["_d"].dt.date)
                    .agg(ISM_softmax=("Indice_Sentimento_softmax", "mean"),
                         ISM_sigmoide=("Indice_Sentimento", "mean"),
                         Qtd_Noticias=("Indice_Sentimento_softmax", "size"),
                         Qtd_Positivas=("Label_Sentimento_softmax",
                                        lambda s: (s == "Positive").sum()),
                         Qtd_Negativas=("Label_Sentimento_softmax",
                                        lambda s: (s == "Negative").sum()),
                         Qtd_Neutras=("Label_Sentimento_softmax",
                                      lambda s: (s == "Neutral").sum()))
                    .reset_index().rename(columns={"_d": "Data"}))
        diario.to_csv(args.saida_indice, index=False, encoding="utf-8-sig")
        print(f"\n  indice diario: {len(diario):,} dias")
        print(f"  correlacao diaria entre as versoes: "
              f"{diario['ISM_softmax'].corr(diario['ISM_sigmoide']):.4f}")

    args.relatorio.write_text(json.dumps({
        "data_execucao": date.today().isoformat(),
        "modo": "recalculo_completo",
        "n_noticias": int(len(df)),
        "concordancia_rotulos": round(float(concorda), 4),
        "certeza": {"sigmoide_media": round(float(df["Score_Confianca"].mean()), 4),
                    "softmax_media": round(float(certeza.mean()), 4),
                    "sigmoide_max": round(float(df["Score_Confianca"].max()), 4),
                    "softmax_max": round(float(certeza.max()), 4)},
        "ism": {"sigmoide_media": round(float(df["Indice_Sentimento"].mean()), 4),
                "softmax_media": round(float(ism.mean()), 4),
                "correlacao": round(float(corr), 4)},
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n[OK] Noticias  -> {args.saida}")
    print(f"[OK] Indice    -> {args.saida_indice}")
    print(f"[OK] Relatorio -> {args.relatorio}")
    print("\nPROXIMO PASSO: refazer o Script 04 (GARCH/XGBoost) apontando para")
    print("o novo indice, e recalibrar com calibrar_ism_com_gabarito.py.")


if __name__ == "__main__":
    main()
