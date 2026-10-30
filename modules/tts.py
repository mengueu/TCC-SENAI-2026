"""
modules/tts.py — Módulo de Síntese de Voz (Text-to-Speech)

pyttsx3 tem um problema bem conhecido: ele não funciona corretamente
quando chamado repetidamente de threads secundárias — o runAndWait()
trava ou para de funcionar após a primeira chamada.

Solução: a engine roda em uma THREAD DEDICADA que fica viva o tempo
todo, e textos são enviados a ela via Queue. Assim, o runAndWait()
é sempre chamado da mesma thread, o que o pyttsx3 suporta corretamente.
"""

import queue
import threading

try:
    import pyttsx3
    PYTTSX3_DISPONIVEL = True
except ImportError:
    PYTTSX3_DISPONIVEL = False
    print("[TTS] AVISO: pyttsx3 nao instalado. Execute: pip install pyttsx3")

TAXA_FALA  = 150
VOLUME_FALA = 1.0

# Sentinela para encerrar o loop interno
_ENCERRAR = object()


class VoiceSpeaker:
    """
    Síntese de voz offline com pyttsx3.
    Usa uma thread dedicada + fila para evitar o problema de
    runAndWait() travar quando chamado de threads diferentes.
    """

    def __init__(self):
        self._fila: queue.Queue = queue.Queue()
        self._thread: threading.Thread | None = None

        if PYTTSX3_DISPONIVEL:
            self._thread = threading.Thread(
                target=self._loop_voz,
                daemon=True,
                name="AlfaIA-TTS",
            )
            self._thread.start()

    def _loop_voz(self):
        """
        Roda em thread dedicada. Inicializa o engine UMA VEZ e fica
        escutando a fila. Chama runAndWait() para cada texto — sempre
        da mesma thread, o que o pyttsx3 suporta corretamente.
        """
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", TAXA_FALA)
            engine.setProperty("volume", VOLUME_FALA)

            # Tenta selecionar voz em português
            vozes = engine.getProperty("voices")
            for voz in vozes:
                nome = voz.name.lower()
                langs = [
                    str(l).lower() for l in (voz.languages or [])
                ]
                if "pt" in nome or "portuguese" in nome or "brazil" in nome \
                        or any("pt" in l for l in langs):
                    engine.setProperty("voice", voz.id)
                    print(f"[TTS] Voz selecionada: {voz.name}")
                    break
            else:
                print("[TTS] Voz em portugues nao encontrada, usando voz padrao.")

            print("[TTS] Motor de voz pronto.")
        except Exception as e:
            print(f"[TTS] Erro ao inicializar motor: {e}")
            return

        while True:
            try:
                texto = self._fila.get(timeout=1)
            except queue.Empty:
                continue

            if texto is _ENCERRAR:
                break

            try:
                engine.say(texto)
                engine.runAndWait()
            except Exception as e:
                print(f"[TTS] Erro ao falar: {e}")

        try:
            engine.stop()
        except Exception:
            pass

    def falar(self, texto: str):
        """
        Envia texto para fila de voz (não bloqueia).
        Se ainda estiver falando algo, a fila acumula (max 1 item).
        """
        if not PYTTSX3_DISPONIVEL:
            print(f"[TTS] (sem voz): {texto}")
            return

        # Descarta mensagens antigas que ainda não foram faladas
        # (para não acumular fila quando o usuário manda várias mensagens rápidas)
        while not self._fila.empty():
            try:
                self._fila.get_nowait()
            except queue.Empty:
                break

        self._fila.put(texto)

    def parar(self):
        """Encerra o loop de voz ordenadamente."""
        if self._thread and self._thread.is_alive():
            self._fila.put(_ENCERRAR)
