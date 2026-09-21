# Pesquisa PETR4 — sentimento de notícias e previsão de preço

**Vanderlei Barbosa da Silva** · Mestrado em Informática · PUCPR/PPGIa
Orientador: Prof. Dr. Julio Cesar Nievola · Coorientação: Prof. Dr. Emerson Cabrera Paraiso

---

## Se você acabou de baixar este projeto noutra máquina

Rode **uma vez**, antes de abrir o Claude Code:

```
python _memoria_claude/restaurar_memoria.py
```

Isso devolve à máquina os 32 arquivos de memória da pesquisa — o que já foi
testado, o que falhou, os números, as decisões e os defeitos conhecidos. Sem esse
passo, o assistente começa do zero e você perde meses de contexto.

Ao fim de uma sessão de trabalho, o caminho inverso:

```
python _memoria_claude/restaurar_memoria.py --salvar
git add _memoria_claude/ && git commit -m "memoria atualizada" && git push
```

---

## Onde fica cada coisa

| Pasta | O que tem |
|---|---|
| **`Artigos/`** | um diretório por artigo, com o texto, as fontes, os dados e o código |
| **`Mentorias/`** | um diretório por reunião, com o que foi pedido e o que foi entregue |
| **`Painel/`** | o painel interativo e o roteiro de apresentação |
| `CVM/` | coleta e análise dos comunicados da CVM |
| `Rotulagem_Especialistas/` | os 224 pareceres de casas de análise |
| `Mestrado_PETR4/` | o corpus de notícias e as bases de preço |
| `src/` | os coletores e o pipeline original |
| `datasets_refino/` | bases intermediárias dos experimentos |
| `docs/` | documentação técnica e respostas à banca |
| `_memoria_claude/` | a memória da pesquisa, versionada |

---

## Os três artigos

| | Título | Estado |
|---|---|---|
| **1** | O relógio da CVM | **escrito** — ~3.600 palavras |
| 2 | Auditoria do classificador | material reunido, falta escrever |
| 3 | Armadilhas de medição | material reunido, falta escrever |

A comparação entre os três está em `Artigos/00_TRES_PROPOSTAS.docx`.

---

## O resultado da pesquisa, em cinco linhas

1. Recuperamos a **hora oficial** de 20.419 comunicados da CVM — informação que
   não consta dos dados abertos da autarquia.
2. Sobre 11.161 eventos em 56 ações, a divulgação eleva a **volatilidade em 9,6%**
   e o **volume em 16,5%**, contra 105.896 pregões de controle.
3. **Não há efeito sobre a direção** do preço.
4. **59% das divulgações não movem o preço** — o efeito médio vem de uma minoria.
5. O que a lei chama de Fato Relevante mexe **2,6 vezes mais** que o Comunicado ao
   Mercado. A hierarquia da norma aparece no preço.

---

## Ambiente

Python 3.12. O PyTorch está quebrado nesta máquina (`c10.dll`); classificação e
treino rodam no Colab, com os cadernos em `CVM/colab/`. Coleta e estatística
rodam localmente.

A rede tem proxy que intercepta SSL: o `yfinance` exige sessão com
`verify=False`, como nos coletores deste projeto.
