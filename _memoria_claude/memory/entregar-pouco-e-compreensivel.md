---
name: entregar-pouco-e-compreensivel
description: 23/10/2026 — "não consegui compreender para explicar para eles"; material correto mas ilegível não serve. Menos peças, adversário explicado antes do número, analogia antes do jargão
metadata:
  type: feedback
---

**23/10/2026.** O Vanderlei escreveu: *"sei que fizemos boa parte do que está
sendo pedido mas professores pediram para revisar tudo (...) pois **eu não
consegui compreender para explicar para eles os resultados**."*

**Isso é retorno sobre o MEU trabalho, não sobre o dele.** Os números estavam
certos e conferidos; o problema foi a forma de entregar. O que eu vinha
fazendo e que causou isso:

- **Peças demais por assunto.** Documento completo + documento resumido +
  planilha + leia-me, por mentoria. Somando as mentorias, virou mais do que
  qualquer pessoa lê antes de uma reunião.
- **Réguas de comparação demais no mesmo lugar.** Classe majoritária, régua
  ancorada, ingênua diária e buy-and-hold convivendo nas mesmas tabelas, sem
  o leitor saber qual vale para qual pergunta.
- **Números sem tradução.** "R²-OS de −532%" não significa nada para quem não
  é da área, e eu os apresentava antes de explicar contra o que estavam sendo
  medidos.
- **Seis braços de modelo lado a lado**, quando a pergunta tinha duas pontas.

**O que funcionou, e deve virar padrão:**

1. **Explicar quem é quem ANTES do resultado**, com analogia: o FinBERT é o
   leitor; o GARCH é o meteorologista (não diz se chove, diz se o tempo está
   instável); o SVM/XGBoost são os apostadores; o Prophet é quem traça a reta
   com a régua. Ver [[preferencia-explicacao-leigo]].
2. **Explicar o adversário antes de mostrar o placar.** "Acertou 52%" não quer
   dizer nada sozinho — se o palpite fixo acerta 53%, o modelo perdeu. Essa
   frase sozinha destrava a leitura de todas as tabelas de direção.
3. **Uma aba "O placar"**: três perguntas, três respostas de uma linha, e
   onde conferir cada uma. O detalhe vem depois, não antes.
4. **Traduzir "melhorou em 5 de 10" como "é o que uma moeda produziria".**
   Foi a frase que tornou o resultado nulo compreensível de imediato.
5. **CORTAR material.** Nesta mentoria deixei de fazer o documento técnico
   que normalmente faria, e disse por quê. Duas peças (leia-me + explicação +
   planilha) em vez de quatro.

**Why:** entrega que ele não consegue explicar ao orientador não cumpriu a
função, por mais correta que esteja. O destinatário real do material é a
conversa dele com Emerson e Julio, não o arquivo.

**How to apply:** antes de fechar qualquer entrega, perguntar: *ele consegue
abrir isto e explicar em voz alta, sem mim?* Se a resposta depender de ler
quatro arquivos, cortar até caber em um. E sempre: analogia antes do jargão,
adversário antes do número, resposta antes do detalhe.
