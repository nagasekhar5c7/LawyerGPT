# LawyerGPT — Project Blueprint

## Overview

LawyerGPT is a **RAG-based (Retrieval-Augmented Generation) legal chatbot** that enables lawyers, attorneys, and legal professionals to ask legal questions and receive accurate, citation-backed answers derived from uploaded legal documents (PDFs). The system ingests legal documents on-demand, stores them as vector embeddings, and uses them to ground LLM responses in factual, source-cited legal content.

---

## Architecture — Three-Layer Design

```
┌─────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                        │
│              React + TypeScript + Tailwind CSS              │
│         (ChatGPT-inspired layout with streaming)            │
├─────────────────────────────────────────────────────────────┤
│                     SERVICE LAYER                           │
│                  Python + FastAPI + SQLite                  │
│         (REST APIs, SSE streaming, file upload)             │
├─────────────────────────────────────────────────────────────┤
│                       AI LAYER                              │
│              Python + LangChain + ChromaDB                  │
│     (Data Ingestion Pipeline + Query Orchestration)         │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Presentation Layer (`client/`)

### Tech Stack
- **Framework:** React 18+ with TypeScript
- **Styling:** Tailwind CSS
- **Build Tool:** Vite
- **HTTP Client:** Axios
- **Streaming:** EventSource API (SSE) for token-by-token LLM streaming

### Layout (ChatGPT-Inspired)
- **Sidebar (left panel):**
  - New Chat button
  - List of past conversations (title + timestamp), fetched from server
  - Each conversation is clickable to reload chat history
- **Main Chat Area (center):**
  - Message thread (alternating user/assistant bubbles)
  - Assistant messages render Markdown with source citations
  - Streaming indicator (typing animation while tokens arrive)
- **Input Bar (bottom):**
  - Text input with send button
  - PDF upload button (triggers document ingestion)
- **Header:**
  - App branding ("LawyerGPT")
  - Model Selector dropdown (user picks which LLM to route queries to)

### Key Frontend Features
- Token-by-token streaming via SSE (Server-Sent Events)
- PDF upload with progress indicator
- Source citation rendering (document name + page number displayed as clickable references)
- Conversation management (create, switch, delete conversations)
- Model selection dropdown (switch between LLMs per query)
- Responsive design (desktop-first, mobile-friendly)

### Model Selection
Users can select which LLM to route their query to via a dropdown in the header. The selected model ID is sent with each chat request to the backend, which forwards it to the engine layer.

**Available Models:**
| Model ID | Display Name | Provider |
|----------|-------------|----------|
| `gpt-5.5` | GPT-5.5 (default) | OpenAI |
| `gpt-4o` | GPT-4o | OpenAI |
| `gpt-4o-mini` | GPT-4o Mini | OpenAI |
| `claude-sonnet-4-6` | Claude Sonnet 4.6 | Anthropic |
| `claude-haiku-4-5` | Claude Haiku 4.5 | Anthropic |

Models are defined in `client/src/types/index.ts` (`AVAILABLE_MODELS` array) and can be extended by adding entries there. The backend `ChatRequest` schema accepts a `model` field and the engine's `generator.py` uses it to instantiate the correct LLM provider.

### Directory Structure
```
client/
├── public/
├── src/
│   ├── components/
│   │   ├── Sidebar/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ConversationList.tsx
│   │   │   └── NewChatButton.tsx
│   │   ├── Chat/
│   │   │   ├── ChatArea.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── CitationCard.tsx
│   │   │   └── StreamingIndicator.tsx
│   │   ├── Input/
│   │   │   ├── ChatInput.tsx
│   │   │   └── FileUpload.tsx
│   │   └── Layout/
│   │       ├── AppLayout.tsx
│   │       └── ModelSelector.tsx
│   ├── hooks/
│   │   ├── useChat.ts
│   │   ├── useConversations.ts
│   │   └── useFileUpload.ts
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── index.html
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

---

## Layer 2: Service Layer (`server/`)

### Tech Stack
- **Framework:** FastAPI
- **Database:** SQLite (via SQLAlchemy, auto-create tables)
- **Streaming:** SSE (Server-Sent Events) via `sse-starlette`
- **File Handling:** `python-multipart` for PDF uploads
- **Dependency Management:** UV

