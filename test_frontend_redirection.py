import webbrowser
import urllib.parse
import argparse


def test_success_redirection(frontend_url, pedido_id):
    """
    Simula o redirecionamento que o Mercado Pago faz após um pagamento aprovado.
    """
    # Parâmetros que o Mercado Pago costuma enviar na query string
    params = {
        "collection_id": "5500112233",
        "collection_status": "approved",
        "payment_id": "5500112233",
        "status": "approved",
        "external_reference": str(pedido_id),
        "payment_type": "credit_card",
        "merchant_order_id": "1122334455",
        "preference_id": "66778899-pref-id",
        "site_id": "MLB",
        "processing_mode": "aggregator",
        "merchant_account_id": "null"
    }

    # Garante que a URL termine com /success ou o path correto
    if not frontend_url.endswith("/success"):
        frontend_url = frontend_url.rstrip("/") + "/success"

    query_string = urllib.parse.urlencode(params)
    full_url = f"{frontend_url}?{query_string}"

    print("\n=== Simulando Redirecionamento Mercado Pago ===")
    print(f"URL de Destino: {full_url}")
    print(f"Pedido ID Sendo Testado: {pedido_id}")
    print("\nAbrindo navegador...")

    webbrowser.open(full_url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Testa o redirecionamento de sucesso do frontend.")
    parser.add_argument("--url", type=str, default="http://localhost:5173/success",
                        help="URL da página de sucesso do seu frontend (default: localhost:5173/success)")
    parser.add_argument("--id", type=int, default=1,
                        help="ID do pedido para simular no external_reference (default: 1)")

    args = parser.parse_args()

    try:
        test_success_redirection(args.url, args.id)
    except Exception as e:
        print(f"Erro ao executar o teste: {e}")

    print("\nSe o seu frontend usa React Router, verifique se a rota '/success' está preparada para ler os SearchParams.")
