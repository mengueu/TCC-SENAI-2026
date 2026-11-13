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
  <img src="https://img.shields.io/badge/Status-Em%20desenvolvimento-yellow" />
</p>

---

## Sobre o Projeto

O **TraçAÍ Educação** é uma aplicação desktop que usa visão computacional para auxiliar crianças em processo de alfabetização. O aluno escreve letras e números **no ar com a própria mão** na frente da webcam, e uma IA analisa o que foi escrito em tempo real, fornecendo feedback imediato.

**Grupo 8:**  
Miguel Augusto Rocha · Ana Luiza Ferreira Antônio · Maria Luiza Aguilar · Pedro Antunes

---

## Estrutura do Repositório

Este repositório está organizado em duas versões principais:

```
TCC-SENAI-2026/
│
├── README.md                  ← Este arquivo
│
├── versao-ptBR/               ← 🇧🇷 Versão em Português (completa e funcional)
│   ├── main.py                   Código principal da aplicação
│   ├── modules/                  Módulos: câmera, OCR, TTS, canvas, etc.
│   ├── assets/                   Logo e recursos visuais
│   ├── data/                     Banco de nomes para os exercícios
│   ├── tessdata/                 Configurações do Tesseract OCR
│   ├── requirements.txt          Dependências Python
│   ├── Guia_do_Usuario.md        Manual de uso para o usuário final
│   ├── Guia_de_Instalacao.md     Guia de instalação e solução de problemas
│   └── DOCUMENTACAO_TCC_SENAI_2026.md  Documentação técnica do TCC
│
└── english-version/           ← 🇺🇸 Versão em Inglês (em breve)
```

### 🇧🇷 `versao-ptBR/` — Versão em Português

Versão completa e funcional do aplicativo, com toda a interface, áudio e conteúdo pedagógico em português brasileiro. Inclui os guias do usuário e de instalação.

→ [Acessar a versão em português](./versao-ptBR/)

### 🇺🇸 `english-version/` — Versão em Inglês

Versão internacionalizada em desenvolvimento. Será publicada em breve com interface e conteúdo traduzidos para o inglês.

→ [Em breve](./english-version/)

---

## Como Executar (versão ptBR)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/TCC-SENAI-2026.git
cd TCC-SENAI-2026/versao-ptBR

# Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute o aplicativo
python main.py
```

> Consulte o [`Guia_de_Instalacao.md`](./versao-ptBR/Guia_de_Instalacao.md) para instruções detalhadas, incluindo como usar o instalador portátil (`.exe`).

---

## Licença

Projeto acadêmico — TCC SENAI 2026. Todos os direitos reservados ao Grupo 8.