### API Design (Production-Grade Separation)

The server follows a strict **Routes → Services → Data (Repository)** separation:

```
server/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point, CORS, lifespan
│   ├── config.py                  # Settings, env vars (OPENAI_API_KEY, etc.)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── conversations.py       # Conversation CRUD endpoints
│   │   ├── chat.py                # Chat/query endpoint (SSE streaming)
│   │   └── documents.py           # PDF upload/ingestion endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── conversation_service.py
│   │   ├── chat_service.py        # Orchestrates query pipeline + streaming
│   │   └── document_service.py    # Orchestrates ingestion pipeline
│   ├── data/
│   │   ├── __init__.py
│   │   ├── database.py            # SQLAlchemy engine, session, base
│   │   ├── models.py              # ORM models (Conversation, Message)
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── conversation_repo.py
│   │       └── message_repo.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── conversation.py        # Pydantic request/response schemas
│   │   ├── chat.py
│   │   └── document.py
│   └── exceptions/
│       ├── __init__.py
│       └── handlers.py            # Global exception handlers
├── logs/                          # Log files directory
└── lawyergpt.db                   # SQLite database file
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/conversations` | Create a new conversation |
| `GET` | `/api/v1/conversations` | List all conversations |
| `GET` | `/api/v1/conversations/{id}` | Get conversation with messages |
| `DELETE` | `/api/v1/conversations/{id}` | Delete a conversation |
| `POST` | `/api/v1/chat/{conversation_id}` | Send a message + model selection, get SSE-streamed response |
| `POST` | `/api/v1/documents/upload` | Upload and ingest a PDF document |
| `GET` | `/api/v1/documents` | List ingested documents |

### Database Schema (SQLite)

**conversations table:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique conversation ID |
| title | VARCHAR | Auto-generated from first message |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last activity timestamp |

**messages table:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique message ID |
| conversation_id | UUID (FK) | Links to conversation |
| role | ENUM | "user" or "assistant" |
| content | TEXT | Message content |
| citations | JSON | Source citations (doc name, page, chunk) |
| created_at | DATETIME | Timestamp |

**documents table:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique document ID |
| filename | VARCHAR | Original file name |
| file_size | INTEGER | File size in bytes |
| total_chunks | INTEGER | Number of chunks created |
| status | ENUM | "processing", "completed", "failed" |
| created_at | DATETIME | Upload timestamp |

### Logging Strategy
- **Library:** Python `logging` module
- **Format:** JSON-structured logs with timestamp, level, module, message
- **Levels:** DEBUG (dev), INFO (production default), ERROR (exceptions)
- **Output:** Console + rotating file handler (`logs/lawyergpt.log`)
- Every service method and route handler logs entry/exit, key parameters, and errors

### Exception Handling Strategy
- Custom exception classes (`DocumentProcessingError`, `LLMError`, `RetrievalError`)
- Global FastAPI exception handler that catches all exceptions, logs them, and returns standardized error responses
- HTTP error responses follow the format: `{"detail": "message", "error_code": "ERROR_TYPE"}`

---

## Layer 3: AI Layer (`engine/`)

### Tech Stack
- **Framework:** LangChain
- **Vector Store:** ChromaDB (persistent local storage)
- **Embeddings Model:** OpenAI `text-embedding-3-large`
- **LLM:** User-selectable — OpenAI (gpt-5.5, gpt-4o, gpt-4o-mini) or Anthropic (claude-sonnet-4-6, claude-haiku-4-5) via LangChain
- **PDF Processing:** `PyPDFLoader` (LangChain) + fallback OCR via `pytesseract`

### Directory Structure

```
engine/
├── __init__.py
├── config.py                      # AI-specific configuration constants
├── ingestion/                     # Data Ingestion Pipeline (ETL)
│   ├── __init__.py
│   ├── loader.py                  # [E] Extract — PDF loading / OCR
│   ├── chunker.py                 # [T] Transform — Recursive text chunking
│   ├── embedder.py                # [T] Transform — Embedding generation
│   └── store.py                   # [L] Load — Batch insert into ChromaDB
├── orchestration/                 # Query Orchestration Pipeline
│   ├── __init__.py
│   ├── retriever.py               # Retrieve relevant chunks from ChromaDB
│   ├── augmentor.py               # Augment prompt with system prompt + context
│   └── generator.py               # Generate response via LLM (streaming)
├── prompts/
│   ├── __init__.py
│   └── templates.py               # System prompt and prompt templates
└── pipeline.py                    # High-level pipeline orchestrator
```

