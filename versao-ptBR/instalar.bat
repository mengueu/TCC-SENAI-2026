@echo off
chcp 65001 >nul
REM instalar.bat - Script de configuracao do TraçAÍ Educação para desenvolvedores
REM Cria o ambiente virtual e instala todas as dependencias Python automaticamente.

title Instalador de Dependencias - TraçAÍ Educacao
cls
echo ====================================================================
echo        TraçAÍ Educação - Instalador de Dependências Python
echo        TCC - Curso Técnico de Desenvolvimento de Sistemas | SENAI 2026
echo ====================================================================
echo.

REM Verifica Python disponivel
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao foi encontrado no sistema!
    echo.
    echo Por favor, instale o Python 3.11 ou superior em:
    echo https://www.python.org/downloads/
    echo (Certifique-se de marcar a opcao "Add Python to PATH" durante a instalacao)
    echo.
    pause
    exit /b 1
)

echo [1/3] Criando ambiente virtual (venv)...
if not exist "venv" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
)
echo [OK] Ambiente virtual pronto.

echo.
echo [2/3] Instalando bibliotecas necessarias...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar as dependencias.
    pause
    exit /b 1
)
echo [OK] Todas as dependencias instaladas com sucesso.

echo.
echo [3/3] Verificando instalacao do Tesseract OCR...
python -c "
from modules.caminhos import obter_tesseract_cmd
import subprocess
cmd = obter_tesseract_cmd()
try:
    res = subprocess.run([cmd, '--version'], capture_output=True, text=True)
    print('[OK] Tesseract OCR detectado com sucesso!')
except Exception:
    print('[AVISO] Tesseract OCR nao detectado automaticamente.')
    print('        Para OCR completo, instale o Tesseract em: https://github.com/UB-Mannheim/tesseract/wiki')
"

echo.
echo ====================================================================
echo   CONFIGURACAO CONCLUIDA COM SUCESSO!
echo ====================================================================
echo.
echo Para executar o projeto via Python:
echo   1. Ative o ambiente virtual:  venv\Scripts\activate
echo   2. Execute o programa:        python main.py
echo.
set /p RUN="Deseja iniciar o TraçAÍ Educação agora? (S/N): "
if /i "%RUN%"=="S" (
    python main.py
)
exit /b 0
