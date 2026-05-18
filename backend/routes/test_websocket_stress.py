import asyncio
import websockets
import json

async def simulate_driver(driver_id):
    # Alterado para apontar para a rota de isolamento limpa no main.py usando IPv4 direto
    uri = f"ws://127.0.0.1:8001/ws/teste_limpo/{driver_id}"

    # Forçamos o Origin para evitar que o Starlette barre o aperto de mão (handshake)
    custom_headers = {
        "Origin": "http://127.0.0.1:8001"
    }

    try:
        # Conexão usando o parâmetro correto 'additional_headers'
        async with websockets.connect(uri, additional_headers=custom_headers) as websocket:
            print(f"✅ Motorista {driver_id} conectado com sucesso na rota de teste.")

            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print(f"🔔 Motorista {driver_id} recebeu: {data.get('type', 'SISTEMA')} - {data.get('mensagem', '')}")

    except Exception as e:
        print(f"❌ Erro no motorista {driver_id}: {e}")

async def main():
    # Inicia o teste em lote para os motoristas de 1 a 5
    drivers = [simulate_driver(i) for i in range(1, 6)]
    await asyncio.gather(*drivers)

if __name__ == "__main__":
    print("🚀 Iniciando teste de stress na rota de isolamento...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Teste encerrado pelo usuário.")