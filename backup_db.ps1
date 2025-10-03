# Script de PowerShell para backup de base de datos SQLite
# Uso: .\backup_db.ps1

param(
    [switch]$AutoCommit = $false
)

# Configuración
$dbFile = "db.sqlite3"
$backupDir = "backups"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "$backupDir\db_backup_$timestamp.sqlite3"

# Crear directorio de backups si no existe
if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    Write-Host "📁 Directorio de backups creado: $backupDir" -ForegroundColor Green
}

# Verificar si existe la base de datos
if (!(Test-Path $dbFile)) {
    Write-Host "❌ Error: No se encontró el archivo $dbFile" -ForegroundColor Red
    exit 1
}

# Crear backup
Write-Host "📁 Creando backup de la base de datos..." -ForegroundColor Yellow
try {
    Copy-Item $dbFile $backupFile
    Write-Host "✅ Backup creado exitosamente: $backupFile" -ForegroundColor Green
    
    # Mostrar tamaño del archivo
    $size = (Get-Item $backupFile).Length
    $sizeFormatted = if ($size -gt 1MB) { 
        "{0:N2} MB" -f ($size / 1MB) 
    } elseif ($size -gt 1KB) { 
        "{0:N2} KB" -f ($size / 1KB) 
    } else { 
        "$size bytes" 
    }
    Write-Host "📊 Tamaño del backup: $sizeFormatted" -ForegroundColor Cyan
    
    # Limpiar backups antiguos (mantener solo los últimos 30)
    Write-Host "🧹 Limpiando backups antiguos..." -ForegroundColor Yellow
    $oldBackups = Get-ChildItem "$backupDir\db_backup_*.sqlite3" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 30
    if ($oldBackups) {
        $oldBackups | Remove-Item
        Write-Host "🗑️ Eliminados $($oldBackups.Count) backups antiguos" -ForegroundColor Yellow
    }
    
    $remainingBackups = (Get-ChildItem "$backupDir\db_backup_*.sqlite3").Count
    Write-Host "📋 Backups restantes: $remainingBackups" -ForegroundColor Cyan
    
    # Opcional: Agregar al git
    $commitMessage = $null
    if ($AutoCommit) {
        $commitMessage = "Backup automático de base de datos - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    } else {
        $response = Read-Host "¿Deseas agregar el backup al repositorio git? (y/N)"
        if ($response -match "^[Yy]") {
            $commitMessage = "Backup manual de base de datos - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        }
    }
    
    if ($commitMessage) {
        git add $backupFile
        git commit -m $commitMessage
        Write-Host "✅ Backup agregado al repositorio" -ForegroundColor Green
        
        if ($AutoCommit) {
            git push
            Write-Host "✅ Backup subido al repositorio remoto" -ForegroundColor Green
        } else {
            $pushResponse = Read-Host "¿Deseas hacer push al repositorio remoto? (y/N)"
            if ($pushResponse -match "^[Yy]") {
                git push
                Write-Host "✅ Backup subido al repositorio remoto" -ForegroundColor Green
            }
        }
    }
    
} catch {
    Write-Host "❌ Error al crear el backup: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Proceso de backup completado" -ForegroundColor Green