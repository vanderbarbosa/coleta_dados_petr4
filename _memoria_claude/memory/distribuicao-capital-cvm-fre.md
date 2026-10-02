---
name: distribuicao-capital-cvm-fre
description: fonte nova — Formulário de Referência (FRE) da CVM dá, por empresa, quantos acionistas (PF/PJ/institucional) e quantas ações em circulação, 2018-2026
metadata:
  type: project
---

**01-02/10/2026.** Pedido do Prof. Julio: "quantidade de ações por investidor" e
"investidores por ação", para medir quantas pessoas uma divulgação afeta.
Vasculhei o projeto inteiro — não havia essa informação em lugar nenhum (a
coleta da CVM só trouxe metadados do comunicado, nunca dado cadastral).

**Fonte encontrada e verificada por download direto** (não por resumo de
busca, que trouxe um número suspeito e só depois confirmei baixando o dado):
`dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_{ano}.zip` —
mesmo portal já usado para os Fatos Relevantes (IPE). Dentro do zip, o
arquivo `fre_cia_aberta_distribuicao_capital_{ano}.csv` traz, por empresa e
data da última assembleia: `Quantidade_Acionistas_PF`, `_PJ`,
`_Investidores_Institucionais`, `Quantidade_Acoes_Ordinarias/Preferenciais/
Total_Circulacao`. Confirmado estável de 2018 a 2026 (mesmas colunas). Há
também `fre_cia_aberta_posicao_acionaria_{ano}.csv`, com os acionistas
relevantes nominalmente (controlador, BNDESPAR etc.), não usado ainda.

**Limitação da própria norma, não da coleta:** a CVM separa as AÇÕES por
classe (ON × PN) mas NÃO separa a CONTAGEM DE ACIONISTAS por classe — o total
de acionistas é da empresa inteira. Não dá para saber quantos acionistas são
"só de PETR4" (PN) vs "só de PETR3" (ON). Também é dado por assembleia
(~1x/ano), não por pregão.

**Coletado para os 62 papéis já mapeados no projeto** (mesmo CNPJ→Ticker do
Artigo 1): `CVM/21_coletar_distribuicao_capital.py` →
`CVM/dados/distribuicao_capital_papeis.csv` (675 linhas, 2018-2026,
gitignored — csv grande) + `distribuicao_capital_resumo.json` (leve, no git).

**PETR4 em números (acionistas / ações-PN em circulação / ações por
acionista):** 2018: 336.071 / 4,33 bi / 20.951 · 2024: 913.200 / 4,41 bi /
8.644 · 2026: 1.183.775 / 4,41 bi / **6.665**. O número de acionistas quase
quadruplicou desde 2018; as ações em circulação quase não mudaram — mais
gente dividindo o mesmo bolo. Bateu exatamente com a imprensa ("Petrobras
atinge 1 milhão de acionistas").

**Achado de qualidade de dado, não corrigido:** a linha de ASAI3 (Assaí),
data-base 2024-12-31, traz `Quantidade_Acionistas_PJ = 6.265.129` — maior que
o total de ações da empresa, logo impossível. É erro de preenchimento da
própria companhia no FRE, replicado como está — não inventei correção.

**Entregue em planilha:** `Mentorias/2026-09-16_Emerson_e_Julio/
16_Distribuicao_de_Capital.xlsx` (3 abas: Resumo 62 papéis, série histórica
PETR4, todos os papéis). Reaproveitado depois em
[[comparativo-top10-ibovespa]] para os 10 papéis do Ibovespa.

**Why:** fecha o item 1 do pedido do Prof. Julio de 30/09/2026, com dado
público verificável, sem fabricar número algum.

**How to apply:** se pedirem o mesmo para outro papel, `21_coletar_
distribuicao_capital.py` já cobre os 62 CNPJs mapeados — só rodar de novo com
os anos atualizados. Para papel fora desses 62, precisa mapear o CNPJ antes
(ver `cvm_comunicados_2018_2026.csv`).
