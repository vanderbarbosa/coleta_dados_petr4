---
name: como-ler-os-numeros
description: Ele é leigo e se confundiu com acurácia × AUC; guia e painel interativo criados em 21/09/2026 — e as metas realistas de cada alvo
metadata:
  type: feedback
---

**21/09/2026:** *"confesso que está tudo muito confuso para mim, preciso saber
isso profundamente para poder debater com os orientadores."* Perguntou antes
se AUC era acurácia, e depois se a meta era "acurácia perto de 1 e AUC acima
de 0,7".

**As duas respostas que precisou:**
- acurácia = quantos acertei; **AUC = sei distinguir um caso do outro**. Quando
  discordam, a AUC diz a verdade sobre haver informação.
- **acurácia perto de 1 é sinal de bug**, não de qualidade. AUC > 0,7 é regra
  da medicina e não se aplica a direção de ações.

**As metas realistas, por alvo:**

| alvo | adversário | medida | meta | onde estamos |
|---|---|---|---|---|
| direção | classe majoritária 53,14% | acurácia + McNemar | 55–58% e p<0,05 | 52,8%, não passa |
| volatilidade | HAR de Corsi | R²-OS | > +5% | +7,5% |
| dia excepcional | base de 6,3% | AUC + ganho no decil | IC da AUC excluir 0,50 | texto 0,624; mercado 0,794 |

**Entregas:** `Mentorias/2026-09-16_Emerson_e_Julio/14_GUIA_Como_ler_os_numeros.docx`
(5 ilustrações em `figuras/`, geradas por `_gerar_figuras_guia.py`) e duas seções
novas no painel, incluindo um **controle deslizante que move o corte de decisão
e mostra a acurácia mudando enquanto a AUC fica parada**.

**Why:** ele vai debater com Julio e Emerson e precisa sustentar os números, não
só recitá-los. E precisa saber recusar um resultado bom demais.

**How to apply:** em toda tabela, acurácia **nunca sozinha** — sempre ao lado da
classe majoritária, do ganho em pontos e do valor-p. Quando um número parecer
bom, checar a AUC antes de comemorar. Ver [[escopo-e-ml-de-verdade]],
[[preferencia-explicacao-leigo]], [[numeros-altos-da-literatura]].
