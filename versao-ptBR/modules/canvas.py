"""
modules/canvas.py — Módulo do Canvas de Escrita

Responsabilidades:
  - Manter uma "folha" virtual (canvas) onde a escrita da criança é armazenada
  - Gerenciar o traço (desenhar, apagar, levantar caneta, limpar tudo)
  - Fornecer o canvas para exibição (mesclagem com o frame da câmera)
  - Fornecer o canvas limpo para o OCR (fundo branco, traço escuro)

O canvas de escrita é uma camada separada do vídeo da câmera.
Isso permite exportar só a escrita para o OCR, sem o "ruído" do fundo da câmera.
"""

import cv2
import numpy as np


class Canvas:
    """
    Gerencia a camada de escrita (canvas) onde a criança escreve com o dedo.
    """

    def __init__(
        self,
        largura: int,
        altura: int,
        cor_traço: tuple = (255, 140, 0),
        espessura: int = 8,
    ):
        self.largura = largura
        self.altura = altura
        self.cor_traço = cor_traço
        self.espessura = espessura

        # Canvas de exibição: fundo preto, traço colorido
        self._canvas_display = np.zeros((altura, largura, 3), dtype=np.uint8)

        # Ponto anterior (para conectar os traços em linhas suaves)
        self._ponto_anterior: tuple[int, int] | None = None

    # ────────────────────────────────────────────────────────────────────────

    def desenhar(self, ponto: tuple[int, int]):
        """
        Desenha um traço do ponto anterior até o ponto atual.
        Chame a cada frame enquanto o gesto "desenhando" estiver ativo.
        """
        if self._ponto_anterior is not None:
            cv2.line(
                self._canvas_display,
                self._ponto_anterior,
                ponto,
                self.cor_traço,
                self.espessura,
                cv2.LINE_AA,
            )
        # Também desenha um círculo na ponta para traços suaves quando parado
        cv2.circle(
            self._canvas_display,
            ponto,
            self.espessura // 2,
            self.cor_traço,
            -1,
            cv2.LINE_AA,
        )
        self._ponto_anterior = ponto

    def levantar_caneta(self):
        """
        Sinaliza que a criança levantou o dedo (não está desenhando agora).
        O próximo ponto de desenho começará sem conectar ao anterior.
        """
        self._ponto_anterior = None

    def apagar(self, ponto: tuple[int, int], raio: int = 40):
        """
        Apaga uma região circular ao redor do ponto (borracha local).
        """
        cv2.circle(self._canvas_display, ponto, raio, (0, 0, 0), -1)
        self._ponto_anterior = None  # evita traço acidental ao voltar a desenhar

    def limpar(self):
        """Limpa todo o canvas (apaga tudo)."""
        self._canvas_display[:] = 0
        self._ponto_anterior = None

    def definir_cor(self, cor: tuple):
        """Atualiza a cor do pincel (chamada pela mão de configuração)."""
        self.cor_traço = cor

    def definir_espessura(self, espessura: int):
        """Atualiza a espessura do pincel (chamada pelo gesto de pinça)."""
        self.espessura = max(1, espessura)

    def definir_borracha(self, ativa: bool):
        """
        Informa ao canvas se o modo borracha está ativo.
        Usado principalmente para garantir que a caneta é levantada
        na transição entre modos (evita traço fantasma).
        """
        if ativa:
            self._ponto_anterior = None  # levanta a caneta ao ativar borracha

    def obter_canvas(self) -> np.ndarray:
        """Retorna o canvas de exibição (fundo preto, traço colorido)."""
        return self._canvas_display.copy()

    def obter_canvas_para_ocr(self) -> np.ndarray:
        """
        Retorna uma versão do canvas otimizada para o OCR:
          - Fundo branco, traço preto nítido (Tesseract prefere isso)
          - Recortada ao redor do desenho (remove margens vazias)
          - Engrossada corretamente (dilatação do traço enquanto ainda é branco)
          - Redimensionada para altura de pelo menos 200 px
          - Padding generoso nas bordas
        """
        cinza = cv2.cvtColor(self._canvas_display, cv2.COLOR_BGR2GRAY)
        _, binaria = cv2.threshold(cinza, 25, 255, cv2.THRESH_BINARY)

        coords = cv2.findNonZero(binaria)
        if coords is None:
            # Nada desenhado: retorna imagem branca pequena
            return np.ones((200, 200), dtype=np.uint8) * 255

        x, y, bw, bh = cv2.boundingRect(coords)
        margem = 25
        x1 = max(0, x - margem)
        y1 = max(0, y - margem)
        x2 = min(binaria.shape[1], x + bw + margem)
        y2 = min(binaria.shape[0], y + bh + margem)

        recorte = binaria[y1:y2, x1:x2].copy()

        # Engrossa o traço BRANCO (garante que linhas finas não quebrem)
        kernel = np.ones((5, 5), np.uint8)
        recorte = cv2.dilate(recorte, kernel, iterations=1)

        # Garante altura mínima para o Tesseract
        h_atual, w_atual = recorte.shape[:2]
        if h_atual < 200:
            escala = 200 / max(h_atual, 1)
            nova_larg = max(1, int(w_atual * escala))
            recorte = cv2.resize(recorte, (nova_larg, 200), interpolation=cv2.INTER_LANCZOS4)

        # Inverte: fundo branco (255), traço preto (0)
        invertida = cv2.bitwise_not(recorte)

        # Padding nas bordas (essencial para o Tesseract segmentar)
        pad = 40
        final = cv2.copyMakeBorder(
            invertida, pad, pad, pad, pad,
            cv2.BORDER_CONSTANT, value=255,
        )

        return final
