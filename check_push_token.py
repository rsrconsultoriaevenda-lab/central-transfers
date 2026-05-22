from sqlalchemy import create_engine, text
from backend.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name='motoristas' AND column_name='push_token'"))
    rows = result.fetchall()
    print('COLUMN_EXISTS', len(rows), rows)
