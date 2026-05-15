import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

# Gera a chave privada usando a curva SECP256R1 (padrão VAPID)
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# Converte para o formato que o navegador e o backend esperam (URL-Safe Base64)
private_bytes = private_key.private_numbers().private_value.to_bytes(32, 'big')
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)


def b64_encode(data):
    return base64.urlsafe_b64encode(data).decode('utf-8').strip("=")


print("\n🚀 SUAS CHAVES VAPID GERADAS:")
print("="*40)
print(f"VAPID_PRIVATE_KEY={b64_encode(private_bytes)}")
print(f"VAPID_PUBLIC_KEY={b64_encode(public_bytes)}")
print("="*40)
print("\n📢 O QUE FAZER AGORA:")
print("1. Salve ambas no seu arquivo .env do Backend.")
print("2. Adicione ambas nas 'Variables' do Railway.")
print("3. LEVE A PUBLIC_KEY para o seu Frontend (Vite) como VITE_VAPID_PUBLIC_KEY.")
