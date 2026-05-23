# Processo de Deploy Central Transfers

Este arquivo descreve o fluxo completo para publicar o projeto em produção.

## 1. Preparação local

1. Garanta que o backend esteja funcionando localmente:
   - `python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001`

## 2. Deploy do backend

### Railway (Backend & Database)

CMD sh -c "python -m alembic upgrade head && uvicorn backend.main:app ..."
1. Crie um projeto no Railway.
2. Adicione um serviço Python e conecte o repositório.
3. **Start Command (Crítico para WebSockets e Concorrência):**
   - `gunicorn -w 1 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:$PORT`
4. **Variáveis de Ambiente:**
   - `ENV=production`
   - `PYTHONPATH=.`
   - `DATABASE_URL` (Use a URL do PostgreSQL do próprio Railway)
   - `WHATSAPP_APP_SECRET`
   - `MERCADO_PAGO_WEBHOOK_SECRET`
   - `FRONTEND_URL=https://centraltransfers.com`
   - `SMTP_USER` / `SMTP_PASS` (Para e-mails reais)
   - `VAPID_PRIVATE_KEY` / `VAPID_PUBLIC_KEY`

### Configuração de Domínio (Railway)
1. Vá em **Settings > Domains**.
2. Adicione `api.centraltransfers.com`.
3. Configure o CNAME no seu DNS.

## 3. Deploy do Frontend

### Vercel

1. Crie um novo projeto Vercel.
2. Selecione o repositório e escolha o diretório `painel-saas/`.
4. Build command: `npm run build`
5. Output directory: `dist`
6. **Variáveis de Ambiente:**
   - `VITE_API_URL=https://api.centraltransfers.com`
   - `VITE_VAPID_PUBLIC_KEY` (Mesma do backend)

### Configuração de Domínio (Vercel)
1. Vá em **Settings > Domains**.
2. Adicione `centraltransfers.com` e `www.centraltransfers.com`.

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
8. [ ] **LOGS:** Configurar retenção de logs no Railway (mínimo 7 dias para auditoria financeira).
9. [ ] **BACKUP:** Ativar backups diários do PostgreSQL no Railway.

## 6. Testes finais

- Acesse o backend com `GET /`.
- Acesse o frontend e submeta um pedido.
- Acesse o painel e cadastre cliente/motorista/serviço.
- Atribua um motorista a um pedido e valide a API