### Pipeline 1: Data Ingestion (ETL)

```
PDF Upload → Extract → Transform (Chunk + Embed) → Load into ChromaDB
```

#### Extract Phase — `loader.py`
- Uses LangChain `PyPDFLoader` to extract text from PDF files
- Preserves page number metadata for citation tracking
- Fallback to `pytesseract` OCR for scanned/image-based PDFs
- Returns: List of `Document` objects with `page_content` and `metadata` (filename, page_number)

#### Transform Phase — `chunker.py`
- Uses LangChain `RecursiveCharacterTextSplitter`
- **Chunk size:** 2000 characters
- **Chunk overlap:** 100 characters
- Preserves metadata from extraction phase (filename, page_number)
- Adds chunk_index metadata for ordering

#### Transform Phase — `embedder.py`
- Uses OpenAI `text-embedding-3-large` model via LangChain `OpenAIEmbeddings`
- Generates vector embeddings for each chunk
- Handles embedding in batches for efficiency

#### Load Phase — `store.py`
- Loads embedded chunks into ChromaDB
- **Batch size:** 100 vectors per batch (configurable, supports 100-200)
- ChromaDB persistent storage directory: `./chroma_db/`
- Collection name: `legal_documents`
- Stores metadata: `filename`, `page_number`, `chunk_index`, `document_id`

### Pipeline 2: Query Orchestration

```
User Query → Retrieve → Augment → Generate (Stream) → Response with Citations
```

#### Retrieve — `retriever.py`
- Queries ChromaDB using similarity search
- **Top-K:** 5 most relevant chunks
- Returns chunks with metadata (for citation construction)
- Uses the same embedding model (`text-embedding-3-large`) to embed the query

#### Augment — `augmentor.py`
- Constructs the full prompt by combining:
  1. **System Prompt:** Defines the assistant's role as a legal expert, instructs it to cite sources, and sets behavioral guidelines
  2. **Conversation History:** Previous messages in the current conversation (for multi-turn context)
  3. **Retrieved Context:** The top-5 relevant chunks, formatted with source metadata
  4. **User Query:** The current question
- Implements conversation history management:
  - Sends full conversation history when context fits within token limits
  - Summarizes older messages when conversation grows too long (using LLM summarization)

#### Generate — `generator.py`
- Receives the user-selected `model` ID from the chat request
- Instantiates the correct LLM provider based on model ID:
  - OpenAI models (`gpt-5.5`, `gpt-4o`, `gpt-4o-mini`) → LangChain `ChatOpenAI`
  - Anthropic models (`claude-sonnet-4-6`, `claude-haiku-4-5`) → LangChain `ChatAnthropic`
- **Streaming:** Uses LangChain's streaming callbacks to yield tokens as they arrive
- Parses LLM response to extract structured citations
- Returns: streamed tokens + final parsed citations (document name, page number)

### System Prompt (Core Behavior)
The system prompt instructs the LLM to:
- Act as a knowledgeable legal research assistant
- ONLY answer based on the provided context from legal documents
- ALWAYS cite sources with document name and page number
- Acknowledge when the provided context doesn't contain enough information
- Never fabricate legal information
- Present information clearly with appropriate legal terminology

---

## Conversation Memory Strategy

### Short Conversations (< threshold)
- Full conversation history is included in the prompt
- All previous user and assistant messages are sent to the LLM

### Long Conversations (> threshold)
- Older messages are summarized using the LLM into a condensed summary
- Recent messages (last N turns) are kept in full
- Summary + recent messages are sent to the LLM
- Threshold and recent-turn count are configurable in `engine/config.py`

---

## Environment Variables

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic (required for Claude models)
ANTHROPIC_API_KEY=sk-ant-...

# Application
APP_ENV=development          # development | production
LOG_LEVEL=INFO               # DEBUG | INFO | WARNING | ERROR

# Database
DATABASE_URL=sqlite:///./lawyergpt.db

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_NAME=legal_documents

