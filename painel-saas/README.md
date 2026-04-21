# Painel SaaS - Central Transfers

Este é o painel administrativo da Central Transfers para gerenciar pedidos, clientes, motoristas e serviços.

## Execução

No diretório `painel-saas`:

```powershell
npm install
npm run dev -- --host 127.0.0.1 --port 5174
```

Acesse: `http://127.0.0.1:5174`

## Backend esperado

O painel espera que o backend esteja rodando em:

- `http://127.0.0.1:8001`

### Endpoints usados

- `GET /pedidos`
- `PUT /pedidos/{pedido_id}/atribuir`
- `GET /clientes`
- `POST /clientes`
- `GET /motoristas`
- `POST /motoristas`
- `GET /servicos`
- `POST /servicos`

## Build de produção

```powershell
npm run build
```

O resultado será gerado em `painel-saas/dist`.
