# Como conseguimos a hora, se a CVM não publica a hora

**Esta é a pergunta que vai ser feita amanhã.** Se a resposta não sair limpa, o
artigo inteiro fica sob suspeita. Leia esta página até o fim — são quatro passos
e você consegue explicar em dois minutos.

---

## A resposta em uma frase

> **A hora não está na planilha, mas está no recibo — e a própria planilha contém
> o número que abre o recibo.**

Não foi estimativa, não foi inferência, não foi raspagem de página. É um documento
oficial da CVM que sempre esteve público.

---

## A analogia

Pense num cartório.

O **livro de registro** anota: *"escritura lavrada em 3 de janeiro de 2018"*. Só a
data. Se você consultar só o livro, é só isso que vai encontrar.

Mas toda escritura tem um **protocolo de entrega** — o comprovante que o cartório
emite quando recebe o documento. E esse comprovante anota **a hora, o minuto e o
segundo**.

O livro não repete a hora, mas **anota o número do protocolo**. Com esse número,
você pede o comprovante e lê a hora ali.

**Foi exatamente isso que fizemos, só que com a CVM.**

---

## Os quatro passos, com dados reais

### Passo 1 — O que a planilha aberta traz

Baixamos os arquivos anuais da série IPE em `dados.cvm.gov.br`. Para um Fato
Relevante da Petrobras, a planilha traz:

| Campo | Conteúdo |
|---|---|
| Empresa | PETRÓLEO BRASILEIRO S.A. - PETROBRAS |
| Categoria | Fato Relevante |
| Assunto | Petrobras assina acordo para encerrar Class Action nos EUA |
| **Data_Entrega** | **2018-01-03** ← *só a data* |

O dicionário oficial do conjunto confirma: o campo se chama *"Data de
entrega/recebimento do documento"*. **Sem hora.**

### Passo 2 — Mas a planilha traz também um endereço

Na mesma linha há uma coluna `Link_Download`:

```
https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx
   ?Tela=ext&descTipo=IPE&CodigoInstituicao=1
   &numProtocolo=592060
   &numSequencia=134856      ← esta é a chave
   &numVersao=1
```

**Dentro do endereço há um número de sequência.** Ele identifica aquele documento
específico dentro do sistema da CVM.

### Passo 3 — Com esse número, pedimos o recibo

O sistema de consulta pública da CVM tem um método que devolve o **Protocolo de
Entrega** de qualquer documento, bastando informar esse número de sequência:

```
POST  frmConsultaExternaCVM.aspx/RetornarProtocoloPDF
      { "numeroSequencialDocumento": 134856, "tipoDocumento": "IPE" }
```

É o mesmo recibo que aparece quando alguém clica em **"Exibir Protocolo de
Entrega"** na tela de consulta da CVM. **Nada foi contornado:** a tela tem um
campo de verificação anti-robô que a própria CVM mantém **desligado**
(`hdnHabilitaCaptcha = N`).

### Passo 4 — O recibo traz a hora

A CVM devolve este documento, em texto literal:

```
Protocolo de Entrega
9512 - PETRÓLEO BRASILEIRO S.A. - PETROBRAS
O documento foi entregue para CVM e B3
Tipo de Documento: Fato Relevante
Tipo de Apresentação: Apresentação
Data do Documento: 03/01/2018
Data da Entrega: 03/01/2018 07:20:19       ← A HORA
Versão: 1
Protocolo: 009512IPE030120180104310213-17
```

**Data, hora, minuto e segundo. Emitido pela CVM.**

---

## Por que confiamos nessa hora

Três verificações foram feitas, e todas constam do artigo:

**1. As duas fontes concordam na data.** Em **100%** dos casos, a data do recibo é
a mesma da planilha aberta. Se fossem fontes diferentes de informação, haveria
divergências.

**2. A cobertura é praticamente total.** Recuperamos **20.419 recibos de 20.421
documentos** — 99,99%. Só dois não retornaram.

**3. E a prova mais forte: a hora prevê o comportamento do mercado.**

Registramos a previsão **antes** de testar: se o carimbo for verdadeiro, quem
divulga de manhã deve mover o preço **no mesmo pregão**, e quem divulga à noite,
**no seguinte**.

| Divulgado | Casos | Movimento em D0 | Movimento em D+1 | Predomina |
|---|---|---|---|---|
| até 09h59 | 1.145 | **1,640** | 1,180 | **D0** |
| 10h–16h59 | 239 | **2,099** | 1,546 | **D0** |
| 17h em diante | 3.086 | 1,092 | **1,419** | **D+1** |

A diferença entre o grupo da manhã e o da noite é de **0,786**, com valor-p de
**3 × 10⁻²³**.

> **Se a hora fosse inventada ou aproximada, esse padrão não apareceria.** Ele só
> aparece porque o carimbo diz a verdade.

---

## O que NÃO fizemos, e por que isso importa

Duas alternativas foram testadas e **descartadas**. Vale conhecê-las, porque um
professor pode sugerir exatamente uma delas.

### A alternativa ruim: o carimbo interno do PDF

Todo arquivo PDF guarda a data em que foi salvo (`ModDate`). Seria fácil usá-la.

**Mas ela mede a coisa errada:** registra quando a *empresa* fechou o arquivo, não
quando a *CVM* recebeu.

E o erro seria material. Numa amostra de 25 documentos, o carimbo do PDF indicava
que **40% das divulgações** ocorriam com o pregão aberto. O dado oficial mostra
**11,6%**.

> Teríamos concluído que o desenho do estudo era frágil, quando ele é bem apoiado.

### A alternativa limitada: a tela de consulta do RAD

A tela pública de consulta da CVM mostra data **e hora** na listagem. Funciona —
mas **só devolve documentos do exercício corrente**. Inútil para uma série que
começa em 2018.

---

## Como responder, se perguntarem

**"Mas a CVM não publica a hora."**
> "Não publica na planilha de dados abertos. Publica no Protocolo de Entrega, que
> é o recibo de cada documento. E a planilha traz o número que abre esse recibo."

**"Você estimou essa hora?"**
> "Não. É documento emitido pela CVM, com hora, minuto e segundo. Posso mostrar o
> recibo de qualquer um dos 20.419."

**"Como sei que está certa?"**
> "Por três coisas. A data do recibo bate com a da planilha em 100% dos casos.
> A cobertura é de 99,99%. E a hora prevê em qual pregão o mercado reage, com
> valor-p de 3 × 10⁻²³ — o que não aconteceria se ela fosse inventada."

**"Isso é raspagem de site? É permitido?"**
> "Não é raspagem de página. É um método de consulta que o próprio sistema da CVM
> expõe, o mesmo que a tela usa quando alguém clica em 'Exibir Protocolo de
> Entrega'. E a verificação anti-robô da tela está desligada pela própria CVM.
> Os dados são públicos por força de lei — a Resolução CVM 44 existe justamente
> para tornar essa informação pública."

---

## Se quiser demonstrar ao vivo

Rode, de dentro da pasta do projeto:

```
python Artigos/Artigo_1_O_Relogio_da_CVM/codigo/02_coletar_hora_oficial.py --limite 3
```

Ele baixa três recibos e mostra a hora de cada um. **Leva dez segundos** e é a
demonstração mais convincente que existe.
