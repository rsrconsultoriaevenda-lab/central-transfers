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
clientes = call("GET", "/clientes/") or []
motoristas = call("GET", "/motoristas/") or []
servicos = call("GET", "/servicos/") or []
pedidos = call("GET", "/pedidos/") or []
print(f"Found {len(clientes)} clientes, {len(motoristas)} motoristas, {len(servicos)} servicos, {len(pedidos)} pedidos")

if not clientes:
    print("Criando cliente de teste...")
