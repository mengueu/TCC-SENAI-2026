"""
modules/camera.py — Módulo de Câmera e Detecção de Mão

Sistema de DUAS MÃOS portado da v7 do projeto da Semana Aberta.

Mão que DESENHA:   indicador = escreve | palma = borracha | joia = confirma
Mão que CONFIGURA: indicador no topo = paleta | pinça = espessura | aberta = limpa tudo
"""

import math
import cv2
import numpy as np
import mediapipe as mp


# ─── Parâmetros (mesmos da v7) ────────────────────────────────────────────────
LARGURA_PROCESSAMENTO   = 640
ALPHA_SUAVIZACAO        = 0.5
SALTO_MAXIMO_PX         = 180
FRAMES_PARA_CONFIRMAR   = 3
FRAMES_TOLERANCIA_PERDA = 6
MIN_CONFIANCA_DETECCAO  = 0.7
MIN_CONFIANCA_RASTREIO  = 0.6
RAIO_BORRACHA           = 60
ALTURA_PALETA           = 80   # px — zona de seleção de cor no topo da tela


class FiltroSuavizacao:
    """Média móvel exponencial com rejeição de saltos bruscos. (v7)"""
    def __init__(self, alpha=ALPHA_SUAVIZACAO, salto_max=SALTO_MAXIMO_PX):
        self.alpha = alpha
        self.salto_max = salto_max
        self.valor = None

    def atualizar(self, novo_ponto):
        if self.valor is None:
            self.valor = (float(novo_ponto[0]), float(novo_ponto[1]))
            return self.valor
        d = math.hypot(novo_ponto[0] - self.valor[0], novo_ponto[1] - self.valor[1])
        if d > self.salto_max:
            return self.valor
        nx = self.alpha * novo_ponto[0] + (1 - self.alpha) * self.valor[0]
        ny = self.alpha * novo_ponto[1] + (1 - self.alpha) * self.valor[1]
        self.valor = (nx, ny)
        return self.valor

    def resetar(self):
        self.valor = None


class EstabilizadorDeGesto:
    """Confirma troca de gesto só após N frames seguidos. (v7)"""
    def __init__(self, n=FRAMES_PARA_CONFIRMAR):
        self.n = n
        self.modo_confirmado = "ocioso"
        self.modo_candidato  = "ocioso"
        self.contagem        = 0

    def atualizar(self, modo):
        if modo == self.modo_candidato:
            self.contagem += 1
        else:
            self.modo_candidato = modo
            self.contagem = 1
        if self.contagem >= self.n:
            self.modo_confirmado = self.modo_candidato
        return self.modo_confirmado

    def resetar(self):
        self.modo_confirmado = "ocioso"
        self.modo_candidato  = "ocioso"
        self.contagem        = 0


# ─── Funções de gesto ─────────────────────────────────────────────────────────

def _dedos_levantados(hand_landmarks, mao_label: str) -> list[int]:
    """[polegar, indicador, medio, anelar, minimo], 1 = levantado. (v7)"""
    lm = hand_landmarks.landmark
    dedos = []
    if mao_label == "Right":
        dedos.append(1 if lm[4].x < lm[3].x else 0)
    else:
        dedos.append(1 if lm[4].x > lm[3].x else 0)
    for ponta, junta in zip([8, 12, 16, 20], [6, 10, 14, 18]):
        dedos.append(1 if lm[ponta].y < lm[junta].y else 0)
    return dedos


def _mao_do_usuario(hand_label: str) -> str:
    """Left do MediaPipe = direita real (espelhamento). (v7)"""
    return "esquerda" if hand_label == "Left" else "direita"


def _gesto_mao_desenho(dedos: list[int]) -> str:
    """
    Gestos da mão que desenha:
      ☝️  Só o indicador          → "caneta"   (desenha OU apaga, conforme modo)
      ✌️  Indicador + médio       → "pairar"   (move sem desenhar — para reposicionar,
                                               fazer pingo do i, etc.)
      👍  Só o polegar            → "confirmar" (envia para o OCR)
      Qualquer outra combinação  → "ocioso"   (nada acontece, cursor some)
    """
    _, ind, med, ane, min_ = dedos
    if ind == 1 and med == 1 and ane == 0 and min_ == 0:
        return "pairar"
    if ind == 1 and med == 0 and ane == 0 and min_ == 0:
        return "caneta"
    if dedos == [1, 0, 0, 0, 0]:
        return "confirmar"
    return "ocioso"


def _gesto_mao_config(dedos: list[int], y_indicador: int) -> str:
    """
    Gestos da mão de configuração (idênticos à v7):
      - 4 dedos abertos → limpar tudo
      - indicador na zona da paleta (topo) → selecionar cor
      - indicador levantado (fora da paleta) → ajustar tamanho (pinça)
    """
    _, ind, med, ane, min_ = dedos
    if ind == 1 and med == 1 and ane == 1 and min_ == 1:
        return "limpar_tudo"
    if ind == 1 and y_indicador < ALTURA_PALETA:
        return "selecionar_cor"
    if ind == 1:
        return "ajustar_tamanho"
    return "ocioso"


