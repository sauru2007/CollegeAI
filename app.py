import os
import json

import faiss
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

from config import Config
from database.db import db
from database.models import User, Document, ChatHistory

# Blueprints
from src.auth.routes import auth_bp
from src.chat.routes import chat_bp as chat_chat_bp
from src.syllabus.routes import syllabus_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)
    CORS(app)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def home():
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return redirect(url_for("auth.login_page"))
    
    
    @app.get("/dashboard")
    def dashboard():
        if "user_id" not in session:
            return redirect(url_for("auth.login_page"))

        user_id = session["user_id"]

        documents_count = Document.query.filter_by(
            user_id=user_id
        ).count()

        questions_count = ChatHistory.query.filter_by(
            user_id=user_id,
            role="user"
        ).count()

        return render_template(
            "dashboard.html",
            user_name=session.get("user_name", ""),
            documents_count=documents_count,
            questions_count=questions_count,
        )


    @app.get("/chat")
    def chat_page():
        if "user_id" not in session:
            return redirect(url_for("auth.login_page"))

        return render_template(
            "chat.html",
            user_name=session.get("user_name", "")
        )


    # Blueprint registration
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_chat_bp)
    app.register_blueprint(syllabus_bp)


    @app.get("/syllabus")
    def syllabus_page():
        if "user_id" not in session:
            return redirect(url_for("auth.login_page"))

        return render_template(
            "syllabus.html",
            user_name=session.get("user_name", "")
        )

    # ---------------- Documents upload (PDF -> chunk -> FAISS) ----------------
    @app.post("/api/upload")
    def upload():
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401

        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF files supported for MVP"}), 400

        user_id = session["user_id"]

        upload_folder = os.path.join(app.instance_path, "uploads", str(user_id))
        os.makedirs(upload_folder, exist_ok=True)

        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Extract text
        with open(filepath, "rb") as f:
            reader = PdfReader(f)

            full_text_parts = []
            for page in reader.pages:
                t = page.extract_text() or ""
                if t.strip():
                    full_text_parts.append(t)

            full_text = "\n".join(full_text_parts)

        # PDF validation (required)
        if not full_text.strip():
            return jsonify({"error": "No readable text found in PDF"}), 400

        # Chunking (single definition, no duplicates)
        def chunk_text(text: str):
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

        chunks = chunk_text(full_text)

        # Persist Document metadata
        doc = Document(user_id=user_id, filename=filename, filepath=filepath)
        db.session.add(doc)
        db.session.commit()

        # Build FAISS
        def ensure_faiss_dir():
            faiss_dir = os.path.join(app.instance_path, Config.FAISS_DIRNAME, str(user_id))
            os.makedirs(faiss_dir, exist_ok=True)
            return faiss_dir

        def meta_path(faiss_dir: str) -> str:
            return os.path.join(faiss_dir, Config.FAISS_META_FILENAME)

        def index_path(faiss_dir: str) -> str:
            return os.path.join(faiss_dir, Config.FAISS_INDEX_FILENAME)

        faiss_dir = ensure_faiss_dir()

        model = SentenceTransformer(Config.EMBEDDING_MODEL_NAME)
        embeddings = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        dim = embeddings.shape[1]

        existing_chunks = []
        final_chunks = chunks

        if os.path.exists(meta_path(faiss_dir)) and os.path.exists(index_path(faiss_dir)):
            with open(meta_path(faiss_dir), "r", encoding="utf-8") as f:
                meta = json.load(f)
            existing_chunks = meta.get("chunks", [])

            combined_chunks = existing_chunks + chunks
            combined_embeddings = model.encode(
                combined_chunks,
                convert_to_numpy=True,
                normalize_embeddings=True
            ).astype("float32")

            index = faiss.IndexFlatIP(dim)
            index.add(combined_embeddings)
            final_chunks = combined_chunks
        else:
            index = faiss.IndexFlatIP(dim)
            index.add(embeddings)
            final_chunks = chunks

        # Persist
        with open(meta_path(faiss_dir), "w", encoding="utf-8") as f:
            json.dump({"dim": dim, "chunks": final_chunks}, f, ensure_ascii=False)

        faiss.write_index(index, index_path(faiss_dir))

        return jsonify({"ok": True, "chunksIndexed": len(chunks), "filename": filename})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
