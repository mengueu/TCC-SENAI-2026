"""
modules/caminhos.py — Gerenciador de caminhos portátil para desenvolvimento e produção (.exe)

Garante que arquivos de dados, configurações e binários portáteis (como o Tesseract)
sejam localizados corretamente tanto rodando em Python quanto compilado em .exe.
"""

import sys
import os
from pathlib import Path


def obter_diretorio_base() -> Path:
    """
    Retorna o diretório base do aplicativo:
    - Se compilado pelo PyInstaller: sys._MEIPASS ou pasta do executável
    - Se rodando direto pelo Python: raiz do projeto
    """
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def obter_tesseract_cmd() -> str:
    """
    Localiza o binário do Tesseract OCR de forma autônoma e portátil.
    Prioridades:
      1. tesseract/tesseract.exe embutido na pasta do app
      2. tesseract.exe junto do executável
      3. C:\\Program Files\\Tesseract-OCR\\tesseract.exe
      4. 'tesseract' do PATH
    """
    base = obter_diretorio_base()
    candidatos = [
        base / "tesseract" / "tesseract.exe",
        (Path(sys.executable).resolve().parent / "tesseract" / "tesseract.exe") if getattr(sys, "frozen", False) else None,
        base / "bin" / "tesseract" / "tesseract.exe",
        Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    ]

    for c in candidatos:
        if c and c.exists():
            # Configura automaticamente TESSDATA_PREFIX para o diretório de dados do Tesseract
            tessdata = c.parent / "tessdata"
            if tessdata.exists():
                os.environ["TESSDATA_PREFIX"] = str(tessdata)
            return str(c)

    return "tesseract"


def obter_caminho_recurso(caminho_relativo: str) -> Path:
    """
    Retorna o Path absoluto de um recurso (ex: 'data/nomes_br.txt' ou 'tessdata/digits.cfg')
    """
    base = obter_diretorio_base()
    candidato = base / caminho_relativo
    if candidato.exists():
        return candidato

    if getattr(sys, "frozen", False):
        candidato_exe = Path(sys.executable).resolve().parent / caminho_relativo
        if candidato_exe.exists():
            return candidato_exe

    return candidato

