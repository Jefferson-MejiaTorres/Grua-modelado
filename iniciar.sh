#!/bin/bash
# Script de inicio para Linux/Mac

echo "==============================================================="
echo "  SISTEMA DE CONTROL DE GRÚA VIGA"
echo "  Proceso de Cromado por Electrólisis"
echo "  Norma ISA 5.1"
echo "==============================================================="
echo ""

# Verificar Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "[ERROR] Python no encontrado. Por favor instale Python 3.8+"
    exit 1
fi

echo "[OK] Python encontrado: $($PYTHON_CMD --version)"
echo ""

# Verificar dependencias
echo "Verificando dependencias..."
$PYTHON_CMD -c "import tkinter; import matplotlib; import numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[ADVERTENCIA] Instalando dependencias..."
    $PYTHON_CMD -m pip install -r requirements.txt
fi

echo "[OK] Dependencias verificadas"
echo ""

# Ejecutar sistema
echo "Iniciando sistema de control..."
echo ""
$PYTHON_CMD main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] El sistema terminó con errores"
    read -p "Presione Enter para continuar..."
fi
