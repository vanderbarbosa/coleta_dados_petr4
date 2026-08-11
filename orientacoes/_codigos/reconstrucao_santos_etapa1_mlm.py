# -*- coding: utf-8 -*-
# =============================================================================
#  RECONSTRUÇÃO — Etapa 1 de Santos, Bianchi e Costa (2023)
#  Adaptação de domínio por Masked Language Modeling (MLM)
# =============================================================================
#
#  ⚠️  ORIGEM DESTE CÓDIGO
#  Este NÃO é o código original dos autores. O código de treinamento do
#  FinBERT-PT-BR NÃO foi publicado (verificado em 04/08/2026 no GitHub pessoal
#  do autor, na organização turing-usp e no repositório HuggingFace).
#
#  Esta é uma RECONSTRUÇÃO FIEL, escrita a partir dos hiperparâmetros
#  documentados no artigo do BWAIF (Seção 3.1) e na monografia (Seção 4.2.2),
#  e já adaptada ao corpus da nossa dissertação (~205 mil notícias de PETR4).
#
#  Hiperparâmetros replicados de Santos:
#    • probabilidade de máscara ....... 15%    (Devlin et al., 2018)
#    • taxa de aprendizado ............ 2e-5   (Sun et al., 2019)
#    • batch size ..................... 16     (limitação de GPU)
#    • épocas ......................... 2
#    • limite de tokens ............... 512
#    • métrica ........................ perplexidade (Chen et al., 1998)
#
#  Referência de resultado: BERTimbau 1,51 → FinBERT-PT-BR 1,24 (ganho ~18%)
#
#  ---------------------------------------------------------------------------
#  POR QUE ESTE EXPERIMENTO IMPORTA (gap G3)
#  É *self-supervised*: NÃO consome um único rótulo humano. É, portanto, a
#  única frente técnica substantiva que pode avançar enquanto a rotulagem
#  manual estiver suspensa por orientação do Prof. Emerson (mentoria 29/07/26).
#  A perplexidade é métrica intrínseca — não depende do conjunto-ouro.
#
#  ONDE RODAR
#  O PyTorch local está inoperante (WinError 1114 / c10.dll). Rodar no Google
#  Colab com GPU, que é o ambiente para o qual a maior parte do pipeline já
#  foi escrita — e é o mesmo tipo de ambiente usado por Santos (Kaggle 2×T4).
# =============================================================================
from __future__ import annotations

import argparse
import json
import math
from datetime import date
from pathlib import Path

