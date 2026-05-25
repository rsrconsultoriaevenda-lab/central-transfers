import os
import json
from pathlib import Path


def check_pwa_assets(build_path="painel-saas/dist"):
    print(f"🧐 Verificando ativos PWA em: {build_path}")
    path = Path(build_path)

    if not path.exists():
        print("❌ Erro: Pasta 'dist' não encontrada. Execute 'npm run build' primeiro.")
        return False

    # 1. Verificar Manifest
    manifests = list(path.glob("**/manifest*.webmanifest")) + \
        list(path.glob("**/site.webmanifest")) + \
        list(path.glob("**/manifest.json"))
    if not manifests:
        print("❌ Erro: Web Manifest não encontrado no build.")
    else:
        print(f"✅ Manifest encontrado: {manifests[0].name}")
        with open(manifests[0], 'r') as f:
            data = json.load(f)
            if 'icons' not in data:
                print("⚠️ Aviso: Manifest sem ícones configurados.")
            if 'display' not in data or data['display'] != 'standalone':
                print(
                    "⚠️ Aviso: display deve ser 'standalone' para melhor experiência PWA.")

    # 2. Verificar Service Worker
    sw_files = list(path.glob("**/sw.js")) + list(path.glob("**/*sw*.js"))
    if not sw_files:
        print("❌ Erro: Service Worker (sw.js) não encontrado.")
    else:
        print(f"✅ Service Worker detectado: {sw_files[0].name}")

    # 3. Verificar HTTPS em Variáveis de Ambiente
    from backend.config import settings
    api_url = os.getenv("VITE_API_URL", "")
    if "localhost" not in api_url and not api_url.startswith("https://"):
        print(
            f"⚠️ PERIGO: VITE_API_URL ({api_url}) não usa HTTPS. O PWA e Push falharão em produção.")
    else:
        print("✅ Configuração de protocolo de rede parece correta.")

    return True


if __name__ == "__main__":
    # Adiciona o diretório atual ao path para importar as configurações do backend se necessário
    import sys
    sys.path.append(os.getcwd())
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass

    print("\n--- PWA PREFLIGHT CHECK ---")
    check_pwa_assets()