# AI Configuration
EMBEDDING_MODEL=text-embedding-3-large
DEFAULT_LLM_MODEL=gpt-5.5   # Fallback if client doesn't send model
CHUNK_SIZE=2000
CHUNK_OVERLAP=100
RETRIEVAL_TOP_K=5
BATCH_SIZE=100
```

---

## Dependency Management

- **Python:** UV (pyproject.toml)
- **Client:** npm (package.json)
- **Python version:** 3.12

### Key Python Dependencies
```
fastapi
uvicorn[standard]
sqlalchemy
langchain
langchain-openai
langchain-anthropic
langchain-community
langchain-chroma
chromadb
openai
python-multipart
sse-starlette
python-dotenv
pytesseract
pypdf
```

### Key Frontend Dependencies
```
react
react-dom
typescript
@types/react
axios
tailwindcss
react-markdown
react-router-dom
```

---

## Project Root Structure

```
LawyerGPT/
├── CLAUDE.md                      # This file — project blueprint
├── pyproject.toml                 # UV/Python project config
├── uv.lock                       # UV lock file
├── main.py                       # Root entry (placeholder)
├── .env                           # Environment variables (git-ignored)
├── .gitignore
├── docs/
│   ├── architecture.excalidraw    # High-level architecture diagram
│   └── diagrams.md                # Mermaid diagrams (user flow, sequence)
├── client/                        # Presentation Layer
│   └── (see client structure above)
├── server/                        # Service Layer
│   ├── app/
│   │   └── (see server structure above)
│   └── logs/
├── engine/                        # AI Layer
│   └── (see engine structure above)
├── skills/                        # Claude Code custom skills
│   └── caveman/
│       └── SKILL.md               # Token optimization skill (caveman mode)
├── chroma_db/                     # ChromaDB persistent storage (git-ignored)
└── uploads/                       # Temporary PDF upload storage (git-ignored)
```

---

## Development Commands

```bash
# Server (Backend)
cd server && uv run uvicorn app.main:app --reload --port 8000

# Client (Frontend)
cd client && npm install && npm run dev

# Full stack (from root)
# Terminal 1: Server
uv run uvicorn server.app.main:app --reload --port 8000
# Terminal 2: Client
cd client && npm run dev
```

---

## Coding Standards

### Python (Server + Engine)
- Follow PEP 8
- Type hints on all function signatures
- Async/await for all FastAPI route handlers and service methods
- Structured JSON logging in every module
- Custom exceptions with descriptive error codes
- Docstrings only where the "why" is non-obvious

### TypeScript (Client)
- Strict TypeScript (no `any` unless unavoidable)
- Functional components with hooks
- Custom hooks for shared logic (useChat, useConversations, useFileUpload)
- Type definitions in dedicated `types/` directory

### API Design
- RESTful conventions
- Versioned endpoints (`/api/v1/`)
- Pydantic schemas for all request/response validation
- Consistent error response format

---

## Skills

### Caveman — Token Optimization Skill (`skills/caveman/SKILL.md`)

- **Name:** `caveman`
- **Description:** Ultra-compressed communication mode that cuts token usage by ~75% while preserving full technical accuracy. Speaks in terse, caveman-style prose — dropping articles, filler, hedging, and pleasantries — but keeps all technical terms, code blocks, and error strings exact.
- **Intensity Levels:** `lite` | `full` (default) | `ultra` | `wenyan-lite` | `wenyan-full` | `wenyan-ultra`

**When to auto-invoke:** Use `/caveman` or trigger automatically whenever:
- User says "caveman mode", "talk like caveman", "use caveman", "less tokens", or "be brief"
- Token efficiency or cost reduction is requested
- Long-running sessions where minimizing output tokens matters

**When to drop caveman temporarily:**
- Security warnings and irreversible action confirmations
- Multi-step sequences where fragments could be misread
- When the user asks for clarification

**Boundaries:** Code, commits, and PR descriptions are always written in normal prose. Deactivate with "stop caveman" or "normal mode".

---

## Non-Goals (Explicitly Out of Scope)
- User authentication / authorization
- Multi-tenancy
- Docker / containerization (local-first)
- Rate limiting
- Paid/subscription features
- Mobile app
