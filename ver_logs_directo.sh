#!/bin/bash
# Script para ver logs en tiempo real del sistema de Control Bovino

echo "======================================================================"
echo "     LOGS EN DIRECTO - Sistema de Control Bovino"
echo "======================================================================"
echo ""
echo "Mostrando logs de:"
echo "  - Gunicorn (salida estándar y errores)"
echo "  - Prints de debug de APIs"
echo ""
echo "Presiona Ctrl+C para detener"
echo "======================================================================"
echo ""

# Ver logs de gunicorn en tiempo real (incluye los prints)
sudo journalctl -u gunicorn-controlbovino -f --no-pager
