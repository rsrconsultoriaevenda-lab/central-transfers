import os
import json
from pathlib import Path


def finalize_pwa():
    print("🚀 Finalizando configurações de PWA...")
    public_path = Path("painel-saas/public")

    if not public_path.exists():
        print("❌ Pasta public do frontend não encontrada.")
        return

    # 1. Garantir existência do Manifest
    manifest_path = public_path / "manifest.json"
    manifest_content = {
        "short_name": "Central",
        "name": "Central Transfers",
        "icons": [
            {
                "src": "icon-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "icon-512x512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ],
        "start_url": ".",
        "display": "standalone",
        "theme_color": "#000000",
        "background_color": "#ffffff"
    }

    with open(manifest_path, "w") as f:
        json.dump(manifest_content, f, indent=2)
    print("✅ manifest.json criado/atualizado.")

    # 2. Gerar Ícones reais ou Placeholders
    # Tenta usar Pillow para gerar ícones a partir de uma imagem base se disponível
    logo_base = Path("logo.png")
    has_pillow = False
    try:
        from PIL import Image
        has_pillow = True
    except ImportError:
        pass

    for size in ["192x192", "512x512"]:
        icon_name = f"icon-{size}.png"
        target = public_path / icon_name
        if not target.exists():
            if has_pillow and logo_base.exists():
                print(
                    f"🎨 Gerando ícone real {icon_name} a partir de logo.png...")
                with Image.open(logo_base) as img:
                    # Extrai a dimensão numérica do texto "192x192"
                    dim = int(size.split('x')[0])
                    img.convert("RGBA").resize(
                        (dim, dim), Image.Resampling.LANCZOS).save(target, "PNG")
            else:
                print(f"⚠️ Criando ícone placeholder {icon_name}...")
                # Fallback: cria arquivo vazio se não houver Pillow ou logo.png
                target.touch()

    # 3. Vincular no index.html
    html_path = Path("painel-saas/index.html")
    if html_path.exists():
        content = html_path.read_text()
        if 'rel="manifest"' not in content:
            print("🔗 Vinculando manifest no index.html...")
            new_content = content.replace(
                "</head>", '  <link rel="manifest" href="/manifest.json">\n  </head>')
            html_path.write_text(new_content)

    # 4. Registrar no App (Suporta .tsx e .jsx)
    for ext in [".tsx", ".jsx"]:
        app_path = Path(f"painel-saas/src/App{ext}")
        if app_path.exists():
            app_content = app_path.read_text()
            if "PWAIntegration" not in app_content:
                print(f"💉 Injetando PWAIntegration no App{ext}...")
                if "import" in app_content:
                    app_content = "import PWAIntegration from './components/PWAIntegration';\n" + app_content
                if "<Routes>" in app_content:
                    app_content = app_content.replace(
                        "<Routes>", "<PWAIntegration />\n      <Routes>")
                elif "return (" in app_content:
                    app_content = app_content.replace(
                        "return (", "return (\n    <PWAIntegration />")
                app_path.write_text(app_content)
            break

    print("\n🏁 Etapa PWA concluída! Rode o 'pwa_status_audit.py' para confirmar.")


if __name__ == "__main__":
    finalize_pwa()
