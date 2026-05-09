FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o conteúdo para uma subpasta 'backend' para preservar a estrutura de pacotes
# Isso permite que 'from backend import ...' funcione corretamente.
COPY . ./backend/

# Define o PYTHONPATH para que o diretório /app seja a raiz de busca de módulos
ENV PYTHONPATH=/app

# Railway utiliza a porta 8080 por padrão. Alinhando com a configuração da UI.
EXPOSE 8080

# 🔥 Executa migrações do banco de dados antes de subir o servidor
CMD ["sh", "-c", "alembic upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]