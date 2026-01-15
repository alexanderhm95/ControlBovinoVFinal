#!/bin/bash
# Script para ver logs filtrados del sistema

echo "======================================================================"
echo "     LOGS FILTRADOS - Control Bovino"
echo "======================================================================"
echo ""
echo "Opciones disponibles:"
echo "  1. Ver solo logs de ARDUINO"
echo "  2. Ver solo logs de MÓVIL"
echo "  3. Ver todos los logs con debug"
echo "  4. Ver logs de errores solamente"
echo "  5. Ver últimas 50 líneas de todos los logs"
echo ""
read -p "Selecciona una opción (1-5): " opcion

case $opcion in
    1)
        echo ""
        echo "Mostrando logs de ARDUINO en tiempo real..."
        echo "Presiona Ctrl+C para detener"
        echo "======================================================================"
        sudo journalctl -u gunicorn-controlbovino -f --no-pager | grep --line-buffered "\[ARDUINO\]"
        ;;
    2)
        echo ""
        echo "Mostrando logs de MÓVIL en tiempo real..."
        echo "Presiona Ctrl+C para detener"
        echo "======================================================================"
        sudo journalctl -u gunicorn-controlbovino -f --no-pager | grep --line-buffered "\[MÓVIL\]"
        ;;
    3)
        echo ""
        echo "Mostrando TODOS los logs en tiempo real..."
        echo "Presiona Ctrl+C para detener"
        echo "======================================================================"
        sudo journalctl -u gunicorn-controlbovino -f --no-pager
        ;;
    4)
        echo ""
        echo "Mostrando solo ERRORES en tiempo real..."
        echo "Presiona Ctrl+C para detener"
        echo "======================================================================"
        sudo journalctl -u gunicorn-controlbovino -f --no-pager | grep --line-buffered -E "ERROR|❌|Exception|Traceback"
        ;;
    5)
        echo ""
        echo "Últimas 50 líneas de logs:"
        echo "======================================================================"
        sudo journalctl -u gunicorn-controlbovino -n 50 --no-pager
        ;;
    *)
        echo "Opción inválida"
        exit 1
        ;;
esac
