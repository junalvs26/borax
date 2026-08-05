# Plataforma de IA Local Modular (PoC)

Esta é a prova de conceito (PoC) para uma **Plataforma de IA Local Modular** utilizando **Python (FastAPI)**, **LanceDB**, **Ollama** e **React (Tauri)**.

---

## 🏗️ Arquitetura do Projeto

```
borax/
├── backend/
│   ├── main.py                  # API FastAPI (Endpoints: /chat, /ingest, /models, /export-pack)
│   ├── requirements.txt         # Dependências Python (fastapi, lancedb, sentence-transformers, etc.)
│   ├── lancedb_data/            # Banco vetorial local LanceDB (gerado automaticamente)
│   └── services/
│       ├── ollama_service.py    # Cliente assíncrono para Ollama (http://localhost:11434)
│       ├── rag_service.py       # Extração de PDF/TXT, chunking e vetores no LanceDB
│       └── pack_service.py      # Gerador de pacotes .knpack (ZIP compilado com manifest + vetores)
└── frontend/
    ├── package.json             # Dependências React + Vite + Tauri
    ├── vite.config.js           # Configuração de build Vite
    ├── src-tauri/               # Configuração da aplicação Desktop Tauri
    └── src/                     # Componentes React (Chat, Drag&Drop, Seletor de Modelo, Exportador)
```

---

## 🚀 Como Rodar o Ambiente Local

### Prerequisites
1. **Python 3.10+** instalado.
2. **Node.js 18+** e `npm` instalados.
3. **Ollama** instalado e rodando em `http://localhost:11434`.
   - Certifique-se de possuir ao menos um modelo instalado (ex: `ollama pull llama3` ou `ollama pull mistral`).

---

### 1️⃣ Iniciando o Backend em Python (FastAPI)

1. Navegue até o diretório `backend`:
   ```bash
   cd backend
   ```

2. Crie e ative um ambiente virtual:
   - **Windows**:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux/macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute o servidor FastAPI:
   ```bash
   python main.py
   ```
   *(O backend estará rodando em `http://127.0.0.1:8000`)*

---

### 2️⃣ Iniciando o Frontend (React / Tauri)

1. Em um novo terminal, navegue até a pasta `frontend`:
   ```bash
   cd frontend
   ```

2. Instale as dependências Node.js:
   ```bash
   npm install
   ```

3. **Modo Web Dev Server** (Acesso pelo navegador):
   ```bash
   npm run dev
   ```
   *(Acesse `http://localhost:1420` no seu navegador)*

4. **Modo Desktop App (Tauri)** (Requer Rust instalado):
   ```bash
   npm run tauri dev
   ```

---

## ⚡ Funcionalidades da PoC

- **`/models`**: Seleção em tempo real dos modelos instalados localmente no Ollama.
- **`/ingest`**: Arraste e solte arquivos `.pdf` e `.txt`. O sistema extrai o texto, realiza o chunking e gera embeddings de alta performance armazenados no **LanceDB** local (`backend/lancedb_data/`).
- **`/chat`**: Interface de chat com respostas em **streaming** e opção de ativar/desativar RAG com contexto relevante do LanceDB.
- **`/export-pack`**: Botão para compilar e baixar a base vetorial atual + instrução de sistema em um arquivo `.knpack` (ZIP estruturado com `manifest.json`, `prompt.txt` e `data.json`).
