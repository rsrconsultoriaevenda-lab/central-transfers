from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg2://avnadmin:AVNS_YKoUmfA9pYTK3wIupNn@central-transfers-central-transfers.c.aivencloud.com:16880/defaultdb?sslmode=require"

engine = create_engine(DATABASE_URL)

try:
    conn = engine.connect()
    print("CONECTADO COM SUCESSO")
    conn.close()

except Exception as e:
    print("ERRO:")
    print(e)
