# -*- coding: utf-8 -*-
# ==============================================================================
#   DISSERTAÇÃO PETR4 — Avaliação do FinBERT-PT-BR contra o conjunto-ouro
#   Autor: Vanderlei Barbosa da Silva | Orientador: Prof. Dr. Julio Cesar Nievola
#
#   Lê a planilha JÁ ROTULADA (conjunto_ouro_para_rotular.xlsx) e o gabarito do
#   modelo, e compara o rótulo HUMANO com o do FinBERT-PT-BR, produzindo:
#     - Acurácia bruta e acurácia REPONDERADA à população (via peso amostral)
#     - Kappa de Cohen (concordância além do acaso) — exigência da banca
#     - Precisão/revocação/F1 por classe e matriz de confusão
#   Saída: Mestrado_PETR4/conjunto_ouro/relatorio_validacao_ouro.txt
#
#   Execute SOMENTE após terminar a rotulagem manual da planilha.
# ==============================================================================

import sys
from pathlib import Path
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "Mestrado_PETR4" / "conjunto_ouro"

from sklearn.metrics import (cohen_kappa_score, confusion_matrix,
                             classification_report, accuracy_score)

MAPA_PT = {"Positivo": "Positive", "Negativo": "Negative", "Neutro": "Neutral"}
ORDEM = ["Negative", "Neutral", "Positive"]

# ── Carga ─────────────────────────────────────────────────────────────────────
rot = pd.read_excel(SAIDA / "conjunto_ouro_para_rotular.xlsx", sheet_name="Rotular")
gab = pd.read_csv(SAIDA / "conjunto_ouro_gabarito_modelo.csv")
df = rot.merge(gab, on="ID_OURO", how="inner")

# considera apenas linhas rotuladas
df = df[df["Sentimento_Humano"].notna() & (df["Sentimento_Humano"].astype(str).str.strip() != "")]
if len(df) == 0:
    print("Nenhuma linha rotulada ainda. Rotule a aba 'Rotular' e rode novamente.")
    sys.exit(0)

df["humano"] = df["Sentimento_Humano"].map(MAPA_PT)
df = df[df["humano"].notna()]
y_humano = df["humano"].values
y_modelo = df["Label_Sentimento"].values

# ── Métricas ──────────────────────────────────────────────────────────────────
acc = accuracy_score(y_humano, y_modelo) * 100
# acurácia reponderada à população (a amostra superrepresenta a classe minoritária)
acerto = (y_humano == y_modelo).astype(float)
peso = df["peso_amostral"].values
acc_pop = float(np.sum(acerto * peso) / np.sum(peso)) * 100
kappa = cohen_kappa_score(y_humano, y_modelo)
cm = confusion_matrix(y_humano, y_modelo, labels=ORDEM)
rep = classification_report(y_humano, y_modelo, labels=ORDEM, digits=3, zero_division=0)

# concordância da relevância (se rotulada)
rel_txt = ""
if "Relevante_PETR4" in df.columns and df["Relevante_PETR4"].notna().any():
    rel = df["Relevante_PETR4"].astype(str).str.strip()
    n_rel = (rel == "Sim").sum(); n_tot = (rel.isin(["Sim", "Não"])).sum()
    if n_tot:
        rel_txt = f"\nRelevância humana: {n_rel}/{n_tot} notícias marcadas como relevantes à PETR4 ({n_rel/n_tot*100:.1f}%)."

def interpreta_kappa(k):
    if k < 0:    return "ruim (pior que o acaso)"
    if k < 0.20: return "leve"
    if k < 0.40: return "razoável (fair)"
    if k < 0.60: return "moderada"
    if k < 0.80: return "substancial"
    return "quase perfeita"

# ── Relatório ─────────────────────────────────────────────────────────────────
linhas = []
linhas.append("=" * 70)
linhas.append("VALIDAÇÃO DO FinBERT-PT-BR CONTRA O CONJUNTO-OURO (rótulo humano)")
linhas.append("=" * 70)
linhas.append(f"Notícias rotuladas avaliadas: {len(df)} de {len(rot)}")
linhas.append("")
linhas.append(f"Acurácia (bruta, na amostra) ....... {acc:6.2f}%")
linhas.append(f"Acurácia (reponderada à população) . {acc_pop:6.2f}%")
linhas.append(f"Kappa de Cohen ..................... {kappa:6.3f}  -> concordância {interpreta_kappa(kappa)}")
linhas.append(rel_txt)
linhas.append("")
linhas.append("Matriz de confusão (linhas = humano, colunas = modelo):")
linhas.append("            " + "  ".join(f"{c:>9s}" for c in ORDEM))
for i, c in enumerate(ORDEM):
    linhas.append(f"{c:>10s}  " + "  ".join(f"{cm[i,j]:9d}" for j in range(len(ORDEM))))
linhas.append("")
linhas.append("Relatório por classe (modelo vs. humano):")
linhas.append(rep)
linhas.append("")
linhas.append("Nota metodológica: a amostra é estratificada com piso para a classe")
linhas.append("minoritária (Positivo); por isso a acurácia BRUTA difere da REPONDERADA")
linhas.append("à população. Reporte ambas, destacando a reponderada como estimativa")
linhas.append("não enviesada do desempenho no corpus completo.")

texto = "\n".join(linhas)
print(texto)
(SAIDA / "relatorio_validacao_ouro.txt").write_text(texto, encoding="utf-8")
print(f"\n[OK] Relatório salvo em: {SAIDA / 'relatorio_validacao_ouro.txt'}")
