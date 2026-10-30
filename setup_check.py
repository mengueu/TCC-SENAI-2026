"""
setup_check.py - Verificador de Instalacao do AlfaIA

Execute este script ANTES de rodar o main.py para verificar se
todas as dependencias estao instaladas corretamente.

Uso:
    python setup_check.py
"""

import sys
import subprocess
import os

# Forca UTF-8 no stdout para evitar erros de encoding no Windows
if sys.stdout.encoding != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def verificar_python():
    versao = sys.version_info
    print(f"  Python: {sys.version}")
    if versao.major == 3 and 10 <= versao.minor <= 12:
        print("  [OK] Versao compativel (3.10 - 3.12)")
        return True
    else:
        print(f"  [ERRO] Versao incompativel! Use Python 3.10, 3.11 ou 3.12")
        print(f"         O MediaPipe 0.10.14 nao funciona com Python 3.13+")
        return False


def verificar_pacote(nome_import: str, nome_pip: str = None):
    nome_pip = nome_pip or nome_import
    try:
        __import__(nome_import)
        print(f"  [OK] {nome_pip} instalado")
        return True
    except ImportError:
        print(f"  [FALTA] {nome_pip} NAO instalado -> execute: pip install {nome_pip}")
        return False


def verificar_tesseract():
    """Verifica se o Tesseract esta instalado e acessivel."""
    import shutil

    # Verifica no PATH do sistema
    if shutil.which("tesseract"):
        try:
            resultado = subprocess.run(
                ["tesseract", "--version"],
                capture_output=True, text=True
            )
            versao = resultado.stdout.split("\n")[0]
            print(f"  [OK] Tesseract encontrado no PATH: {versao}")
            return True
        except Exception as e:
            print(f"  [AVISO] Tesseract encontrado no PATH mas com erro: {e}")
            return False

    # Verifica no caminho padrao do Windows
    caminho_padrao = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(caminho_padrao):
        try:
            resultado = subprocess.run(
                [caminho_padrao, "--version"],
                capture_output=True, text=True
            )
            versao = resultado.stdout.split("\n")[0]
            print(f"  [OK] Tesseract encontrado em: {caminho_padrao}")
            print(f"       Versao: {versao}")
            return True
        except Exception as e:
            print(f"  [AVISO] Tesseract encontrado mas com erro: {e}")

    print("  [FALTA] Tesseract NAO encontrado!")
    print("          Como instalar:")
    print("          1. Acesse: https://github.com/UB-Mannheim/tesseract/wiki")
    print("          2. Baixe o instalador Windows (.exe)")
    print("          3. Durante a instalacao, adicione o idioma Portugues")
    print("          4. Caminho padrao: C:\\Program Files\\Tesseract-OCR\\")
    return False


def verificar_camera():
    """Testa se a camera esta acessivel."""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("  [OK] Camera (indice 0) acessivel")
            cap.release()
            return True
        else:
            print("  [ERRO] Camera (indice 0) nao acessivel")
            print("         Verifique se sua webcam esta conectada")
            return False
    except Exception as e:
        print(f"  [ERRO] Erro ao acessar camera: {e}")
        return False


def main():
    print("=" * 60)
    print("  AlfaIA - Verificador de Instalacao")
    print("=" * 60)

    resultados = []

    print("\n[Python]")
    resultados.append(verificar_python())

    print("\n[Pacotes Python]")
    pacotes = [
        ("cv2",          "opencv-python"),
        ("mediapipe",    "mediapipe==0.10.14"),
        ("numpy",        "numpy"),
        ("pytesseract",  "pytesseract"),
        ("Levenshtein",  "python-Levenshtein"),
        ("pyttsx3",      "pyttsx3"),
        ("PIL",          "Pillow"),
    ]
    for nome_import, nome_pip in pacotes:
        resultados.append(verificar_pacote(nome_import, nome_pip))

    print("\n[Tesseract OCR - motor externo]")
    resultados.append(verificar_tesseract())

    print("\n[Camera]")
    resultados.append(verificar_camera())

    print("\n" + "=" * 60)
    total = len(resultados)
    ok = sum(resultados)
    print(f"  Resultado: {ok}/{total} verificacoes passaram")

    if ok == total:
        print("  [TUDO OK] Tudo instalado! Execute: python main.py")
    else:
        falhas = total - ok
        print(f"  [ATENCAO] {falhas} item(ns) precisam de atencao (veja os [FALTA] acima)")
    print("=" * 60)


if __name__ == "__main__":
    main()
