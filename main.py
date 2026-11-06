"""
TCC SENAI 2026 — Ferramenta de Alfabetização com Visão Computacional

Grupo 8: Miguel Augusto Rocha, Ana Luiza Ferreira Antônio,
         Maria Luiza Aguilar e Pedro Antunes.

Fluxo de telas:
  1. Boas-vindas          → escolhe matéria
  2a. Língua Portuguesa   → lateralidade → exercício de nome
  2b. Matemática          → menu da operação → lateralidade → exercício de conta

Gestos da mão que DESENHA:
  ☝️  Indicador           → Caneta (escreve ou apaga)
  ✌️  Indicador + Médio   → Pairar (move sem desenhar)
  👍  Polegar             → Confirmar (envia para a IA)

Mão de CONFIGURAÇÃO:
  Indicador no topo → seleciona cor
  Pinça             → ajusta espessura
  Mão aberta        → limpa tudo

Botão borracha (lateral direita): passe o dedo por 1 s para ligar/desligar.
Teclado: C=limpar | E=borracha | ESPAÇO=próxima questão | ESC/Q=sair
"""

import math
import time
import cv2
import numpy as np

from modules.camera     import Camera
from modules.canvas     import Canvas
from modules.ocr        import OCRReader
from modules.feedback   import FeedbackEngine
from modules.matematica import GeradorProblema
from modules.tts        import VoiceSpeaker
from modules.texto      import escrever, medir

# ─── Configurações gerais ─────────────────────────────────────────────────────
CAMERA_INDEX  = 0
FRAME_WIDTH   = 1280
FRAME_HEIGHT  = 720
WINDOW_NAME   = "TCC SENAI 2026"

COR_INICIAL  = (255, 140, 0)
ESP_INICIAL  = 12
ESP_MIN      = 4
ESP_MAX      = 60

PALETA_CORES = [
    (0,   0,   255),
    (0,   140, 255),
    (0,   255, 255),
    (0,   255,   0),
    (255, 200,   0),
    (255,   0,   0),
    (255,   0, 255),
    (255, 255, 255),
]
ALTURA_PALETA        = 80
COOLDOWN_LIMPAR      = 1.5
COOLDOWN_CONFIRMAR   = 1.5
TEMPO_HOVER_BORRACHA = 1.0
RAIO_BOTAO_BORRACHA  = 42

# ─── Cores de UI (BGR) ───────────────────────────────────────────────────────
C_HUD    = (20,  20,  30)
C_BRANCO = (255, 255, 255)
C_AMARELO= (80,  210, 255)
C_VERDE  = (80,  210,  80)
C_VERM   = (80,   80, 255)
C_CINZA  = (160, 160, 160)
C_LARANJA= (60,  140, 255)
C_AZUL   = (200, 100,  40)
C_ROXO   = (200,  60, 180)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _overlay(frame: np.ndarray, alpha: float = 0.65) -> np.ndarray:
    """Escurece o frame para melhorar legibilidade do texto."""
    ov = frame.copy()
    cv2.rectangle(ov, (0, 0), (frame.shape[1], frame.shape[0]), (8, 8, 15), -1)
    cv2.addWeighted(ov, alpha, frame, 1 - alpha, 0, frame)
    return frame


