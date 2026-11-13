@echo off
REM instalar.bat - Script de instalacao do AlfaIA para Windows
REM Execute como: instalar.bat
REM Requer Python 3.10, 3.11 ou 3.12 instalado no sistema

echo ============================================================
echo   AlfaIA - Instalacao automatica
echo ============================================================
echo.

REM Verifica se o Python 3.11 esta disponivel via launcher py
py -3.11 --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Python 3.11 encontrado via launcher py
    set PYTHON_CMD=py -3.11
    goto :criar_venv
)

REM Tenta Python 3.12
py -3.12 --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Python 3.12 encontrado via launcher py
    set PYTHON_CMD=py -3.12
    goto :criar_venv
)

REM Tenta Python 3.10
py -3.10 --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Python 3.10 encontrado via launcher py
    set PYTHON_CMD=py -3.10
    goto :criar_venv
)

echo [ERRO] Python 3.10, 3.11 ou 3.12 nao encontrado!
echo.
echo  Para instalar:
echo  1. Acesse: https://www.python.org/downloads/
echo  2. Baixe Python 3.11.x (recomendado)
echo  3. Durante a instalacao, marque "Add Python to PATH"
echo.
pause
exit /b 1

:criar_venv
echo.
echo [1/4] Criando ambiente virtual com %PYTHON_CMD%...
%PYTHON_CMD% -m venv venv
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao criar ambiente virtual
    pause
    exit /b 1
)
echo [OK] Ambiente virtual criado em ./venv/

echo.
echo [2/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo [3/4] Instalando dependencias Python...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

echo.
echo [4/4] Verificando instalacao...
python setup_check.py

echo.
echo ============================================================
echo  IMPORTANTE: O Tesseract OCR precisa ser instalado separadamente!
echo.
echo  Acesse: https://github.com/UB-Mannheim/tesseract/wiki
echo  Baixe o instalador .exe e instale com o idioma Portugues
echo ============================================================
echo.
pause
