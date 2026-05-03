import cloudinary
import cloudinary.uploader
from backend.config import settings

# Configuração global do Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)


async def upload_image_to_cloudinary(file):
    """
    Realiza o upload do arquivo para o Cloudinary e retorna a URL segura.
    """
    # O atributo .file do UploadFile do FastAPI contém o stream de bytes
    result = cloudinary.uploader.upload(file.file)
    return result.get("secure_url")
