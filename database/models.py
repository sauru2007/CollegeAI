from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from database.db import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    chat_history = db.relationship("ChatHistory", backref="user", lazy=True)
    documents = db.relationship("Document", backref="user", lazy=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Document(db.Model):
    """
    Stores uploaded PDF metadata.
    The actual text chunks + vectors live in FAISS + meta.json (per-user).
    """
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(1000), nullable=False)

    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class ChatHistory(db.Model):
    __tablename__ = "chat_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    role = db.Column(db.String(20), nullable=False)  # "user" or "assistant"
    message = db.Column(db.Text, nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class SyllabusAnalysis(db.Model):
    __tablename__ = "syllabus_analysis"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    subject_name = db.Column(db.String(255))
    units = db.Column(db.Text)

    important_topics = db.Column(db.Text)
    difficulty_analysis = db.Column(db.Text)
    exam_weightage = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
