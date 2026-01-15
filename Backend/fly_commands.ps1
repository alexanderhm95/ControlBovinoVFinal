# Script de comandos rápidos para Fly.io
# Usar: .\fly_commands.ps1 [comando]

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

$APP_NAME = "control-bovino-vfinal"

function Show-Help {
    Write-Host "`n=== Comandos Fly.io para Control Bovino ===" -ForegroundColor Cyan
    Write-Host "`nUso: .\fly_commands.ps1 [comando]`n" -ForegroundColor Yellow
    
    Write-Host "Comandos disponibles:" -ForegroundColor Green
    Write-Host "  deploy       - Desplegar la aplicación"
    Write-Host "  logs         - Ver logs en tiempo real"
    Write-Host "  status       - Ver estado de la aplicación"
    Write-Host "  open         - Abrir la aplicación en el navegador"
    Write-Host "  ssh          - Conectar por SSH a la aplicación"
    Write-Host "  migrate      - Ejecutar migraciones"
    Write-Host "  createsuperuser - Crear superusuario"
    Write-Host "  restart      - Reiniciar la aplicación"
    Write-Host "  scale        - Ver opciones de escalado"
    Write-Host "  secrets      - Ver variables de entorno"
    Write-Host "  dashboard    - Abrir dashboard en navegador"
    Write-Host "  help         - Mostrar esta ayuda`n"
}

function Deploy-App {
    Write-Host "`nDesplegando aplicación..." -ForegroundColor Green
    flyctl deploy
}

function Show-Logs {
    Write-Host "`nMostrando logs (Ctrl+C para salir)..." -ForegroundColor Green
    flyctl logs
}

function Show-Status {
    Write-Host "`nEstado de la aplicación:" -ForegroundColor Green
    flyctl status --app $APP_NAME
}

function Open-App {
    Write-Host "`nAbriendo aplicación en el navegador..." -ForegroundColor Green
    flyctl open --app $APP_NAME
}

function Connect-SSH {
    Write-Host "`nConectando por SSH..." -ForegroundColor Green
    flyctl ssh console --app $APP_NAME
}

function Run-Migrate {
    Write-Host "`nEjecutando migraciones..." -ForegroundColor Green
    flyctl ssh console --app $APP_NAME -C "python manage.py migrate"
}

function Create-SuperUser {
    Write-Host "`nCreando superusuario..." -ForegroundColor Green
    flyctl ssh console --app $APP_NAME -C "python manage.py createsuperuser"
}

function Restart-App {
    Write-Host "`nReiniciando aplicación..." -ForegroundColor Green
    flyctl apps restart $APP_NAME
}

function Show-Scale {
    Write-Host "`nOpciones de escalado:" -ForegroundColor Green
    Write-Host "`nEscalar memoria:"
    Write-Host "  flyctl scale memory 1024 --app $APP_NAME"
    Write-Host "  flyctl scale memory 2048 --app $APP_NAME"
    Write-Host "`nEscalar CPU:"
    Write-Host "  flyctl scale cpu 1 --app $APP_NAME"
    Write-Host "  flyctl scale cpu 2 --app $APP_NAME"
    Write-Host "`nEscalar instancias:"
    Write-Host "  flyctl scale count 1 --app $APP_NAME"
    Write-Host "  flyctl scale count 2 --app $APP_NAME"
}

function Show-Secrets {
    Write-Host "`nVariables de entorno configuradas:" -ForegroundColor Green
    flyctl secrets list --app $APP_NAME
}

function Open-Dashboard {
    Write-Host "`nAbriendo dashboard..." -ForegroundColor Green
    flyctl dashboard --app $APP_NAME
}

# Ejecutar comando
switch ($Command.ToLower()) {
    "deploy" { Deploy-App }
    "logs" { Show-Logs }
    "status" { Show-Status }
    "open" { Open-App }
    "ssh" { Connect-SSH }
    "migrate" { Run-Migrate }
    "createsuperuser" { Create-SuperUser }
    "restart" { Restart-App }
    "scale" { Show-Scale }
    "secrets" { Show-Secrets }
    "dashboard" { Open-Dashboard }
    "help" { Show-Help }
    default {
        Write-Host "`nComando no reconocido: $Command" -ForegroundColor Red
        Show-Help
    }
}
