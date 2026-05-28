# [SISTEMA] Script de Deploy Automatizado - Central Transfers

$ErrorActionPreference = "Stop"

Write-Host "`n--- 🔍 [1/3] Iniciando Auditoria e Validação ---" -ForegroundColor Cyan
try {
    .\build-all.ps1
} catch {
    Write-Host "`n❌ Falha na validação. O deploy foi cancelado para sua segurança." -ForegroundColor Red
    exit
}

Write-Host "`n--- 📝 [2/3] Preparando Git Commit ---" -ForegroundColor Cyan
$msg = Read-Host "Digite a mensagem do commit (ou pressione Enter para 'update: general improvements')"
if (-not $msg) { $msg = "update: general improvements" }

Write-Host "`n--- 📤 [3/3] Enviando para Produção (GitHub -> Render/Vercel) ---" -ForegroundColor Cyan
git add .
git commit -m "$msg"
git push origin main

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host "✅ DEPLOY INICIADO COM SUCESSO!" -ForegroundColor Green
Write-Host "O Render e a Vercel estão processando as mudanças." -ForegroundColor Green
Write-Host "Acompanhe os logs nos painéis das plataformas." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "[DICA]: Use python diagnose_database.py em 2 minutos para checar o banco." -ForegroundColor Gray