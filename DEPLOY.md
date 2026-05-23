# Deploy Central Transfers

Este guia descreve como hospedar o backend FastAPI e os dois frontends React.

## Estrutura de deploy

- `backend/` - API Python FastAPI
- `painel-saas/` - painel administrativo

## Backend

### 1. Escolha um serviço

Recomendado:
- Railway
- Fly

### 2. Configuração geral

- Diretório de deploy: `backend/`
- `backend/requirements.txt` já está pronto
- `Procfile` já está pronto:

```text
web: uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### 3. Variáveis de ambiente

> ⚠️ **AVISO DE SEGURANÇA:** Nunca adicione arquivos `.env` ao seu repositório Git. 
> Use o painel da plataforma (Render/Railway) para configurar os segredos.
> Adicione `.env` ao seu arquivo `.gitignore`.

Defina no serviço de hosting:
 
- `DATABASE_URL` (preferencial, formato `mysql+pymysql://user:pass@host:port/dbname?ssl_disabled=false`)
- OU, para configuração granular (usado como fallback se DATABASE_URL não for definida):
  - `DB_HOST`
  - `DB_PORT` (deve ser um número, ex: `3306`)
  - `DB_USER`
  - `DB_PASSWORD`
  - `DB_NAME`
- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_API_VERSION`

> Se estiver usando o banco de dados local apenas para desenvolvimento, use o `.env` local. Em produção, configure as variáveis pelo painel da plataforma.

### 4. Railway

1. Crie um novo projeto no Railway.
2. Conecte a pasta `backend/` ou importe o repositório inteiro.
3. Configure o comando de start como:
   - `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Adicione as variáveis de ambiente do banco e do WhatsApp.
5. Se usar MySQL gerenciado, configure o banco pelo Railway e use os valores gerados.

> Se preferir, use o arquivo `render.yaml` no root do projeto para configurar o backend e os sites estáticos `frontend` e `painel-saas` em uma única definição.

### 6. Fly

1. Crie um app no Fly.
2. Defina a raíz do projeto como `backend` em `fly.toml` ou no painel.
3. Use `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` como comando de start.
4. Defina as variáveis de ambiente com `fly secrets set DB_HOST=... DB_USER=...` etc.
5. Conecte um volume de banco de dados externo ou use um MySQL remoto.

## Frontend e Painel

### 1. Build local

No diretório `painel-saas/`:

```powershell
npm install
npm run build
```

### 2. Hospedar como site estático

Use:
- Vercel
- Netlify
- Cloudflare Pages

O projeto `painel-saas` centraliza as 3 interfaces do sistema.

> O projeto já inclui `_redirects` em `frontend/` e `painel-saas/` para suportar rotas de SPA em Netlify e Cloudflare Pages.

> O backend também inclui um `Dockerfile` em `backend/` para deploys baseados em container.

### 3. Variáveis de ambiente

Para cada site, configure:

- `VITE_API_URL` = URL pública do backend

Exemplo:

```text
VITE_API_URL=https://meu-backend.onrender.com
```

## Hospedagem nas plataformas

### Vercel

- Crie um novo projeto Vercel e importe o repositório.
- Selecione o diretório `frontend/` para o app cliente e `painel-saas/` para o painel.
- O comando de build é:
  - `npm run build`
- O diretório de saída é:
  - `dist`
- Configure a variável:
  - `VITE_API_URL`

### Netlify

- Crie um novo site e conecte o repositório.
- Defina a pasta base para `frontend/` ou `painel-saas/` conforme o projeto.
- Build command:
  - `npm run build`
- Publish directory:
  - `dist`
- Defina a variável de ambiente:
  - `VITE_API_URL`

### Cloudflare Pages

- Crie um novo projeto e escolha `frontend/` ou `painel-saas/`.
- Build command:
  - `npm run build`
- Output directory:
  - `dist`
- Configure `VITE_API_URL` nas Environment Variables.

## Ajustes de URL

As aplicações React já usam `import.meta.env.VITE_API_URL` e caem em `http://127.0.0.1:8001` como padrão. Portanto, em produção, o importante é definir `VITE_API_URL` no ambiente.

## Testes pós-deploy

- Acesse o backend e verifique `GET /`.
- Acesse o frontend e crie um pedido.
- Acesse o painel e cadastre um motorista ou serviço.

## Dicas rápidas

- Se usar Railway, conecte um banco de dados PostgreSQL/MySQL gerenciado e ajuste as variáveis de ambiente.
- Se usar Vercel, escolha `frontend` e `painel-saas` como projetos separados e adicione `VITE_API_URL` em cada um.
- Use o Swagger do backend em `/docs` para validar os endpoints.

### 1. Build local

No diretório `frontend/`:

```powershell
npm install
npm run build
```

No diretório `painel-saas/`:

```powershell
npm install
npm run build
```

### 2. Hospedar como site estático

Use:
- Vercel
- Netlify
- Cloudflare Pages

Cada repositório (`frontend` e `painel-saas`) pode ser deployado separadamente.

### 3. Variáveis de ambiente

Para cada site, configure:

- `VITE_API_URL` = URL pública do backend

Exemplo:

```text
VITE_API_URL=https://meu-backend.onrender.com
```

## Ajustes de URL

As aplicações React já usam `import.meta.env.VITE_API_URL` e caem em `http://127.0.0.1:8001` como padrão. Portanto, em produção, o importante é definir `VITE_API_URL` no ambiente.

## Testes pós-deploy

- Acesse o backend e verifique `GET /`.
- Acesse o frontend e crie um pedido.
- Acesse o painel e cadastre um motorista ou serviço.

## Dicas rápidas

- Se usar Railway, conecte um banco de dados PostgreSQL/MySQL gerenciado e ajuste as variáveis de ambiente.
- Se usar Vercel, escolha `frontend` e `painel-saas` como projetos separados e adicione `VITE_API_URL` em cada um.
- Use o Swagger do backend em `/docs` para validar os endpoints.
