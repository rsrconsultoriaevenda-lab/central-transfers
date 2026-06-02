import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("❌ Erro: Biblioteca 'Pillow' não instalada.")
    print("👉 Execute: pip install Pillow")
    sys.exit(1)


def generate_pwa_icons(source_file: Path, output_folder: Path):
    """
    Gera ícones PWA nos tamanhos padrão a partir de uma imagem de origem.
    Utiliza a biblioteca Pillow para garantir alta qualidade no redimensionamento.
    """
    sizes = [192, 512]
    src = source_file
    dest = output_folder

    if not src.exists():
        print(f"❌ Erro: Imagem de origem '{source_file}' não encontrada.")
        print("💡 Dica: Coloque um arquivo 'logo.png' (quadrado, min. 512x512) na raiz do projeto.")
        return

    if not dest.exists():
        print(f"📂 Criando pasta de destino: {dest}")
        dest.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Iniciando processamento de ícones a partir de: {src.absolute()}")

    try:
        with Image.open(src) as img:
            # Garante que a imagem esteja no modo RGBA para suportar transparência
            img = img.convert("RGBA")

            for size in sizes:
                icon_filename = f"icon-{size}x{size}.png"
                target_path = dest / icon_filename

                # Remove placeholder antigo se for um arquivo vazio
                if target_path.exists() and target_path.stat().st_size == 0:
                    target_path.unlink()

                # Redimensionamento de alta qualidade usando o algoritmo LANCZOS
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                resized.save(target_path, "PNG")
                print(f"✅ Gerado: {icon_filename} ({size}x{size})")

        print("\n✨ Processamento concluído! Seus ícones PWA estão prontos.")
    except Exception as e:
        print(f"❌ Falha ao processar imagem: {e}")


if __name__ == "__main__":
    # Detecta automaticamente a raiz baseada no local do script
    BASE_DIR = Path(__file__).parent
    SOURCE = BASE_DIR / "logo.png"
    OUTPUT = BASE_DIR / "painel-saas" / "public"

    generate_pwa_icons(SOURCE, OUTPUT)
