# TraçAÍ Educação — TCC SENAI 2026

<p align="center">
  <img src="versao-ptBR/assets/logo.png" alt="Logo TraçAÍ Educação" width="160"/>
</p>

<p align="center">
  <strong>Ferramenta de Alfabetização e Matemática com Visão Computacional</strong><br/>
  TCC — Curso Técnico de Desenvolvimento de Sistemas | SENAI 2026
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" />
  <img src="https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv" />
  <img src="https://img.shields.io/badge/MediaPipe-0.10-orange" />
  <img src="https://img.shields.io/badge/Status-Completo-brightgreen" />
</p>

---

## 📥 Como Instalar e Executar

Escolha a forma mais conveniente para você:

### 🚀 Método Fácil: Baixar o Aplicativo Pronto (Recomendado)
Se você quer apenas usar o aplicativo sem precisar configurar nada:

1. Clique no link para acessar e baixar a versão mais recente para Windows:  
   👉 **[Clique aqui para Baixar o Instalador (GitHub Releases)](https://github.com/mengueu/TCC-SENAI-2026/releases/latest)**
2. Baixe o arquivo `.zip` do lançamento (ex.: `TracAI_TCC_SENAI_Instalador.zip`);
3. Extraia o arquivo ZIP em qualquer pasta do seu computador;
4. Dê 2 cliques no arquivo **`Instalar_TracaAI.bat`** (ele criará um atalho prático na sua Área de Trabalho e Menu Iniciar) ou execute diretamente o **`TracaAI.exe`** dentro da pasta.

> ✨ **Vantagem:** Você **não precisa** instalar Python, nem Tesseract OCR, nem bibliotecas. Tudo já vem embutido e pronto para uso!

---

### 🛠️ Método Manual: Instalação via Código-Fonte (Desenvolvedores)
Caso você queira inspecionar o código ou rodar o projeto manualmente pelo Python, você precisará instalar os pré-requisitos antes:

#### 1. Pré-requisitos necessários:
- **Python 3.11:** Baixe em [python.org](https://www.python.org/downloads/) *(certifique-se de marcar a opção **"Add Python to PATH"** durante a instalação)*.
- **Tesseract OCR (Windows):** Baixe o instalador em [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki). Na etapa de seleção de componentes do instalador, expanda *Additional language data* e marque o idioma **Portuguese** (Português).

#### 2. Instalação e execução do código:

**Opção Automática (com 1 clique):**
Abra a pasta `versao-ptBR` e dê 2 cliques no arquivo:
```
👉 versao-ptBR/instalar.bat
```
*(Ele criará o ambiente virtual `venv`, instalará todas as dependências do `requirements.txt` e verificará o Tesseract automaticamente).*

**Opção Manual pelo Terminal:**
```bash
# 1. Clone o repositório e acesse a pasta da versão em português:
git clone https://github.com/mengueu/TCC-SENAI-2026.git
cd TCC-SENAI-2026/versao-ptBR

# 2. Crie e ative o ambiente virtual:
python -m venv venv
venv\Scripts\activate

# 3. Instale as bibliotecas necessárias:
pip install -r requirements.txt

# 4. Inicie o aplicativo:
python main.py
```

---

## 🧠 Sobre o Projeto

O **TraçAÍ Educação** é uma aplicação desktop que utiliza visão computacional e inteligência artificial para auxiliar crianças no processo de alfabetização e letramento matemático. 

A criança escreve números e letras **diretamente no ar com o próprio dedo**, na frente da webcam. O sistema reconhece os traços em tempo real, processa a escrita através do Tesseract OCR e fornece retorno pedagógico imediato por texto e síntese de voz (TTS).

**Grupo 8:**  
Miguel Augusto Rocha · Ana Luiza Ferreira Antônio · Maria Luiza Aguilar · Pedro Antunes

---

## 🗂️ Estrutura do Repositório

```
TCC-SENAI-2026/
│
├── README.md                  ← Este guia e visão geral
│
├── versao-ptBR/               ← 🇧🇷 Versão em Português (completa e funcional)
│   ├── main.py                   Ponto de entrada do sistema
│   ├── modules/                  Módulos de visão computacional, OCR, áudio e canvas
│   ├── assets/                   Identidade visual, logos e ícones
│   ├── data/                     Base lexical de nomes brasileiros
│   ├── tessdata/                 Configurações de reconhecimento do OCR
│   ├── requirements.txt          Lista de dependências Python
│   ├── instalar.bat              Script de instalação rápida do ambiente Python
│   └── README.md                 Documentação técnica e pedagógica detalhada
│
└── english-version/           ← 🇺🇸 Versão em Inglês (em breve)
```

---

## Licença

Projeto acadêmico — TCC SENAI 2026. Todos os direitos reservados ao Grupo 8.
