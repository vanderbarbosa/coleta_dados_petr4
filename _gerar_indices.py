# -*- coding: utf-8 -*-
# ==============================================================================
#   Gera os arquivos LEIA-ME de cada pasta
#   Idempotente: sobrescreve os índices, não toca em mais nada.
# ==============================================================================
from pathlib import Path

AQUI = Path(__file__).resolve().parent

# ──────────────────────────────────────────────────────────────── raiz ──────
RAIZ = """# Pesquisa PETR4 — sentimento de notícias e previsão de preço

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
"""

# ────────────────────────────────────────────────────────────── memória ─────
MEMORIA = """# A memória da pesquisa

Estes arquivos são o que o assistente **sabe** sobre esta pesquisa: o que já foi
testado, o que falhou e por quê, os números confirmados, os defeitos conhecidos
das ferramentas e as preferências de trabalho.

## Por que isso existe

A memória fica fora do repositório, num diretório que o Claude associa ao caminho
do projeto. **Ao clonar em outra máquina, ela não vem junto.** Sem ela, o
assistente repete experimentos já feitos, reintroduz defeitos já corrigidos e
esquece números que custaram meses.

## Como usar

**Ao abrir o projeto numa máquina nova:**

```
python _memoria_claude/restaurar_memoria.py
```

**Ao terminar uma sessão de trabalho:**

```
python _memoria_claude/restaurar_memoria.py --salvar
```

E então dar commit, para que a próxima máquina receba o que foi aprendido.

## O que está guardado

O índice é o `memory/MEMORY.md` — uma linha por assunto. Entre os registros mais
importantes:

- **`cvm-estudo-de-evento.md`** — os 11.161 eventos e o que se mediu
- **`efeito-de-cauda-auditoria-noticia.md`** — a tese central da dissertação
- **`bug-problem-type-sigmoide.md`** — o defeito do FinBERT que corrompe escores
- **`ambiente-torch-quebrado.md`** — por que rodamos no Colab
- **`g3-adaptacao-esquecimento.md`** — a linha de trabalho que foi encerrada
- **`onde-a-literatura-nos-supera.md`** — os trabalhos que nos superam, e por quê

## Uma advertência

A memória reflete o que era verdade quando foi escrita. **Se um registro citar um
arquivo, uma função ou um número, confira antes de agir sobre ele.**
"""

