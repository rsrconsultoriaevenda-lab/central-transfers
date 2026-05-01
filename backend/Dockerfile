FROM python:3.11-slim

WORKDIR /app

# Como o Root Directory é /backend, o arquivo está na "raiz" do contexto
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia tudo o que está em /backend para a raiz /app do container
COPY . .

EXPOSE 8000

# O comando agora aponta para main:app diretamente, pois estamos dentro de /app
# ... (mantenha o restante como está)

EXPOSE 8000

# Usar o formato de string simples permite que o sistema entenda o $PORT
CMD uvicorn backend.main:app --host 0.0.0.0 --port $PORT