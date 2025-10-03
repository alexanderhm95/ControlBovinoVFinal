#!/bin/bash

# Script para hacer backup manual de la base de datos SQLite
# Uso: ./backup_db.sh

# Configuración
DB_FILE="db.sqlite3"
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sqlite3"

# Crear directorio de backups si no existe
mkdir -p "${BACKUP_DIR}"

# Verificar si existe la base de datos
if [ ! -f "${DB_FILE}" ]; then
    echo "❌ Error: No se encontró el archivo ${DB_FILE}"
    exit 1
fi

# Crear backup
echo "📁 Creando backup de la base de datos..."
cp "${DB_FILE}" "${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    echo "✅ Backup creado exitosamente: ${BACKUP_FILE}"
    
    # Mostrar tamaño del archivo
    SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "📊 Tamaño del backup: ${SIZE}"
    
    # Limpiar backups antiguos (mantener solo los últimos 30)
    echo "🧹 Limpiando backups antiguos..."
    cd "${BACKUP_DIR}"
    ls -t db_backup_*.sqlite3 2>/dev/null | tail -n +31 | xargs -r rm
    REMAINING=$(ls -1 db_backup_*.sqlite3 2>/dev/null | wc -l)
    echo "📋 Backups restantes: ${REMAINING}"
    cd ..
    
    # Opcional: Agregar al git
    read -p "¿Deseas agregar el backup al repositorio git? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add "${BACKUP_FILE}"
        git commit -m "Backup manual de base de datos - $(date +%Y-%m-%d\ %H:%M:%S)"
        echo "✅ Backup agregado al repositorio"
        
        read -p "¿Deseas hacer push al repositorio remoto? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push
            echo "✅ Backup subido al repositorio remoto"
        fi
    fi
    
else
    echo "❌ Error al crear el backup"
    exit 1
fi