---
name: revisao-ponderacao-confianca
description: "CORREÇÃO na dissertação: ponderar o ISM por confiança PIORA a direção (−3,57pp); os 54,93% eram número de validação, não de teste"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-17T23:48:34.684Z
---

Feito em 17/08/2026, provocado por um levantamento do Vanderlei no NotebookLM que insistia que "o sinal preditivo está na intensidade e certeza da classificação". Script: `src/sentimento/testar_ponderacao_confianca.py` → `ponderacao_confianca.json` e `ponderacao_confianca_apos17h.json`. Nova Seção 4.n da dissertação.

## A prova aritmética de que o escore NÃO é softmax
Num softmax de 3 classes a classe vencedora **não pode** ficar abaixo de 1/3 (as três somam 1, a maior é no mínimo a média). No corpus: mínimo **0,2845**, máximo 0,8729, **397 escores abaixo de 0,3333**. Confirma [[bug-problem-type-sigmoide]] por via independente e refuta a afirmação do NotebookLM.

## O reexame (recorte após-17h, o MESMO da medição original, 1.906 pregões)
| Construção | \|r\| vol | Acur. validação | Acur. TESTE |
|---|---|---|---|
| Ponderada por confiança | 0,0513 | **56,64%** | **50,31%** |
| **Polaridade pura** | 0,0503 | 53,85% | **53,88%** |
| Só alta confiança | 0,0436 | 53,50% | 53,04% |
| Saldo de votos | 0,0503 | 53,85% | 53,88% |

1. **Ponderar PIORA a direção: −3,57pp** no recorte original, −1,41pp no corpus integral. Sentido oposto ao reportado.
2. **Validação 56,64% → teste 50,31%**: queda de 6,3pp = assinatura de seleção sobre validação. Explica plausivelmente os 54,93% da tabela original.
3. **Polaridade pura ≡ saldo de votos** por identidade algébrica: média de {+1,0,−1} = (n_pos − n_neg)/n_total. A tabela original dava 54,53% e 50,30% para grandezas idênticas. ⚠️ **Código da suíte de refinamento NÃO foi preservado** — a origem da discrepância não pôde ser reconstituída.

Na volatilidade a ponderação rende +0,0084 no corpus integral (p=0,021) — real mas modesto: **+6% contra +23% do filtro de relevância**. Séries ponderada × pura correlacionam a **0,9903**.

**Why:** a dissertação afirmava que "o sinal reside na intensidade e no grau de certeza" e que o FinBERT-PT-BR fornece "escore de confiança calibrado" — o que contradizia frontalmente a própria Seção 4.j (sigmoide). Contradição interna corrigida.

**How to apply:**
- ✅ **Recalcular o ISM com softmax deixa de ser prioridade** — a ponderação quase não redistribui (r=0,9903), então a escala errada é praticamente inócua. O achado da 4.j vale como alerta a terceiros, não como ameaça às conclusões.
- Manter a construção ponderada por continuidade, mas **sem lhe atribuir mérito**.
- Terceiro ponto de apoio para o padrão: corpus +23% > agregação +6% > modelo 0%.

## Sobre o NotebookLM (avaliação em `orientacoes/AVALIACAO_NOTEBOOKLM.md`)
⚠️ **Ele leu um PDF DESATUALIZADO.** Devolveu como "recomendações": zona morta, filtro de relevância, quantílica, parcimônia, regra das 17h — tudo já no texto. Pior: recomendou "rotular 500–1000 e ajustar BERTimbau-large", frase que **removemos** por contradizer o G3. **Reenviar o PDF atual antes de nova consulta.**

Erros: (a) diz 1,6 milhão de sentenças no corpus do Santos — o cartão do modelo diz **1,4 milhão**, o nosso número está certo; (b) afirma que o escore é softmax — refutado acima.

**O que valeu:** duas fontes citantes novas e verificadas — **Pinheiro, Muinhos & Fernandes** (Fiscal Sentiment Index FSI-BR → curva de juros) e **Costa Neto & Anjos** (USP/FIPECAFI, 25.804 notas explicativas, dimensões Boilerplateness/Completeness/Density).

## 💡 A MELHOR IDEIA: usar embeddings, não a cabeça de sentimento
As duas fontes novas usam o FinBERT-PT-BR como **extrator de embeddings + K-means**, não como classificador. **Todos os nossos problemas estão na cabeça de sentimento** — viés de 87%, teto 0,58, sigmoide, zero pregões positivos, erro no Neutro. **Nenhum afeta os embeddings**, que vêm da parte adaptada com 1,4 milhão de textos. É linha nova que **contorna** em vez de consertar o componente que resistiu a nove intervenções.

⚠️ Ao reivindicar originalidade: dizer "original para o mercado brasileiro e ativo individual em português". Em inglês há dois trabalhos equivalentes ([[encoders-ingles-levantamento]]) e a banca pode apresentá-los.

Ver [[bug-problem-type-sigmoide]], [[filtro-relevancia-primeiro-ganho]], [[encoders-ingles-levantamento]] e [[efeito-de-cauda-auditoria-noticia]].
