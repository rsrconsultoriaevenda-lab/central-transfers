import requests
import time

# Para teste local, mude para: "http://127.0.0.1:8001/webhook"
# Para teste em produção (Railway):
# Ajustado para o prefixo da rota
BASE_URL = "https://sua-url-aqui.up.railway.app/whatsapp/webhook"

CLIENT_PHONE = "5554999999999"
# Certifique-se de cadastrar este motorista no painel antes
DRIVER_PHONE = "5554888888888"


def send_msg(sender, text):
    payload = {"sender": sender, "message": text}
    print(f"\n[Enviando de {sender} para {BASE_URL}]: {text}")
    resp = requests.post(BASE_URL, json=payload)
    print(f"[Resposta]: {resp.status_code} - {resp.text}")
    return resp.status_code


def run_test_flow():
    print("=== INICIANDO TESTE AUTOMATIZADO WHATSAPP ===")

    # 1. Criar pedido
    msg_pedido = "Pedido transfer origem: Aeroporto destino: Hotel data: 20/04/2026 14:00 valor: 250"
    send_msg(CLIENT_PHONE, msg_pedido)

    print("\n💡 Como o processamento é assíncrono (Background Task),")
    print("verifique o ID do pedido criado nos LOGS do Railway.")
    print("Depois, envie manualmente no WhatsApp ou use este script")
    print("com o ID fixo para testar os próximos passos.")

    # Exemplo de como testar passos específicos com ID conhecido:
    # pedido_id = 15
    # send_msg(CLIENT_PHONE, f"pago pedido {pedido_id}")
    # time.sleep(1)
    # send_msg(DRIVER_PHONE, f"aceito pedido {pedido_id}")

    print("\n=== FLUXO CONCLUÍDO ===")


if __name__ == "__main__":
    try:
        run_test_flow()
    except Exception as e:
        print(f"Erro ao conectar com o backend: {e}")
        print("Certifique-se de que o backend está rodando em http://127.0.0.1:8001")
