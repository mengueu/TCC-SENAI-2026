"""
modules/ocr.py — Módulo de Reconhecimento de Texto (OCR)

Usa o Tesseract OCR com múltiplos modos de segmentação (PSM) e
pré-processamento otimizado para escrita manual de crianças:
  - Tenta PSM 8 (palavra única)  → melhor para nomes curtos
  - Tenta PSM 7 (linha única)    → fallback para nomes mais longos
  - Tenta PSM 13 (linha raw)     → fallback final
  Retorna o resultado com mais conteúdo útil entre as tentativas.

Pré-processamento extra:
  - Fechamento morfológico (fecha traços quebrados)
  - Upscale maior (250 px mínimo de altura)
  - Whitelist só com letras + espaço (evita OCR gerar números/símbolos)
"""

import re
import cv2
import numpy as np

try:
    import pytesseract
    TESSERACT_DISPONIVEL = True
except ImportError:
    TESSERACT_DISPONIVEL = False
    print("[OCR] AVISO: pytesseract nao instalado. Execute: pip install pytesseract")

# ─── Caminho do Tesseract no Windows ─────────────────────────────────────────
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ─── Configurações a tentar (em ordem de preferência) ────────────────────────
# PSM 8  → Trata a imagem como uma única PALAVRA  (ótimo para nomes curtos)
# PSM 7  → Trata a imagem como uma única LINHA    (bom para nomes mais longos)
# PSM 13 → Linha raw, sem análise de layout       (fallback agressivo)
# --oem 1 → Usa só LSTM (mais preciso para manuscrito)
#
# NOTA: Não usamos -c tessedit_char_whitelist aqui porque no Windows o
# pytesseract passa a config como argumento de subprocess, e aspas dentro
# da string causam erro "No closing quotation". A filtragem de caracteres
# é feita em Python pelo método _limpar(), que é equivalente e mais seguro.
_CONFIGS = [
    "--oem 1 --psm 8",
    "--oem 1 --psm 7",
    "--oem 1 --psm 13",
]


class OCRReader:
    def __init__(self):
        if TESSERACT_DISPONIVEL:
            try:
                pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
                pytesseract.get_tesseract_version()
                print("[OCR] Tesseract inicializado com sucesso.")
            except Exception as e:
                print(f"[OCR] AVISO: Tesseract nao encontrado. Erro: {e}")
                print(f"      Ajuste TESSERACT_PATH em modules/ocr.py")

    def ler_escrita(self, canvas_ocr: np.ndarray) -> str:
        """
        Recebe a imagem do canvas (saída de Canvas.obter_canvas_para_ocr())
        e retorna o texto mais provável lido pelo Tesseract.

        Tenta múltiplos modos PSM e retorna o resultado mais longo e limpo
        (heurística: mais caracteres úteis = melhor leitura).
        """
        if not TESSERACT_DISPONIVEL:
            return ""

        img = self._preprocessar(canvas_ocr)
        melhor = ""

        for config in _CONFIGS:
            try:
                raw = pytesseract.image_to_string(img, lang="por+eng", config=config)
                limpo = self._limpar(raw)
                # Fica com o resultado mais longo (mais informação útil)
                if len(limpo) > len(melhor):
                    melhor = limpo
            except Exception as e:
                print(f"[OCR] Erro com config '{config}': {e}")

        return melhor

    # ─────────────────────────────────────────────────────────────────────────

    def _preprocessar(self, img: np.ndarray) -> np.ndarray:
        """
        Pré-processamento otimizado para escrita manual de crianças.

        Etapas:
          1. Upscale para pelo menos 250 px de altura
             (Tesseract funciona MUITO melhor com imagens grandes)
          2. Suavização leve (reduz ruído de pixel isolado)
          3. Fechamento morfológico: fecha gaps em letras (ex: traços
             quebrados do "a", "e", "o" escritos a dedo no ar)
          4. Threshold OTSU adaptativo (melhor que threshold fixo)
          5. Padding generoso nas bordas
        """
        h, w = img.shape[:2]

        # 1. Upscale
        altura_alvo = 250
        if h < altura_alvo:
            escala = altura_alvo / max(h, 1)
            img = cv2.resize(
                img,
                (int(w * escala), int(h * escala)),
                interpolation=cv2.INTER_CUBIC,
            )

        # 2. Suavização
        img = cv2.GaussianBlur(img, (3, 3), 0)

        # 3. Fechamento morfológico (fecha traços quebrados)
        # Kernel horizontal mais largo para conectar traços de letras
        kernel_fechar = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel_fechar)

        # 4. Threshold OTSU (calcula automaticamente o melhor limiar)
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 5. Padding
        pad = 50
        img = cv2.copyMakeBorder(
            img, pad, pad, pad, pad,
            cv2.BORDER_CONSTANT, value=255,
        )

        return img

    def _limpar(self, texto: str) -> str:
        """
        Limpa o resultado do Tesseract:
        - Remove tudo que não for letra ou espaço
        - Normaliza espaços
        - Capitaliza (Primeira Letra Maiúscula)
        """
        # Mantém só letras unicode e espaço
        limpo = re.sub(r"[^\w\s]", "", texto, flags=re.UNICODE)
        limpo = re.sub(r"\d+", "", limpo)          # remove números
        limpo = re.sub(r"\s+", " ", limpo).strip() # normaliza espaços
        return limpo.title()