# ───────────────────────────────────────────────────────────── mentorias ────
MENTORIAS = {
"2026-08-13_Emerson": """# Mentoria de 13 de agosto de 2026 — Prof. Emerson

## O que foi pedido

Procurar **outras pesquisas que façam o mesmo que a nossa** — ler notícias e
prever direção e volatilidade —, independentemente do ativo e do idioma. E dizer
se dá para usar ou adaptar algo delas.

## O que foi feito, em linguagem simples

Levantamos **25 pesquisas** e lemos cada uma. Depois fomos conferir os números que
elas anunciam, porque alguns pareciam bons demais.

**E três não resistiram ao exame:**

- Um trabalho muito citado anuncia 86,7% de acerto. São **13 acertos em 15 dias**,
  e a análise **foi refutada** em 2017.
- Outro anuncia 71,2%, mas mede o preço **vinte minutos depois** da notícia, não
  no dia seguinte. E 71,2% é o melhor de seis recortes; no recorte por ação
  individual, cai para 56,9%.
- Um terceiro anuncia 0,955 de "acurácia", mas prevê o **preço em reais**, não a
  direção. Prever o preço de amanhã é fácil: basta responder "o mesmo de hoje".

**Mas três nos superam de verdade**, e isso também foi registrado. O principal
deles usa 404 ações e dados de 5 em 5 minutos, contra a nossa uma ação e dado
diário. **É falta de dado, não ausência de sinal.**

## O achado que mudou o rumo da pesquisa

Uma das pesquisas (Hashami e Maldonado, sobre petróleo) testou o **mesmo modelo**
de duas formas:

| Como usaram o modelo | Acerto |
|---|---|
| como classificador de sentimento | **0,5368** — o pior da tabela |
| como extrator de *embeddings* | **0,6694** — vence a referência |

Treze pontos de diferença, no mesmo modelo. **Todos os defeitos que auditamos no
nosso classificador estão na parte que rende 0,5368.**

## O que está nesta pasta

Os documentos comparativos, o glossário de termos, as fichas de leitura das 25
pesquisas e **15 PDFs** das que têm acesso aberto.
""",

"2026-08-26_Emerson_e_Julio": """# Mentoria de 26 de agosto de 2026 — Profs. Emerson e Julio

## O que foi pedido

Duas coisas.

**Primeira:** buscar sites ou blogs de especialistas em mercado financeiro,
verificar se eles classificam as notícias, e conferir no preço se o que eles
previram aconteceu.

**Segunda:** buscar publicações no site da CVM, classificá-las com o nosso
programa, e avaliar o impacto delas nos principais ativos da B3.

## O que foi feito, em linguagem simples

### Sobre os especialistas

**Não precisou buscar na internet — eles já estavam no nosso corpus.** Casas de
análise publicam o parecer, e a imprensa reproduz na manchete:

> *"Guide: reajuste do preço do GLP é positivo para a Petrobras"*

Encontramos **224 notícias assim, de 30 casas de análise** — BTG, XP, Itaú BBA,
Fitch, Moody's, S&P e outras.

**E o resultado foi duro para o nosso programa.** Diante das mesmas 224 notícias:

| | Positivas | Neutras | Negativas |
|---|---|---|---|
| Os analistas viram | **84,8%** | 3,1% | 12,1% |
| Nosso programa viu | **21,9%** | 52,7% | 25,4% |

**Ele reconhece a notícia ruim e é cego para a boa.**

### Uma armadilha que foi apontada e evitada

O pedido encadeava três coisas diferentes: (a) o especialista classifica a
notícia, (b) o especialista prevê alta ou baixa, (c) confere-se no preço. **O item
(c) valida o (b), não o (a).**

Se o analista disser "esta notícia é ruim" e a ação subir, **isso não torna o
rótulo errado** — mostra apenas que naquele pregão outra coisa pesou mais. Usar o
preço para julgar o rótulo seria medir com uma régua que já sabíamos ser de cara
ou coroa.

### Sobre a CVM

Coletamos **89.902 comunicados** dos dados abertos da CVM, de 2018 a 2026. E
descobrimos que a pergunta central — *essas publicações causaram impacto?* — **não
precisa do nosso programa**. É estudo de evento puro.

O resultado está detalhado na mentoria seguinte.

## O que está nesta pasta

O protocolo do experimento, o resultado da rotulagem por especialistas e o
primeiro resultado da CVM.
""",

"2026-09-16_Emerson_e_Julio": """# Mentoria de 16 de setembro de 2026 — Profs. Emerson e Julio

## O que foi pedido

Uma **engenharia reversa**: temos a publicação e temos o que o preço fez depois.
Confrontar as duas coisas.

Com um recorte importante, sugerido pelos professores: **usar só o que foi
publicado após o fechamento do pregão**, e olhar o **pregão seguinte**.

Em duas rodadas — primeiro com a classificação que já vem na publicação, depois
com a nossa.

E uma sugestão do Prof. Emerson: comparar a volatilidade do dia seguinte com a
**média da semana anterior**, e não com uma média distante.

## O que foi feito, em linguagem simples

### O recorte da noite é a melhor parte do desenho

> É como trancar todo mundo fora do estádio, pôr a notícia no telão, e só então
> abrir os portões. **Ninguém pôde reagir antes.**

Para fazer esse recorte precisávamos da hora exata. **A CVM não publica a hora nos
dados abertos** — e recuperá-la virou a principal contribuição da pesquisa. Como
isso foi feito está em `Artigos/Artigo_1_O_Relogio_da_CVM/03_COMO_OBTIVEMOS_A_HORA.md`.

### A sugestão do Prof. Emerson estava certa, e é mais exigente

Volatilidade é grudenta: depois de uma semana agitada vem outra agitada. **Bater a
média da própria semana anterior é muito mais difícil** que bater uma média de
cem dias atrás.

### Uma correção que evitou dois números errados

A razão entre o dia e a média da semana **já vale mais que 1,00 sem evento
algum** — porque um dia pode ser cinco vezes mais agitado que a média, mas nunca
cinco vezes menos. Medimos esse piso em 105.896 pregões sem comunicado.

Sem esse controle teríamos anunciado **+21,9%** de volatilidade e **+44,6%** de
volume. Os números corretos são **+9,6%** e **+16,5%**.

## Os resultados

| Pergunta | Resposta |
|---|---|
| A publicação move o preço? | **Sim — o risco, não a direção** |
| Move sempre? | **Não. 59% não movem nada** |
| Dá para saber o lado? | Só com a nossa leitura, e só no Fato Relevante |
| A lei acerta? | **Sim. Fato Relevante mexe 2,6× mais que Comunicado** |

## O que está nesta pasta

O plano do experimento, os resultados das duas rodadas, a explicação completa em
linguagem comum e a planilha de apoio.
""",

"2026-09-20_Julio_e_Emerson": """# Mentoria de 20 de setembro de 2026 — Profs. Julio e Emerson

## O que foi pedido

Apresentar a evolução do artigo, com vistas ao seminário de novembro e à
submissão de dezembro.

## O que foi preparado

### Três propostas de artigo, para escolha dos senhores

| | Título | Contribuição | Estado |
|---|---|---|---|
| **1** | O relógio da CVM | a hora oficial de 20.419 comunicados | **escrito** |
| 2 | Auditoria do classificador | 224 pareceres de 30 casas de análise | reunido |
| 3 | Armadilhas de medição | quatro erros quantificados | reunido |

**Os três não são fatias do mesmo estudo.** Perguntas, literaturas e públicos
distintos. O Artigo 1 não usa aprendizado de máquina algum — se a crítica do
Artigo 2 estiver certa, o Artigo 1 continua de pé.

### Uma ressalva de prazo

São dez semanas até a submissão, com a dissertação em paralelo. **Três artigos
terminados não é realista.** O alcançável é um pronto para submeter e dois em
rascunho avançado.

## O Artigo 1, em resumo

**A tese:** *a presunção legal de relevância é válida em média e falsa na maioria
dos casos individuais.*

O conjunto dos Fatos Relevantes move volatilidade e volume com significância
inequívoca. **O Fato Relevante mediano não move nada.**

## O que está nesta pasta

As três propostas e o Artigo 1 completo.

## Para a apresentação

O roteiro do painel interativo está em `Painel/00_COMO_APRESENTAR.md`.
"""
}