def _botao(
    frame, p1, p2, cor_borda, hover: bool,
    texto: str, cor_texto: tuple,
    tam_txt: int = 30,
    subtexto: str = "", cor_sub: tuple = None,
):
    """Desenha um botão com hover, texto centralizado e subtexto opcional."""
    cor_sub = cor_sub or C_CINZA
    cor_bg = (80, 80, 90) if hover else (40, 40, 50)
    cv2.rectangle(frame, p1, p2, cor_bg, -1)
    cv2.rectangle(frame, p1, p2, cor_borda, 3 if hover else 1)

    # Texto principal centralizado
    tw, th = medir(texto, tam_txt)
    cx = (p1[0] + p2[0]) // 2
    cy = (p1[1] + p2[1]) // 2
    offset_y = -th // 2 - (medir(subtexto, 20)[1] // 2 + 4) if subtexto else -th // 2
    frame = escrever(frame, texto, (cx - tw // 2, cy + offset_y), tam_txt, cor_texto, negrito=hover)

    if subtexto:
        sw, sh = medir(subtexto, 20)
        frame = escrever(frame, subtexto, (cx - sw // 2, cy + th // 2 + 6), 20, cor_sub)

    return frame


def _dentro(pos, p1, p2) -> bool:
    return bool(pos and p1[0] <= pos[0] <= p2[0] and p1[1] <= pos[1] <= p2[1])


def _mesclar(frame: np.ndarray, canvas: np.ndarray) -> np.ndarray:
    cinza = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, inv = cv2.threshold(cinza, 20, 255, cv2.THRESH_BINARY_INV)
    inv = cv2.cvtColor(inv, cv2.COLOR_GRAY2BGR)
    return cv2.bitwise_or(cv2.bitwise_and(frame, inv), canvas)


# ══════════════════════════════════════════════════════════════════════════════
# TELA 1 — BOAS-VINDAS
# ══════════════════════════════════════════════════════════════════════════════

def tela_boas_vindas(cap: cv2.VideoCapture) -> str | None:
    """
    Retorna: 'matematica' | 'portugues' | None (sair)
    """
    mouse = {"pos": None, "clique": None}

    def _mouse(ev, x, y, f, p):
        mouse["pos"] = (x, y)
        if ev == cv2.EVENT_LBUTTONDOWN:
            mouse["clique"] = (x, y)

    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, _mouse)

    while True:
        ok, frame = cap.read()
        if not ok:
            frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), np.uint8)
        else:
            frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        frame = _overlay(frame, 0.70)

        # ── Título ────────────────────────────────────────────────────────────
        titulo  = "Seja bem-vindo!"
        subtit  = "Projeto de TCC — SENAI 2026"
        instruc = "Escolha qual exercício deseja trabalhar:"

        tw, _ = medir(titulo, 70)
        frame = escrever(frame, titulo,  (w//2 - tw//2, h//2 - 230), 70, C_AMARELO, negrito=True)

        sw, _ = medir(subtit, 26)
        frame = escrever(frame, subtit,  (w//2 - sw//2, h//2 - 155), 26, C_CINZA)

        iw, _ = medir(instruc, 30)
        frame = escrever(frame, instruc, (w//2 - iw//2, h//2 -  95), 30, C_BRANCO)

        # ── Botões ────────────────────────────────────────────────────────────
        mat_p1 = (w//2 - 380, h//2 - 55); mat_p2 = (w//2 - 20, h//2 + 90)
        por_p1 = (w//2 +  20, h//2 - 55); por_p2 = (w//2 + 380, h//2 + 90)

        hm = _dentro(mouse["pos"], mat_p1, mat_p2)
        hp = _dentro(mouse["pos"], por_p1, por_p2)

        frame = _botao(frame, mat_p1, mat_p2, C_AZUL,   hm, "Matemática",
                       C_AZUL, 36, "Adição · Divisão · Multiplicação", C_CINZA)
        frame = _botao(frame, por_p1, por_p2, C_VERDE,  hp, "Língua Portuguesa",
                       C_VERDE, 32, "Escrita do seu nome", C_CINZA)

        # ── Rodapé ────────────────────────────────────────────────────────────
        rod = "Clique num botão  |  M = Matemática  |  P = Português  |  Q = Sair"
        rw, _ = medir(rod, 19)
        frame = escrever(frame, rod, (w//2 - rw//2, h - 32), 19, C_CINZA)

        cv2.imshow(WINDOW_NAME, frame)

        if mouse["clique"]:
            cl = mouse["clique"]; mouse["clique"] = None
            if _dentro(cl, mat_p1, mat_p2): return "matematica"
            if _dentro(cl, por_p1, por_p2): return "portugues"

        k = cv2.waitKey(1) & 0xFF
        if k in (ord('m'), ord('M')): return "matematica"
        if k in (ord('p'), ord('P')): return "portugues"
        if k in (ord('q'), ord('Q'), 27): return None


# ══════════════════════════════════════════════════════════════════════════════
# TELA 2 — MENU MATEMÁTICA
# ══════════════════════════════════════════════════════════════════════════════

def tela_menu_matematica(cap: cv2.VideoCapture) -> str | None:
    """
    Retorna: 'adicao' | 'subtracao' | 'multiplicacao' | 'divisao' | None (voltar)
    """
    mouse = {"pos": None, "clique": None}

    def _mouse(ev, x, y, f, p):
        mouse["pos"] = (x, y)
        if ev == cv2.EVENT_LBUTTONDOWN:
            mouse["clique"] = (x, y)

    cv2.setMouseCallback(WINDOW_NAME, _mouse)

    # Quatro opções: adição, subtração, multiplicação, divisão
    opcoes = [
        ("adicao",        "Adição",         "+",  C_VERDE,   "Somar números"),
        ("subtracao",     "Subtração",       "−",  C_VERM,    "Diminuir números"),
        ("multiplicacao", "Multiplicação",   "×",  C_AMARELO, "Multiplicar números"),
        ("divisao",       "Divisão",         "÷",  C_LARANJA, "Dividir números"),
    ]

    while True:
        ok, frame = cap.read()
        if not ok:
            frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), np.uint8)
        else:
            frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        frame = _overlay(frame, 0.72)

        # Título
        titulo = "Matemática — Escolha a operação:"
        tw, _ = medir(titulo, 42)
        frame = escrever(frame, titulo, (w//2 - tw//2, h//2 - 230), 42, C_AMARELO, negrito=True)

        # Botões em grade 2×2
        bw, bh = 270, 130
        gap     = 24
        x_esq   = w//2 - bw - gap//2
        x_dir   = w//2 + gap//2
        y_top   = h//2 - bh - gap//2
        y_bot   = h//2 + gap//2

        posicoes = [
            (x_esq, y_top, x_esq + bw, y_top + bh),
            (x_dir, y_top, x_dir + bw, y_top + bh),
            (x_esq, y_bot, x_esq + bw, y_bot + bh),
            (x_dir, y_bot, x_dir + bw, y_bot + bh),
        ]

        teclas = ['1', '2', '3', '4']

        for i, ((chave, nome, sim, cor, desc), (x1, y1, x2, y2)) in enumerate(
            zip(opcoes, posicoes)
        ):
            p1, p2 = (x1, y1), (x2, y2)
            hov = _dentro(mouse["pos"], p1, p2)
            frame = _botao(frame, p1, p2, cor, hov,
                           f"{sim}  {nome}", cor, 30, desc, C_CINZA)

        # Rodapé
        rod = "Clique numa operação  |  1=Adição  2=Subtração  3=Multiplicação  4=Divisão  |  ESC=Voltar"
        rw, _ = medir(rod, 17)
        frame = escrever(frame, rod, (w//2 - rw//2, h - 32), 17, C_CINZA)

        cv2.imshow(WINDOW_NAME, frame)

        if mouse["clique"]:
            cl = mouse["clique"]; mouse["clique"] = None
            for (chave, *_), (x1, y1, x2, y2) in zip(opcoes, posicoes):
                if _dentro(cl, (x1, y1), (x2, y2)):
                    return chave

        k = cv2.waitKey(1) & 0xFF
        if k == ord('1'): return "adicao"
        if k == ord('2'): return "subtracao"
        if k == ord('3'): return "multiplicacao"
        if k == ord('4'): return "divisao"
        if k in (27, ord('q'), ord('Q')): return None


# ══════════════════════════════════════════════════════════════════════════════
# TELA 3 — ESCOLHA DE LATERALIDADE
# ══════════════════════════════════════════════════════════════════════════════

def tela_lateralidade(cap: cv2.VideoCapture) -> str | None:
    """Retorna 'destro', 'canhoto' ou None (voltar)."""
    mouse = {"pos": None, "clique": None}

    def _mouse(ev, x, y, f, p):
        mouse["pos"] = (x, y)
        if ev == cv2.EVENT_LBUTTONDOWN:
            mouse["clique"] = (x, y)

    cv2.setMouseCallback(WINDOW_NAME, _mouse)

    while True:
        ok, frame = cap.read()
        if not ok:
            frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), np.uint8)
        else:
            frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        frame = _overlay(frame, 0.65)

        titulo = "Você é destro ou canhoto?"
        tw, _ = medir(titulo, 46)
        frame = escrever(frame, titulo, (w//2 - tw//2, h//2 - 190), 46, C_AMARELO, negrito=True)

        sub = "Qual mão você usa para escrever?"
        sw, _ = medir(sub, 26)
        frame = escrever(frame, sub, (w//2 - sw//2, h//2 - 135), 26, C_CINZA)

        d_p1 = (w//2 - 360, h//2 - 70); d_p2 = (w//2 - 20, h//2 + 80)
        c_p1 = (w//2 +  20, h//2 - 70); c_p2 = (w//2 + 360, h//2 + 80)

        hd = _dentro(mouse["pos"], d_p1, d_p2)
        hc = _dentro(mouse["pos"], c_p1, c_p2)

        frame = _botao(frame, d_p1, d_p2, C_VERDE,   hd,
                       "[ D ]  Destro",    C_VERDE,   34, "Mão direita desenha", C_CINZA)
        frame = _botao(frame, c_p1, c_p2, C_AMARELO, hc,
                       "[ C ]  Canhoto",   C_AMARELO, 34, "Mão esquerda desenha", C_CINZA)

        rod = "Clique num botão  |  D = Destro  |  C = Canhoto  |  ESC = Voltar"
        rw, _ = medir(rod, 19)
        frame = escrever(frame, rod, (w//2 - rw//2, h - 32), 19, C_CINZA)

        cv2.imshow(WINDOW_NAME, frame)

        if mouse["clique"]:
            cl = mouse["clique"]; mouse["clique"] = None
            if _dentro(cl, d_p1, d_p2): return "destro"
            if _dentro(cl, c_p1, c_p2): return "canhoto"

        k = cv2.waitKey(1) & 0xFF
        if k in (ord('d'), ord('D')): return "destro"
        if k in (ord('c'), ord('C')): return "canhoto"
        if k in (27, ord('q'), ord('Q')): return None


# ══════════════════════════════════════════════════════════════════════════════
# UI DO EXERCÍCIO — elementos compartilhados
# ══════════════════════════════════════════════════════════════════════════════

def _ui_paleta(frame, cor_atual):
    h, w = frame.shape[:2]
    passo = w // len(PALETA_CORES)
    for i, cor in enumerate(PALETA_CORES):
        x1 = i * passo
        x2 = (i+1)*passo if i < len(PALETA_CORES)-1 else w
        cv2.rectangle(frame, (x1, 0), (x2, ALTURA_PALETA), cor, -1)
        if cor == cor_atual:
            cv2.rectangle(frame, (x1+4, 4), (x2-4, ALTURA_PALETA-4), C_BRANCO, 3)
    return frame


def _ui_botao_borracha(frame, cx, cy, ativa, progresso):
    cor_bg = C_LARANJA if ativa else (60, 60, 70)
    cv2.circle(frame, (cx, cy), RAIO_BOTAO_BORRACHA, cor_bg, -1)
    cv2.circle(frame, (cx, cy), RAIO_BOTAO_BORRACHA, C_BRANCO, 2)
    if 0 < progresso < 1:
        ang = int(360 * progresso)
        cv2.ellipse(frame, (cx, cy), (RAIO_BOTAO_BORRACHA+6,)*2, -90, 0, ang, C_LARANJA, 4)
    ci = C_BRANCO if not ativa else (20, 20, 30)
    cv2.rectangle(frame, (cx-15, cy-8), (cx+15, cy+8), ci, -1)
    cv2.rectangle(frame, (cx-15, cy-8), (cx+15, cy+8),
                  cor_bg if not ativa else C_BRANCO, 2)
    cv2.line(frame, (cx+4, cy-8), (cx+4, cy+8),
             cor_bg if not ativa else C_BRANCO, 2)
    lbl = "APAGAR"
    lw, _ = medir(lbl, 15)
    frame = escrever(frame, lbl, (cx - lw//2, cy + RAIO_BOTAO_BORRACHA + 5),
                     15, (20,20,30) if ativa else C_CINZA)
    return frame


def _ui_cursor(frame, gesto, ponta, ativa_borracha, cor, esp):
    if ponta is None:
        return frame
    if gesto == "pairar":
        cv2.circle(frame, ponta, 18, (255, 200, 50), 3, cv2.LINE_AA)
        cv2.circle(frame, ponta, 5,  (255, 200, 50), -1, cv2.LINE_AA)
        pw, _ = medir("PAIRANDO", 18)
        frame = escrever(frame, "PAIRANDO", (ponta[0]-pw//2, ponta[1]-34), 18, (255, 200, 50))
    elif gesto == "caneta":
        if ativa_borracha:
            r = max(esp, 20)
            cv2.circle(frame, ponta, r, C_LARANJA, 2, cv2.LINE_AA)
            cv2.line(frame, (ponta[0]-r//2, ponta[1]-r//2),
                     (ponta[0]+r//2, ponta[1]+r//2), C_LARANJA, 2)
            cv2.line(frame, (ponta[0]+r//2, ponta[1]-r//2),
                     (ponta[0]-r//2, ponta[1]+r//2), C_LARANJA, 2)
        else:
            cv2.circle(frame, ponta, max(esp//2, 4), cor, -1, cv2.LINE_AA)
            cv2.circle(frame, ponta, max(esp//2, 4), C_BRANCO, 1, cv2.LINE_AA)
    return frame


def _ui_rodape(frame, mao, esp, cor, borracha_ativa):
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, h-50), (w, h), C_HUD, -1)
    outro = "esq." if mao == "direita" else "dir."
    txt = (f"Mão {mao.capitalize()}: Indicador=caneta  Ind+Médio=pairar  Polegar=confirmar  |  "
           f"Mão {outro}: Topo=cor  Pinça=tam.  Aberta=limpa")
    frame = escrever(frame, txt, (10, h-42), 15, C_CINZA)
    modo = "[ APAGANDO ]" if borracha_ativa else "[ ESCREVENDO ]"
    cor_m = C_LARANJA if borracha_ativa else C_VERDE
    mw, _ = medir(modo, 20)
    frame = escrever(frame, modo, (w//2 - mw//2, h-40), 20, cor_m, negrito=True)
    cx_b, cy_b = w-95, h-25
    cv2.circle(frame, (cx_b, cy_b), max(esp//2, 4), cor, -1)
    cv2.circle(frame, (cx_b, cy_b), max(esp//2, 4), C_BRANCO, 1)
    frame = escrever(frame, str(esp), (cx_b+max(esp//2,4)+4, cy_b-7), 16, C_BRANCO)
    return frame


def _ui_analisando(frame):
    h, w = frame.shape[:2]
    ov = frame.copy()
    cv2.rectangle(ov, (w//2-340, h//2-70), (w//2+340, h//2+70), C_HUD, -1)
    cv2.addWeighted(ov, 0.92, frame, 0.08, 0, frame)
    txt = "Analisando..."
    tw, _ = medir(txt, 42)
    frame = escrever(frame, txt, (w//2-tw//2, h//2-22), 42, C_AMARELO, negrito=True)
    return frame


def _ui_feedback(frame, mensagem, tipo):
    h, w = frame.shape[:2]
    cor = {
        "sucesso": C_VERDE,
        "dica":    C_AMARELO,
        "erro":    C_VERM,
    }.get(tipo, C_BRANCO)

    ov = frame.copy()
    cv2.rectangle(ov, (0, h//2-160), (w, h//2+200), (10, 10, 20), -1)
    cv2.addWeighted(ov, 0.90, frame, 0.10, 0, frame)
    cv2.rectangle(frame, (0, h//2-160), (w, h//2-152), cor, -1)

    # Quebra mensagem em linhas
    palavras = mensagem.split()
    linhas, atual = [], ""
    for p in palavras:
        if len(atual) + len(p) + 1 <= 46:
            atual += (" " if atual else "") + p
        else:
            linhas.append(atual); atual = p
    if atual: linhas.append(atual)

    for i, linha in enumerate(linhas):
        lw, _ = medir(linha, 36)
        frame = escrever(frame, linha, (w//2 - lw//2, h//2 - 120 + i*52),
                         36, cor, negrito=(i == 0))

    rod = "ESPAÇO = próxima questão  |  ESC = voltar ao menu"
    rw, _ = medir(rod, 22)
    frame = escrever(frame, rod, (w//2 - rw//2, h//2 + 160), 22, C_CINZA)
    return frame


# ══════════════════════════════════════════════════════════════════════════════
# EXERCÍCIO — loop principal de escrita / OCR / feedback
# ══════════════════════════════════════════════════════════════════════════════

def executar_exercicio(
    cap: cv2.VideoCapture,
    mao_desenho: str,
    modo: str,                        # 'portugues' ou tipo matemático
    gerador: GeradorProblema | None = None,
    feedback_engine: FeedbackEngine | None = None,
    ocr: OCRReader | None = None,
    voz: VoiceSpeaker | None = None,
):
    """
    Loop do exercício. Retorna True para continuar, False para sair totalmente.
    """
    cam    = Camera(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, mao_desenho)
    canvas = Canvas(FRAME_WIDTH, FRAME_HEIGHT, COR_INICIAL, ESP_INICIAL)

    cor_pincel     = COR_INICIAL
    espessura      = ESP_INICIAL
    borracha_ativa = False

    BOTAO_X = FRAME_WIDTH - 60
    BOTAO_Y = FRAME_HEIGHT // 2
    t_hover  = 0.0
    em_hover = False

    t_confirmar = 0.0
    t_limpar    = 0.0

    ST_ESCREVENDO = "escrevendo"
    ST_ANALISANDO = "analisando"
    ST_FEEDBACK   = "feedback"
    estado = ST_ESCREVENDO

    msg_feedback  = ""
    tipo_feedback = "sucesso"

    # Problema inicial (se for matemática)
    if gerador:
        gerador.gerar()

    modo_matematica = modo not in ("portugues",)

    print(f"[Exercício] modo={modo}  mão={mao_desenho}")

    continuar = True
    while continuar:
        frame = cam.ler_frame()
        if frame is None:
            break

        frame, info = cam.processar_frame(frame)
        gesto_d = info["gesto_desenho"]
        gesto_c = info["gesto_config"]
        ponta   = info["ponta_indicador"]
        ind_cfg = info["pos_ind_config"]
        pol_cfg = info["pos_pol_config"]
        dist_p  = info["dist_pinca"]
        h, w    = frame.shape[:2]

        if estado == ST_ESCREVENDO:

            # ── Mão de configuração ───────────────────────────────────────────
            if gesto_c == "limpar_tudo":
                agora = time.time()
                if agora - t_limpar > COOLDOWN_LIMPAR:
                    canvas.limpar(); t_limpar = agora
                tw, _ = medir("LIMPOU TUDO!", 44)
                frame = escrever(frame, "LIMPOU TUDO!", (w//2-tw//2, h//2-22), 44, C_VERM, True)

            elif gesto_c == "selecionar_cor" and ind_cfg:
                cv2.circle(frame, ind_cfg, 15, C_BRANCO, -1)
                passo = w // len(PALETA_CORES)
                for i, cor in enumerate(PALETA_CORES):
                    x1 = i * passo
                    x2 = (i+1)*passo if i < len(PALETA_CORES)-1 else w
                    if x1 < ind_cfg[0] < x2:
                        cor_pincel = cor; canvas.definir_cor(cor_pincel); break

            elif gesto_c == "ajustar_tamanho" and ind_cfg and pol_cfg:
                cv2.line(frame, pol_cfg, ind_cfg, C_BRANCO, 3)
                nova_esp = int(np.interp(dist_p, [20, 250], [ESP_MIN, ESP_MAX]))
                espessura = max(ESP_MIN, min(nova_esp, ESP_MAX))
                canvas.definir_espessura(espessura)
                cx_ = (pol_cfg[0]+ind_cfg[0])//2
                cy_ = (pol_cfg[1]+ind_cfg[1])//2
                cv2.circle(frame, (cx_, cy_), max(espessura//2, 4), cor_pincel, -1)
                cv2.circle(frame, (cx_, cy_), max(espessura//2, 4), C_BRANCO, 2)

            # ── Botão borracha ────────────────────────────────────────────────
            agora = time.time()
            prog  = 0.0
            if ponta is not None:
                dist_b = math.hypot(ponta[0]-BOTAO_X, ponta[1]-BOTAO_Y)
                if dist_b <= RAIO_BOTAO_BORRACHA + 10:
                    if not em_hover:
                        t_hover = agora; em_hover = True
                    prog = min((agora - t_hover) / TEMPO_HOVER_BORRACHA, 1.0)
                    if prog >= 1.0 and em_hover:
                        borracha_ativa = not borracha_ativa
                        canvas.definir_borracha(borracha_ativa)
                        em_hover = False; t_hover = agora + 99
                else:
                    em_hover = False
            else:
                em_hover = False

            # ── Mão de desenho ────────────────────────────────────────────────
            if gesto_d == "caneta" and ponta:
                if borracha_ativa:
                    canvas.apagar(ponta, raio=max(espessura, 20))
                else:
                    canvas.desenhar(ponta)
            elif gesto_d in ("pairar", "ocioso", "confirmar"):
                canvas.levantar_caneta()

            if gesto_d == "confirmar":
                if agora - t_confirmar > COOLDOWN_CONFIRMAR:
                    t_confirmar = agora; estado = ST_ANALISANDO

            # ── Render ───────────────────────────────────────────────────────
            frame = _mesclar(frame, canvas.obter_canvas())
            frame = _ui_paleta(frame, cor_pincel)

            # Enunciado do exercício (abaixo da paleta)
            if modo_matematica and gerador:
                enunciado = f"{gerador.texto_problema}  =  ?"
                ew, _ = medir(enunciado, 90)
                frame = escrever(frame, enunciado, (w//2 - ew//2, ALTURA_PALETA + 10), 90, C_AMARELO, True)
                # Dica de operação
                op = gerador.nome_operacao()
                dw, _ = medir(op, 22)
                frame = escrever(frame, op, (w//2 - dw//2, ALTURA_PALETA + 108), 22, C_CINZA)
            else:
                perg = "Qual o seu nome?"
                pw, _ = medir(perg, 50)
                frame = escrever(frame, perg, (w//2 - pw//2, ALTURA_PALETA + 14), 50, C_AMARELO, True)

            frame = _ui_botao_borracha(frame, BOTAO_X, BOTAO_Y, borracha_ativa, prog)
            frame = _ui_cursor(frame, gesto_d, ponta, borracha_ativa, cor_pincel, espessura)
            frame = _ui_rodape(frame, mao_desenho, espessura, cor_pincel, borracha_ativa)

        elif estado == ST_ANALISANDO:
            frame = _mesclar(frame, canvas.obter_canvas())
            if modo_matematica and gerador:
                ew, _ = medir(f"{gerador.texto_problema}  =  ?", 90)
                frame = escrever(frame, f"{gerador.texto_problema}  =  ?",
                                 (w//2 - ew//2, ALTURA_PALETA + 10), 90, C_AMARELO, True)
            frame = _ui_analisando(frame)
            cv2.imshow(WINDOW_NAME, frame)
            cv2.waitKey(1)

            img_ocr = canvas.obter_canvas_para_ocr()
            if modo_matematica:
                texto = ocr.ler_numero(img_ocr)
                print(f"[OCR-num] '{texto}'")
                msg_feedback, tipo_feedback = gerador.verificar(texto)
            else:
                texto = ocr.ler_escrita(img_ocr)
                print(f"[OCR-txt] '{texto}'")
                msg_feedback, tipo_feedback, _ = feedback_engine.gerar_feedback_nome(texto)

            print(f"[Feedback] {tipo_feedback}: {msg_feedback}")
            voz.falar(msg_feedback)
            estado = ST_FEEDBACK

        elif estado == ST_FEEDBACK:
            frame = _mesclar(frame, canvas.obter_canvas())
            if modo_matematica and gerador:
                ew, _ = medir(f"{gerador.texto_problema}  =  ?", 90)
                frame = escrever(frame, f"{gerador.texto_problema}  =  ?",
                                 (w//2 - ew//2, ALTURA_PALETA + 10), 90, C_AMARELO, True)
            frame = _ui_feedback(frame, msg_feedback, tipo_feedback)

        cv2.imshow(WINDOW_NAME, frame)

        # ── Teclas ────────────────────────────────────────────────────────────
        k = cv2.waitKey(1) & 0xFF
        if k in (27, ord('q'), ord('Q')):
            continuar = False
        elif k == ord(' '):
            canvas.limpar()
            borracha_ativa = False
            canvas.definir_borracha(False)
            if gerador:
                gerador.gerar()
            estado = ST_ESCREVENDO
        elif k in (ord('c'), ord('C')) and estado == ST_ESCREVENDO:
            canvas.limpar()
        elif k in (ord('e'), ord('E')) and estado == ST_ESCREVENDO:
            borracha_ativa = not borracha_ativa
            canvas.definir_borracha(borracha_ativa)

    cam.encerrar()
    return continuar


# ══════════════════════════════════════════════════════════════════════════════
# PONTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    if not cap.isOpened():
        print("[ERRO] Não foi possível abrir a câmera."); return

    # Módulos compartilhados (inicializados uma vez)
    ocr      = OCRReader()
    feedback = FeedbackEngine()
    voz      = VoiceSpeaker()

    print("[TCC SENAI 2026] Iniciado.")

    sair_total = False
    while not sair_total:

        # ── Tela 1: Boas-vindas ───────────────────────────────────────────────
        materia = tela_boas_vindas(cap)
        if materia is None:
            break

        if materia == "portugues":
            lat = tela_lateralidade(cap)
            if lat is None:
                continue  # volta ao menu
            mao = "direita" if lat == "destro" else "esquerda"
            continuar = executar_exercicio(cap, mao, "portugues",
                                           feedback_engine=feedback, ocr=ocr, voz=voz)
            if not continuar:
                sair_total = True

        elif materia == "matematica":
            tipo_op = tela_menu_matematica(cap)
            if tipo_op is None:
                continue  # volta ao menu principal

            lat = tela_lateralidade(cap)
            if lat is None:
                continue
            mao = "direita" if lat == "destro" else "esquerda"

            gerador = GeradorProblema(tipo_op)
            continuar = executar_exercicio(cap, mao, tipo_op,
                                           gerador=gerador, ocr=ocr, voz=voz)
            if not continuar:
                sair_total = True

    voz.parar()
    cap.release()
    cv2.destroyAllWindows()
    print("[TCC SENAI 2026] Encerrado.")


if __name__ == "__main__":
    main()
