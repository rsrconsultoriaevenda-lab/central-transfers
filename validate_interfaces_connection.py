import requests
import sys

BASE_URL = "http://localhost:8001"
ADMIN_EMAIL = "rsrconsultoriaevenda@gmail.com"
ADMIN_PASS = "Ren@220382"


def test_section(name):
    print(f"\n--- 🔍 Validando Interface: {name} ---")


def check(feature, response):
    if response.status_code in [200, 201]:
        print(f"✅ {feature}: OK ({response.status_code})")
        return True
    else:
        print(
            f"❌ {feature}: FALHOU ({response.status_code}) - {response.text[:100]}")
        return False


def run_unified_validation():
    print("🚀 Iniciando Teste Unificado de Conectividade")
    print("=" * 50)

    # 0. Health Check inicial
    try:
        requests.get(BASE_URL, timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"❌ ERRO CRÍTICO: Backend não encontrado em {BASE_URL}")
        print("Certifique-se de rodar 'python run_dev.py' antes.")
        sys.exit(1)

    # 1. INTERFACE: STORE (CLIENTE / PÚBLICO)
    test_section("STORE (Web/WhatsApp)")
    # A Store depende de listar serviços e criar pedidos/clientes
    res_servicos = requests.get(f"{BASE_URL}/servicos/")
    check("Catálogo de Serviços (Public)", res_servicos)

    # Simulação de Webhook do WhatsApp (Handshake)
    res_wp = requests.get(f"{BASE_URL}/whatsapp/incoming", params={
        "hub.mode": "subscribe",
        "hub.verify_token": "central_secret_token",
        "hub.challenge": "1234"
    })
    check("Conectividade Webhook WhatsApp", res_wp)

    # 2. INTERFACE: DASHBOARD (ADMIN / SAAS)
    test_section("DASHBOARD (Administrativo)")
    # Login Admin
    login_admin = requests.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL, "senha": ADMIN_PASS
    })

    if check("Autenticação Admin", login_admin):
        admin_token = login_admin.json().get("access_token")
        headers_admin = {"Authorization": f"Bearer {admin_token}"}

        # Estatísticas do Painel
        res_stats = requests.get(
            f"{BASE_URL}/dashboard/stats", headers=headers_admin)
        check("KPIs Financeiros / Stats", res_stats)

        # Listagem de Pedidos
        res_pedidos = requests.get(
            f"{BASE_URL}/pedidos/", headers=headers_admin)
        check("Gestão de Pedidos", res_pedidos)

    # 3. INTERFACE: DRIVER (MOTORISTA)
    test_section("DRIVER (App do Motorista)")

    # Vamos tentar logar com o padrão telefone@motorista.com
    # Primeiro listamos motoristas via admin para pegar um telefone real se existir
    motoristas = requests.get(
        f"{BASE_URL}/motoristas/", headers=headers_admin).json()

    if motoristas:
        m_tel = motoristas[0]['telefone']
        # Nota: O driver usa a mesma senha do admin no seed ou a cadastrada
        login_driver = requests.post(f"{BASE_URL}/auth/login", json={
            "email": f"{m_tel}@motorista.com", "senha": ADMIN_PASS
        })

        if login_driver.status_code == 200:
            driver_token = login_driver.json().get("access_token")
            headers_driver = {"Authorization": f"Bearer {driver_token}"}

            # Saldo Próprio
            res_saldo = requests.get(
                f"{BASE_URL}/motoristas/me/saldo", headers=headers_driver)
            check("Consulta de Saldo/Extrato", res_saldo)

            # Atualização de GPS
            res_gps = requests.post(f"{BASE_URL}/motoristas/localizacao",
                                    json={"latitude": -29.37,
                                          "longitude": -50.87},
                                    headers=headers_driver)
            check("Envio de Telemetria/GPS", res_gps)
        else:
            print(
                "⚠️ Pulando testes de Driver: Falha no login (Usuário pode não existir com senha padrão)")
    else:
        print("⚠️ Pulando testes de Driver: Nenhum motorista cadastrado no banco.")

    print("\n" + "=" * 50)
    print("🏁 Validação finalizada!")


if __name__ == "__main__":
    run_unified_validation()
