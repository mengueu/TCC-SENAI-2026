"""
modules/feedback.py — Módulo de Geração de Feedback

Compara o texto escrito com nomes brasileiros usando Levenshtein.
A comparação é feita sobre strings SEM acentos para lidar com
erros comuns de OCR em escrita manual (ex: "Isão" → "João",
"Lucaz" → "Lucas").
"""

import re
import unicodedata
from pathlib import Path

try:
    from Levenshtein import distance as levenshtein_distance
    LEVENSHTEIN_DISPONIVEL = True
except ImportError:
    LEVENSHTEIN_DISPONIVEL = False
    print("[Feedback] AVISO: python-Levenshtein nao instalado. Usando fallback.")


# ─── Limiares ────────────────────────────────────────────────────────────────
LIMIAR_SUCESSO = 0.20   # ≤ 20% diferente (sem acento) → sucesso
LIMIAR_DICA    = 0.55   # ≤ 55% diferente              → dica
TAMANHO_MINIMO = 2


def _remover_acentos(texto: str) -> str:
    """
    Remove acentos e cedilhas de uma string.
    "João" → "joao", "Isão" → "isao", "Luísa" → "luisa"

    Isso é fundamental para o OCR: o Tesseract frequentemente confunde
    letras com acento, especialmente em escrita manual. Ao comparar sem
    acentos, "Isão" e "João" ficam muito mais próximos (distância 1).
    """
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


class FeedbackEngine:
    """Gera feedback personalizado para a criança com base no que ela escreveu."""

    def __init__(self):
        self._nomes_br = self._carregar_nomes()
        # Pré-computa versões sem acento para comparação rápida
        self._nomes_sem_acento = [
            (_remover_acentos(n).lower(), n) for n in self._nomes_br
        ]
        print(f"[Feedback] {len(self._nomes_br)} nomes carregados.")

    # ─────────────────────────────────────────────────────────────────────────

    def gerar_feedback_nome(self, texto_lido: str) -> tuple[str, str, str]:
        """
        Analisa o texto do OCR e retorna (mensagem, tipo, nome_detectado).
        tipo: "sucesso" | "dica" | "erro"
        """
        texto = texto_lido.strip()

        # Caso 1: OCR não leu nada útil
        if len(texto) < TAMANHO_MINIMO:
            return (
                "Hmm, não consegui ler o que você escreveu. "
                "Tente escrever mais devagar, letra por letra!",
                "erro", "",
            )

        nome_proximo, dist_norm = self._nome_mais_proximo(texto)

        # Caso 2: Correto (ou muito próximo)
        if dist_norm <= LIMIAR_SUCESSO:
            nome = nome_proximo or texto
            return (
                f"Olá, {nome}! Parabéns, você escreveu seu nome certinho!",
                "sucesso", nome,
            )

        # Caso 3: Próximo mas com erros — dica
        if dist_norm <= LIMIAR_DICA and nome_proximo:
            dica = self._gerar_dica(texto, nome_proximo)
            return (
                f"Você quis dizer que seu nome é {nome_proximo}? "
                f"{dica} Tente de novo!",
                "dica", nome_proximo,
            )

        # Caso 4: Muito diferente
        return (
            f"Não reconheci esse nome. Você escreveu '{texto}'. "
            f"Tente escrever com calma, uma letra de cada vez!",
            "erro", texto,
        )

    # ─────────────────────────────────────────────────────────────────────────

    def _carregar_nomes(self) -> list[str]:
        caminho = Path(__file__).parent.parent / "data" / "nomes_br.txt"
        if caminho.exists():
            with open(caminho, encoding="utf-8") as f:
                return [l.strip().title() for l in f
                        if l.strip() and not l.strip().startswith("#")]
        print("[Feedback] AVISO: data/nomes_br.txt nao encontrado. Usando lista embutida.")
        return [
            "Miguel", "Arthur", "Heitor", "Theo", "Davi", "Gabriel", "Bernardo",
            "Samuel", "Lucas", "Pedro", "Mateus", "Rafael", "Enzo", "Guilherme",
            "Nicolas", "Felipe", "Vitor", "Eduardo", "Gustavo", "Daniel",
            "Joao", "João", "Carlos", "Paulo", "Andre", "Marcelo", "Diego",
            "Sofia", "Alice", "Laura", "Isabella", "Valentina", "Julia",
            "Beatriz", "Helena", "Mariana", "Lara", "Camila", "Leticia",
            "Ana", "Luiza", "Maria", "Clara", "Vitoria", "Giovanna", "Livia",
            "Yasmin", "Manuela", "Fernanda", "Bianca", "Gabriela",
            "Ana Luiza", "Ana Clara", "Maria Luiza", "Maria Eduarda",
        ]

    def _distancia_sem_acento(self, a: str, b_sem_acento: str) -> float:
        """
        Compara 'a' (texto do OCR) com 'b_sem_acento' (nome já normalizado).
        Ambos já devem estar em minúsculas sem acento.
        """
        if LEVENSHTEIN_DISPONIVEL:
            dist = levenshtein_distance(a, b_sem_acento)
        else:
            dist = self._levenshtein_fallback(a, b_sem_acento)
        tamanho_max = max(len(a), len(b_sem_acento))
        return 0.0 if tamanho_max == 0 else dist / tamanho_max

    def _nome_mais_proximo(self, texto: str) -> tuple[str, float]:
        """
        Encontra o nome mais próximo usando comparação SEM acentos.
        Também testa cada parte do nome (para nomes compostos).
        """
        texto_sa = _remover_acentos(texto).lower()

        melhor_nome = ""
        melhor_dist = 1.0

        for nome_sa, nome_original in self._nomes_sem_acento:
            # Nome completo
            dist = self._distancia_sem_acento(texto_sa, nome_sa)
            if dist < melhor_dist:
                melhor_dist = dist
                melhor_nome = nome_original

            # Partes do nome (primeiro nome isolado, etc.)
            for parte_sa, parte_orig in zip(
                nome_sa.split(), nome_original.split()
            ):
                d = self._distancia_sem_acento(texto_sa, parte_sa)
                if d < melhor_dist:
                    melhor_dist = d
                    melhor_nome = parte_orig

        return melhor_nome, melhor_dist

    def _gerar_dica(self, escrito: str, correto: str) -> str:
        """Gera dica sobre qual parte provavelmente está errada."""
        # Compara sem acento para achar a primeira diferença real
        e = _remover_acentos(escrito).lower()
        c = _remover_acentos(correto).lower()

        for i, (ce, cc) in enumerate(zip(e, c)):
            if ce != cc:
                letra_correta = correto[i].upper() if i < len(correto) else "?"
                return (f"Parece que a letra '{letra_correta}' ficou diferente. "
                        f"Escreva '{correto}' com calma!")

        if len(escrito) < len(correto):
            faltou = correto[len(escrito):]
            return f"Faltou '{faltou.upper()}' no final!"
        if len(escrito) > len(correto):
            return "Sobrou uma letra. Tente escrever mais devagar!"
        return "Tente escrever as letras com mais calma!"

    @staticmethod
    def _levenshtein_fallback(a: str, b: str) -> int:
        m, n = len(a), len(b)
        dp = list(range(n + 1))
        for i in range(1, m + 1):
            ant = dp[:]
            dp[0] = i
            for j in range(1, n + 1):
                dp[j] = ant[j - 1] if a[i-1] == b[j-1] else 1 + min(ant[j], dp[j], ant[j-1])
        return dp[n]
