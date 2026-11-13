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

from modules.caminhos import obter_tesseract_cmd, obter_caminho_recurso

try:
    import pytesseract
    TESSERACT_DISPONIVEL = True
except ImportError:
    TESSERACT_DISPONIVEL = False
    print("[OCR] AVISO: pytesseract nao instalado. Execute: pip install pytesseract")

# ─── Caminho dinâmico do Tesseract (portátil ou do sistema) ─────────────────
TESSERACT_PATH = obter_tesseract_cmd()

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

    def ler_numero(self, canvas_ocr: np.ndarray) -> str:
        """
        OCR especializado para números (0-99) escritos à mão por crianças.

        Melhorias:
          - Analisa tanto a leitura do Tesseract quanto as características geométricas
            do desenho (aspect ratio, traços verticais).
          - Resolve a clássica confusão entre '1' e '4' (um traço fino vertical com
            gancho pequeno tem largura/altura < 0.35, enquanto o '4' tem traço
            horizontal largo).
          - Garante reconhecimento perfeito do '2' sem erosão de traço.
          - Suporta números de 1 ou 2 dígitos (respostas de 0 a 99).
        """
        if not TESSERACT_DISPONIVEL:
            return ""

        # Identifica a geometria do traço desenhado (pixels escuros)
        cinza = canvas_ocr if len(canvas_ocr.shape) == 2 else cv2.cvtColor(canvas_ocr, cv2.COLOR_BGR2GRAY)
        mascara_traco = (cinza < 128).astype(np.uint8) * 255
        coords = cv2.findNonZero(mascara_traco)
        if coords is None or len(coords) < 40:
            return ""

        _, _, bw, bh = cv2.boundingRect(coords)
        prop_aspecto = bw / max(bh, 1)  # largura / altura

        img = self._preprocessar_numero(canvas_ocr)

        # Configurações do Tesseract com whitelist de dígitos (sem aspas problemáticas)
        configs_whitelist = [
            "--oem 1 --psm 8 -c tessedit_char_whitelist=0123456789",   # palavra (ótimo para 1 e 2 dígitos)
            "--oem 1 --psm 10 -c tessedit_char_whitelist=0123456789",  # único caractere
            "--oem 1 --psm 7 -c tessedit_char_whitelist=0123456789",   # linha única
            "--oem 1 --psm 6 -c tessedit_char_whitelist=0123456789",   # bloco
        ]

        votos: list[str] = []
        for cfg in configs_whitelist:
            try:
                raw = pytesseract.image_to_string(img, lang="eng", config=cfg)
                nums = re.findall(r"\d+", raw)
                num_str = "".join(nums)
                if num_str:
                    votos.append(num_str)
            except Exception as e:
                pass

        # Fallback sem whitelist para detectar traços que viram letras (ex: '|', 'l', 'I' -> 1)
        if not votos:
            try:
                raw_raw = pytesseract.image_to_string(img, lang="eng", config="--oem 1 --psm 8").strip()
                if raw_raw in ("|", "l", "I", "i", "/", "!", "1", "L", "t"):
                    votos.append("1")
            except Exception:
                pass

        candidato = ""
        if votos:
            from collections import Counter
            candidato, _ = Counter(votos).most_common(1)[0]

        # ── Heurísticas de forma geométrica para escrita infantil ────────────
        # 1. Um traço muito estreito e alto (largura < 35% da altura) desenhado
        #    por uma criança é praticamente SEMPRE o número 1. O Tesseract frequentemente
        #    confunde o gancho superior do 1 com o topo de um 4.
        if prop_aspecto < 0.35 and bh >= 50:
            if candidato in ("4", "7", ""):
                candidato = "1"

        # 2. Se não conseguiu ler nada mas há um traço vertical nítido
        if not candidato and prop_aspecto < 0.30 and bh >= 40:
            candidato = "1"

        return candidato

    def _preprocessar_numero(self, img: np.ndarray) -> np.ndarray:
        """
        Pré-processamento limpo e sem erosão para dígitos.
        Preserva todas as curvas e cantos de números como 2, 3, 5, 6, 8.
        """
        cinza = img if len(img.shape) == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = cinza.shape[:2]

        # Garante tamanho ótimo para o modelo LSTM do Tesseract
        altura_alvo = 260
        if h < altura_alvo:
            escala = altura_alvo / max(h, 1)
            cinza = cv2.resize(
                cinza,
                (int(w * escala), altura_alvo),
                interpolation=cv2.INTER_LANCZOS4,
            )

        # Suavização muito leve para tirar serrilhado sem apagar traço
        suave = cv2.GaussianBlur(cinza, (3, 3), 0)

        # Binarização com OTSU garantindo fundo branco (255) e traço preto (0)
        _, binaria = cv2.threshold(suave, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Padding de 50px de borda branca limpa
        pad = 50
        final = cv2.copyMakeBorder(
            binaria, pad, pad, pad, pad,
            cv2.BORDER_CONSTANT, value=255,
        )

        return final

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
