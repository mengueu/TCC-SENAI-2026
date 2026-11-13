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

O **TraçAÍ Educação** é uma aplicação desktop que usa visão computacional para auxiliar crianças em processo de alfabetização. O aluno escreve letras e números **no ar com a própria mão** na frente da webcam, e uma IA analisa o que foi escrito em tempo real, fornecendo feedback imediato por texto e voz.

**Grupo 8:**  
Miguel Augusto Rocha · Ana Luiza Ferreira Antônio · Maria Luiza Aguilar · Pedro Antunes

---

## Estrutura do Repositório

O repositório é organizado em duas versões:

```
TCC-SENAI-2026/
│
├── README.md                  ← Informações gerais do projeto
│
├── versao-ptBR/               ← 🇧🇷 Versão em Português (código-fonte e recursos)
│   ├── main.py                   Ponto de entrada da aplicação
│   ├── modules/                  Módulos de câmera, IA/OCR, áudio e interface
│   ├── assets/                   Logo e identidade visual
│   ├── data/                     Base de nomes para os exercícios
│   ├── tessdata/                 Configurações do Tesseract OCR
│   └── README.md                 Manual técnico e pedagógico detalhado
│
└── english-version/           ← 🇺🇸 Versão em Inglês (em breve)
```

### 🇧🇷 `versao-ptBR/` — Versão em Português

Versão completa e funcional do aplicativo em português brasileiro. Contém a interface, retorno por voz (TTS), reconhecimento óptico de caracteres com Tesseract e exercícios de escrita e operações matemáticas.

→ [Acessar a pasta versao-ptBR](./versao-ptBR/)

### 🇺🇸 `english-version/` — Versão em Inglês

Versão internacionalizada atualmente em desenvolvimento para atender outros idiomas.

→ [Em breve](./english-version/)

---

## Como Executar

Para executar o código-fonte em Python diretamente:

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/TCC-SENAI-2026.git
cd TCC-SENAI-2026/versao-ptBR

# Execute o aplicativo
python main.py
```

Também disponibilizamos o instalador portátil autônomo (empacotado com Tesseract e dependências integradas), que não requer a instalação do Python.

---

## Licença

Projeto acadêmico — TCC SENAI 2026. Todos os direitos reservados ao Grupo 8.
