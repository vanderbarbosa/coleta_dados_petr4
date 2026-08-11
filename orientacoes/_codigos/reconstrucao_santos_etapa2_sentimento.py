# -*- coding: utf-8 -*-
# =============================================================================
#  RECONSTRUÇÃO — Etapa 2 de Santos, Bianchi e Costa (2023)
#  Classificador de sentimento com GRADUAL UNFREEZING
# =============================================================================
#
#  ⚠️  ORIGEM DESTE CÓDIGO
#  Reconstrução — o código original NÃO foi publicado. Escrito a partir do
#  artigo do BWAIF (Seção 3.2) e da monografia (Seção 4.2.4).
#
#  Hiperparâmetros replicados de Santos:
#    • técnica ........................ gradual unfreezing das camadas de encoder
#    • taxa de aprendizado ............ 5e-6   (uma ordem abaixo do usual)
#    • épocas ......................... 11
#    • validação ...................... cruzada, 5 folds, sobre 70% da base
#    • teste .......................... 30% restantes
#    • cabeça ......................... sobre a 1ª dimensão de saída ([CLS])
#
#  ---------------------------------------------------------------------------
#  POR QUE ISTO EXISTE
#  Nossos experimentos de encoder (BERTimbau base/large e Albertina-100M,
#  jul/2026) usaram 3 ÉPOCAS, SEM gradual unfreezing e SEM adaptação de domínio
#  prévia. O resultado foi o colapso para a classe majoritária — kappa 0,000 em
#  3 dos 5 folds do Albertina, F1-macro de 25–29% (ver experimentos_encoder/
#  log_albertina.txt). Este script corrige o protocolo.
#
#  ⚠️  DEPENDE DE RÓTULO. A rotulagem manual está suspensa por orientação do
#  Prof. Emerson (29/07/2026). Rodar apenas sobre o conjunto-ouro JÁ EXISTENTE
#  (300 manchetes), e com a ressalva de que o gabarito tem anotador único e,
#  portanto, nenhuma métrica de concordância (ver gap G5).
# =============================================================================
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# ─── Hiperparâmetros de Santos ──────────────────────────────────────────────
TAXA_APRENDIZADO = 5e-6   # Santos, Seção 3.2 — evita esquecimento catastrófico
EPOCAS = 11               # Santos: 11 épocas
N_FOLDS = 5               # validação cruzada com 5 divisões
FRACAO_TREINO = 0.70      # 70% treino+validação, 30% teste
BATCH_SIZE = 16
MAX_TOKENS = 512

# Ordem de rótulos do FinBERT-PT-BR — CONTRAINTUITIVA, conferir sempre.
# id2label = {0: POSITIVE, 1: NEGATIVE, 2: NEUTRAL}
ROTULOS = {"Positive": 0, "Negative": 1, "Neutral": 2}


class ConjuntoManchetes(Dataset):
    def __init__(self, textos, rotulos, tokenizer):
        self.enc = tokenizer(list(textos), truncation=True, max_length=MAX_TOKENS,
                             padding="max_length", return_tensors="pt")
        self.y = torch.tensor(list(rotulos), dtype=torch.long)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        item = {k: v[i] for k, v in self.enc.items()}
        item["labels"] = self.y[i]
        return item


# ─── O núcleo do método: gradual unfreezing ─────────────────────────────────
def _blocos_encoder(model):
    """Devolve a lista de camadas do encoder, seja BERT ou DeBERTa."""
    base = getattr(model, "bert", None) or getattr(model, "deberta", None)
    if base is None:
        base = model.base_model
    return base


def congelar_tudo(model) -> None:
    """Congela embeddings e todas as camadas de encoder. Só a cabeça treina."""
    base = _blocos_encoder(model)
    for p in base.parameters():
        p.requires_grad = False


def descongelar_ate(model, n: int) -> None:
    """Libera as `n` camadas SUPERIORES do encoder.

    Santos aplicou a técnica sobre as 11 camadas de encoder, liberando-as
    gradativamente ao longo das 11 épocas. A intuição: as camadas superiores
    codificam informação mais específica da tarefa e podem ser ajustadas antes;
    as inferiores guardam a linguagem geral e devem ser preservadas mais tempo.
    """
    camadas = _blocos_encoder(model).encoder.layer
    n = min(n, len(camadas))
    for layer in camadas[len(camadas) - n:]:
        for p in layer.parameters():
            p.requires_grad = True


