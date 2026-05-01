FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o conteúdo para uma subpasta 'backend' para preservar a estrutura de pacotes
# Isso permite que 'from backend import ...' funcione corretamente.
COPY . ./backend/

# Define o PYTHONPATH para que o diretório atual seja reconhecido como base de pacotes
ENV PYTHONPATH=/app

EXPOSE 8000

CMD sh -c "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"