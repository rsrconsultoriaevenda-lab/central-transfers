# Frontend - Central Transfers

Este é o aplicativo de cliente da Central Transfers. Ele consome a API do backend para listar e criar pedidos de transferência.

## Execução

No diretório `frontend`:

```powershell
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Acesse: `http://127.0.0.1:5173`

## Backend esperado

O frontend espera que o backend esteja rodando em:

- `http://127.0.0.1:8001`

### Endpoints usados

- `GET /pedidos`
- `POST /pedidos`
- `GET /clientes`
- `GET /servicos`

## Build de produção

```powershell
npm run build
```

O resultado será gerado em `frontend/dist`.
