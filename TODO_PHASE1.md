# Phase 1 MVP TODO

## Step 1 — Project refactor (backend)
- Create `src/` app factory + config
- Add Flask Blueprints: auth, uploads/files, chat

## Step 2 — Database
- Add SQLAlchemy models (Users, Documents, ChatHistory)
- Initialize SQLite DB in `instance/college_ai.db`

## Step 3 — Authentication
- Implement register/login/logout routes
- Add protected dashboard route

## Step 4 — RAG with FAISS
- Implement PDF text extraction
- Chunking
- Sentence-Transformers embeddings (all-MiniLM-L6-v2)
- Store vectors in FAISS and persist/load

## Step 5 — Chat API upgrade
- `/api/chat` now requires auth
- Retrieve relevant chunks via FAISS
- Save conversation history to DB

## Step 6 — Frontend skeleton
- Create `templates/login.html`, `register.html`, `dashboard.html`, `chat.html`
- Add dark/light mode toggle
- Simple dashboard cards + recent chats

