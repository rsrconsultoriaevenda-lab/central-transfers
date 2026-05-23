FROM python:3.11-slim

WORKDIR /app

# Instala dependências antes de copiar todo o projeto para aproveitar cache de build
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto para dentro de /app
COPY . .

# Define a raiz de busca de módulos do Python para evitar erros de importação
ENV PYTHONPATH=/app

# O Railway injeta a porta dinamicamente, mas deixamos a porta padrão como fallback
EXPOSE 8000

# Usamos shell form para garantir que a variável de ambiente $PORT seja expandida corretamente
CMD sh -c "alembic upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"