FROM python:3.11-slim

WORKDIR /app

# Como o Railway já está dentro da pasta backend, o requirements está na raiz do contêiner
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos locais para o contêiner
COPY . .

# Define a raiz de busca de módulos do Python
ENV PYTHONPATH=/app

EXPOSE 8000

# Inicialização limpa e direta
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]