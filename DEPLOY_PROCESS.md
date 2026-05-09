# Processo de Deploy Central Transfers

Este arquivo descreve o fluxo completo para publicar o projeto em produção.

## 1. Preparação local

1. Garanta que o backend esteja funcionando localmente:
   - `python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001`

## 2. Deploy do backend

### Railway (Backend & Database)

1. Crie um projeto Railway.
2. Adicione um serviço Python e conecte o repositório.
3. **Start Command (Crítico para WebSockets):**
   - `gunicorn -w 1 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:$PORT`
4. **Variáveis de Ambiente:**
   - `ENV=production`
   - `PYTHONPATH=.`
   - `DATABASE_URL` (Use a URL do PostgreSQL do próprio Railway)
   - `WHATSAPP_APP_SECRET`
   - `MERCADO_PAGO_WEBHOOK_SECRET`

## 3. Deploy do Frontend

### Vercel

1. Crie um novo projeto Vercel.
2. Selecione o repositório e escolha o diretório `painel-saas/`.
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
- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_API_VERSION`
- `MERCADO_PAGO_WEBHOOK_SECRET` (Crítico para segurança)
- `WHATSAPP_APP_SECRET` (Para validar assinaturas Meta)
- `VALIDATION_MODE=false` (Garante que bypass de login esteja desligado)

## 5.1 Checklist de Segurança Pré-Voo

1. [ ] As chaves do Mercado Pago são de PRODUÇÃO?
2. [ ] O `ALLOWED_ORIGINS` no backend está restrito aos domínios oficiais?
3. [ ] O banco de dados de produção tem backups automáticos ativados?
4. [ ] O webhook do WhatsApp foi testado com o App da Meta em modo "Live"?
5. [ ] **MIGRAÇÃO:** Rodou `alembic upgrade head` no ambiente de produção.
7. [ ] **MONITORAMENTO:** Endpoint `/health` adicionado ao UptimeRobot/Cron-job.

## 6. Testes finais

- Acesse o backend com `GET /`.
- Acesse o frontend e submeta um pedido.
- Acesse o painel e cadastre cliente/motorista/serviço.
- Atribua um motorista a um pedido e valide a API
