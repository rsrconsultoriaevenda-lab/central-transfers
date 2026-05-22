FROM python:3.11-slim

WORKDIR /app

# Copia todo o repositório para dentro de /app
COPY . .

# Usamos o requirements do backend para garantir todas as dependências do FastAPI
# quando o contexto de build está no root do projeto.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

# Define a raiz de busca de módulos do Python para evitar erros de importação
ENV PYTHONPATH=/app

# O Railway injeta a porta dinamicamente, mas deixamos o aviso da porta padrão
EXPOSE 8000

# Inicialização flexível: usa a porta do Railway ou a 8000 como plano de fundo
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]