class Camera:
    """
    Câmera + sistema de duas mãos do AlfaIA.
    Portado diretamente da v7 do projeto da Semana Aberta.
    """

    def __init__(
        self,
        indice: int = 0,
        largura: int = 1280,
        altura: int = 720,
        mao_desenho: str = "direita",
    ):
        self.cap = cv2.VideoCapture(indice)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, largura)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, altura)
        self.largura    = largura
        self.altura     = altura
        self.mao_desenho = mao_desenho
        self.mao_config  = "esquerda" if mao_desenho == "direita" else "direita"

        self.mp_hands = mp.solutions.hands
        self.mp_draw  = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=MIN_CONFIANCA_DETECCAO,
            min_tracking_confidence=MIN_CONFIANCA_RASTREIO,
        )

        # Filtros de suavização
        self.filtro_indicador = FiltroSuavizacao()
        self.filtro_palma     = FiltroSuavizacao()

        # Estabilizadores
        self.estab_desenho = EstabilizadorDeGesto()
        self.estab_config  = EstabilizadorDeGesto()

        self._frames_sem_mao = FRAMES_TOLERANCIA_PERDA + 1

    def ler_frame(self) -> np.ndarray | None:
        ok, frame = self.cap.read()
        return cv2.flip(frame, 1) if ok else None

    def processar_frame(self, frame: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Processa as duas mãos e retorna dict com:
          gesto_desenho, gesto_config,
          ponta_indicador, centro_palma,          ← mão que desenha
          pos_ind_config, pos_pol_config,          ← mão que configura
          dist_pinca,                              ← distância polegar↔indicador (config)
          mao_desenho_visivel
        """
        h, w = frame.shape[:2]
        escala    = LARGURA_PROCESSAMENTO / w
        frame_det = cv2.resize(frame, (LARGURA_PROCESSAMENTO, int(h * escala)))
        rgb = cv2.cvtColor(frame_det, cv2.COLOR_BGR2RGB)
        resultado = self.hands.process(rgb)

        mao_visivel     = False
        ponta_ind       = None
        centro_palma    = None
        pos_ind_cfg     = None
        pos_pol_cfg     = None
        dist_pinca      = 0.0
        gesto_d_bruto   = "ocioso"
        gesto_c_bruto   = "ocioso"

        if resultado.multi_hand_landmarks and resultado.multi_handedness:
            for lms, handedness in zip(
                resultado.multi_hand_landmarks, resultado.multi_handedness
            ):
                mao_label = handedness.classification[0].label
                lado = _mao_do_usuario(mao_label)
                self.mp_draw.draw_landmarks(
                    frame, lms, self.mp_hands.HAND_CONNECTIONS
                )
                dedos = _dedos_levantados(lms, mao_label)

                # ── Mão que desenha ───────────────────────────────────────
                if lado == self.mao_desenho:
                    mao_visivel = True
                    self._frames_sem_mao = 0
                    gesto_d_bruto = _gesto_mao_desenho(dedos)

                    # Indicador (para desenhar)
                    lm8 = lms.landmark[8]
                    fx, fy = self.filtro_indicador.atualizar(
                        (int(lm8.x * w), int(lm8.y * h))
                    )
                    ponta_ind = (int(fx), int(fy))

                    # Palma (para borracha)
                    lm9 = lms.landmark[9]
                    pfx, pfy = self.filtro_palma.atualizar(
                        (int(lm9.x * w), int(lm9.y * h))
                    )
                    centro_palma = (int(pfx), int(pfy))

                # ── Mão que configura ─────────────────────────────────────
                elif lado == self.mao_config:
                    lm = lms.landmark
                    x_ind = int(lm[8].x * w)
                    y_ind = int(lm[8].y * h)
                    x_pol = int(lm[4].x * w)
                    y_pol = int(lm[4].y * h)

                    pos_ind_cfg = (x_ind, y_ind)
                    pos_pol_cfg = (x_pol, y_pol)
                    dist_pinca  = math.hypot(x_ind - x_pol, y_ind - y_pol)

                    gesto_c_bruto = _gesto_mao_config(dedos, y_ind)

        # Tolerância a perda momentânea
        if not mao_visivel:
            self._frames_sem_mao += 1
            if self._frames_sem_mao > FRAMES_TOLERANCIA_PERDA:
                self.filtro_indicador.resetar()
                self.filtro_palma.resetar()
                self.estab_desenho.resetar()
                ponta_ind    = None
                centro_palma = None

        gesto_d = self.estab_desenho.atualizar(gesto_d_bruto)
        gesto_c = self.estab_config.atualizar(gesto_c_bruto)

        return frame, {
            "gesto_desenho":       gesto_d,
            "gesto_config":        gesto_c,
            "ponta_indicador":     ponta_ind,
            "centro_palma":        centro_palma,
            "pos_ind_config":      pos_ind_cfg,
            "pos_pol_config":      pos_pol_cfg,
            "dist_pinca":          dist_pinca,
            "mao_desenho_visivel": mao_visivel,
        }

    def encerrar(self):
        self.cap.release()
        self.hands.close()