def treinar_fold(nome_modelo, X_tr, y_tr, X_val, y_val, tokenizer, device):
    """Treina um fold com gradual unfreezing e devolve o modelo de menor loss.

    ⚠️ problem_type="single_label_classification" é obrigatório: o config.json
    publicado do FinBERT-PT-BR declara "multi_label_classification", o que faz o
    modelo usar BCEWithLogitsLoss e esperar alvos [batch, 3] em vez de [batch].
    Sem isso o treino falha com "Target size must be the same as input size".
    """
    model = AutoModelForSequenceClassification.from_pretrained(
        nome_modelo, num_labels=3, ignore_mismatched_sizes=True,
        problem_type="single_label_classification").to(device)
    congelar_tudo(model)

    dl_tr = DataLoader(ConjuntoManchetes(X_tr, y_tr, tokenizer),
                       batch_size=BATCH_SIZE, shuffle=True)
    dl_val = DataLoader(ConjuntoManchetes(X_val, y_val, tokenizer),
                        batch_size=BATCH_SIZE)

    melhor_loss, melhor_estado = float("inf"), None

    for epoca in range(EPOCAS):
        # uma camada a mais liberada por época — o "gradual" do gradual unfreezing
        descongelar_ate(model, n=epoca + 1)
        otim = torch.optim.AdamW(
            [p for p in model.parameters() if p.requires_grad],
            lr=TAXA_APRENDIZADO)

        model.train()
        for lote in dl_tr:
            lote = {k: v.to(device) for k, v in lote.items()}
            otim.zero_grad()
            saida = model(**lote)
            saida.loss.backward()
            otim.step()

        model.eval()
        perdas = []
        with torch.no_grad():
            for lote in dl_val:
                lote = {k: v.to(device) for k, v in lote.items()}
                perdas.append(model(**lote).loss.item())
        loss_val = float(np.mean(perdas))
        print(f"    época {epoca + 1:2d}/{EPOCAS} | camadas liberadas: "
              f"{epoca + 1:2d} | loss_val={loss_val:.4f}")

        # Santos: "o modelo com a melhor convergência (mínima função de custo)
        # da validação foi utilizado para classificar a base de teste"
        if loss_val < melhor_loss:
            melhor_loss = loss_val
            melhor_estado = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    model.load_state_dict(melhor_estado)
    return model, melhor_loss


def prever(model, X, tokenizer, device):
    dl = DataLoader(ConjuntoManchetes(X, [0] * len(X), tokenizer), batch_size=BATCH_SIZE)
    model.eval()
    preds = []
    with torch.no_grad():
        for lote in dl:
            lote.pop("labels")
            lote = {k: v.to(device) for k, v in lote.items()}
            preds.extend(model(**lote).logits.argmax(-1).cpu().tolist())
    return np.array(preds)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gabarito", type=Path, required=True,
                   help="CSV do conjunto-ouro (coluna de texto + coluna de rótulo humano)")
    p.add_argument("--col-texto", default="titulo")
    p.add_argument("--col-rotulo", default="rotulo_humano")
    p.add_argument("--modelo", default="lucas-leme/FinBERT-PT-BR")
    p.add_argument("--saida", type=Path, default=Path("experimentos_encoder"))
    args = p.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Dispositivo: {device}")
    if device == "cpu":
        print("⚠️  Em CPU isso leva horas. Preferir Colab com GPU.")

    df = pd.read_csv(args.gabarito).dropna(subset=[args.col_texto, args.col_rotulo])
    df["y"] = df[args.col_rotulo].map(ROTULOS)
    df = df.dropna(subset=["y"])
    X, y = df[args.col_texto].values, df["y"].astype(int).values
    print(f"Conjunto-ouro: {len(X)} manchetes | distribuição: "
          f"{pd.Series(y).value_counts().to_dict()}")

    # 70/30 estratificado, como Santos
    X_dev, X_te, y_dev, y_te = train_test_split(
        X, y, train_size=FRACAO_TREINO, stratify=y, random_state=42)

    tokenizer = AutoTokenizer.from_pretrained(args.modelo)
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)

    melhor_global, melhor_loss_global = None, float("inf")
    for i, (idx_tr, idx_val) in enumerate(skf.split(X_dev, y_dev), 1):
        print(f"\n  fold {i}/{N_FOLDS}")
        model, loss = treinar_fold(args.modelo, X_dev[idx_tr], y_dev[idx_tr],
                                   X_dev[idx_val], y_dev[idx_val], tokenizer, device)
        if loss < melhor_loss_global:
            melhor_loss_global, melhor_global = loss, model

    # avaliação final no conjunto de teste, nunca visto
    y_pred = prever(melhor_global, X_te, tokenizer, device)
    metricas = {
        "acuracia": round(float(accuracy_score(y_te, y_pred)), 4),
        "f1_macro": round(float(f1_score(y_te, y_pred, average="macro")), 4),
        "kappa": round(float(cohen_kappa_score(y_te, y_pred)), 4),
    }
    print(f"\nTESTE (30%): {metricas}")
    print("Referência Santos (notícias gerais): acurácia 0,76 | F1 0,73")
    print("Referência nossa (FinBERT sem retreino, 300 manchetes): 0,58 | κ 0,371")

    args.saida.mkdir(parents=True, exist_ok=True)
    destino = args.saida / f"gradual_unfreezing_{date.today().isoformat()}.json"
    destino.write_text(json.dumps({
        "data": date.today().isoformat(),
        "modelo": args.modelo,
        "n_total": len(X), "n_teste": len(X_te),
        "hiperparametros": {"lr": TAXA_APRENDIZADO, "epocas": EPOCAS,
                            "folds": N_FOLDS, "gradual_unfreezing": True},
        "metricas_teste": metricas,
        "melhor_loss_validacao": round(melhor_loss_global, 4),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✓ Salvo em {destino}")


if __name__ == "__main__":
    main()
