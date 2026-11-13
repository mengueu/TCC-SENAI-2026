"""
modules/matematica.py — Gerador de Exercícios de Matemática

Gera problemas simples de adição, subtração, multiplicação e divisão
adequados para crianças em fase de alfabetização matemática.

Também verifica a resposta escrita pela criança (lida via OCR) e
gera um feedback personalizado.
"""

import random
import re


# ─── Faixas numéricas por operação (mantém as contas simples para crianças) ──
FAIXAS = {
    "adicao":         {"a": (1, 10), "b": (1, 10)},
    "subtracao":      {"a": (5, 15), "b": (1,  9)},
    "multiplicacao":  {"a": (2,  9), "b": (1,  5)},
    "divisao":        {"result": (1, 9), "div": (2, 5)},
}

# ─── Símbolos exibidos na tela (Unicode bonito) ───────────────────────────────
SIMBOLOS = {
    "adicao":        "+",
    "subtracao":     "−",
    "multiplicacao": "×",
    "divisao":       "÷",
}

# ─── Nomes amigáveis ──────────────────────────────────────────────────────────
NOMES = {
    "adicao":        "Adição",
    "subtracao":     "Subtração",
    "multiplicacao": "Multiplicação",
    "divisao":       "Divisão",
}


class GeradorProblema:
    """
    Gera problemas matemáticos simples e verifica a resposta da criança.
    """

    def __init__(self, tipo: str):
        """
        tipo: 'adicao' | 'subtracao' | 'multiplicacao' | 'divisao'
        """
        if tipo not in FAIXAS:
            raise ValueError(f"Tipo desconhecido: {tipo}. Use: {list(FAIXAS.keys())}")
        self.tipo = tipo
        self.operando_a: int = 0
        self.operando_b: int = 0
        self.resposta_correta: int = 0
        self.texto_problema: str = ""
        self.gerar()

    def gerar(self) -> tuple[str, int]:
        """
        Gera um novo problema aleatório.
        Retorna (texto_do_problema, resposta_correta).
        """
        f = FAIXAS[self.tipo]
        sim = SIMBOLOS[self.tipo]

        if self.tipo == "adicao":
            self.operando_a = random.randint(*f["a"])
            self.operando_b = random.randint(*f["b"])
            self.resposta_correta = self.operando_a + self.operando_b

        elif self.tipo == "subtracao":
            self.operando_b = random.randint(*f["b"])
            self.operando_a = random.randint(self.operando_b, f["a"][1])
            self.resposta_correta = self.operando_a - self.operando_b

        elif self.tipo == "multiplicacao":
            self.operando_a = random.randint(*f["a"])
            self.operando_b = random.randint(*f["b"])
            self.resposta_correta = self.operando_a * self.operando_b

        elif self.tipo == "divisao":
            self.resposta_correta = random.randint(*f["result"])
            self.operando_b      = random.randint(*f["div"])
            self.operando_a      = self.operando_b * self.resposta_correta

        self.texto_problema = f"{self.operando_a} {sim} {self.operando_b}"
        return self.texto_problema, self.resposta_correta

    def verificar(self, texto_ocr: str) -> tuple[str, str]:
        """
        Verifica a resposta da criança (lida pelo OCR) e retorna
        (mensagem_feedback, tipo_feedback).
        tipo_feedback: 'sucesso' | 'dica' | 'erro'
        """
        numeros = re.findall(r"\d+", texto_ocr.strip())

        if not numeros:
            return (
                "Não consegui ler o número que você escreveu. "
                "Tente escrever com mais calma, bem grande!",
                "erro",
            )

        tentativa = int(numeros[-1])

        if tentativa == self.resposta_correta:
            return (
                f"Correto! {self.texto_problema} = {self.resposta_correta}. Muito bem!",
                "sucesso",
            )

        if abs(tentativa - self.resposta_correta) <= 1:
            return (
                f"Quase! Você escreveu {tentativa}, mas a resposta é "
                f"{self.resposta_correta}. Tente de novo!",
                "dica",
            )

        return (
            f"Não é {tentativa}. Pense de novo: "
            f"{self.texto_problema} = ? Você consegue!",
            "erro",
        )

    def nome_operacao(self) -> str:
        return NOMES.get(self.tipo, self.tipo)

