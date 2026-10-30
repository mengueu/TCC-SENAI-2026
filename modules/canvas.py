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
          - Fundo branco, traço preto (Tesseract prefere isso)
          - Recortada ao redor do texto (remove margens vazias)
          - Redimensionada para altura mínima de 150 px
        """
        cinza = cv2.cvtColor(self._canvas_display, cv2.COLOR_BGR2GRAY)

        # Inverte: fundo branco, traço escuro
        invertida = cv2.bitwise_not(cinza)
        _, binaria = cv2.threshold(invertida, 200, 255, cv2.THRESH_BINARY)

        # Dilata para engrossar o traço
        kernel = np.ones((3, 3), np.uint8)
        dilatada = cv2.dilate(binaria, kernel, iterations=1)

        # Recorta ao bounding box do conteúdo (remove bordas em branco)
        # Isso envia ao OCR só a região onde há escrita de fato
        coords = cv2.findNonZero(cv2.bitwise_not(dilatada))  # pixels escuros = escrita
        if coords is not None:
            x, y, bw, bh = cv2.boundingRect(coords)
            margem = 20
            x  = max(0, x - margem)
            y  = max(0, y - margem)
            x2 = min(dilatada.shape[1], x + bw + margem * 2)
            y2 = min(dilatada.shape[0], y + bh + margem * 2)
            dilatada = dilatada[y:y2, x:x2]

        # Garante altura mínima para o Tesseract (funciona melhor com imagens maiores)
        h_atual = dilatada.shape[0]
        if h_atual < 150:
            escala = 150 / max(h_atual, 1)
            nova_larg = int(dilatada.shape[1] * escala)
            dilatada = cv2.resize(dilatada, (nova_larg, 150), interpolation=cv2.INTER_CUBIC)

        return dilatada
