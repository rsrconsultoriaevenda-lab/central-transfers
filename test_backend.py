import json
import sys
import urllib.error
import urllib.request

base = "http://127.0.0.1:8001"


def call(method, path, data=None):
    url = base + path
    body = None
    headers = {"Content-Type": "application/json"}
    if data is not None:
        body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode("utf-8")
            print(method, path, resp.status)
            if not text:
                return None
            return json.loads(text)
    except urllib.error.HTTPError as e:
        print("HTTP ERROR", method, path, e.code, e.read().decode("utf-8"))
        return None
    except Exception as exc:
        print("REQUEST FAILED", method, path, exc)
        return None


print("=== BACKEND TEST ===")
print("Health:", call("GET", "/"))
print("Fetching lists...")
clientes = call("GET", "/clientes") or []
motoristas = call("GET", "/motoristas") or []
servicos = call("GET", "/servicos") or []
pedidos = call("GET", "/pedidos") or []
print(f"Found {len(clientes)} clientes, {len(motoristas)} motoristas, {len(servicos)} servicos, {len(pedidos)} pedidos")

if not clientes:
    print("Criando cliente de teste...")
    call("POST", "/clientes", {"nome": "Cliente Teste",
         "telefone": "11999990000", "email": "teste@example.com"})

if not motoristas:
    print("Criando motorista de teste...")
    call("POST", "/motoristas", {"nome": "Motorista Teste", "telefone": "11999990000",
         "carro": "Gol", "placa": "ABC1234", "modelo": "2022", "ano": 2022})

if not servicos:
    print("Criando servico de teste...")
    call("POST", "/servicos", {"nome": "Transporte Teste",
         "tipo": "Aeroporto", "descricao": "Serviço de teste"})

print("Recarregando listas...")
clientes = call("GET", "/clientes") or []
motoristas = call("GET", "/motoristas") or []
servicos = call("GET", "/servicos") or []
pedidos = call("GET", "/pedidos") or []
print(f"After setup: {len(clientes)} clientes, {len(motoristas)} motoristas, {len(servicos)} servicos, {len(pedidos)} pedidos")

if not pedidos:
    print("Criando pedido de teste...")
    if not clientes or not servicos:
        print("Não foi possível criar pedido porque cliente ou servico está ausente")
    else:
        cliente_id = clientes[0].get("id")
        servico_id = servicos[0].get("id")
        call("POST", "/pedidos", {
            "cliente_id": cliente_id,
            "servico_id": servico_id,
            "origem": "Aeroporto",
            "destino": "Hotel",
            "data_servico": "2026-04-16T12:00:00",
            "valor": 150.0,
            "observacoes": "Pedido de teste",
        })

print("Recarregando pedidos...")
pedidos = call("GET", "/pedidos") or []
print(f"Total pedidos: {len(pedidos)}")
if pedidos:
    print("Pedido 0:", pedidos[0])
    if motoristas:
        pid = pedidos[0].get("id")
        mid = motoristas[0].get("id")
        if pid is not None and mid is not None:
            print("Atribuindo motorista ao pedido...", pid, mid)
            call("PUT", f"/pedidos/{pid}/aceitar", {"motorista_id": mid})
            pedidos = call("GET", "/pedidos") or []
            if pedidos:
                print("Pedido atualizado:", pedidos[0])
        else:
            print("Não foi possível atribuir motorista: id ausente")
    else:
        print("Não há motoristas para atribuir.")
print("=== TEST FINISHED ===")
