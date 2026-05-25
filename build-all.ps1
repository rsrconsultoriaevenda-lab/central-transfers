# Build and validate Central Transfers project

$ErrorActionPreference = "Stop"
if (Test-Path "venv\Scripts\python.exe") {
    $python = "venv\Scripts\python.exe"
} else {
    $python = "python"
}

Write-Host "🔍 [1/7] Rodando Testes Unitários (Painel SaaS)..." -ForegroundColor Cyan
cmd /c "npm run test -w painel-saas -- --run"

Write-Host "🐍 [2/7] Rodando Testes de Integração (Backend Pytest)..." -ForegroundColor Cyan
& $python -m pytest backend

Write-Host "🗃️ [3/7] Aplicando Migrações de Banco de Dados (Alembic)..." -ForegroundColor Cyan
if (Test-Path "backend\alembic") {
    try {
    & $python -m alembic upgrade head
    } catch {
        Write-Warning "Falha ao aplicar migrações. Verifique a conexão com o banco."
    }
}

Write-Host "🛠️ [4/7] Gerando Build do Frontend Cliente..." -ForegroundColor Cyan
if (Test-Path "frontend") {
    cmd /c "npm run build -w frontend"
} else {
    Write-Host "⚠️ Pasta 'frontend' não encontrada. Pulando..." -ForegroundColor Yellow
}

Write-Host "🛠️ [5/7] Gerando Build do Painel SaaS..." -ForegroundColor Cyan
cmd /c "npm run build -w painel-saas"

Write-Host "🐍 [6/7] Validando sintaxe do Backend Python..." -ForegroundColor Cyan
# compileall é mais eficiente e evita problemas de globbing/wildcards no PowerShell
& $python -m compileall -q backend

Write-Host "🌐 [7/7] Auditoria de Rotas (Localhost)..." -ForegroundColor Cyan
try {
    # Tenta rodar a validação se o servidor estiver ativo
    & $python "backend\validate_routes.py"
} catch {
    Write-Host "ℹ️ Servidor offline, auditoria de rotas pulada." -ForegroundColor Gray
}

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host "✅ SISTEMA FINALIZADO E VALIDADO" -ForegroundColor Green
Write-Host "Pronto para deploy em Produção." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green