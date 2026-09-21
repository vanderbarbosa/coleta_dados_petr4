---
name: ambiente-torch-quebrado
description: O PyTorch do Anaconda local não carrega (WinError 1114 / c10.dll) — nenhum experimento de encoder roda nesta máquina
metadata: 
  node_type: memory
  type: project
  originSessionId: 08181b53-ca1d-41ae-a256-cc9d79527860
  modified: 2026-08-04T01:44:12.672Z
---

Desde algum ponto entre jul/2026 e 03/08/2026, `import torch` falha no Anaconda local (`C:\Users\Vanderlei\anaconda3.12`):

```
OSError: [WinError 1114] ... Error loading "...\site-packages\torch\lib\c10.dll"
```

O `torch` 2.12.1 está instalado e registrado, mas não carrega. A falha é **pré-existente e isolada** (não foi causada por instalação de pacote). Os experimentos de encoder de julho rodaram normalmente em CPU, então algo mudou no ambiente (provável: MSVC Redistributable, conflito de `libiomp5md.dll` entre a MKL do Anaconda e a do PyTorch, ou torch × numpy 1.26.4).

**Why:** enquanto não for corrigido, **nenhum script de sentimento ou de encoder roda localmente** — Scripts 03, 12 e a avaliação do conjunto-ouro estão bloqueados.

**How to apply:** não gastar tempo depurando o ambiente local para tarefas pesadas — a pipeline já foi escrita para o **Google Colab** (monta o Drive em `/content/drive/MyDrive/Mestrado_PETR4/`), que é também o tipo de ambiente usado por Santos (Kaggle 2×T4). Rodar o MLM de domínio lá. Detalhe: `pip install` nesta máquina exige `--trusted-host pypi.org --trusted-host files.pythonhosted.org` (erro de certificado SSL).

Ver [[mentoria-emerson-agosto2026]] e [[encoders-sentimento-ptbr]].
