"""
modules/texto.py — Renderização de texto UTF-8 com acentos no OpenCV

O cv2.putText() não suporta caracteres acentuados (UTF-8) por padrão —
ele usa apenas a tabela de caracteres do Hershey, que não inclui
Ã, Ç, Ó, etc.

Este módulo usa o Pillow (PIL) para renderizar texto com fontes TTF do
sistema, suportando todo o alfabeto português com acentos e cedilhas,
e depois converte de volta para uma imagem OpenCV (numpy array BGR).
"""

from __future__ import annotations
from pathlib import Path

import cv2
import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_DISPONIVEL = True
except ImportError:
    PIL_DISPONIVEL = False

# ─── Fonte padrão (usa Arial se disponível, senão Segoe UI) ──────────────────
_FONTES_CANDIDATAS = [
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\ARIAL.TTF",
    r"C:\Windows\Fonts\ARIALN.TTF",
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\calibri.ttf",
]

_fonte_path: str | None = None
for _f in _FONTES_CANDIDATAS:
    if Path(_f).exists():
        _fonte_path = _f
        break


def _carregar_fonte(tamanho: int) -> "ImageFont.FreeTypeFont | ImageFont.ImageFont":
    """Carrega a fonte TTF no tamanho pedido, com fallback para bitmap default."""
    if PIL_DISPONIVEL and _fonte_path:
        try:
            return ImageFont.truetype(_fonte_path, tamanho)
        except Exception:
            pass
    if PIL_DISPONIVEL:
        return ImageFont.load_default()
    return None


# ─── Função principal ─────────────────────────────────────────────────────────

def escrever(
    frame: np.ndarray,
    texto: str,
    pos: tuple[int, int],
    tamanho: int,
    cor: tuple[int, int, int],
    negrito: bool = False,
) -> np.ndarray:
    """
    Renderiza `texto` com acentos sobre o frame OpenCV usando Pillow.

    Parâmetros:
        frame:   imagem BGR do OpenCV
        texto:   string com possíveis acentos/cedilhas
        pos:     (x, y) — canto superior esquerdo do texto
        tamanho: tamanho da fonte em pontos (equivalente a cv2 fontScale ≈ tamanho/32)
        cor:     (B, G, R) — cor BGR (como no OpenCV)
        negrito: se True, aplica pseudo-negrito desenhando o texto duas vezes

    Retorna:
        frame com o texto renderizado
    """
    if not PIL_DISPONIVEL:
        # Fallback sem acento
        cv2.putText(frame, texto, pos, cv2.FONT_HERSHEY_SIMPLEX,
                    tamanho / 32, cor, 1, cv2.LINE_AA)
        return frame

    fonte = _carregar_fonte(tamanho)

    # Converte BGR → RGB para o PIL
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    # PIL usa (R, G, B)
    cor_rgb = (cor[2], cor[1], cor[0])

    if negrito:
        # Pseudo-negrito: desenha levemente deslocado + normal
        for dx, dy in [(1, 0), (0, 1), (1, 1)]:
            draw.text((pos[0] + dx, pos[1] + dy), texto, font=fonte, fill=cor_rgb)
    draw.text(pos, texto, font=fonte, fill=cor_rgb)

    # Converte de volta para BGR
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def medir(texto: str, tamanho: int) -> tuple[int, int]:
    """
    Retorna (largura, altura) do texto renderizado com Pillow.
    Útil para centralizar texto na tela.
    """
    if not PIL_DISPONIVEL:
        # Estimativa aproximada sem PIL
        return len(texto) * tamanho // 2, tamanho
    fonte = _carregar_fonte(tamanho)
    try:
        bbox = fonte.getbbox(texto)   # (left, top, right, bottom)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        # Versões antigas do Pillow
        w, h = fonte.getsize(texto)
        return w, h
