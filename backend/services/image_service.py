import cloudinary
import cloudinary.uploader
import os


async def upload_image_to_cloudinary(file):
    """
    Faz o upload de uma imagem para o Cloudinary.
    Certifique-se de ter as credenciais no .env
    """
    try:
        result = cloudinary.uploader.upload(file.file)
        return result.get("secure_url")
    except Exception as e:
        print(f"Erro no upload Cloudinary: {e}")
        return None
