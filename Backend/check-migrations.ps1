# Verificar migraciones en Fly.io
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
Write-Host "Conectando a Fly.io..." -ForegroundColor Yellow
Write-Host "Ejecutando comando: python manage.py showmigrations" -ForegroundColor Gray
Write-Host ""
flyctl ssh console -C 'python manage.py showmigrations'
