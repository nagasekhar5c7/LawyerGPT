# LawyerGPT — Flow & Sequence Diagrams

---

## 1. User Flow Diagram

```mermaid
flowchart TD
    A["User Opens LawyerGPT"] --> B{"New or Existing\nConversation?"}

    B -->|"New Chat"| C["Create New Conversation"]
    B -->|"Existing Chat"| D["Load Conversation\nHistory from Sidebar"]

    C --> E["Chat Interface"]
    D --> E

    E --> F{"User Action"}

    F -->|"Upload PDF"| G["Select PDF File"]
    G --> H["Upload to Server\n(POST /api/v1/documents/upload)"]
    H --> I{"Ingestion Pipeline (ETL)"}

    I --> I1["Extract:\nLoad PDF / OCR"]
    I1 --> I2["Transform:\nChunk Text\n(2000 chars, 100 overlap)"]
    I2 --> I3["Transform:\nGenerate Embeddings\n(text-embedding-3-large)"]
    I3 --> I4["Load:\nBatch Insert into ChromaDB\n(100 per batch)"]
    I4 --> I5["Upload Complete\n(Document Indexed)"]
    I5 --> E

    F -->|"Ask Legal Question"| N["Type Question in Chat Input"]
    N --> O["Send to Server\n(POST /api/v1/chat/{id})"]
    O --> P{"Query Orchestration Pipeline"}

    P --> P1["Retrieve:\nSimilarity Search\n(Top-5 Chunks from ChromaDB)"]
    P1 --> P2["Augment:\nSystem Prompt + History +\nRetrieved Context + Query"]
    P2 --> P3["Generate:\nStream via GPT-5.5"]
    P3 --> P4["Display Streamed Response\nwith Source Citations"]
    P4 --> E

    F -->|"Switch Conversation"| D
    F -->|"Delete Conversation"| U["Remove Conversation\nfrom Sidebar"]
    U --> E

    style A fill:#dbeafe,stroke:#1971c2
    style E fill:#dbeafe,stroke:#1971c2
    style I fill:#f3e8ff,stroke:#9c36b5
    style P fill:#f3e8ff,stroke:#9c36b5
    style I1 fill:#e9d5ff,stroke:#9c36b5
    style I2 fill:#e9d5ff,stroke:#9c36b5
    style I3 fill:#e9d5ff,stroke:#9c36b5
    style I4 fill:#e9d5ff,stroke:#9c36b5
    style I5 fill:#dcfce7,stroke:#2f9e44
    style P1 fill:#e9d5ff,stroke:#9c36b5
    style P2 fill:#e9d5ff,stroke:#9c36b5
    style P3 fill:#e9d5ff,stroke:#9c36b5
    style P4 fill:#dcfce7,stroke:#2f9e44
    style H fill:#dcfce7,stroke:#2f9e44
    style O fill:#dcfce7,stroke:#2f9e44
```

---

## 2. Sequence Diagram — Document Upload (Ingestion)

```mermaid
sequenceDiagram
    actor User
    participant Client as Client<br/>(React)
    participant Server as Server<br/>(FastAPI)
    participant Loader as loader.py<br/>(Extract)
    participant Chunker as chunker.py<br/>(Transform)
    participant Embedder as embedder.py<br/>(Transform)
    participant Store as store.py<br/>(Load)
    participant ChromaDB as ChromaDB
    participant OpenAI as OpenAI API

    User->>Client: Select & upload PDF
    Client->>Server: POST /api/v1/documents/upload (multipart)
    Server->>Server: Save PDF to uploads/ directory
    Server->>Server: Create document record (status: processing)

    rect rgb(243, 232, 255)
        Note over Loader,Store: Data Ingestion Pipeline (ETL)

        Server->>Loader: Extract text from PDF
        Loader->>Loader: PyPDFLoader (or OCR fallback)
        Loader-->>Server: List[Document] with page metadata

        Server->>Chunker: Split documents into chunks
        Chunker->>Chunker: RecursiveCharacterTextSplitter<br/>(size=2000, overlap=100)
        Chunker-->>Server: List[Document] (chunked, with metadata)

        Server->>Embedder: Generate embeddings for chunks
        Embedder->>OpenAI: text-embedding-3-large (batch)
        OpenAI-->>Embedder: Vector embeddings
        Embedder-->>Server: Embedded chunks

        Server->>Store: Load into vector store
        loop Batch processing (100 per batch)
            Store->>ChromaDB: Upsert batch with metadata<br/>(filename, page_number, chunk_index)
        end
        Store-->>Server: Success (total chunks stored)
    end

    Server->>Server: Update document record (status: completed)
    Server-->>Client: 200 OK { document_id, filename, total_chunks }
    Client-->>User: Display upload success notification
```

