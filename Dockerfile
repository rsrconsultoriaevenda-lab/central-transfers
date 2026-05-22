FROM python:3.11-slim

WORKDIR /app

# Como o Railway já está configurado na pasta backend, 
# o requirements.txt está diretamente na raiz do contexto de build
COPY requirements.txt ./requirements.txt

# Atualiza o pip e instala as dependências sem gerar cache (deixa a imagem leve)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o restante dos arquivos do projeto para dentro de /app
COPY . .

# Define a raiz de busca de módulos do Python para evitar erros de importação
ENV PYTHONPATH=/app

# O Railway injeta a porta dinamicamente, mas deixamos o aviso da porta padrão
EXPOSE 8000

# Inicialização flexível: usa a porta do Railway ou a 8000 como plano de fundo
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]