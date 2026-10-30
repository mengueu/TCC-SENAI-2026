"""
AlfaIA — Ferramenta de Alfabetização com Visão Computacional
TCC do Curso Técnico de Desenvolvimento de Sistemas — SENAI 2026

Grupo 8: Miguel Augusto Rocha, Ana Luiza Ferreira Antônio,
         Maria Luiza Aguilar e Pedro Antunes.

Sistema de duas mãos (portado da v7 da Semana Aberta):

  Mão que DESENHA:
    ☝️  Indicador       → Caneta (desenha ou apaga, conforme modo ativo)
    ✌️  Indicador+médio → Pairar (move sem desenhar — para reposicionar,
                          fazer pingos, acentos, etc.)
    👍  Polegar          → Confirmar (envia para o OCR)
    👊  Mão fechada      → Nada (cursor some)

  Mão que CONFIGURA:
    Indicador no topo da tela → Seleciona cor na paleta
    Pinça (polegar+indicador) → Ajusta espessura
    Mão aberta (4 dedos)      → Limpa tudo

  Botão de Borracha (UI):
    - Botão circular visível na lateral direita
    - Passe o dedo sobre ele por 1 segundo para ativar/desativar
    - Quando ativo, o modo CANETA apaga em vez de desenhar
    - Indicador visual claro do modo atual (ESCREVENDO / APAGANDO)
"""

import math
import time
import cv2
import numpy as np

from modules.camera   import Camera
from modules.canvas   import Canvas
from modules.ocr      import OCRReader
from modules.feedback import FeedbackEngine
from modules.tts      import VoiceSpeaker
from modules.texto    import escrever, medir   # renderização UTF-8 com acentos

# ─── Configurações gerais ─────────────────────────────────────────────────────
CAMERA_INDEX = 0
FRAME_WIDTH  = 1280
FRAME_HEIGHT = 720
WINDOW_NAME  = "AlfaIA"

COR_TRAÇO_INICIAL = (255, 140, 0)
ESPESSURA_INICIAL = 12
ESPESSURA_MIN     = 4
ESPESSURA_MAX     = 60

# Paleta de cores (BGR) — igual à v7
PALETA_CORES = [
    (0,   0,   255),  # vermelho
    (0,   140, 255),  # laranja
    (0,   255, 255),  # amarelo
    (0,   255, 0),    # verde
    (255, 200, 0),    # azul claro
    (255, 0,   0),    # azul
    (255, 0,   255),  # rosa
    (255, 255, 255),  # branco
]
ALTURA_PALETA = 80

COOLDOWN_LIMPAR    = 1.5
COOLDOWN_CONFIRMAR = 1.5

TEMPO_HOVER_BORRACHA = 1.0
RAIO_BOTAO_BORRACHA  = 42

# ─── Estados ─────────────────────────────────────────────────────────────────
ST_ESCREVENDO = "escrevendo"
ST_ANALISANDO = "analisando"
ST_FEEDBACK   = "feedback"

# ─── Cores de UI (BGR) ───────────────────────────────────────────────────────
C_HUD_BG   = (20,  20,  30)
C_BRANCO   = (255, 255, 255)
C_AMARELO  = (80,  210, 255)
C_VERDE    = (80,  210, 80)
C_VERMELHO = (80,  80,  255)
C_CINZA    = (160, 160, 160)
C_LARANJA  = (60,  140, 255)


# ─────────────────────────────────────────────────────────────────────────────
# TELA DE ESCOLHA DESTRO / CANHOTO
# ─────────────────────────────────────────────────────────────────────────────

