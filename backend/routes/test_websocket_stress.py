import asyncio
import websockets
import json


async def simulate_driver(driver_id):
    uri = f"ws://localhost:8001/ws/notifications/{driver_id}"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Motorista {driver_id} conectado.")
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print(
                    f"🔔 Motorista {driver_id} recebeu: {data['type']} - {data.get('mensagem', '')}")
    except Exception as e:
        print(f"❌ Erro no motorista {driver_id}: {e}")


async def main():
    # Simula 5 motoristas conectando simultaneamente
    drivers = [simulate_driver(i) for i in range(1, 6)]
    await asyncio.gather(*drivers)

if __name__ == "__main__":
    print("🚀 Iniciando teste de stress de WebSockets...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTeste encerrado.")
