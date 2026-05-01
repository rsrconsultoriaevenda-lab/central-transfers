FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Para manter a estrutura de pacotes e os imports funcionando (ex: from backend import models)
# copiamos os arquivos para dentro de uma pasta chamada 'backend' no WORKDIR
COPY . ./backend/

EXPOSE 8080

# Usamos sh -c para garantir que o shell expanda a variável $PORT do Railway/Render
CMD sh -c "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"