# A memória da pesquisa

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
