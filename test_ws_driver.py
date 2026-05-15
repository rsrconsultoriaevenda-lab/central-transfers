import asyncio
import websockets
import json
import sys


async def simulate_driver(motorista_id):
    # URL do seu backend. Ajuste para localhost ou sua URL do Railway
    uri = f"ws://localhost:8001/ws/{motorista_id}"

    print(f"🚀 Iniciando simulador de motorista (ID: {motorista_id})")
    print(f"🔗 Conectando a {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conexão estabelecida! O motorista está ONLINE.")
            print("⏳ Aguardando notificações de novos pedidos em tempo real...")

            while True:
                try:
                    # Aguarda mensagens enviadas pelo ConnectionManager
                    message = await websocket.recv()
                    data = json.loads(message)

                    print("\n" + "="*40)
                    print("🔔 NOTIFICAÇÃO RECEBIDA!")
                    print(f"Tipo: {data.get('type')}")
                    print(f"Mensagem: {data.get('mensagem')}")
                    if 'valor' in data:
                        print(f"Valor: R$ {data['valor']}")
                    print("="*40)
                except websockets.exceptions.ConnectionClosed:
                    print("❌ Conexão encerrada pelo servidor.")
                    break
    except Exception as e:
        print(f"💥 Erro ao conectar: {e}")

if __name__ == "__main__":
    id_teste = sys.argv[1] if len(sys.argv) > 1 else 1
    asyncio.run(simulate_driver(id_teste))
