# src/syllabus/routes.py
import os
import json
from datetime import datetime

from flask import Blueprint, request, jsonify, render_template, session
from sqlalchemy import select

from config import Config
from database.db import db
from database.models import Document, SyllabusAnalysis

from openai import OpenAI
from groq import Groq

syllabus_bp = Blueprint("syllabus", __name__, url_prefix="/api/syllabus")


def require_login():
    return session.get("user_id")


def extract_pdf_text(filepath: str) -> str:
    from PyPDF2 import PdfReader

    if not filepath or not os.path.exists(filepath):
        return ""

    with open(filepath, "rb") as f:
        reader = PdfReader(f)
        parts = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                parts.append(t)
        return "\n".join(parts)


def analyze_with_llm(groq_key: str | None, openai_key: str | None, syllabus_text: str) -> dict:
    system_prompt = (
        "You are an academic syllabus analyzer.\n\n"
        "Analyze the uploaded syllabus and return structured JSON only.\n"
        "Return keys exactly:\n"
        "- subject\n"
        "- units\n"
        "- important_topics\n"
        "- difficulty_analysis\n"
        "- exam_weightage\n"
        "- recommended_study_order\n\n"
        "No markdown. No extra keys. Valid JSON only."
    )

    user_prompt = (
        "Here is the syllabus text:\n\n"
        f"{syllabus_text[:200000]}\n\n"
        "Return JSON only."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    if groq_key:
        client = Groq(api_key=groq_key)
        resp = client.chat.completions.create(
            model=Config.GROQ_TEXT_MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=900,
        )
        content = resp.choices[0].message.content
    else:
        client = OpenAI(api_key=openai_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
            max_tokens=900,
        )
        content = resp.choices[0].message.content

    # Best-effort JSON parsing
    try:
        return json.loads(content)
    except Exception:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(content[start : end + 1])
        raise


@syllabus_bp.post("/analyze")
def analyze():
    user_id = require_login()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True) or {}
    document_id = data.get("document_id")
    if not document_id:
        return jsonify({"error": "document_id is required"}), 400

    doc = db.session.execute(
        select(Document).where(Document.id == int(document_id), Document.user_id == user_id)
    ).scalar_one_or_none()

    if not doc:
        return jsonify({"error": "Document not found"}), 404

    syllabus_text = extract_pdf_text(doc.filepath)
    if not syllabus_text.strip():
        return jsonify({"error": "Could not extract text from the PDF"}), 400

    result = analyze_with_llm(Config.GROQ_API_KEY, Config.OPENAI_API_KEY, syllabus_text)

    # Persist analysis
    # Store lists as JSON strings to keep MVP schema simple.
    analysis = SyllabusAnalysis(
        user_id=user_id,
        subject_name=result.get("subject"),
        units=json.dumps(result.get("units", []), ensure_ascii=False),
        important_topics=json.dumps(result.get("important_topics", []), ensure_ascii=False),
        difficulty_analysis=result.get("difficulty_analysis"),
        exam_weightage=result.get("exam_weightage"),
        created_at=datetime.utcnow(),
    )
    db.session.add(analysis)
    db.session.commit()

    return jsonify(result)


@syllabus_bp.get("/page")
def syllabus_page():
    # Optional page route (if you want to render at /api/syllabus/page)
    return render_template("syllabus.html")
