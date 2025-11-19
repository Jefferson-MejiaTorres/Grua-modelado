@echo off
REM Script de inicio del Sistema de Control de Grúa Viga
REM Universidad de Pamplona

echo ===============================================================
echo   SISTEMA DE CONTROL DE GRUA VIGA
echo   Proceso de Cromado por Electrolisis
echo   Norma ISA 5.1
echo ===============================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado. Intentando con py...
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] No se encontro Python instalado.
        echo Por favor instale Python 3.8 o superior.
        pause
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

echo [OK] Python encontrado
echo.

REM Verificar dependencias
echo Verificando dependencias...
%PYTHON_CMD% -c "import tkinter; import matplotlib; import numpy" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ADVERTENCIA] Algunas dependencias faltan. Instalando...
    %PYTHON_CMD% -m pip install -r requirements.txt
)

echo [OK] Dependencias verificadas
echo.

REM Ejecutar sistema
echo Iniciando sistema de control...
echo.
%PYTHON_CMD% main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] El sistema termino con errores
    pause
)
