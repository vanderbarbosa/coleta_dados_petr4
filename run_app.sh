#!/usr/bin/env bash
# ============================================================================
#  PETR4 - Executa a aplicacao completa (backend + frontend) com UM comando.
#  Instala tudo na 1a vez e sobe os dois servidores. (macOS / Linux)
#
#  Uso:   bash run_app.sh
#  Pre-requisitos: Python 3.11+ e Node.js 20+ instalados.
# ============================================================================
set -e
cd "$(dirname "$0")"

command -v python3 >/dev/null 2>&1 || { echo "[ERRO] Python 3.11+ nao encontrado."; exit 1; }
command -v node    >/dev/null 2>&1 || { echo "[ERRO] Node.js 20+ nao encontrado."; exit 1; }

# 1) Ambiente Python + dependencias
if [ ! -d .venv ]; then
  echo "[1/4] Criando ambiente Python isolado (.venv)..."
  python3 -m venv .venv
fi
echo "[2/4] Instalando dependencias Python (pode demorar na 1a vez)..."
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r site/backend/requirements.txt

# 2) Dependencias do frontend
echo "[3/4] Instalando dependencias do frontend (npm)..."
[ -d site/frontend/node_modules ] || ( cd site/frontend && npm install )

# 3) Sobe backend em segundo plano; encerra junto ao sair
echo "[4/4] Subindo backend (porta 8000) e frontend (porta 5173)..."
./.venv/bin/python -m uvicorn app:app --port 8000 --app-dir site/backend &
BACK=$!
trap "kill $BACK 2>/dev/null" EXIT

# 4) Sobe o frontend e abre o navegador
cd site/frontend && npm run dev -- --open
