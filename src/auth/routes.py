from flask import Blueprint, request, session, redirect, url_for, jsonify, render_template

from sqlalchemy import select

from config import Config
from database.db import db
from database.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.get("/login")
def login_page():
    return render_template("login.html")


@auth_bp.get("/register")
def register_page():
    return render_template("register.html")


@auth_bp.post("/api/register")
def register_api():
    data = request.get_json(force=True)

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm = data.get("confirm_password") or ""

    if not name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400
    if password != confirm:
        return jsonify({"error": "Passwords do not match"}), 400

    existing = db.session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    user = User(name=name, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    session["user_email"] = user.email
    session["user_name"] = user.name

    return jsonify({"ok": True})


@auth_bp.post("/api/login")
def login_api():
    data = request.get_json(force=True)

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    user = db.session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user.id
    session["user_email"] = user.email
    session["user_name"] = user.name

    return jsonify({"ok": True})


@auth_bp.post("/api/logout")
def logout_api():
    session.clear()
    return jsonify({"ok": True})


def login_required():
    if "user_id" not in session:
        return None
    return session["user_id"]
