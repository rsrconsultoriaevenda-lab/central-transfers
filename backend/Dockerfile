FROM python:3.11-slim

WORKDIR /app

# 1. Copia o requirements correto que está dentro de backend
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copia todo o projeto para a subpasta backend, mantendo a estrutura que você planejou
COPY . ./backend/

# 3. Define a raiz de busca de módulos do Python
ENV PYTHONPATH=/app

EXPOSE 8080

# 4. 🔥 Inicialização LIMPA: Apenas o Uvicorn, sem Alembic para travar o boot
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]