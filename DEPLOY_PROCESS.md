# Processo de Deploy Central Transfers

Este arquivo descreve o fluxo completo para publicar o projeto em produção.

## 1. Preparação local

1. Garanta que o backend esteja funcionando localmente:
   - `python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8001`
2. Garanta que os frontends compilem:
   - `npm --prefix painel-saas run build`
3. Verifique se o backend compila:
   - `python -m py_compile backend/*.py backend/routes/*.py backend/services/*.py`

## 2. Deploy do backend

> Recomendado para produção: backend em Render e frontends em Vercel.

### Render (recomendado)

1. Crie uma conta em Render e faça login.
2. Crie um novo serviço do tipo `Web Service`.
3. Aponte para o repositório e selecione a raiz do projeto.
4. Configure a pasta de deploy como `backend/`.
5. Comando de start:
   - `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6. Configure variáveis de ambiente:
   - `DB_HOST`
   - `DB_PORT`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME`
   - `WHATSAPP_TOKEN`
   - `WHATSAPP_PHONE_NUMBER_ID`
   - `WHATSAPP_API_VERSION`
7. Valide que `GET /` responde `{"status": "ok"}`.

### Railway (alternativa)

1. Crie um projeto Railway.
2. Adicione um serviço Python e conecte o repositório.
3. Use o comando de start:
   - `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. **Atenção à Região:** Evite `EU West (Amsterdam)` em caso de instabilidade de volumes. Prefira `US East`.
5. Adicione as mesmas variáveis de ambiente.
6. Use um banco MySQL gerenciado do Railway, se preferir.

### Fly (alternativa)

1. Crie um app no Fly.
2. Use o `backend/fly.toml` gerado ou configure manualmente.
3. Configure o start command:
   - `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Defina `fly secrets set` para as variáveis de ambiente.

### Deploy com Docker

1. Se quiser um deploy em container, use o arquivo `backend/Dockerfile`.
2. Ele cria uma imagem Python baseada em `python:3.11-slim` e expõe a porta `8000`.
3. O comando final do container é:
   - `uvicorn backend.main:app --host 0.0.0.0 --port 8000`

## 3. Deploy das Interfaces (SaaS / Cliente / Motorista)

### Vercel

1. Crie um novo projeto Vercel.
2. Selecione o repositório e escolha o diretório `painel-saas/`.
3. Este projeto contém as 3 interfaces:
   - `/store` -> Cliente
   - `/driver` -> Motorista
   - `/dashboard` -> Administrador
4. Build command: `npm run build`
5. Output directory: `dist`
6. Configure a variável `VITE_API_URL` para a URL pública do backend.

## 5. Configuração das variáveis de ambiente

Defina em cada deploy de site estático:

- `VITE_API_URL=https://seu-backend-publico`

Defina no backend:

- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `WHATSAPP_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_API_VERSION`

## 6. Testes finais

- Acesse o backend com `GET /`.
- Acesse o frontend e submeta um pedido.
- Acesse o painel e cadastre cliente/motorista/serviço.
- Atribua um motorista a um pedido e valide a API.
