# ==============================================================================
#  Dockerfile do BACKEND DE PREVISÃO (FastAPI) — dissertação PETR4
#  Pronto para o Hugging Face Spaces (SDK: Docker) ou qualquer host de contêiner.
#
#  Requer, ao lado do app.py, os arquivos do modelo (pequenos):
#    modelo_xgb_fusion.json, modelo_meta.json  → colocados em ./dados/
#    taxonomia.py                              → cópia de src/comum/taxonomia.py
#  (ver README_HF.md). O FinBERT-PT-BR é baixado do Hugging Face no 1º uso.
# ==============================================================================
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/app/.cache/huggingface \
    DADOS_DIR=/app/dados

WORKDIR /app

# Dependências primeiro (melhor cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código + taxonomia + dados/modelos
COPY app.py taxonomia.py ./
COPY dados/ ./dados/

# Cache do Hugging Face gravável (usuário não-root do Spaces)
RUN mkdir -p /app/.cache/huggingface && chmod -R 777 /app/.cache

# O Hugging Face Spaces expõe a porta 7860
EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
