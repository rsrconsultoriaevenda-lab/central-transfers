from pathlib import Path
import os


def clean_env():
    """Remove linhas malformadas do arquivo .env que causam erros no python-dotenv."""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado na raiz.")
        return

    lines = env_path.read_text(encoding="utf-8").splitlines()
    # Mantém apenas chaves válidas ou comentários
    cleaned = [line.strip() for line in lines if "=" in line or line.strip(
    ).startswith("#") or not line.strip()]

    env_path.write_text("\n".join(cleaned) + "\n", encoding="utf-8")
    print("✨ Arquivo .env sanitizado! Os erros de parse devem sumir agora.")


if __name__ == "__main__":
    clean_env()
