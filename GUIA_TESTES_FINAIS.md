# 🧪 GUIA DE TESTES FINAIS - Central Transfers

**Objetivo:** Validar que o backend está pronto, frontend-backend estão comunicando, e dados estão sendo persistidos.

---

## 📋 PRÉ-REQUISITOS

✅ Verifique que você tem:
- [ ] Python 3.11+ instalado
- [ ] `.env` configurado na raiz do projeto
- [ ] PostgreSQL conectado (ou SQLite local)
- [ ] Dependências instaladas: `pip install -r backend/requirements.txt`

---

## 🚀 PASSO 1: DIAGNÓSTICO INICIAL

```bash
# Terminal 1: Validar banco de dados
python diagnose_database.py
```

**Esperado:**
```
✅ Conexão bem-sucedida com PostgreSQL
✅ Usuario              →      1 registros
✅ Motorista            →     10 registros  
✅ Cliente              →     20 registros
✅ Pedido               →     50 registros
✅ Servico              →      5 registros
```

Se estiver vazio, execute:
```bash
python seed_db.py  # Popula dados iniciais
```

---

## 🚀 PASSO 2: INICIAR O BACKEND

```bash
# Terminal 1: Backend rodando
python run_dev.py
```

**Esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Press CTRL+C to quit
```

---

## 🚀 PASSO 3: TESTAR O FRONTEND

```bash
# Terminal 2: Execute o frontend ou painel local
cd painel-saas
npm install
npm run dev
```

Verifique se o `VITE_API_URL` está apontando para `http://127.0.0.1:8001`.

---

## 📌 DICAS DE RECUPERAÇÃO

### "Testes falhando com imports"
```bash
pip install -r backend/requirements.txt
```

### "Login falhando"
```bash
python backend/setup_admin.py
```

---

## 📊 RESUMO ESPERADO

Quando tudo está funcionando, você deve ver:

```
✅ Backend online e respondendo
✅ Banco de dados conectado
✅ Autenticação JWT funcionando
✅ Endpoints REST respondendo
✅ Criar motoristas/pedidos via API
```
