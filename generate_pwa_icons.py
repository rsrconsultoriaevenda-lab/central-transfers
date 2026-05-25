import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("❌ Erro: Biblioteca 'Pillow' não instalada.")
    print("👉 Execute: pip install Pillow")
    sys.exit(1)


def generate_pwa_icons(source_file: str, output_folder: str):
    """
    Gera ícones PWA nos tamanhos padrão a partir de uma imagem de origem.
    Utiliza a biblioteca Pillow para garantir alta qualidade no redimensionamento.
    """
    sizes = [192, 512]
    src = Path(source_file)
    dest = Path(output_folder)

    if not src.exists():
        print(f"❌ Erro: Imagem de origem '{source_file}' não encontrada.")
        print("💡 Dica: Coloque um arquivo 'logo.png' (quadrado, min. 512x512) na raiz do projeto.")
        return

    if not dest.exists():
        print(f"❌ Erro: Pasta de destino '{output_folder}' não encontrada.")
        return

    print(f"🚀 Iniciando processamento de ícones a partir de: {src.name}")

    try:
        with Image.open(src) as img:
            # Garante que a imagem esteja no modo RGBA para suportar transparência
            img = img.convert("RGBA")

            for size in sizes:
                icon_filename = f"icon-{size}x{size}.png"
                target_path = dest / icon_filename

                # Redimensionamento de alta qualidade usando o algoritmo LANCZOS
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                resized.save(target_path, "PNG")
                print(f"✅ Gerado: {icon_filename} ({size}x{size})")

        print("\n✨ Processamento concluído! Seus ícones PWA estão prontos.")
    except Exception as e:
        print(f"❌ Falha ao processar imagem: {e}")


if __name__ == "__main__":
    # Caminhos absolutos conforme a estrutura do projeto Central Transfers
    PROJECT_ROOT = "c:/Users/rolof/Desktop/central-transfers"
    SOURCE = os.path.join(PROJECT_ROOT, "logo.png")
    OUTPUT = os.path.join(PROJECT_ROOT, "painel-saas/public")

    generate_pwa_icons(SOURCE, OUTPUT)
