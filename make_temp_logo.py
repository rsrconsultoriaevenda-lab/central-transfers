from PIL import Image, ImageDraw

def create_minimalist_logo():
    # Cria uma imagem quadrada de 512x512 com fundo preto/grafite escuro
    size = (512, 512)
    image = Image.new("RGBA", size, "#121214")
    draw = ImageDraw.Draw(image)

    # Desenha um elemento geométrico minimalista representando conexão/rota
    # Círculo de origem
    draw.ellipse([140, 236, 180, 276], fill="#7C3AED")

    # Linha de transferência/trajeto
    draw.line([180, 256, 332, 256], fill="#7C3AED", width=8)

    # Flecha/Triângulo de destino
    draw.polygon([332, 230, 372, 256, 332, 282], fill="#9945FF")

    # Salva o arquivo diretamente como logo.png
    image.save("logo.png", "PNG")
    print("✅ Arquivo 'logo.png' criado com sucesso na raiz do projeto!")

if __name__ == "__main__":
    create_minimalist_logo()