---

## 3. Sequence Diagram — Chat Query (RAG Flow)

```mermaid
sequenceDiagram
    actor User
    participant Client as Client<br/>(React)
    participant Server as Server<br/>(FastAPI)
    participant ChatSvc as chat_service.py
    participant DB as SQLite
    participant Retriever as retriever.py
    participant Augmentor as augmentor.py
    participant Generator as generator.py
    participant ChromaDB as ChromaDB
    participant OpenAI as OpenAI API

    User->>Client: Type legal question & send
    Client->>Server: POST /api/v1/chat/{conversation_id}<br/>{ "message": "..." }

    Server->>DB: Save user message to messages table
    Server->>ChatSvc: Process query

    ChatSvc->>DB: Fetch conversation history
    DB-->>ChatSvc: Previous messages (user + assistant)

    alt Conversation is long (exceeds token threshold)
        ChatSvc->>OpenAI: Summarize older messages
        OpenAI-->>ChatSvc: Condensed summary
    end

    rect rgb(243, 232, 255)
        Note over Retriever,Generator: Query Orchestration Pipeline

        ChatSvc->>Retriever: Retrieve relevant context
        Retriever->>OpenAI: Embed user query (text-embedding-3-large)
        OpenAI-->>Retriever: Query embedding vector
        Retriever->>ChromaDB: Similarity search (top_k=5)
        ChromaDB-->>Retriever: Top 5 relevant chunks + metadata
        Retriever-->>ChatSvc: Retrieved context with source info

        ChatSvc->>Augmentor: Build augmented prompt
        Note over Augmentor: Combines:<br/>1. System prompt (legal expert role)<br/>2. Conversation history / summary<br/>3. Retrieved context (5 chunks)<br/>4. Current user query
        Augmentor-->>ChatSvc: Augmented prompt (messages list)

        ChatSvc->>Generator: Generate streaming response
        Generator->>OpenAI: ChatCompletion (gpt-5.5, stream=true)

        loop Token-by-token streaming
            OpenAI-->>Generator: Token chunk
            Generator-->>ChatSvc: Yield token
            ChatSvc-->>Server: SSE event: { "token": "..." }
            Server-->>Client: SSE stream data
            Client-->>User: Render token in real-time
        end

        Generator-->>ChatSvc: Final response + parsed citations
    end

    ChatSvc->>DB: Save assistant message + citations
    Server-->>Client: SSE event: { "done": true, "citations": [...] }
    Client-->>User: Display source citations<br/>(document name, page number)
```

---

## 4. Sequence Diagram — Conversation Management

```mermaid
sequenceDiagram
    actor User
    participant Client as Client<br/>(React)
    participant Server as Server<br/>(FastAPI)
    participant DB as SQLite

    Note over User,DB: Create New Conversation
    User->>Client: Click "New Chat"
    Client->>Server: POST /api/v1/conversations
    Server->>DB: INSERT conversation
    DB-->>Server: conversation_id
    Server-->>Client: { id, title, created_at }
    Client-->>User: Open empty chat interface

    Note over User,DB: List Conversations (Sidebar)
    User->>Client: Open app / Refresh sidebar
    Client->>Server: GET /api/v1/conversations
    Server->>DB: SELECT all conversations (ordered by updated_at)
    DB-->>Server: List of conversations
    Server-->>Client: [{ id, title, updated_at }, ...]
    Client-->>User: Render conversation list in sidebar

    Note over User,DB: Load Existing Conversation
    User->>Client: Click conversation in sidebar
    Client->>Server: GET /api/v1/conversations/{id}
    Server->>DB: SELECT conversation + messages
    DB-->>Server: Conversation with full message history
    Server-->>Client: { id, title, messages: [...] }
    Client-->>User: Render full chat history

    Note over User,DB: Delete Conversation
    User->>Client: Click delete on conversation
    Client->>Server: DELETE /api/v1/conversations/{id}
    Server->>DB: DELETE conversation + CASCADE messages
    DB-->>Server: Deleted
    Server-->>Client: 204 No Content
    Client-->>User: Remove from sidebar, redirect to new chat
```
