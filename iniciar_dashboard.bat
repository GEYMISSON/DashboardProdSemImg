@echo off

title Dashboard de Imagens

cd /d "%~dp0"

echo ==========================================
echo       DASHBOARD DE IMAGENS
echo ==========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Ambiente Python nao encontrado.
    echo.
    echo Criando ambiente virtual...
    python -m venv .venv
)

echo.
echo Instalando/verificando dependencias...
echo.

.venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo Iniciando dashboard...
echo.

.venv\Scripts\python.exe -m streamlit run app.py

pause