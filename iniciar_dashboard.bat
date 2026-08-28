@echo off
setlocal
cd /d "%~dp0"
title Dashboard de Imagens

echo ==========================================
echo        DASHBOARD DE IMAGENS
 echo ==========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo ERRO: Python nao encontrado.
        pause
        exit /b 1
    )
)

echo Atualizando pip...
.venv\Scripts\python.exe -m pip install --upgrade pip

echo Instalando dependencias...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo Iniciando Dashboard...
echo.
.venv\Scripts\python.exe -m streamlit run app.py
pause
