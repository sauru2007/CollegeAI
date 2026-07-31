import json
import os
import uuid
from datetime import datetime

from flask import Blueprint, request, jsonify, session

from sqlalchemy import select

from config import Config
from database.db import db
from database.models import ChatHistory

from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")

# ---- Embeddings + FAISS (MVP: single index per-user stored on disk) ----
_embedding_model = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        # Loads locally/cached by sentence-transformers
        _embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL_NAME)
    return _embedding_model


def ensure_faiss_dir(instance_path: str, user_id: int) -> str:
    # folder per user to keep things simple for MVP
    faiss_base = os.path.join(instance_path, Config.FAISS_DIRNAME, str(user_id))
    os.makedirs(faiss_base, exist_ok=True)
    return faiss_base


def meta_path(faiss_dir: str) -> str:
    return os.path.join(faiss_dir, Config.FAISS_META_FILENAME)


def index_path(faiss_dir: str) -> str:
    return os.path.join(faiss_dir, Config.FAISS_INDEX_FILENAME)


def chunk_text(text: str):
    """
    Simple char-based chunking for MVP. Later we can do token-aware chunking.
    """
    text = text or ""
    size = Config.CHUNK_CHAR_SIZE
    overlap = Config.CHUNK_CHAR_OVERLAP
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start += size - overlap
    return chunks


def extract_pdf_text(file_stream) -> str:
    # file_stream is the uploaded file handle
    reader = PdfReader(file_stream)
    full_text = []
    for page in reader.pages:
        t = page.extract_text() or ""
        if t.strip():
            full_text.append(t)
    return "\n".join(full_text)


def load_faiss(user_id: int, instance_path: str):
    faiss_dir = ensure_faiss_dir(instance_path, user_id)
    mpath = meta_path(faiss_dir)
    ipath = index_path(faiss_dir)

    if not os.path.exists(mpath) or not os.path.exists(ipath):
        return None, []

    with open(mpath, "r", encoding="utf-8") as f:
        meta = json.load(f)

    vectors_dim = int(meta["dim"])
    texts = meta["chunks"]

    index = faiss.read_index(ipath)
    # Basic sanity:
    if index.d != vectors_dim:
        # If mismatch, treat as empty for safety
        return None, []

    return index, texts


def persist_faiss(user_id: int, instance_path: str, index, chunks, dim: int):
    faiss_dir = ensure_faiss_dir(instance_path, user_id)
    with open(meta_path(faiss_dir), "w", encoding="utf-8") as f:
        json.dump({"dim": dim, "chunks": chunks}, f, ensure_ascii=False)

    faiss.write_index(index, index_path(faiss_dir))


def build_or_add_index(user_id: int, instance_path: str, chunks):
    """
    MVP strategy:
    - Load existing index+meta if present
    - Else create new FAISS index
    - Embed all chunks and rebuild index (simple and stable for MVP)
    """
    if not chunks:
        return

    model = get_embedding_model()

    # Embed
    # Convert to list[float32 vector]
    embeddings = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
    embeddings = embeddings.astype("float32")
    dim = embeddings.shape[1]

    existing_index, existing_chunks = load_faiss(user_id, instance_path)

    combined_chunks = (existing_chunks or []) + chunks

    # Re-embed combined for simplicity (stable MVP)
    combined_embeddings = model.encode(combined_chunks, convert_to_numpy=True, normalize_embeddings=True).astype("float32")

    # Cosine similarity with normalized vectors => inner product
    index = faiss.IndexFlatIP(dim)
    index.add(combined_embeddings)

    persist_faiss(user_id, instance_path, index, combined_chunks, dim)


def retrieve_context(user_id: int, instance_path: str, query: str, top_k: int = 5):
    index, chunks = load_faiss(user_id, instance_path)
    if index is None or not chunks:
        return ""

    model = get_embedding_model()
    q = model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
    scores, idx = index.search(q, min(top_k, len(chunks)))

    top_chunks = []
    for i in idx[0]:
        if 0 <= int(i) < len(chunks):
            top_chunks.append(chunks[int(i)])

    return "\n\n---\n\n".join(top_chunks)


@chat_bp.post("")
def chat():
    """
    POST /api/chat
    body:
      {
        "message": "...",
        "assistantMode": "Friend|Mentor|Academic Tutor|Placement Coach" (optional MVP ignored for now),
        "history": [{"role":"user","content":"..."}, ...] (optional)
      }
    """
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True)
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    user_id = session["user_id"]

    # For MVP: we only use DB history optionally, but to keep consistent we’ll read nothing from "history"
    # and rely on FAISS context retrieval.
    instance_path = os.path.abspath(os.path.join(os.getcwd(), "instance"))

    # Save user message
    db.session.add(ChatHistory(user_id=user_id, role="user", message=message, timestamp=datetime.utcnow()))
    db.session.commit()

    # Retrieve context
    context = retrieve_context(user_id, instance_path, message, top_k=Config.TOP_K)

    system_prompt = (
        f"{Config.SYSTEM_RAG_INSTRUCTIONS}\n\n"
        f"REFERENCE CONTEXT:\n{context if context else '[No reference context available]'}"
    )

    # Choose LLM: prefer Groq if available
    groq_key = Config.GROQ_API_KEY
    openai_key = Config.OPENAI_API_KEY

    if not groq_key and not openai_key:
        assistant_text = "LLM is not configured. Set GROQ_API_KEY or OPENAI_API_KEY."
        db.session.add(ChatHistory(user_id=user_id, role="assistant", message=assistant_text, timestamp=datetime.utcnow()))
        db.session.commit()
        return jsonify({"response": assistant_text})

    # Build request
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]

    assistant_text = None
    if groq_key:
        from groq import Groq
        groq_client = Groq(api_key=groq_key)
        resp = groq_client.chat.completions.create(
            model=Config.GROQ_TEXT_MODEL,
            messages=messages,
            temperature=0.4,
            max_tokens=700,
        )
        assistant_text = resp.choices[0].message.content
    else:
        from openai import OpenAI
        openai_client = OpenAI(api_key=openai_key)
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
            max_tokens=700,
        )
        assistant_text = resp.choices[0].message.content

    # Save assistant message
    db.session.add(ChatHistory(user_id=user_id, role="assistant", message=assistant_text, timestamp=datetime.utcnow()))
    db.session.commit()

    return jsonify({"response": assistant_text, "hasContext": bool(context)})


@chat_bp.get("/history")
def history():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]
    rows = (
        db.session.execute(
            select(ChatHistory).where(ChatHistory.user_id == user_id).order_by(ChatHistory.timestamp.desc()).limit(50)
        )
        .scalars()
        .all()
    )

    # Return chronological order
    rows_sorted = list(reversed(rows))
    out = [{"role": r.role, "content": r.message, "timestamp": r.timestamp.isoformat()} for r in rows_sorted]
    return jsonify({"history": out})
