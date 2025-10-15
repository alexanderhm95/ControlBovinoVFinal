# Abrir aplicacion en el navegador
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
Write-Host "Abriendo aplicacion en el navegador..." -ForegroundColor Cyan
fly apps open
