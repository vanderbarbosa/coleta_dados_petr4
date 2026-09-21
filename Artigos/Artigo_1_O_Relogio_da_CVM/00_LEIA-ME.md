# Artigo 1 — O relógio da CVM

**Divulgação obrigatória e reação do preço: evidência de 11.161 comunicados com
hora oficial de entrega**

## O que ler primeiro

| Arquivo | Para quê |
|---|---|
| **`03_COMO_OBTIVEMOS_A_HORA.md`** | **a pergunta que vão fazer.** Leia antes da reunião |
| `01_ARTIGO.docx` | o artigo completo, ~3.600 palavras |
| `02_EXPLICACAO_SIMPLES.md` | o artigo em linguagem comum |
| `fontes/` | os documentos de apoio que deram origem ao artigo |
| `dados/` | os números, em JSON e CSV, que sustentam cada tabela |
| `codigo/` | os seis scripts, na ordem em que rodam |

## A contribuição

O conjunto de dados abertos da CVM registra apenas a **data** de entrega.
Recuperamos a **hora oficial** de 20.419 documentos, com precisão de segundos, a
partir do Protocolo de Entrega emitido pela própria autarquia.

Isso viabiliza o desenho central: isolar o que foi divulgado **com o mercado
fechado** e observar o pregão seguinte, quando a informação pôde ser negociada
pela primeira vez.

## Os números

| | |
|---|---|
| documentos com hora oficial | 20.419 de 20.421 |
| eventos analisados | 11.161 |
| papéis | 56 |
| período | jan/2018 a ago/2026 |
| pregões de controle | 105.896 |

| Achado | Valor | valor-p |
|---|---|---|
| volatilidade | +9,6% | 7 × 10⁻⁵⁵ |
| volume | +16,5% | 4 × 10⁻⁶² |
| direção | nulo | 0,74 |
| Fato Relevante × Comunicado | 2,6× | 7 × 10⁻¹⁸ |
| **não movem o preço** | **59,0%** | — |

## O que falta antes de submeter

- [ ] conferir volume, número e paginação das **referências canônicas** de método
      (Parkinson, Corsi, MacKinlay, Brown e Warner, Fama, Engle)
- [ ] decidir idioma — português (revista nacional) ou inglês (*Finance Research
      Letters*)
- [ ] decidir autoria e ordem de assinatura
- [ ] decidir sobre a coautoria do Prof. Emerson, autor da medida de volatilidade
      relativa à semana anterior
