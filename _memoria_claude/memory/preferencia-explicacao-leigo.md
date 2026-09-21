---
name: preferencia-explicacao-leigo
description: "O Vanderlei é leigo em aprendizado de máquina — explicar TUDO em linguagem comum, com analogias, sem jargão"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-10T23:04:56.439Z
---

Em 10/08/2026 o Vanderlei disse, sobre uma explicação técnica que dei: *"sou totalmente leigo, não entendi nada do que falou, sinceramente, é como se estivesse falando em grego para mim"*.

**Why:** ele é mestrando em Informática e entende de pesquisa, mas **não tem formação em aprendizado de máquina / PLN**. Termos como F1-macro, kappa, perplexidade, MLM, bootstrap, p-valor, prior shift e esquecimento catastrófico não significam nada para ele. Explicações que assumem esse vocabulário são inúteis — e ele fica sem conseguir defender o próprio trabalho.

**How to apply:**
- **Nenhum termo técnico sem explicação imediata**, na primeira vez que aparecer.
- **Usar analogias do dia a dia.** As que funcionaram: o modelo como um *funcionário contratado para ler notícias*; corpo/cabeça como *formação/função*; perplexidade como *entre quantas palavras ele hesita ao completar a frase*; bootstrap como *margem de erro de pesquisa eleitoral*; esquecimento catastrófico como *o funcionário que fez curso de vocabulário técnico e esqueceu de julgar*.
- **Todo número acompanhado do que significa.** "kappa 0,37" sozinho não diz nada; "acerto descontada a sorte, numa escala de 0 a 1" diz.
- **Explicar também o PORQUÊ de cada etapa**, não só o resultado. Ele pediu isso explicitamente.
- Ao gerar documento técnico, considerar gerar **também** uma versão em linguagem comum. Modelo que funcionou: `orientacoes/EXPLICACAO_SIMPLES_EXPERIMENTO_G3.docx` (gerado por `_gerar_docx_explicacao_leigo.py`) — história em uma página, glossário com analogias, o experimento contado como narrativa, e um glossário final de todos os termos usados nos outros documentos.
- **Não ser condescendente.** Ele entende pesquisa e método; o que falta é o vocabulário de ML.

Ver [[padrao-documentacao-dissertacao]] e [[preferencia-idioma-portugues]].