# ──────────────────────────────────────────────────────────────── artigos ───
ARTIGOS = {
"Artigo_1_O_Relogio_da_CVM": """# Artigo 1 — O relógio da CVM

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
""",

"Artigo_2_Auditoria_do_Classificador": """# Artigo 2 — Auditoria do classificador

**O que um classificador de sentimento financeiro em português não enxerga**

## Estado: material reunido, falta escrever

## A contribuição

Uma auditoria sistemática do FinBERT-PT-BR contra **referência externa
independente**: 224 notícias em que trinta casas de análise declararam
publicamente se o fato era favorável ou desfavorável à companhia.

## Os achados reunidos

- viés estrutural: 48,5% do corpus rotulado negativo; **zero pregões com maioria
  positiva em oito anos**
- contra o gabarito profissional: **21,9% contra 84,8%**; kappa de 0,075
- defeito de configuração que faz a biblioteca aplicar sigmoide em vez de softmax
- o modelo é *cased* e quebra com as 21.619 manchetes em caixa alta
- nove tentativas de melhoria, oito fracassaram
- em texto regulatório, 79,2% saem neutros

## O que falta

- [ ] **auditar à mão os 224 pareceres** — `dados/224_pareceres_PARA_AUDITAR.csv`
      tem duas colunas em branco para isso. Sem essa conferência, o número
      principal fica preliminar. Cerca de duas horas.
- [ ] escrever

## Cuidado editorial

O texto precisa ser escrito **sem tom de ataque** ao trabalho de Santos, Bianchi e
Costa (2023). O enquadramento correto é o de **estudo de limites de
aplicabilidade**: o modelo foi treinado para uma tarefa e está sendo cobrado por
outra.
""",

"Artigo_3_Armadilhas_de_Medicao": """# Artigo 3 — Armadilhas de medição

**Quatro armadilhas em estudos de evento com dados textuais, e como corrigi-las**

## Estado: material reunido, falta escrever

## A ideia

Cada armadilha foi **cometida e corrigida** no curso desta pesquisa. Nenhuma é
óbvia, e todas alteram a conclusão publicada.

| Armadilha | Número errado | Número certo |
|---|---|---|
| o piso da razão não é 1,00 | +21,9% | **+9,6%** |
| a regra ingênua vira constante | 47,8% de acerto | **53,8%** |
| a composição da amostra infla o bruto | +71,8% de volume | **+16,5%** |
| eventos agrupados não são atribuíveis | 28,8% dos casos | — |

## O que torna o artigo publicável

Não é apontar as armadilhas — é **quantificá-las** sobre a mesma base de 11.161
eventos e 105.896 pregões de controle.

## O que falta

- [ ] escrever
- [ ] decidir o veículo — é gênero de **nota de pesquisa**
"""
}


def escreve(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")
    print(f"    {caminho.relative_to(AQUI)}")


def main() -> None:
    print("=" * 70)
    print("GERANDO OS ÍNDICES")
    print("=" * 70)
    print("\n  raiz e memória")
    escreve(AQUI / "00_LEIA-ME.md", RAIZ)
    escreve(AQUI / "_memoria_claude" / "LEIA-ME.md", MEMORIA)

    print("\n  mentorias")
    for pasta, txt in MENTORIAS.items():
        escreve(AQUI / "Mentorias" / pasta / "00_LEIA-ME.md", txt)

    print("\n  artigos")
    for pasta, txt in ARTIGOS.items():
        escreve(AQUI / "Artigos" / pasta / "00_LEIA-ME.md", txt)

    print(f"\n  {2 + len(MENTORIAS) + len(ARTIGOS)} arquivos escritos.")


if __name__ == "__main__":
    main()
