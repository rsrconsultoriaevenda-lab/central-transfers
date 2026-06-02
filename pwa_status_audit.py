import os
import json
from pathlib import Path


def calculate_pwa_readiness():
    score = 0
    total = 6
    steps = []

    # 1. Manifest
    manifest_files = list(Path("painel-saas/public").glob("manifest.*"))
    if manifest_files:
        try:
            with open(manifest_files[0], "r", encoding="utf-8") as f:
                content = json.load(f)
                if content.get("name") == "CENTRAL TRANSFER":
                    score += 1
                    steps.append("✅ Web Manifest com nome 'CENTRAL TRANSFER'")
                else:
                    steps.append(
                        f"⚠️ Manifest com nome incorreto: '{content.get('name')}'")
        except Exception:
            steps.append("❌ Erro ao ler manifest.json")
    else:
        steps.append("❌ Faltando manifest.json/webmanifest")

    # 2. Service Worker
    sw_path = Path("painel-saas/public/sw.js")
    if sw_path.exists():
        with open(sw_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "CENTRAL TRANSFER" in content:
                score += 1
                steps.append(
                    "✅ Service Worker configurado com 'CENTRAL TRANSFER'")
            else:
                steps.append("⚠️ sw.js existe mas não contém o nome da marca")
    else:
        steps.append("❌ Faltando sw.js")

    # 3. VAPID Keys
    from backend.config import settings
    if settings.VAPID_PUBLIC_KEY and "cole_seu" not in settings.VAPID_PUBLIC_KEY:
        score += 1
        steps.append("✅ Chaves VAPID (Push) configuradas")
    else:
        steps.append("❌ Chaves VAPID não geradas no .env")

    # 4. HTTPS Context
    if os.getenv("ENV") == "production" or os.getenv("VITE_API_URL", "").startswith("https"):
        score += 1
        steps.append("✅ Protocolo Seguro (HTTPS) detectado")
    else:
        steps.append("⚠️ Ambiente ainda em HTTP (Push falhará)")

    # 5. Icons
    icons_exists = any(Path("painel-saas/public").glob("icon-*.png"))
    if icons_exists:
        score += 1
        steps.append("✅ Ícones de instalação presentes")
    else:
        steps.append("❌ Ícones de marca (App Icons) ausentes")

    # 6. Componente de Registro (Suporta .tsx e .jsx)
    found_app = False
    for ext in [".tsx", ".jsx"]:
        app_path = Path(f"painel-saas/src/App{ext}")
        if app_path.exists():
            found_app = True  # Set found_app to true here
            with open(app_path, "r", encoding="utf-8") as f:  # Specify UTF-8 encoding
                if "PWAIntegration" in f.read():
                    score += 1
                    steps.append(f"✅ Registro de PWA no App{ext}")
                else:
                    steps.append(
                        f"❌ Componente PWAIntegration não montado em App{ext}")
            break

    if not found_app:
        steps.append("❌ Arquivo App.tsx/jsx não encontrado no frontend")

    percent = (score / total) * 100
    print(f"\n📊 STATUS PWA: {percent:.1f}%")
    for s in steps:
        print(f"  {s}")
    return percent


if __name__ == "__main__":
    calculate_pwa_readiness()