def escolher_lateralidade(cap: cv2.VideoCapture) -> str | None:
    """Retorna 'destro', 'canhoto' ou None (sair)."""
    mouse = {"pos": None, "clique": None}

    def ao_mouse(ev, x, y, flags, param):
        mouse["pos"] = (x, y)
        if ev == cv2.EVENT_LBUTTONDOWN:
            mouse["clique"] = (x, y)

    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, ao_mouse)

    def dentro(pos, p1, p2):
        return pos and p1[0] <= pos[0] <= p2[0] and p1[1] <= pos[1] <= p2[1]

    while True:
        ok, frame = cap.read()
        frame = cv2.flip(frame, 1) if ok else np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), np.uint8)
        h, w = frame.shape[:2]

        ov = frame.copy()
        cv2.rectangle(ov, (0, 0), (w, h), (10, 10, 10), -1)
        cv2.addWeighted(ov, 0.6, frame, 0.4, 0, frame)

        # Título
        lw, _ = medir("AlfaIA", 80)
        frame = escrever(frame, "AlfaIA", (w//2 - lw//2, h//2 - 220), 80, C_AMARELO, negrito=True)

        # Subtítulo
        sub = "Você é destro ou canhoto?"
        sw, _ = medir(sub, 36)
        frame = escrever(frame, sub, (w//2 - sw//2, h//2 - 145), 36, C_BRANCO)

        d_p1 = (w//2 - 360, h//2 - 80); d_p2 = (w//2 - 30, h//2 + 80)
        c_p1 = (w//2 + 30,  h//2 - 80); c_p2 = (w//2 + 360, h//2 + 80)

        hd = dentro(mouse["pos"], d_p1, d_p2)
        hc = dentro(mouse["pos"], c_p1, c_p2)

        # Botão Destro
        cv2.rectangle(frame, d_p1, d_p2, (95,95,95) if hd else (55,55,55), -1)
        if hd:
            cv2.rectangle(frame, d_p1, d_p2, C_VERDE, 3)
        frame = escrever(frame, "[ D ]  Destro",    (w//2-345, h//2-52), 34, C_VERDE, negrito=hd)
        frame = escrever(frame, "Mão direita desenha", (w//2-345, h//2+10), 24, C_CINZA)

        # Botão Canhoto
        cv2.rectangle(frame, c_p1, c_p2, (95,95,95) if hc else (55,55,55), -1)
        if hc:
            cv2.rectangle(frame, c_p1, c_p2, C_AMARELO, 3)
        frame = escrever(frame, "[ C ]  Canhoto",      (w//2+40, h//2-52), 34, C_AMARELO, negrito=hc)
        frame = escrever(frame, "Mão esquerda desenha", (w//2+40, h//2+10), 24, C_CINZA)

        # Rodapé
        rod = "Clique num botão, ou pressione D / C  |  Q ou ESC para sair"
        rw, _ = medir(rod, 20)
        frame = escrever(frame, rod, (w//2 - rw//2, h - 40), 20, C_CINZA)

        cv2.imshow(WINDOW_NAME, frame)

        if mouse["clique"]:
            cl = mouse["clique"]; mouse["clique"] = None
            if dentro(cl, d_p1, d_p2): return "destro"
            if dentro(cl, c_p1, c_p2): return "canhoto"

        k = cv2.waitKey(1) & 0xFF
        if k in (ord('d'), ord('D')): return "destro"
        if k in (ord('c'), ord('C')): return "canhoto"
        if k in (ord('q'), ord('Q'), 27): return None


# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES DE DESENHO DE UI
# ─────────────────────────────────────────────────────────────────────────────

def _mesclar(frame: np.ndarray, canvas: np.ndarray) -> np.ndarray:
    cinza = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, inv = cv2.threshold(cinza, 20, 255, cv2.THRESH_BINARY_INV)
    inv = cv2.cvtColor(inv, cv2.COLOR_GRAY2BGR)
    return cv2.bitwise_or(cv2.bitwise_and(frame, inv), canvas)


def _desenhar_paleta(frame: np.ndarray, cor_atual: tuple) -> np.ndarray:
    h, w = frame.shape[:2]
    passo = w // len(PALETA_CORES)
    for i, cor in enumerate(PALETA_CORES):
        x1 = i * passo
        x2 = (i+1)*passo if i < len(PALETA_CORES)-1 else w
        cv2.rectangle(frame, (x1, 0), (x2, ALTURA_PALETA), cor, -1)
        if cor == cor_atual:
            cv2.rectangle(frame, (x1+4, 4), (x2-4, ALTURA_PALETA-4), C_BRANCO, 3)

    # Pergunta centralizada abaixo da paleta
    pergunta = "Qual o seu nome?"
    pw, _ = medir(pergunta, 46)
    frame = escrever(frame, pergunta, (w//2 - pw//2, ALTURA_PALETA + 12), 46, C_AMARELO, negrito=True)
    return frame


def _desenhar_botao_borracha(
    frame: np.ndarray, cx: int, cy: int,
    borracha_ativa: bool, progresso_hover: float,
) -> np.ndarray:
    cor_fundo = C_LARANJA if borracha_ativa else (60, 60, 70)
    cv2.circle(frame, (cx, cy), RAIO_BOTAO_BORRACHA, cor_fundo, -1)
    cv2.circle(frame, (cx, cy), RAIO_BOTAO_BORRACHA, C_BRANCO, 2)

    if 0 < progresso_hover < 1.0:
        angulo = int(360 * progresso_hover)
        cv2.ellipse(frame, (cx, cy),
                    (RAIO_BOTAO_BORRACHA+6, RAIO_BOTAO_BORRACHA+6),
                    -90, 0, angulo, C_LARANJA, 4)

    # Ícone de borracha
    cor_icon = C_BRANCO if not borracha_ativa else (20, 20, 30)
    cv2.rectangle(frame, (cx-15, cy-8), (cx+15, cy+8), cor_icon, -1)
    cv2.rectangle(frame, (cx-15, cy-8), (cx+15, cy+8),
                  cor_fundo if not borracha_ativa else C_BRANCO, 2)
    cv2.line(frame, (cx+4, cy-8), (cx+4, cy+8),
             cor_fundo if not borracha_ativa else C_BRANCO, 2)

    label = "APAGAR"
    lw, _ = medir(label, 16)
    frame = escrever(frame, label,
                     (cx - lw//2, cy + RAIO_BOTAO_BORRACHA + 6), 16,
                     (20,20,30) if borracha_ativa else C_CINZA)
    return frame


def _desenhar_indicador_modo(
    frame: np.ndarray, borracha_ativa: bool, gesto: str,
    ponta: tuple | None, cor_pincel: tuple, espessura: int,
) -> np.ndarray:
    if ponta is None:
        return frame

    if gesto == "pairar":
        cv2.circle(frame, ponta, 18, (255, 200, 50), 3, cv2.LINE_AA)
        cv2.circle(frame, ponta, 5,  (255, 200, 50), -1, cv2.LINE_AA)
        pw, _ = medir("PAIRANDO", 20)
        frame = escrever(frame, "PAIRANDO",
                         (ponta[0] - pw//2, ponta[1] - 36), 20, (255, 200, 50))
    elif gesto == "caneta":
        if borracha_ativa:
            r = max(espessura, 20)
            cv2.circle(frame, ponta, r, C_LARANJA, 2, cv2.LINE_AA)
            cv2.line(frame, (ponta[0]-r//2, ponta[1]-r//2),
                     (ponta[0]+r//2, ponta[1]+r//2), C_LARANJA, 2)
            cv2.line(frame, (ponta[0]+r//2, ponta[1]-r//2),
                     (ponta[0]-r//2, ponta[1]+r//2), C_LARANJA, 2)
        else:
            cv2.circle(frame, ponta, max(espessura//2, 4), cor_pincel, -1, cv2.LINE_AA)
            cv2.circle(frame, ponta, max(espessura//2, 4), C_BRANCO, 1, cv2.LINE_AA)
    return frame


def _hud_rodape(
    frame: np.ndarray, mao_d: str, espessura: int,
    cor: tuple, borracha_ativa: bool,
) -> np.ndarray:
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, h-50), (w, h), C_HUD_BG, -1)

    outro = "esq." if mao_d == "direita" else "dir."
    lado  = mao_d.capitalize()
    instrucao = (
        f"Mão {lado}: Indicador=caneta  Indicador+Médio=pairar  Polegar=confirmar  |  "
        f"Mão {outro}: Topo=cor  Pinça=tamanho  Aberta=limpar"
    )
    frame = escrever(frame, instrucao, (10, h-42), 17, C_CINZA)

    # Indicador de modo (centro do rodapé)
    modo_str = "[ APAGANDO ]" if borracha_ativa else "[ ESCREVENDO ]"
    cor_modo  = C_LARANJA if borracha_ativa else C_VERDE
    mw, _ = medir(modo_str, 22)
    frame = escrever(frame, modo_str, (w//2 - mw//2, h-40), 22, cor_modo, negrito=True)

    # Bolinha de cor + espessura (canto direito)
    cx_b = w - 95
    cy_b = h - 25
    cv2.circle(frame, (cx_b, cy_b), max(espessura//2, 4), cor, -1)
    cv2.circle(frame, (cx_b, cy_b), max(espessura//2, 4), C_BRANCO, 1)
    frame = escrever(frame, str(espessura),
                     (cx_b + max(espessura//2, 4) + 5, cy_b - 8), 18, C_BRANCO)
    return frame


def _hud_analisando(frame: np.ndarray) -> np.ndarray:
    h, w = frame.shape[:2]
    ov = frame.copy()
    cv2.rectangle(ov, (w//2-340, h//2-70), (w//2+340, h//2+70), C_HUD_BG, -1)
    cv2.addWeighted(ov, 0.92, frame, 0.08, 0, frame)
    txt = "Analisando sua escrita..."
    tw, _ = medir(txt, 40)
    frame = escrever(frame, txt, (w//2 - tw//2, h//2 - 22), 40, C_AMARELO, negrito=True)
    return frame


def _hud_feedback(frame: np.ndarray, mensagem: str, tipo: str) -> np.ndarray:
    h, w = frame.shape[:2]
    cor = {"sucesso": C_VERDE, "dica": C_AMARELO, "erro": C_VERMELHO}.get(tipo, C_BRANCO)

    ov = frame.copy()
    cv2.rectangle(ov, (0, h//2-150), (w, h//2+190), (12, 12, 22), -1)
    cv2.addWeighted(ov, 0.90, frame, 0.10, 0, frame)
    cv2.rectangle(frame, (0, h//2-150), (w, h//2-143), cor, -1)

    # Quebra a mensagem em linhas de ~50 caracteres
    palavras = mensagem.split()
    linhas, atual = [], ""
    for p in palavras:
        if len(atual) + len(p) + 1 <= 50:
            atual += (" " if atual else "") + p
        else:
            linhas.append(atual); atual = p
    if atual:
        linhas.append(atual)

    for i, linha in enumerate(linhas):
        lw, _ = medir(linha, 38)
        frame = escrever(frame, linha,
                         (w//2 - lw//2, h//2 - 110 + i*55), 38, cor, negrito=(i==0))

    rod = "Pressione ESPAÇO para tentar de novo"
    rw, _ = medir(rod, 26)
    frame = escrever(frame, rod, (w//2 - rw//2, h//2 + 152), 26, C_CINZA)
    return frame


# ─────────────────────────────────────────────────────────────────────────────
# LOOP PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def main():
    cap_raw = cv2.VideoCapture(CAMERA_INDEX)
    cap_raw.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap_raw.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    if not cap_raw.isOpened():
        print("[ERRO] Não foi possível abrir a câmera."); return

    lateralidade = escolher_lateralidade(cap_raw)
    if lateralidade is None:
        cap_raw.release(); cv2.destroyAllWindows(); return

    mao_desenho = "direita" if lateralidade == "destro" else "esquerda"
    print(f"[AlfaIA] Perfil: {lateralidade.upper()} | Mão que desenha: {mao_desenho}")

    # ── Módulos ───────────────────────────────────────────────────────────────
    cor_pincel = COR_TRAÇO_INICIAL
    espessura  = ESPESSURA_INICIAL

    cam      = Camera(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, mao_desenho)
    canvas   = Canvas(FRAME_WIDTH, FRAME_HEIGHT, cor_pincel, espessura)
    ocr      = OCRReader()
    feedback = FeedbackEngine()
    voz      = VoiceSpeaker()

    estado           = ST_ESCREVENDO
    msg_feedback     = ""
    tipo_feedback    = "sucesso"
    t_confirmar      = 0.0
    t_limpar         = 0.0
    borracha_ativa   = False

    BOTAO_X = FRAME_WIDTH - 60
    BOTAO_Y = FRAME_HEIGHT // 2
    t_hover_borracha  = 0.0
    em_hover_borracha = False

    print("[AlfaIA] Iniciado.")
    print("  Gestos da mão que escreve:")
    print("    Indicador           = caneta (escreve ou apaga)")
    print("    Indicador + Médio   = pairar (move sem escrever)")
    print("    Polegar             = confirmar (envia para IA)")
    print("  Botão de borracha: passe o dedo sobre ele por 1 segundo")
    print("  Teclado: C=limpar | E=toggle borracha | ESPAÇO=nova tentativa | Q=sair")

    while True:
        frame = cam.ler_frame()
        if frame is None:
            print("[ERRO] Frame perdido."); break

        frame, info = cam.processar_frame(frame)

        gesto_d = info["gesto_desenho"]
        gesto_c = info["gesto_config"]
        ponta   = info["ponta_indicador"]
        ind_cfg = info["pos_ind_config"]
        pol_cfg = info["pos_pol_config"]
        dist_p  = info["dist_pinca"]

        h, w = frame.shape[:2]

        if estado == ST_ESCREVENDO:

            # ── Mão de configuração ───────────────────────────────────────────
            if gesto_c == "limpar_tudo":
                agora = time.time()
                if agora - t_limpar > COOLDOWN_LIMPAR:
                    canvas.limpar(); t_limpar = agora
                tw, _ = medir("LIMPOU TUDO!", 44)
                frame = escrever(frame, "LIMPOU TUDO!",
                                 (w//2 - tw//2, h//2 - 22), 44, C_VERMELHO, negrito=True)

            elif gesto_c == "selecionar_cor" and ind_cfg:
                cv2.circle(frame, ind_cfg, 15, C_BRANCO, -1)
                passo = w // len(PALETA_CORES)
                for i, cor in enumerate(PALETA_CORES):
                    x1 = i * passo
                    x2 = (i+1)*passo if i < len(PALETA_CORES)-1 else w
                    if x1 < ind_cfg[0] < x2:
                        cor_pincel = cor
                        canvas.definir_cor(cor_pincel)
                        break

            elif gesto_c == "ajustar_tamanho" and ind_cfg and pol_cfg:
                cv2.line(frame, pol_cfg, ind_cfg, C_BRANCO, 3)
                nova_esp = int(np.interp(dist_p, [20, 250], [ESPESSURA_MIN, ESPESSURA_MAX]))
                espessura = max(ESPESSURA_MIN, min(nova_esp, ESPESSURA_MAX))
                canvas.definir_espessura(espessura)
                cx = (pol_cfg[0]+ind_cfg[0])//2
                cy = (pol_cfg[1]+ind_cfg[1])//2
                cv2.circle(frame, (cx, cy), max(espessura//2, 4), cor_pincel, -1)
                cv2.circle(frame, (cx, cy), max(espessura//2, 4), C_BRANCO, 2)

            # ── Botão de borracha ─────────────────────────────────────────────
            agora = time.time()
            progresso_botao = 0.0
            if ponta is not None:
                dist_botao = math.hypot(ponta[0] - BOTAO_X, ponta[1] - BOTAO_Y)
                if dist_botao <= RAIO_BOTAO_BORRACHA + 10:
                    if not em_hover_borracha:
                        t_hover_borracha  = agora
                        em_hover_borracha = True
                    tempo_no_botao  = agora - t_hover_borracha
                    progresso_botao = min(tempo_no_botao / TEMPO_HOVER_BORRACHA, 1.0)
                    if progresso_botao >= 1.0 and em_hover_borracha:
                        borracha_ativa    = not borracha_ativa
                        canvas.definir_borracha(borracha_ativa)
                        em_hover_borracha = False
                        t_hover_borracha  = agora + 99
                else:
                    em_hover_borracha = False
            else:
                em_hover_borracha = False

            # ── Mão que DESENHA ───────────────────────────────────────────────
            if gesto_d == "caneta" and ponta:
                if borracha_ativa:
                    canvas.apagar(ponta, raio=max(espessura, 20))
                else:
                    canvas.desenhar(ponta)
            elif gesto_d in ("pairar", "ocioso", "confirmar"):
                canvas.levantar_caneta()

            if gesto_d == "confirmar":
                agora = time.time()
                if agora - t_confirmar > COOLDOWN_CONFIRMAR:
                    t_confirmar = agora
                    estado = ST_ANALISANDO

            # ── Renderização ──────────────────────────────────────────────────
            frame = _mesclar(frame, canvas.obter_canvas())
            frame = _desenhar_paleta(frame, cor_pincel)
            frame = _desenhar_botao_borracha(frame, BOTAO_X, BOTAO_Y,
                                             borracha_ativa, progresso_botao)
            frame = _desenhar_indicador_modo(frame, borracha_ativa, gesto_d,
                                             ponta, cor_pincel, espessura)
            frame = _hud_rodape(frame, mao_desenho, espessura, cor_pincel, borracha_ativa)

        elif estado == ST_ANALISANDO:
            frame = _mesclar(frame, canvas.obter_canvas())
            frame = _hud_analisando(frame)
            cv2.imshow(WINDOW_NAME, frame)
            cv2.waitKey(1)

            img_ocr = canvas.obter_canvas_para_ocr()
            texto = ocr.ler_escrita(img_ocr)
            print(f"[OCR] Texto lido: '{texto}'")

            msg_feedback, tipo_feedback, _ = feedback.gerar_feedback_nome(texto)
            print(f"[Feedback] {tipo_feedback}: {msg_feedback}")
            voz.falar(msg_feedback)
            estado = ST_FEEDBACK

        elif estado == ST_FEEDBACK:
            frame = _mesclar(frame, canvas.obter_canvas())
            frame = _hud_feedback(frame, msg_feedback, tipo_feedback)

        cv2.imshow(WINDOW_NAME, frame)

        k = cv2.waitKey(1) & 0xFF
        if k in (ord('q'), ord('Q'), 27):
            break
        elif k == ord(' '):
            canvas.limpar()
            borracha_ativa = False
            canvas.definir_borracha(False)
            estado = ST_ESCREVENDO
        elif k in (ord('c'), ord('C')) and estado == ST_ESCREVENDO:
            canvas.limpar()
        elif k in (ord('e'), ord('E')) and estado == ST_ESCREVENDO:
            borracha_ativa = not borracha_ativa
            canvas.definir_borracha(borracha_ativa)
            print(f"[AlfaIA] Borracha: {'ON' if borracha_ativa else 'OFF'}")

    voz.parar()
    cam.encerrar()
    cv2.destroyAllWindows()
    print("[AlfaIA] Encerrado.")


if __name__ == "__main__":
    main()
