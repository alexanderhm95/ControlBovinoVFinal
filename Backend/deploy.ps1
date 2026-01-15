# Script de Despliegue Rapido a Fly.io
# Ejecutar con: .\deploy.ps1

Write-Host "Iniciando despliegue a Fly.io..." -ForegroundColor Green
Write-Host ""

# 1. Actualizar PATH
Write-Host "Configurando PATH..." -ForegroundColor Yellow
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# 2. Verificar estado actual
Write-Host "Verificando estado de la aplicacion..." -ForegroundColor Yellow
flyctl status

Write-Host ""
Write-Host "Iniciando despliegue..." -ForegroundColor Cyan
Write-Host "Esto tomara aproximadamente 2-5 minutos..." -ForegroundColor Gray
Write-Host ""

# 3. Desplegar
flyctl deploy

Write-Host ""
Write-Host "Despliegue completado!" -ForegroundColor Green
Write-Host ""

# 4. Mostrar logs
Write-Host "Mostrando logs recientes..." -ForegroundColor Yellow
flyctl logs --lines 20

Write-Host ""
Write-Host "Tu aplicacion esta en: https://control-bovino-vfinal.fly.dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "Comandos utiles:" -ForegroundColor Yellow
Write-Host "   - Ver logs en tiempo real: .\logs.ps1" -ForegroundColor Gray
Write-Host "   - Abrir en navegador: .\open.ps1" -ForegroundColor Gray
Write-Host "   - Verificar migraciones: .\check-migrations.ps1" -ForegroundColor Gray