import pandas as pd
from datasets import Dataset
from transformers import (
    AutoModelForMaskedLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

# ─── Hiperparâmetros de Santos (não alterar sem justificar na dissertação) ───
PROB_MASCARA = 0.15      # Devlin et al. (2018)
TAXA_APRENDIZADO = 2e-5  # Sun et al. (2019)
BATCH_SIZE = 16          # limitação de alocação do modelo + textos na GPU
EPOCAS = 2               # Santos: 2 épocas em 11 h sobre 1,4 milhão de textos
MAX_TOKENS = 512         # limite da arquitetura BERT

# ─── Candidatos a modelo de partida ─────────────────────────────────────────
#   (1) lucas-leme/FinBERT-PT-BR ...... já é financeiro; MENOS limpo, porque o
#       artefato publicado é o CLASSIFICADOR (BertForSequenceClassification) e
#       não o modelo de linguagem puro — a cabeça de MLM será reinicializada.
#   (2) neuralmind/bert-large-portuguese-cased ... replica fielmente a receita
#       de Santos (partir de um BERTimbau), em porte maior.
#   Rodar AS DUAS: a comparação entre elas é, ela própria, um resultado.
MODELOS = {
    "finbert": "lucas-leme/FinBERT-PT-BR",
    "bertimbau-large": "neuralmind/bert-large-portuguese-cased",
    "bertimbau-base": "neuralmind/bert-base-portuguese-cased",
}


def carregar_corpus(caminho_csv: Path, coluna: str) -> pd.DataFrame:
    """Lê o corpus de notícias e remove vazios e duplicatas.

    A limpeza de Santos (regex para textos malformados, caracteres especiais e
    código-fonte) não foi publicada; a nossa base já passou pela filtragem do
    Script 02c, então aqui fazemos apenas o saneamento mínimo.
    """
    df = pd.read_csv(caminho_csv)
    if coluna not in df.columns:
        raise KeyError(f"Coluna '{coluna}' ausente. Disponíveis: {list(df.columns)}")
    df = df[[coluna]].dropna().drop_duplicates()
    df[coluna] = df[coluna].astype(str).str.strip()
    return df[df[coluna].str.len() >= 20].reset_index(drop=True)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--corpus", type=Path, required=True,
                   help="CSV com as notícias (ex.: base_textual_petr4_wordpress_2016_2026.csv)")
    p.add_argument("--coluna", default="titulo", help="Coluna de texto a usar")
    p.add_argument("--modelo", default="finbert", choices=sorted(MODELOS),
                   help="Modelo de partida")
    p.add_argument("--saida", type=Path, default=Path("modelos/finbert-petr4"))
    p.add_argument("--n-holdout", type=int, default=10_000,
                   help="Textos reservados para medir perplexidade (Santos usou 100 mil)")
    p.add_argument("--limite", type=int, default=None,
                   help="Limita o corpus — útil para um teste rápido antes da rodada cheia")
    args = p.parse_args()

    nome_modelo = MODELOS[args.modelo]
    print(f"Modelo de partida : {nome_modelo}")

    df = carregar_corpus(args.corpus, args.coluna)
    if args.limite:
        df = df.head(args.limite)
    print(f"Corpus            : {len(df):,} textos")

    tokenizer = AutoTokenizer.from_pretrained(nome_modelo)
    # AutoModelForMaskedLM descarta a cabeça de classificação (quando existir)
    # e inicializa uma cabeça de MLM — é o passo que permite partir do
    # classificador publicado. O aviso de "newly initialized" é esperado AQUI.
    model = AutoModelForMaskedLM.from_pretrained(nome_modelo)

    ds = Dataset.from_pandas(df.rename(columns={args.coluna: "text"}))
    ds = ds.train_test_split(test_size=min(args.n_holdout, len(ds) // 5), seed=42)

    def tokenizar(lote):
        # truncation=True aplica o filtro de 512 tokens de Santos; ele descartou
        # os textos mais longos, nós truncamos — manchetes raramente passam disso
        return tokenizer(lote["text"], truncation=True, max_length=MAX_TOKENS)

    ds = ds.map(tokenizar, batched=True, remove_columns=["text"],
                desc="Tokenizando")

    collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=True, mlm_probability=PROB_MASCARA)

    args_treino = TrainingArguments(
        output_dir=str(args.saida),
        learning_rate=TAXA_APRENDIZADO,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        num_train_epochs=EPOCAS,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=200,
        fp16=True,               # acelera bastante em T4/A100
        report_to=[],            # Santos usou wandb; deixamos desligado por padrão
        dataloader_num_workers=2,
        # Santos precisou de alocação dinâmica de memória com 1,4 milhão de
        # textos e 30 GB de RAM. Com ~205 mil textos isso não é necessário;
        # se o corpus crescer, trocar por load_dataset(..., streaming=True).
    )

    trainer = Trainer(
        model=model,
        args=args_treino,
        train_dataset=ds["train"],
        eval_dataset=ds["test"],
        data_collator=collator,
    )

    # ─── Perplexidade ANTES (linha de base do modelo de partida) ─────────────
    ppl_antes = math.exp(trainer.evaluate()["eval_loss"])
    print(f"Perplexidade ANTES : {ppl_antes:.4f}")

    trainer.train()

    # ─── Perplexidade DEPOIS ────────────────────────────────────────────────
    ppl_depois = math.exp(trainer.evaluate()["eval_loss"])
    print(f"Perplexidade DEPOIS: {ppl_depois:.4f}")
    print(f"Ganho relativo     : {(ppl_antes - ppl_depois) / ppl_antes:.2%}")

    args.saida.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(args.saida))
    tokenizer.save_pretrained(str(args.saida))

    resultado = {
        "data": date.today().isoformat(),
        "modelo_partida": nome_modelo,
        "n_textos": len(df),
        "n_holdout": len(ds["test"]),
        "hiperparametros": {
            "mlm_probability": PROB_MASCARA,
            "learning_rate": TAXA_APRENDIZADO,
            "batch_size": BATCH_SIZE,
            "epocas": EPOCAS,
            "max_tokens": MAX_TOKENS,
        },
        "perplexidade_antes": round(ppl_antes, 4),
        "perplexidade_depois": round(ppl_depois, 4),
        "ganho_relativo": round((ppl_antes - ppl_depois) / ppl_antes, 4),
        "referencia_santos": {"bertimbau": 1.51, "finbert_pt_br": 1.24},
    }
    (args.saida / "resultado_mlm.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✓ Modelo e resultado salvos em {args.saida}")


if __name__ == "__main__":
    main()
