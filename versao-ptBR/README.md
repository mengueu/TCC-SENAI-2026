# 🖊️ TraçAÍ Educação — Ferramenta de Alfabetização com Visão Computacional

> **TCC — Curso Técnico de Desenvolvimento de Sistemas | SENAI 2026**  
> Grupo 8: Miguel Augusto Rocha, Ana Luiza Ferreira Antônio, Maria Luiza Aguilar e Pedro Antunes.

---

## 🧠 O que é o TraçAÍ Educação?

O **TraçAÍ Educação** é uma ferramenta educacional interativa voltada para crianças em processo de alfabetização. Usando a câmera do computador, a criança **escreve com o próprio dedo no ar** — sem mouse, teclado, caneta ou tablet — e a IA lê o que foi escrito e devolve um **feedback personalizado** em texto e voz.

A proposta é ser um **caderno mágico digital**: a criança pratica escrita, leitura e matemática de forma lúdica, sem custos e 100% offline.

---

## 🎯 Origem do Projeto

| Semana Aberta (origem) | TraçAÍ Educação (TCC) |
|---|---|
| Quadro de desenho livre | Ferramenta educacional com propósito pedagógico |
| Feedback visual (traço na tela) | Feedback da IA em texto e voz |
| Qualquer público | Crianças em fase de alfabetização |
| Sem objetivo pedagógico | Prática de escrita, leitura e matemática |

---

## ✨ Funcionalidades

### Módulo de Língua Portuguesa
1. A tela exibe *"Qual é o seu nome?"*
2. A criança escreve o nome com o dedo no ar
3. O Tesseract OCR lê a imagem do canvas
4. Um algoritmo de similaridade (Levenshtein) compara com nomes brasileiros comuns
5. O app responde com feedback personalizado e fala em voz alta:
   - ✅ Correto: *"Olá, [Nome]! Parabéns, você escreveu seu nome certinho!"*
   - 🔄 Próximo: *"Você quis dizer [Nome]? Tente a letra '[X]' com mais calma!"*
   - ❓ Não reconhecido: *"Hmm, não consegui ler. Tente escrever mais devagar!"*

### Módulo de Matemática
- Exercícios de **adição, subtração, multiplicação e divisão**
- Contas simples adaptadas para crianças (ex: `3 + 4 = ?`)
- A criança escreve o resultado no ar e a IA verifica e fala o feedback
- Nova conta gerada automaticamente ao pressionar Espaço

---

## 🕹️ Como usar

### Gestos da mão que escreve
| Gesto | Ação |
|---|---|
| ☝️ 1 dedo (indicador) | Caneta — escreve na tela |
| ✌️ 2 dedos (indicador + médio) | Pairar — move o cursor sem escrever |
| 👍 Polegar ("joia") | Confirmar — envia para a IA analisar |

### Gestos da mão de configuração (mão oposta)
| Gesto | Ação |
|---|---|
| ☝️ Indicador no topo da tela | Seleciona uma nova cor |
| 🤏 Pinça | Ajusta a espessura do traço |
| 🖐️ 4 dedos abertos | Limpa tudo |

### Teclado (atalhos)
| Tecla | Ação |
|---|---|
| `ESC` / `M` | Volta ao menu principal |
| `Q` | Fecha o programa |
| `Espaço` | Próxima questão / limpar |
| `C` | Limpar tela |
| `E` | Ativar/desativar borracha |

---

## 🛠️ Tecnologias

| Ferramenta | Função |
|---|---|
| **Python 3.11** | Linguagem principal |
| **OpenCV** | Captura de câmera, desenho e processamento de imagem |
| **MediaPipe** | Detecção dos 21 pontos da mão (landmarks) |
| **Tesseract OCR** | Reconhecimento óptico de caracteres da escrita |
| **python-Levenshtein** | Medição de similaridade entre palavras |
| **pyttsx3** | Síntese de voz offline |
| **PyInstaller** | Empacotamento em executável standalone (.exe) |

> ✅ **100% gratuito e offline** — sem APIs pagas, sem conexão com internet.

---

## 📦 Distribuição (Executável Standalone)

