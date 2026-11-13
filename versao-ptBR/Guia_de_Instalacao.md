# Guia de Instalação — TraçAÍ Educação

**Versão:** 1.0.0  
**Projeto:** TCC — Curso Técnico de Desenvolvimento de Sistemas | SENAI 2026  
**Grupo 8:** Miguel Augusto Rocha · Ana Luiza Ferreira Antônio · Maria Luiza Aguilar · Pedro Antunes

---

## Índice

1. [Requisitos do Sistema](#1-requisitos-do-sistema)
2. [O que está incluído no pacote](#2-o-que-está-incluído-no-pacote)
3. [Opção 1 — Instalação com atalho (recomendada)](#3-opção-1--instalação-com-atalho-recomendada)
4. [Opção 2 — Uso portátil (sem instalação)](#4-opção-2--uso-portátil-sem-instalação)
5. [Opção 3 — Modo depurador (diagnóstico)](#5-opção-3--modo-depurador-diagnóstico)
6. [Situações especiais](#6-situações-especiais)
7. [Desinstalação](#7-desinstalação)
8. [Problemas comuns e soluções](#8-problemas-comuns-e-soluções)
9. [Contato e suporte](#9-contato-e-suporte)

---

## 1. Requisitos do Sistema

| Item | Requisito mínimo |
|------|-----------------|
| **Sistema Operacional** | Windows 10 ou superior (64 bits) |
| **Processador** | Intel Core i3 / AMD equivalente (2 GHz ou mais) |
| **Memória RAM** | 4 GB (8 GB recomendado) |
| **Espaço em disco** | ~600 MB livres |
| **Webcam** | Recomendada (USB ou integrada) — sem webcam funciona em Modo Demonstração |
| **Permissões** | Usuário comum (não precisa de administrador) |
| **Internet** | **Não necessária** — funciona completamente offline |

> [!IMPORTANT]
> O TraçAÍ Educação é um aplicativo portátil. Ele **não instala Python, drivers adicionais nem bibliotecas** no computador. Tudo já está embutido no pacote.

---

## 2. O que está incluído no pacote

Após extrair o arquivo ZIP, você verá os seguintes arquivos:

```
TracaAI_TCC_SENAI_Instalador.zip
├── TracaAI/                          ← Pasta principal do aplicativo
│   ├── TracaAI.exe                   ← Executável principal
│   ├── tesseract/                    ← Motor de reconhecimento de texto (embutido)
│   ├── _internal/                    ← Bibliotecas internas (não mover/apagar)
│   └── assets/                       ← Imagens e recursos visuais
├── Instalar_TracaAI.bat              ← Instalador com atalho na Área de Trabalho
├── Iniciar_TracaAI_Depuracao.bat     ← Modo diagnóstico (mostra logs)
├── INSTRUCOES_COMO_TESTAR_NA_ESCOLA.txt
├── Guia_do_Usuario.pdf               ← Manual de uso do aplicativo
└── Guia_de_Instalacao.pdf            ← Este documento
```

> [!WARNING]
> **Nunca execute o aplicativo diretamente de dentro do arquivo ZIP** sem extrair primeiro. Isso pode causar erros de leitura de arquivos. Sempre extraia tudo antes de abrir.

---

## 3. Opção 1 — Instalação com atalho (recomendada)

Esta é a forma mais simples. Cria um ícone na Área de Trabalho para abrir o aplicativo facilmente.

### Passo a Passo

**Passo 1 — Baixar o arquivo**

Receba o arquivo `TracaAI_TCC_SENAI_Instalador.zip` via pendrive, e-mail, Google Drive ou outro meio.

**Passo 2 — Extrair o ZIP**

1. Clique com o **botão direito** no arquivo ZIP
2. Selecione **"Extrair tudo..."** (ou "Extrair aqui")
3. Escolha uma pasta de destino (ex.: Área de Trabalho ou Documentos)
4. Clique em **Extrair**

> [!CAUTION]
> Não pule este passo! Executar diretamente do ZIP sem extrair causará erros.

**Passo 3 — Executar o instalador**

Dentro da pasta extraída, clique duas vezes em:

```
👉 Instalar_TracaAI.bat
```

Se aparecer uma janela de segurança do Windows ("Windows protegeu seu PC"), clique em **"Mais informações"** e depois em **"Executar assim mesmo"**. Isso é normal para aplicativos não assinados digitalmente.

**Passo 4 — Aguardar a instalação**

Uma janela preta (Prompt de Comando) aparecerá com as mensagens:

```
[1/3] Copiando arquivos do aplicativo...
[2/3] Criando atalho na Área de Trabalho...
[3/3] Criando atalho no Menu Iniciar...
INSTALAÇÃO CONCLUÍDA COM SUCESSO!
```

**Passo 5 — Abrir o aplicativo**

Após a instalação, um ícone chamado **"TraçAÍ Educação - TCC SENAI 2026"** aparecerá na Área de Trabalho. Clique duas vezes nele para abrir o programa.

Você também pode responder **S** quando o instalador perguntar se deseja iniciar agora.

---

## 4. Opção 2 — Uso portátil (sem instalação)

Ideal para usar em pendrive ou quando não quiser criar atalhos no computador.

### Passo a Passo

1. Extraia o ZIP para qualquer pasta (ou diretamente em um pendrive)
2. Abra a pasta **`TracaAI`**
3. Clique duas vezes em:

```
👉 TracaAI.exe
```

O aplicativo abre diretamente, sem instalar nada no computador.

> [!TIP]
> No pendrive, mantenha a estrutura de pastas intacta. Não mova o arquivo `TracaAI.exe` para fora da pasta `TracaAI/`, pois ele depende dos arquivos internos ao lado dele.

---

## 5. Opção 3 — Modo depurador (diagnóstico)

Use esta opção quando o aplicativo não abrir normalmente ou para ver mensagens de erro detalhadas.

1. Na pasta extraída, clique duas vezes em:

```
👉 Iniciar_TracaAI_Depuracao.bat
```

2. Uma janela preta aparecerá com todos os logs do sistema em tempo real
3. Se houver erros, eles aparecerão em vermelho com a mensagem de diagnóstico
4. O arquivo `tracaai_debug.log` também é salvo automaticamente na pasta do aplicativo

---

## 6. Situações especiais

### O computador não tem webcam

Sem problema! Ao abrir, o TraçAÍ exibirá uma mensagem:

> *"Nenhuma webcam foi detectada. Deseja iniciar no Modo Demonstração?"*

Clique em **Sim**. No Modo Demonstração, você pode:
- Navegar por todos os menus normalmente
- Desenhar na tela usando o **mouse** no lugar da mão
- Pressionar **ENTER** ou **ESPAÇO** para enviar a resposta ao reconhecimento

### O Windows Defender bloqueou o aplicativo

Isso pode acontecer porque o executável não possui assinatura digital comercial (normal para projetos acadêmicos). Para liberar:

1. Clique em **"Mais informações"** na janela de aviso
2. Clique em **"Executar assim mesmo"**

Alternativamente, clique com o botão direito em `TracaAI.exe` → **Propriedades** → marque **"Desbloquear"** na aba Geral → clique em OK.

### O antivírus sinalizou o arquivo

Falsos positivos são comuns com executáveis PyInstaller. O TraçAÍ Educação é um projeto acadêmico de código aberto, sem nenhum código malicioso. Para adicionar uma exceção no Windows Defender:

1. Abra o **Windows Security** (Segurança do Windows)
2. Vá em **Proteção contra vírus e ameaças** → **Configurações**
3. Em **Exclusões**, clique em **Adicionar uma exclusão**
4. Selecione a pasta `TracaAI` completa

### Instalar em múltiplos computadores

Basta copiar o ZIP (ou o pendrive) e repetir o processo em cada máquina. Não há limite de instalações.

---

## 7. Desinstalação

Como o instalador copia os arquivos para `%LOCALAPPDATA%\TracaAI_TCC\`:

**Para remover completamente:**

1. Abra o **Explorador de Arquivos**
2. Na barra de endereço, cole: `%LOCALAPPDATA%\TracaAI_TCC`
3. Pressione Enter e delete a pasta
4. Delete também os atalhos da Área de Trabalho e do Menu Iniciar

**Se usou em modo portátil (pendrive ou pasta):** basta apagar a pasta `TracaAI/` extraída.

> [!NOTE]
> Não há entradas no Registro do Windows, nem drivers instalados. A remoção é completa apenas deletando as pastas.

---

## 8. Problemas comuns e soluções

| Problema | Causa provável | Solução |
|----------|---------------|---------|
| O aplicativo não abre (sem mensagem) | Arquivo ZIP não foi extraído | Extraia o ZIP e abra a partir da pasta extraída |
| Tela preta ao iniciar | Webcam sendo inicializada | Aguarde 5 segundos; se persistir, use o Modo Demonstração |
| "Não foi possível encontrar a pasta do aplicativo" | Executou o `.bat` de dentro do ZIP | Extraia tudo primeiro |
| Aviso de segurança do Windows | Executável sem assinatura digital | Clique em "Mais informações" → "Executar assim mesmo" |
| Lentidão na detecção da mão | Computador com processador fraco | Feche outros programas abertos; use iluminação adequada |
| Webcam não detectada em computador com câmera | Driver da câmera desatualizado | Use o Modo Demonstração ou atualize o driver da webcam |
| Erro "No module named..." | Arquivos internos corrompidos | Baixe e extraia o ZIP novamente |
| O log não aparece no modo depurador | Pasta sem permissão de escrita | Mova a pasta `TracaAI` para Documentos ou Desktop |

### Verificar o log de erros

O arquivo `tracaai_debug.log` é salvo automaticamente na mesma pasta do `TracaAI.exe`. Para visualizá-lo:

1. Abra o **Bloco de Notas**
2. Vá em **Arquivo → Abrir**
3. Navegue até a pasta `TracaAI` e abra `tracaai_debug.log`

---

## 9. Contato e suporte

Este é um projeto acadêmico desenvolvido como TCC do Curso Técnico de Desenvolvimento de Sistemas do SENAI 2026.

**Grupo 8:**
- Miguel Augusto Rocha
- Ana Luiza Ferreira Antônio
- Maria Luiza Aguilar
- Pedro Antunes

Em caso de dúvidas durante os testes, utilize o **Modo Depurador** (item 5 deste guia) e anote as mensagens de erro para diagnóstico.

---

*Documento gerado para o TraçAÍ Educação — TCC SENAI 2026*
