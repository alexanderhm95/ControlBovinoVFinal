# Ver logs en tiempo real
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
Write-Host "Logs en tiempo real (Ctrl+C para salir)..." -ForegroundColor Yellow
flyctl logs
