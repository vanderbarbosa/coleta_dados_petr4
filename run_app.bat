@echo off
REM ============================================================================
REM  PETR4 - Executa a aplicacao completa (backend classificadores + frontend)
REM  com UM comando. Instala tudo na 1a vez e sobe os dois servidores.
REM
REM  Uso:  duplo-clique neste arquivo,  ou  no terminal:  run_app.bat
REM  Pre-requisitos: Python 3.11+ e Node.js 20+ instalados (no PATH).
REM ============================================================================
setlocal
cd /d "%~dp0"

REM --- Checagem de pre-requisitos -------------------------------------------
where python >nul 2>nul || (echo [ERRO] Python nao encontrado no PATH. Instale o Python 3.11+ ^(https://www.python.org^). & pause & exit /b 1)
where node   >nul 2>nul || (echo [ERRO] Node.js nao encontrado no PATH. Instale o Node.js 20+ ^(https://nodejs.org^). & pause & exit /b 1)

REM --- 1) Ambiente Python + dependencias dos classificadores ----------------
if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Criando ambiente Python isolado ^(.venv^)...
  python -m venv .venv || (echo [ERRO] Falha ao criar o ambiente virtual. & pause & exit /b 1)
)
echo [2/4] Instalando dependencias Python ^(pode demorar na 1a vez - baixa torch/transformers^)...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r "site\backend\requirements.txt" || (echo [ERRO] Falha no pip install. & pause & exit /b 1)

REM --- 2) Dependencias do frontend ------------------------------------------
echo [3/4] Instalando dependencias do frontend ^(npm^)...
if not exist "site\frontend\node_modules" (
  pushd "site\frontend"
  call npm install || (echo [ERRO] Falha no npm install. & popd & pause & exit /b 1)
  popd
)

REM --- 3) Sobe o backend em uma janela separada -----------------------------
echo [4/4] Subindo backend ^(porta 8000^) e frontend ^(porta 5173^)...
start "PETR4 Backend (classificadores)" "%~dp0.venv\Scripts\python.exe" -m uvicorn app:app --port 8000 --app-dir "%~dp0site\backend"

REM --- 4) Sobe o frontend e abre o navegador --------------------------------
pushd "site\frontend"
call npm run dev -- --open
popd

endlocal
