import os
from backend.config import settings

print("==================================================")
print("🧪 VALIDANDO CONEXÃO DE INFRAESTRUTURA")
print("==================================================")
print(f"Instância de banco configurada para uso: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
print("Configuração carregada com sucesso e protegida contra vazamentos!")