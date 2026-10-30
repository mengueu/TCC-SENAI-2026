# 📚 AlfaIA — Ferramenta de Alfabetização com Visão Computacional

> **TCC do Curso Técnico de Desenvolvimento de Sistemas — SENAI 2026**  
> Evolução do projeto da Semana Aberta: de um quadro de desenho livre para uma ferramenta educacional de alfabetização infantil.

---

## 🧠 O que é o AlfaIA?

O **AlfaIA** é uma ferramenta educacional interativa voltada para crianças em processo de alfabetização. Usando a câmera do computador, a criança **escreve com o próprio dedo no ar** — sem precisar de mouse, teclado, caneta ou tablet — e a IA lê o que foi escrito, interpreta e devolve um **feedback personalizado** na tela.

A ideia não é um jogo, mas uma **ferramenta de prática**: como um caderno mágico onde a criança pratica escrita, leitura e, futuramente, matemática, de forma lúdica e sem custos.

---

## 🎯 Por que evoluir o projeto da Semana Aberta?

O projeto anterior mostrou que é possível capturar gestos e movimentos das mãos com precisão usando tecnologia acessível (câmera comum + Python). A evolução natural é **dar propósito pedagógico** a isso:

| Projeto anterior | TCC (AlfaIA) |
|---|---|
| Quadro de desenho livre | Ferramenta de prática educacional |
| Feedback visual apenas (traço na tela) | Feedback da IA (lê, interpreta, responde) |
| Qualquer público | Crianças em alfabetização |
| Sem objetivo pedagógico | Prática de escrita, leitura e matemática |

---

## ✨ Funcionalidades (Módulo 1 — Nome)

> Esta é a primeira funcionalidade implementada. Outras virão em versões futuras.

1. **Pergunta**: A tela exibe *"Qual o seu nome?"*
2. **Escrita**: A criança usa o dedo indicador para escrever o nome no ar
3. **Confirmação**: Um gesto (ex: mão aberta) finaliza a escrita e envia para análise
4. **Análise**: O Tesseract OCR lê a imagem do canvas; um algoritmo de similaridade compara com nomes comuns
5. **Feedback**: A IA responde com uma mensagem personalizada na tela:
   - ✅ Escrita correta: *"Olá, Miguel! Parabéns, você escreveu seu nome direitinho! 🎉"*
   - 🔄 Escrita parecida: *"Você quis dizer que seu nome é Miguel? Tente a letra 'M' com mais calma!"*
   - ❓ Não reconhecido: *"Hmm, não consegui ler bem. Tente escrever mais devagar, letra por letra!"*

---

## 🔭 Funcionalidades Futuras (Roadmap)

- [ ] **Módulo de Leitura**: A tela mostra uma palavra e a criança a copia por escrito
- [ ] **Módulo de Matemática**: Operações simples (ex: "Quanto é 2 + 3?" → criança escreve "5")
- [ ] **Perfil de progresso**: Salva o histórico da criança e mostra evolução
- [ ] **Modo daltônico / acessível**
- [ ] **Suporte a múltiplas línguas**

---

## 🛠️ Tecnologias e Ferramentas

| Ferramenta | Papel no projeto | Custo |
|---|---|---|
| **Python 3.10–3.12** | Linguagem principal | Gratuito |
| **OpenCV** | Captura da câmera, desenho na tela, processamento de imagem | Gratuito |
| **MediaPipe** | Detecção da mão e dos 21 pontos (landmarks) dos dedos | Gratuito |
| **NumPy** | Manipulação do canvas como matriz | Gratuito |
| **Tesseract OCR** | Lê o texto escrito pela criança (reconhecimento óptico de caracteres) | Gratuito |
| **pytesseract** | Wrapper Python para usar o Tesseract | Gratuito |
| **python-Levenshtein** | Mede a distância entre palavras (ex: "Migel" → "Miguel") | Gratuito |
| **pyttsx3** | Síntese de voz — fala o feedback para a criança | Gratuito |

> ✅ **100% gratuito e offline** — nenhuma API paga, nenhuma conexão com internet necessária para funcionar.

---

## 📦 O que é o Tesseract OCR?

O **Tesseract** é um motor de reconhecimento de caracteres (OCR — *Optical Character Recognition*) de código aberto, desenvolvido originalmente pela HP e mantido atualmente pelo Google. Em termos simples: **ele olha para uma imagem e transforma o que está escrito nela em texto**.

### Como funciona?
1. Recebe uma imagem (pode ser foto, screenshot, ou nosso canvas desenhado)
2. Identifica regiões de texto na imagem
3. Reconhece cada letra/símbolo
4. Devolve o texto em formato de string Python

### Como instalar o Tesseract?

O Tesseract precisa ser instalado **no sistema operacional** (não é só um `pip install`). Depois, instalamos o `pytesseract` (wrapper Python) via pip.

**Passo 1 — Instalar o Tesseract no Windows:**
1. Acesse: https://github.com/UB-Mannheim/tesseract/wiki
2. Baixe o instalador mais recente (ex: `tesseract-ocr-w64-setup-5.x.x.exe`)
3. Durante a instalação, marque a opção **"Additional language data (download)"** e selecione **Português**
4. Anote o caminho de instalação (geralmente `C:\Program Files\Tesseract-OCR\`)

**Passo 2 — Adicionar ao PATH (opcional, mas recomendado):**
- Pesquise "Variáveis de ambiente" no Windows
- Em "Variáveis do sistema", encontre `Path` e adicione o caminho do Tesseract

**Passo 3 — Instalar as dependências Python:**
```bash
pip install -r requirements.txt
```

---

## ▶️ Como executar

```bash
# Ativar o ambiente virtual (use Python 3.10, 3.11 ou 3.12)
py -3.11 -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar o módulo principal
python main.py
```

---

## 📁 Estrutura do projeto

```
TCC-SENAI-2026/
├── README.md               ← Este arquivo
├── requirements.txt        ← Dependências Python
├── main.py                 ← Ponto de entrada principal
├── modules/
│   ├── camera.py           ← Captura de câmera e detecção de mão (MediaPipe)
│   ├── canvas.py           ← Lógica do canvas de escrita
│   ├── ocr.py              ← Reconhecimento de texto (Tesseract)
│   ├── feedback.py         ← Geração de feedback para a criança
│   └── tts.py              ← Síntese de voz (pyttsx3)
├── assets/
│   ├── fonts/              ← Fontes para a interface
│   └── sounds/             ← Sons de feedback (opcional)
└── data/
    └── nomes_br.txt        ← Lista de nomes brasileiros comuns (para comparação)
```

---

## 👥 Equipe

*Grupo 8: Miguel Augusto Rocha, Ana Luiza Ferreira Antônio, Maria Luiza Aguilar e Pedro Antunes.*

---

## 🏫 Sobre

Projeto desenvolvido como Trabalho de Conclusão de Curso (TCC) do Curso Técnico de Desenvolvimento de Sistemas do SENAI, 2026.  
Evolução direta do projeto apresentado na Semana Aberta.
