# Central Transfers

Central Transfers é uma aplicação FastAPI + React para gerenciar pedidos de transfer, clientes, motoristas e serviços.

## Estrutura

- `backend/` - API FastAPI em Python
- `frontend/` - app de cliente para registrar pedidos
- `painel-saas/` - painel administrativo para gerenciar dados e atribuir motoristas

## Pré-requisitos

- Python 3.11+ (ou outra versão recente do Python 3)
- Node.js 18+ / npm
- MySQL rodando localmente

## Configuração do banco de dados

A API se conecta a um banco MySQL com estas configurações:

- host: `localhost`
- user: `root`
- password: `123456`
- database: `central_transfers`

Crie o banco e as tabelas necessárias antes de executar a aplicação.

### Exemplo de tabelas mínimas

```sql
CREATE DATABASE central_transfers;
USE central_transfers;

CREATE TABLE clientes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  telefone VARCHAR(100) NOT NULL,
  email VARCHAR(255)
);

CREATE TABLE motoristas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  telefone VARCHAR(100) NOT NULL,
  carro VARCHAR(255) NOT NULL,
  placa VARCHAR(50) NOT NULL,
  modelo VARCHAR(255) NOT NULL,
  ano INT NOT NULL
);

CREATE TABLE servicos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  tipo VARCHAR(255) NOT NULL,
  descricao TEXT NOT NULL
);

CREATE TABLE pedidos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  cliente_id INT NOT NULL,
  servico_id INT NOT NULL,
  motorista_id INT DEFAULT NULL,
  origem VARCHAR(255) NOT NULL,
  destino VARCHAR(255) NOT NULL,
  data_servico DATETIME NOT NULL,
  valor DECIMAL(10,2) NOT NULL,
  observacoes TEXT,
  status VARCHAR(50) DEFAULT 'PENDENTE',
  FOREIGN KEY (cliente_id) REFERENCES clientes(id),
  FOREIGN KEY (servico_id) REFERENCES servicos(id),
  FOREIGN KEY (motorista_id) REFERENCES motoristas(id)
);
```

## Backend

1. Abra um terminal no diretório raiz `central-transfers`
2. Crie e ative o ambiente virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Instale as dependências do backend:

```powershell
pip install fastapi uvicorn mysql-connector-python pydantic requests sqlalchemy passlib "bcrypt<4.0.0" python-multipart python-dotenv
```

4. Configure o WhatsApp (opcional, necessário para envio de notificações e recepção de pedidos via WhatsApp):

- Crie um arquivo `backend/.env` com estas variáveis:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=central_transfers
WHATSAPP_TOKEN=SEU_TOKEN_REAL
WHATSAPP_PHONE_NUMBER_ID=SEU_PHONE_NUMBER_ID
WHATSAPP_API_VERSION=v20.0
```

- O backend carrega automaticamente `backend/.env` se existir, e também aceita variáveis de ambiente do sistema.

5. Execute a API:

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8001
```

A API estará disponível em `http://127.0.0.1:8001` e o Swagger em `http://127.0.0.1:8001/docs`.

## Frontend

No diretório `frontend/`:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

A interface do cliente ficará disponível em `http://127.0.0.1:5173`.

## Painel SaaS

No diretório `painel-saas/`:

```powershell
cd painel-saas
npm install
npm run dev -- --host 127.0.0.1 --port 5174
```

O painel administrativo ficará disponível em `http://127.0.0.1:5174`.

## Comandos de build

```powershell
npm --prefix frontend run build
npm --prefix painel-saas run build
```

### Build e validação automática

Para compilar ambos os frontends e validar o backend Python em um só comando, use:

```powershell
.\build-all.ps1
```

## Deploy e hospedagem inicial

### Hospedagem gratuita recomendada
- Frontend e painel: Vercel, Netlify ou Cloudflare Pages (sites estáticos gerados por `npm run build`).
- Backend: Railway, Render ou Fly (serviço Python com `backend/requirements.txt` e `backend/Procfile`).

> Recomendado para entrega final: backend em `Render` e frontends em `Vercel`.

### Passo a passo inicial
1. Faça deploy do backend em um serviço gratuito Python.
   - Use `backend/requirements.txt`.
   - Configure o comando de inicialização: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.
   - Configure as variáveis de ambiente no serviço:
     - `DB_HOST`
     - `DB_PORT`
     - `DB_USER`
     - `DB_PASSWORD`
     - `DB_NAME`
     - `WHATSAPP_TOKEN`
     - `WHATSAPP_PHONE_NUMBER_ID`
     - `WHATSAPP_API_VERSION`
2. Faça deploy do `frontend/` e do `painel-saas/` como sites estáticos.
   - Cada site deve apontar para a URL pública do backend.
   - Configure `VITE_API_URL` no ambiente de build para a URL do backend público.
   - Exemplo: `VITE_API_URL=https://meu-backend.onrender.com`.
   - Se preferir, use `frontend/.env.example` e `painel-saas/.env.example` como referência.
3. Verifique os endpoints após o deploy.
   - Backend: `GET /` deve retornar `{ "status": "ok" }`.
   - Frontend: formulário de pedido e listagem de serviços.
   - Painel: cadastro de clientes, motoristas, serviços e atribuição de pedidos.

### Fluxo de teste rápido local
- Backend: `http://127.0.0.1:8001`
- Frontend: `http://127.0.0.1:5173`
- Painel admin: `http://127.0.0.1:5174`

### Expôr localmente sem hospedagem
- Para testes rápidos, use um túnel como `ngrok` ou `cloudflared` para expor seu backend local e/ou frontends.
- **AVISO:** O túnel (ngrok) é apenas para desenvolvimento. Se o computador for desligado, a integração para.
- Se o comando `ngrok` não for reconhecido, use o Node.js para rodar:
```powershell
npx ngrok http 8001
```
- Copie a URL `https` gerada e use-a na configuração do Webhook da Meta.

> Para o passo a passo completo de deploy, veja `DEPLOY_PROCESS.md`.

## Endpoints principais

- `GET /clientes`
- `POST /clientes`
- `GET /motoristas`
- `POST /motoristas`
- `GET /servicos`
- `POST /servicos`
- `GET /pedidos`
- `GET /pedidos/{pedido_id}`
- `POST /pedidos`
- `POST /pedidos/{pedido_id}/anunciar`
- `PUT /pedidos/{pedido_id}/atribuir`
- `PUT /pedidos/{pedido_id}/aceitar`
- `PUT /pedidos/{pedido_id}/status`
- `POST /whatsapp/incoming` (recebe pedidos via WhatsApp, confirma pagamento e aceita serviço)

### Uso WhatsApp
- Cliente pode enviar pedido em formato livre com `origem:`, `destino:`, `data:` e `valor:`.
- Para pagar, a central poderá usar PIX ou transferência bancária.
- Dados da central são enviados automaticamente na resposta do WhatsApp ao criar o pedido.
- Para confirmar pagamento, envie `pago pedido <id>`.
- Motorista cadastrado pode aceitar serviço usando `aceito pedido <id>`.

## Observações

- Ajuste as configurações de conexão MySQL em `backend/database.py` caso use outro usuário, senha ou host.
- O frontend e painel usam `http://127.0.0.1:8001` como backend padrão.
