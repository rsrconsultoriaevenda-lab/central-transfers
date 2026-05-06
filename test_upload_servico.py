import requests
import json
import os

BASE_URL = "http://localhost:8001"
ADMIN_EMAIL = "rsrconsultoriaevenda@gmail.com"
ADMIN_PASS = "Ren@220382"

def test_upload_service():
    print("\n🚀 Iniciando Teste de Upload de Serviço")
    print("-" * 50)

    # 1. Obter Token de Admin
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"email": ADMIN_EMAIL, "senha": ADMIN_PASS})
    if login_res.status_code != 200:
        print("❌ Falha no login")
        return
    
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Preparar arquivo de imagem (Cria um dummy se não houver test.jpg)
    file_path = "test_image.jpg"
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(b"\xFF\xD8\xFF\xE0" + b"\x00" * 100) # JPG Dummy

    # 3. Preparar dados do formulário
    # Note que enviamos 'data' (campos de texto) e 'files' (imagem)
    payload = {
        "nome": "Tour Premium Gramado",
        "categoria": "PREMIUM",
        "valor": 550.00,
        "descricao": "Serviço de teste com upload de imagem para Cloudinary."
    }

    try:
        with open(file_path, "rb") as img:
            files = {"imagem": (file_path, img, "image/jpeg")}
            print(f"📝 Enviando serviço e imagem...")
            
            response = requests.post(f"{BASE_URL}/servicos/", headers=headers, data=payload, files=files)

        if response.status_code in [200, 201]:
            print("✅ SUCESSO! Serviço criado.")
            print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")

    except Exception as e:
        print(f"💥 Falha na requisição: {e}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    test_upload_service()