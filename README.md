# Nexus Multimodal & Multilingual AI Voice Assistant

Nexus is an enterprise-grade, multimodal & multilingual AI voice assistant designed for local execution on Windows. It combines conversational intelligence with multilingual understanding (**Hindi, English, Hinglish, Spanish, French, German, Japanese, Bengali, Marathi, and more**), interactive voice assistance (speech-to-text & neural text-to-speech), document knowledge retrieval (RAG), multimodal computer vision, and live web search.

---

## Table of Contents

1. [Key Features](#1-key-features)
2. [Architecture & Technology Stack](#2-architecture--technology-stack)
3. [Folder Structure](#3-folder-structure)
4. [Prerequisites](#4-prerequisites)
5. [Windows Quick Start Guide](#5-windows-quick-start-guide)
6. [Multilingual & Voice Assistance](#6-multilingual--voice-assistance)
7. [Manual Step-by-Step Installation](#7-manual-step-by-step-installation)
8. [Environment Configuration & API Keys](#8-environment-configuration--api-keys)
9. [Database Setup & Migrations](#9-database-setup--migrations)
10. [Running the Application](#10-running-the-application)
11. [Using Multimodal Capabilities](#11-using-multimodal-capabilities)
    * [Voice Assistant & Auto-Speak](#voice-assistant--auto-speak)
    * [Multilingual Conversations (Hindi, English, etc.)](#multilingual-conversations-hindi-english-etc)
    * [Vision & Image Analysis](#vision--image-analysis)
    * [Document Processing & RAG](#document-processing--rag)
    * [Live Web Search](#live-web-search)
    * [Structured Outputs](#structured-outputs)
12. [Running the Automated Test Suite](#12-running-the-automated-test-suite)
13. [Troubleshooting & FAQ](#13-troubleshooting--faq)
14. [Security & Deployment Considerations](#14-security--deployment-considerations)
15. [Future Roadmap](#15-future-roadmap)

---

## 1. Key Features

- **🎙️ Interactive Voice Assistance:** Seamless two-way spoken conversation. Speak into your microphone and hear natural spoken replies with neural voices (`Edge-TTS` and `gTTS`). Includes an **Auto-Speak Responses** mode for hands-free dialogue.
- **🌐 Multilingual Intelligence:** Fluent in **Hindi (हिन्दी)**, **English (US & India)**, **Hinglish (मिक्स)**, **Spanish (Español)**, **French (Français)**, **German (Deutsch)**, **Japanese (日本語)**, **Bengali (বাংলা)**, **Marathi (मराठी)**, **Tamil**, **Telugu**, **Arabic**, and **Russian**.
- **🖼️ Multimodal Vision:** Upload PNG, JPG, and WebP images for computer vision analysis using LLaMA 3.2 Vision, GPT-4o, or Gemini.
- **📄 Conversation-Scoped RAG:** Document indexing for PDF, DOCX, PPTX, CSV, TXT, and Markdown files with source citations and strict isolation per chat session.
- **🌐 Live Web Search:** Free DuckDuckGo real-time search (zero API key required) or Tavily.
- **🚀 Single-Click Windows Runnable:** Double-click `run.bat` or `start.bat` to launch both backend and frontend, automatically opening in your default web browser.
- **⚡ Provider-Independent AI Layer:** Built-in modular adapters for **Groq**, **OpenAI**, **Hugging Face**, **Google Gemini**, local **Ollama**, and a zero-cost built-in **Mock Provider** fallback for offline use.

---

## 2. Architecture & Technology Stack

```
               ┌────────────────────────────────────────────────────────┐
               │              Streamlit Frontend (:8501)                │
               │   Chat UI • File Attachments • Audio Recording/Player  │
               └───────────────────────────┬────────────────────────────┘
                                           │ REST API (JSON / Multipart)
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │                FastAPI Backend (:8000)                 │
               │   Routers: Chat, Models, Documents, Audio, Search, DB  │
               └───────────┬───────────────┬──────────────────┬─────────┘
                           │               │                  │
         ┌─────────────────▼──┐   ┌────────▼─────────┐   ┌────▼─────────────┐
         │   Database Layer   │   │  RAG & Vector    │   │  AI Provider     │
         │ SQLAlchemy ORM     │   │ Sentence Transf. │   │ Groq / OpenAI    │
         │ SQLite/PostgreSQL  │   │ FAISS / NumPy    │   │ Hugging Face     │
         │ Alembic Migrations │   │ Doc Parsers      │   │ Gemini / Mock    │
         └────────────────────┘   └──────────────────┘   └──────────────────┘
```

- **Frontend:** Streamlit 1.38+, Custom Responsive CSS.
- **Backend:** FastAPI, Pydantic v2, Uvicorn, httpx.
- **Database:** SQLAlchemy 2.0 ORM, Alembic, SQLite (local default) / PostgreSQL 16.
- **Embeddings & Vector Search:** Sentence-Transformers (`all-MiniLM-L6-v2`), FAISS-CPU (with pure NumPy cosine similarity fallback).
- **Document Extractors:** PyMuPDF (`fitz`), `python-docx`, `python-pptx`, `pandas`.
- **Search Provider:** DuckDuckGo Search (no key required), Tavily API (optional).
- **Audio Services:** `edge-tts` (Microsoft Neural Voices), `gTTS`, `SpeechRecognition`, Groq/OpenAI Whisper.

---

## 3. Folder Structure

```
chatbot/
├── backend/
│   ├── api/                     # FastAPI route handlers
│   │   ├── routes_audio.py      # Audio transcription and TTS synthesis
│   │   ├── routes_chat.py       # Core chat & multimodal reasoning endpoint
│   │   ├── routes_conversations.py # CRUD & export for conversations
│   │   ├── routes_documents.py  # File upload & document index management
│   │   ├── routes_health.py     # Backend & database health verification
│   │   ├── routes_models.py     # Available models & readiness status
│   │   ├── routes_search.py     # Web search endpoint
│   │   └── routes_settings.py   # System configuration overview
│   ├── core/                    # Core system infrastructure
│   │   ├── config.py            # Pydantic BaseSettings (.env loader)
│   │   ├── database.py          # SQLAlchemy engine, session & ping
│   │   └── security.py          # Path traversal prevention & file sanitizer
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── conversation.py      # Conversation session model
│   │   ├── message.py           # Message & metadata model
│   │   ├── document.py          # Document & chunk models
│   │   └── setting.py           # Application settings model
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── services/
│   │   ├── ai/                  # AI Provider abstraction & adapters
│   │   ├── audio/               # Voice synthesis and transcription
│   │   ├── documents/           # Text parsers (PDF, DOCX, PPTX, CSV) & chunker
│   │   ├── rag/                 # Embeddings, FAISS vector store, and RAG coordinator
│   │   └── search/              # Real-time search service
│   └── main.py                  # FastAPI application entry point & CORS
├── frontend/
│   ├── components/              # Modular Streamlit UI components
│   │   ├── chat_message.py      # Message bubbles, citations & TTS buttons
│   │   ├── message_composer.py  # Attachment bar, voice recording, structured formats
│   │   ├── sidebar.py           # History, model selector, file library
│   │   └── settings_dialog.py   # Diagnostics & configuration inspector
│   ├── styles/
│   │   └── custom.css           # Custom CSS styling
│   ├── api_client.py            # Frontend HTTP client wrapper
│   └── app.py                   # Streamlit main entrypoint
├── data/
│   ├── uploads/                 # Uploaded documents storage
│   └── vector_store/            # Scoped FAISS / NumPy vector indexes
├── alembic/                     # Alembic database migrations
├── scripts/
│   ├── init_db.py               # Database verification script
│   └── check_env.py             # Environment verification script
├── tests/                       # Pytest test suite (health, RAG, db, AI)
├── docker-compose.yml           # Optional PostgreSQL container configuration
├── setup.bat                    # One-click Windows setup script
├── start.bat                    # One-click Windows start script
├── stop.bat                     # Windows process stop script
├── requirements.txt             # Project dependencies
├── .env.example                 # Example configuration template
└── README.md                    # Complete documentation
```

---

## 4. Prerequisites

1. **Operating System:** Windows 10 or 11 (64-bit).
2. **Python:** Python 3.10, 3.11, or 3.12 (Python 3.12 recommended).
   - Ensure **"Add Python to PATH"** was checked during Python installation.
3. **Optional:** Docker Desktop (only if you wish to run PostgreSQL instead of the built-in SQLite).

---

## 5. Windows Quick Start Guide

The easiest way to set up and run the application on Windows:

1. **Run Setup:**
   Double-click `setup.bat` (or open PowerShell in the project directory and run `.\setup.bat`).
   * This creates a Python virtual environment (`.venv`), installs all dependencies, creates `.env` from `.env.example`, and initializes the database tables.

2. **Configure API Keys (Optional):**
   Open `.env` in Notepad and add your free `GROQ_API_KEY` or `OPENAI_API_KEY`. If you don't have one, you can skip this step—the chatbot starts immediately in **Mock/Local Mode**!

3. **Start the Chatbot:**
   Double-click `start.bat`.
   * The FastAPI backend starts at `http://localhost:8000`.
   * The Streamlit UI opens automatically at `http://localhost:8501`.

4. **Stop the Application:**
   Double-click `stop.bat` to terminate both server processes.

---

## 6. Manual Step-by-Step Installation

If you prefer to configure manually via PowerShell or Command Prompt:

```powershell
# 1. Navigate to the project directory
cd c:\Users\Asus\OneDrive\Desktop\chatbot

# 2. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Copy the environment configuration file
copy .env.example .env

# 5. Initialize the database
python scripts\init_db.py
```

---

## 7. Environment Configuration & API Keys

All configuration is managed through the `.env` file in the root folder.

### Key Settings:

| Environment Variable | Description | Default Value |
|----------------------|-------------|---------------|
| `DATABASE_URL` | SQLAlchemy connection URL | `sqlite:///./chatbot.db` |
| `AI_PROVIDER` | Default AI model provider | `mock` (or `groq`, `openai`, `huggingface`) |
| `AI_MODEL` | Default model identifier | `mock-model` (or `llama-3.1-8b-instant`) |
| `GROQ_API_KEY` | Recommended for fast free-tier inference & vision | *(Empty)* |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o / Whisper | *(Empty)* |
| `HUGGINGFACE_API_KEY` | Hugging Face Hub token for serverless models | *(Empty)* |
| `GEMINI_API_KEY` | Google Gemini API key | *(Empty)* |
| `SEARCH_PROVIDER` | Web search provider (`duckduckgo` is 100% free) | `duckduckgo` |
| `TTS_ENGINE` | Speech synthesis engine (`edge-tts` is free) | `edge-tts` |
| `MAX_UPLOAD_MB` | Maximum allowed document upload size | `15` |

### Recommended Free-Tier Setup:
- **Groq:** Sign up at [https://console.groq.com/](https://console.groq.com/) and create a free API key. Set:
  ```env
  AI_PROVIDER=groq
  AI_MODEL=llama-3.1-8b-instant
  GROQ_API_KEY=gsk_your_key_here
  ```
  Groq provides lightning-fast responses (~500 tokens/sec) and supports LLaMA 3.2 Vision on the free tier.

---

## 8. Database Setup & Migrations

### Local SQLite (Default)
By default, the application uses SQLite (`chatbot.db`). It requires no servers to be installed or configured and runs immediately.

### PostgreSQL with Docker (Optional)
To use production PostgreSQL:
1. Start the PostgreSQL container:
   ```bash
   docker-compose up -d
   ```
2. Update your `.env` file:
   ```env
   DATABASE_URL=postgresql://postgres:postgrespassword@localhost:5432/chatbot_db
   ```
3. Run Alembic migrations:
   ```bash
   alembic upgrade head
   ```

---

## 9. Running the Application

### Option A: Using Startup Script
```cmd
start.bat
```

### Option B: Running Services Manually in Two Terminals

**Terminal 1 (FastAPI Backend):**
```powershell
.\.venv\Scripts\activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*API Documentation available at: [http://localhost:8000/docs](http://localhost:8000/docs)*

**Terminal 2 (Streamlit Frontend):**
```powershell
.\.venv\Scripts\activate
streamlit run frontend/app.py --server.port 8501
```
*Web Application available at: [http://localhost:8501](http://localhost:8501)*

---

## 10. Using Multimodal Capabilities

### Text & Conversation Management
- Click **"➕ New Conversation"** in the sidebar to start a fresh thread.
- Switch between past conversations in the sidebar history.
- Click the **⚙️** icon beside any chat in the history to **Rename**, **Delete**, or **Export** the transcript as Markdown or plain text.

### Vision & Image Analysis
1. In the chat composer, expand **"📎 Attach Media / Document / Voice"**.
2. Upload a PNG, JPG, or WebP image under **"🖼️ Image (Vision)"**.
3. Select a vision-capable model (e.g. `LLaMA 3.2 11B Vision` or `GPT-4o`).
4. Ask your question (e.g. *"Describe the diagram in this picture and list key observations"*).
5. If a text-only model is selected, the application politely notifies you that the chosen model lacks vision capabilities rather than failing silently.

### Document Processing & RAG
1. Expand **"📎 Attach Media / Document / Voice"** and choose a document (PDF, DOCX, PPTX, CSV, TXT).
2. Click **"📤 Index Document"**. The file is extracted, split into overlapping chunks, embedded, and indexed into the conversation's vector store.
3. Ask a question regarding the document.
4. The assistant will answer using the retrieved context and render an expandable **"📚 Document Sources"** card showing exact document names, page numbers, similarity scores, and text snippets.

### Live Web Search
1. In the sidebar, toggle **"🌐 Live Web Search"** to ON.
2. Ask a current-events or live fact question (e.g. *"What happened in the latest SpaceX launch?"*).
3. The chatbot searches DuckDuckGo, synthesizes the results, and displays an expandable **"🌐 Web Sources"** card with clickable source URLs.

### Voice Input & Output
- **Voice Input:** Use the microphone recorder under the attachment bar or upload an audio clip. Click **"Transcribe Voice"** to convert speech into text for review before sending.
- **Voice Output:** Every assistant message includes a **"🔊 Read Aloud"** button. Clicking it generates natural neural audio using Edge-TTS and plays it directly in your browser.

### Structured Outputs
Use the **Structured Output Mode** dropdown to instruct the model to return:
- **Executive Summary:** Bullet-pointed key takeaways.
- **Checklist:** Actionable task items with Markdown checkboxes.
- **Comparison Table:** Tabular side-by-side analysis.
- **JSON:** Formatted valid JSON data.

---

## 11. Running the Automated Test Suite

The test suite covers backend endpoints, database operations, RAG vector indexing, conversation isolation, and AI fallback behavior.

Run tests using pytest:
```powershell
.\.venv\Scripts\activate
pytest tests/ -v
```

All external network calls to paid AI providers are mocked so tests run 100% offline and cost \$0.

---

## 12. Troubleshooting & FAQ

**Q: Port 8000 or 8501 is already in use.**
- Run `stop.bat` to terminate any hanging server processes, or change `BACKEND_PORT` / `FRONTEND_PORT` in `.env`.

**Q: "No API key configured" notice appears.**
- The application automatically falls back to **Mock Assistant** when keys are absent. Add your free key to `.env` (`GROQ_API_KEY=...`) and restart.

**Q: PyMuPDF or FAISS installation issues on Windows.**
- The codebase includes a zero-dependency **pure NumPy cosine similarity vector store fallback** that activates automatically if FAISS is not present.

**Q: Where are uploaded files stored?**
- Files are saved in `data/uploads/` with sanitized, UUID-prefixed names to prevent path traversal attacks.

---

## 13. Security & Deployment Considerations

- **Single-User MVP:** Designed for local development and personal productivity on Windows.
- **Path Traversal Protection:** All filenames are sanitized with regex before writing to disk.
- **Conversation Isolation:** Vector indexes and document metadata are isolated per conversation ID.
- **Secret Masking:** API keys are never exposed in logs, API responses, or frontend components.
- **Environment Isolation:** Secrets reside strictly in `.env`, which is excluded from Git via `.gitignore`.

---

## 14. Future Roadmap

- Multi-user authentication via JWT.
- GraphRAG for complex multi-hop knowledge retrieval.
- Local Whisper STT model acceleration via CTranslate2 / faster-whisper.
- Export to PDF and PowerPoint reports.

#   M M - C H h a t b o t  
 