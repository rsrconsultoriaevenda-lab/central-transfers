import requests
import time

BASE_URL = "http://127.0.0.1:8001/whatsapp/incoming"
CLIENT_PHONE = "5554999999999"
# Certifique-se de cadastrar este motorista no painel antes
DRIVER_PHONE = "5554888888888"


def send_msg(sender, text):
    payload = {"sender": sender, "message": text}
    print(f"\n[Enviando de {sender}]: {text}")
    resp = requests.post(BASE_URL, json=payload)
    print(f"[Resposta]: {resp.status_code} - {resp.json()}")
    return resp.json()


def run_test_flow():
    print("=== INICIANDO TESTE AUTOMATIZADO WHATSAPP ===")

    # 1. Criar pedido
    msg_pedido = "Pedido transfer origem: Aeroporto destino: Hotel data: 20/04/2026 14:00 valor: 250"
    res = send_msg(CLIENT_PHONE, msg_pedido)
    pedido_id = res.get("pedido_id")

    if not pedido_id:
        print("Falha ao criar pedido.")
        return

    time.sleep(1)

    # 2. Confirmar Pagamento
    msg_pago = f"pago pedido {pedido_id}"
    send_msg(CLIENT_PHONE, msg_pago)

    time.sleep(1)

    # 3. Motorista Aceitar (Simulando que o motorista já existe no DB com esse telefone)
    msg_aceito = f"aceito pedido {pedido_id}"
    send_msg(DRIVER_PHONE, msg_aceito)

    print("\n=== FLUXO CONCLUÍDO ===")


if __name__ == "__main__":
    try:
        run_test_flow()
    except Exception as e:
        print(f"Erro ao conectar com o backend: {e}")
        print("Certifique-se de que o backend está rodando em http://127.0.0.1:8001")
