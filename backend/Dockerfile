FROM python:3.11-slim

WORKDIR /app

# Copia o arquivo de dependências presente no contexto backend/ para instalação
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o backend para /app/backend para preservar o package path
COPY . ./backend/

# Define a raiz de busca de módulos do Python para evitar erros de importação
ENV PYTHONPATH=/app

# O Railway injeta a porta dinamicamente, mas deixamos a porta padrão como fallback
EXPOSE 8000

CMD python -m alembic upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port $PORT