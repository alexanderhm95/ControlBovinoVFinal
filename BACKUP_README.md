# Documentación del Sistema de Backup para Base de Datos SQLite

## 📁 Estructura de Archivos

- `.github/workflows/backup-database.yml` - GitHub Action para backup automático diario
- `backup_db.sh` - Script de bash para backup manual (Linux/Mac)  
- `backup_db.ps1` - Script de PowerShell para backup manual (Windows)
- `temp_car/management/commands/backup_db.py` - Comando Django personalizado
- `backups/` - Directorio donde se almacenan los backups

## 🚀 Métodos de Backup

### 1. Backup Automático Diario (GitHub Actions)
- Se ejecuta automáticamente todos los días a las 2:00 AM UTC
- Mantiene los últimos 30 backups
- Se puede ejecutar manualmente desde GitHub Actions

### 2. Comando Django
```bash
# Backup básico
python manage.py backup_db

# Backup con commit automático
python manage.py backup_db --auto-commit

# Personalizar número de backups a mantener
python manage.py backup_db --max-backups 50
```

### 3. Script PowerShell (Windows)
```powershell
# Backup manual
.\backup_db.ps1

# Backup con commit automático
.\backup_db.ps1 -AutoCommit
```

### 4. Script Bash (Linux/Mac)
```bash
# Hacer ejecutable (solo la primera vez)
chmod +x backup_db.sh

# Ejecutar backup
./backup_db.sh
```

## 📅 Programación Recomendada

### Para desarrollo activo:
- Backup manual antes de cambios importantes
- Backup automático diario via GitHub Actions

### Para producción:
- Backup diario automático
- Backup manual antes de actualizaciones

## 🔄 Restauración de Backup

Para restaurar un backup:
```bash
# Detener la aplicación
# Copiar el backup deseado
cp backups/db_backup_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3
# Reiniciar la aplicación
```

## 📊 Monitoreo

- Los backups se almacenan en el directorio `backups/`
- Cada backup incluye timestamp para fácil identificación
- Se mantienen automáticamente solo los últimos 30 backups
- Tamaño del archivo se reporta en cada backup

## ⚠️ Consideraciones Importantes

1. **SQLite en Producción**: Para aplicaciones con alto tráfico, considera migrar a PostgreSQL
2. **Tamaño de Repositorio**: Los backups aumentan el tamaño del repositorio
3. **Seguridad**: No incluyas datos sensibles en repositorios públicos
4. **Frecuencia**: Ajusta la frecuencia según tus necesidades

## 🔧 Configuración Personalizada

### Cambiar horario del backup automático:
Edita `.github/workflows/backup-database.yml` línea con `cron:`

### Cambiar ubicación de backups:
Modifica la variable `BACKUP_DIR` en los scripts

### Cambiar retención de backups:
Modifica el parámetro `--max-backups` o las líneas que eliminan archivos antiguos