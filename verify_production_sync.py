import requests
import sys

# AJUSTE ESTAS URLs COM SEUS DOMÍNIOS REAIS
URLS = {
    "BACKEND (Railway)": "https://api.centraltransfers.com",
    "PAINEL/DRIVER (Vercel)": "https://centraltransfers.com/driver",
    "STOREFRONT (Vercel)": "https://centraltransfers.com"
}

def test_connectivity():
    print("\n🔍 Iniciando Auditoria de Comunicação das 3 Pontas...")
    print("=" * 60)
    
    all_ok = True

    for name, url in URLS.items():
        try:
            # Para o backend, testamos o health
            target = f"{url}/health" if "BACKEND" in name else url
            resp = requests.get(target, timeout=10)
            
            status = "✅ ONLINE" if resp.status_code == 200 else f"⚠️ STATUS {resp.status_code}"
            print(f"{name:<25} | {status} | URL: {url}")
            
            if resp.status_code != 200: all_ok = False
            
            if "BACKEND" in name and resp.status_code == 200:
                data = resp.json()
                print(f"   └─ Database: {data.get('database')} | Env: {data.get('environment', 'production')}")
                
        except Exception as e:
            print(f"{name:<25} | ❌ OFFLINE | Erro: {str(e)[:40]}...")
            all_ok = False

    if all_ok:
        print("\n🚀 SUCESSO: As 3 pontas estão visíveis e operacionais!")
    else:
        print("\n🛑 FALHA: Existem problemas de conexão. Verifique o deploy e os logs.")

if __name__ == "__main__":
    test_connectivity()