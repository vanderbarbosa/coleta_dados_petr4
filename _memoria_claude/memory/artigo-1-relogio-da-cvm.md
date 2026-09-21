---
name: artigo-1-relogio-da-cvm
description: o Artigo 1 escrito (set/2026) — a recuperação da hora oficial da CVM, a tese, e a explicação de como a hora foi obtida
metadata:
  type: project
---

Escrito em 19/09/2026, escolhido pelo Vanderlei entre três propostas. Em
`Artigos/Artigo_1_O_Relogio_da_CVM/`. ~3.600 palavras, 6 tabelas.

**Título:** *O relógio da CVM — divulgação obrigatória e reação do preço:
evidência de 11.161 comunicados com hora oficial de entrega*

**A tese:** a presunção legal de relevância é válida em média e falsa na maioria
dos casos individuais.

**COMO A HORA FOI OBTIDA** — o Vanderlei perguntou isso e a resposta está em
`03_COMO_OBTIVEMOS_A_HORA.md`, que é o documento a ler antes de qualquer defesa:

1. a planilha IPE dos dados abertos traz só a data (o dicionário oficial confirma)
2. mas a coluna `Link_Download` contém `numSequencia=NNNNNN`
3. com esse número, o método público
   `frmConsultaExternaCVM.aspx/RetornarProtocoloPDF` devolve o **Protocolo de
   Entrega** — o recibo que a CVM emite por documento
4. o recibo traz `Data da Entrega: 03/01/2018 07:20:19`

**A hora nunca esteve escondida: não está na planilha, está no recibo, e a
planilha aponta para ele.** O captcha da tela está desligado pela própria CVM
(`hdnHabilitaCaptcha = N`); nada foi contornado.

**Três validações no artigo:** a data do recibo bate com a da planilha em 100% dos
casos; cobertura de 20.419 de 20.421; e a hora **prevê** em qual pregão o mercado
reage (p = 3e-23), o que não ocorreria se fosse inventada.

**Alternativas descartadas, documentadas na Seção 3.2:** o `ModDate` do PDF (mede
quando a EMPRESA fechou o arquivo; indicava 40% de divulgação intradiária contra
os 11,6% reais) e a tela do RAD (só exercício corrente).

**Pendências antes de submeter:** conferir paginação das referências canônicas de
método (Parkinson, Corsi, MacKinlay, Brown e Warner, Fama, Engle), que foram
arroladas de conhecimento consolidado e não verificadas na fonte; decidir idioma,
autoria, e a coautoria do Prof. Emerson, autor da medida de volatilidade relativa
à semana anterior.

Os Artigos 2 e 3 estão com material reunido e por escrever — ver
[[organizacao-do-projeto]] e [[cvm-estudo-de-evento]].