O projeto inclui um instalador portátil que **não requer Python, Tesseract, Git ou qualquer dependência** instalada no computador:

1. Extraia o arquivo `TraçaAI_Instalador.zip`
2. Execute `Instalar_TraçAÍ.bat` *(cria atalho na Área de Trabalho)*
3. Ou abra direto: `TraçaAI/TraçaAI.exe`

> **Sem webcam?** O programa detecta automaticamente e oferece o **Modo Demonstração** com mouse.

---

## 📁 Estrutura desta Versão (versao-ptBR)

```
versao-ptBR/
├── main.py                       ← Ponto de entrada e fluxo de telas
├── requirements.txt              ← Dependências Python
├── instalar.bat                  ← Script automático de instalação da venv
├── assets/
│   ├── logo.png                  ← Logo do TraçAÍ Educação (1024×1024 RGBA)
│   └── logo.ico                  ← Ícone para o executável Windows
├── modules/
│   ├── camera.py                 ← Captura de câmera e detecção de mão (MediaPipe)
│   ├── canvas.py                 ← Lógica do canvas de escrita
│   ├── ocr.py                    ← Reconhecimento de texto (Tesseract)
│   ├── feedback.py               ← Geração de feedback personalizado
│   ├── matematica.py             ← Gerador de exercícios matemáticos
│   ├── tts.py                    ← Síntese de voz (pyttsx3)
│   ├── texto.py                  ← Renderização de texto na tela
│   └── caminhos.py               ← Resolução de caminhos portáteis (dev ↔ .exe)
├── data/
│   └── nomes_br.txt              ← Lista de nomes brasileiros comuns
└── tessdata/
    └── digits.cfg                ← Config Tesseract para dígitos
```

---

## 📥 Como Instalar e Executar

### 🚀 Método Fácil: Baixar o Aplicativo Pronto (Recomendado)
Se você quer apenas usar o programa sem precisar configurar nada:

1. Acesse o link de download direto da versão mais recente:  
   👉 **[Baixar Instalador Pronto (.ZIP) em Releases](https://github.com/mengueu/TCC-SENAI-2026/releases/latest)**
2. Baixe o arquivo `.zip` disponibilizado (ex.: `TracAI_TCC_SENAI_Instalador.zip`);
3. Extraia o conteúdo no seu computador;
4. Dê 2 cliques em `Instalar_TracaAI.bat` para criar o atalho na Área de Trabalho (ou abra diretamente pelo `TracaAI.exe`).

> ✨ **Vantagem:** Não precisa instalar Python, nem Tesseract, nem bibliotecas. Tudo já vem configurado!

---

### 🛠️ Método Manual: Instalação via Código-Fonte (Desenvolvedores)
Caso queira rodar o projeto manualmente pelo Python, você precisará instalar:

#### 1. Pré-requisitos necessários:
- **Python 3.11:** Baixe em [python.org](https://www.python.org/downloads/) *(marque a opção **"Add Python to PATH"** durante a instalação)*.
- **Tesseract OCR (Windows):** Baixe em [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki). Na tela de componentes, marque o idioma **Portuguese** (Português).

#### 2. Instalação das bibliotecas e execução:

**Opção Automática:**
Basta dar 2 cliques no arquivo `instalar.bat` desta pasta. Ele criará o ambiente virtual `venv`, instalará todas as dependências do `requirements.txt` e testará o Tesseract automaticamente.

**Opção Manual pelo Terminal:**
```bash
# Ativar ou criar o ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instalar as bibliotecas
pip install -r requirements.txt

# Executar a aplicação
python main.py
```

---

## 👥 Equipe

**Grupo 8 — SENAI 2026**

- Miguel Augusto Rocha
- Ana Luiza Ferreira Antônio
- Maria Luiza Aguilar
- Pedro Antunes

---

## 🏫 Sobre

Projeto desenvolvido como Trabalho de Conclusão de Curso (TCC) do Curso Técnico de Desenvolvimento de Sistemas do SENAI, 2026.  
Evolução direta do projeto de quadro de escrita apresentado na Semana Aberta, agora com propósito pedagógico e feedback por inteligência artificial.
