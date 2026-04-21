# Build and validate Central Transfers project

Write-Host "Building frontend..."
npm --prefix frontend run build

Write-Host "Building painel-saas..."
npm --prefix painel-saas run build

Write-Host "Validating backend Python syntax..."
$python = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
& $python -m py_compile backend\*.py backend\routes\*.py backend\services\*.py

Write-Host "Build and validation completed successfully."