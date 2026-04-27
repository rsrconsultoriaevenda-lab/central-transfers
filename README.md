Central Transfers — Documentação Oficial
🚀 Visão do Produto

O Central Transfers é uma plataforma SaaS para gestão e automação de operações de transporte e transferências, permitindo o controle completo de:

Clientes
Motoristas
Serviços
Pedidos de transporte
Operações via WhatsApp
Painel administrativo em tempo real

O sistema foi projetado para escalar operações de pequenas centrais até empresas estruturadas de logística e mobilidade.

🧠 Arquitetura do Sistema
🔷 Visão Geral
[ Frontend Cliente ]      →  React (Vite)
[ Painel Admin ]          →  React (Vite)
[ Backend API ]           →  FastAPI (Python)
[ Banco de Dados ]        →  PostgreSQL (Aiven / Cloud)
[ Integração WhatsApp ]   →  Meta API
🧱 Estrutura do Projeto
central-transfers/
│
├── backend/            # API principal (FastAPI)
│   ├── auth/           # autenticação JWT
│   ├── models/        # ORM (SQLAlchemy)
│   ├── routes/        # endpoints REST
│   ├── services/      # regras de negócio
│   └── database/      # conexão com PostgreSQL
│
├── frontend/           # portal do cliente
├── painel-saas/        # painel administrativo
├── seed_db.py          # dados iniciais
├── render.yaml         # deploy backend
└── README.md
🔐 Segurança e Autenticação
Sistema de autenticação

O sistema utiliza:

JWT (JSON Web Token)
Hash de senha (bcrypt)
Middleware de proteção de rotas
Fluxo:
Login → Validação → Geração JWT → Acesso protegido
Endpoints de autenticação
Método	Endpoint	Descrição
POST	/auth/register	Criação de usuário
POST	/auth/login	Login e token
GET	/auth/me	Dados do usuário autenticado
🗄️ Modelo de Dados
Entidades principais
👤 Clientes
id
nome
telefone
email
🚗 Motoristas
id
nome
telefone
carro
placa
status
🧾 Pedidos
cliente_id
motorista_id
origem
destino
data
valor
status
🔄 Fluxo de Operação
1. Criação de pedido
Cliente envia solicitação (web ou WhatsApp)
Sistema registra pedido
Status inicial: PENDENTE
2. Atribuição
Admin seleciona motorista
Pedido muda para ATRIBUÍDO
3. Execução
Motorista aceita corrida
Status: EM_EXECUÇÃO
4. Finalização
Serviço concluído
Status: FINALIZADO
📲 Integração WhatsApp
Visão

O sistema permite operação completa via WhatsApp utilizando Meta API.

Fluxo
Cliente → WhatsApp → Backend → Pedido criado → Resposta automática
Comandos suportados
criação de pedido via texto livre
confirmação de pagamento
aceite de corrida por motorista
Webhook
POST /whatsapp/incoming
🌐 API REST
Base URL
http://localhost:8000
Principais endpoints
Clientes
GET /clientes
POST /clientes
Motoristas
GET /motoristas
POST /motoristas
Serviços
GET /servicos
POST /servicos
Pedidos
GET /pedidos
POST /pedidos
PUT /pedidos/{id}/status
💻 Frontend (Cliente)
Responsabilidade

Interface para:

criação de pedidos
acompanhamento de status
visualização de serviços
Stack
React (Vite)
Axios
Tailwind CSS (opcional)
🧑‍💼 Painel Administrativo
Responsabilidade

Controle operacional completo:

gestão de clientes
gestão de motoristas
atribuição de pedidos
monitoramento em tempo real
🚀 Deploy em Produção
Backend (Render / Railway)
Start command:
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
Variáveis obrigatórias:
DATABASE_URL=
WHATSAPP_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_API_VERSION=
Frontend (Vercel / Netlify)
npm run build
Configuração de ambiente
VITE_API_URL=https://api.suaempresa.com
