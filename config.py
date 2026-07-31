import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # SQLite for MVP
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///college_ai.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask upload limits (bytes)
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(25 * 1024 * 1024)))  # 25MB

    # OpenAI/Groq
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # Models
    # Chat model for Groq (Llama)
    GROQ_TEXT_MODEL = os.getenv("GROQ_TEXT_MODEL", "llama-3.1-8b-instant")

    # Vision model for future phases (MVP not required)
    OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")

    # Embeddings
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

    # FAISS persistence
    # Stored under: instance/faiss/
    FAISS_DIRNAME = os.getenv("FAISS_DIRNAME", "faiss")
    FAISS_INDEX_FILENAME = os.getenv("FAISS_INDEX_FILENAME", "index.faiss")
    FAISS_META_FILENAME = os.getenv("FAISS_META_FILENAME", "meta.json")

    # Retrieval
    TOP_K = int(os.getenv("RAG_TOP_K", "5"))
    CHUNK_CHAR_SIZE = int(os.getenv("CHUNK_CHAR_SIZE", "1200"))
    CHUNK_CHAR_OVERLAP = int(os.getenv("CHUNK_CHAR_OVERLAP", "150"))

    # Prompt hardening (MVP)
    SYSTEM_RAG_INSTRUCTIONS = (
        "You are an academic assistant for college students. "
        "Answer using the provided reference context from the uploaded documents. "
        "If the answer is not present in the reference context, say: "
        "\"I don't have that information from the uploaded documents.\" "
        "Be concise, accurate, and structured."
    )
