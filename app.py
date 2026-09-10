#!/usr/bin/env python3
"""
Hayyat Clinic - Website for Dr. Rasheed Ahmad
Mithay Wali Village, Balochistan
Secure Flask application with OTP signup, appointments, and multi-theme support.
"""

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import sqlite3
import os
import re
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Strong random secret key

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), "clinic.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            otp TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            patient_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            reason TEXT,
            preferred_date TEXT,
            preferred_time TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Security helpers
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def clean_phone(phone):
    """Normalize Pakistani phone numbers"""
    phone = re.sub(r"\D", "", phone)
    if phone.startswith("92"):
        phone = "0" + phone[2:]
    if phone.startswith("3") and len(phone) == 10:
        phone = "0" + phone
    return phone

def generate_otp():
    return f"{secrets.randbelow(1000000):06d}"

# Routes
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("signup"))
    return render_template("home.html",
                           doctor_name="Dr. Rasheed Ahmad",
                           clinic_name="Hayyat Clinic",
                           village="Mithay Wali",
                           phone="0341858874",
                           whatsapp="03416995056")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = clean_phone(request.form.get("phone", ""))
        password = request.form.get("password", "")

        if not name or len(name) < 2:
            flash("Please enter a valid name.", "danger")
            return render_template("signup.html")
        if not re.match(r"^03\d{9}$", phone):
            flash("Please enter a valid Pakistani mobile number (03XXXXXXXXX).", "danger")
            return render_template("signup.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("signup.html")

        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE phone = ?", (phone,)).fetchone()
        if existing:
            conn.close()
            flash("This number is already registered. Please login.", "warning")
            return redirect(url_for("login"))

        # Generate and store OTP
        otp = generate_otp()
        expires = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        conn.execute("INSERT INTO otps (phone, otp, expires_at) VALUES (?, ?, ?)",
                     (phone, otp, expires))
        password_hash = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (phone, name, password_hash, is_verified) VALUES (?, ?, ?, 0)",
            (phone, name, password_hash)
        )
        conn.commit()
        conn.close()

        # In real system: send SMS via API. Here we store for demo.
        session["pending_phone"] = phone
        session["demo_otp"] = otp  # Only for demonstration
        flash(f"OTP sent to {phone}. (Demo OTP: {otp})", "success")
        return redirect(url_for("verify_otp"))

    return render_template("signup.html")

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    phone = session.get("pending_phone")
    if not phone:
        return redirect(url_for("signup"))

    if request.method == "POST":
        user_otp = request.form.get("otp", "").strip()
        conn = get_db()
        row = conn.execute(
            "SELECT id, otp, expires_at FROM otps WHERE phone = ? AND used = 0 ORDER BY id DESC LIMIT 1",
            (phone,)
        ).fetchone()

        if not row:
            conn.close()
            flash("No OTP found. Please signup again.", "danger")
            return redirect(url_for("signup"))

        if datetime.fromisoformat(row["expires_at"]) < datetime.utcnow():
            conn.close()
            flash("OTP expired. Please signup again.", "danger")
            return redirect(url_for("signup"))

        if row["otp"] != user_otp:
            conn.close()
            flash("Incorrect OTP. Try again.", "danger")
            return render_template("verify_otp.html", phone=phone)

        # Mark verified
        conn.execute("UPDATE otps SET used = 1 WHERE id = ?", (row["id"],))
        conn.execute("UPDATE users SET is_verified = 1 WHERE phone = ?", (phone,))
        user = conn.execute("SELECT id, name FROM users WHERE phone = ?", (phone,)).fetchone()
        conn.commit()
        conn.close()

        session.pop("pending_phone", None)
        session.pop("demo_otp", None)
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_phone"] = phone
        flash("Account verified successfully! Welcome to Hayyat Clinic.", "success")
        return redirect(url_for("index"))

    return render_template("verify_otp.html", phone=phone, demo_otp=session.get("demo_otp"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        phone = clean_phone(request.form.get("phone", ""))
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT id, name, password_hash, is_verified FROM users WHERE phone = ?",
            (phone,)
        ).fetchone()
        conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid phone or password.", "danger")
            return render_template("login.html")
        if not user["is_verified"]:
            flash("Please verify your OTP first.", "warning")
            session["pending_phone"] = phone
            return redirect(url_for("verify_otp"))

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_phone"] = phone
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/appointment", methods=["GET", "POST"])
@login_required
def appointment():
    if request.method == "POST":
        patient_name = request.form.get("patient_name", "").strip()
        phone = clean_phone(request.form.get("phone", session.get("user_phone", "")))
        reason = request.form.get("reason", "").strip()
        preferred_date = request.form.get("preferred_date", "")
        preferred_time = request.form.get("preferred_time", "")

        if not patient_name or not phone:
            flash("Name and phone are required.", "danger")
            return render_template("appointment.html")

        conn = get_db()
        conn.execute(
            """INSERT INTO appointments
               (user_id, patient_name, phone, reason, preferred_date, preferred_time)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session["user_id"], patient_name, phone, reason, preferred_date, preferred_time)
        )
        conn.commit()
        conn.close()
        flash("Appointment request submitted successfully! Doctor will contact you soon.", "success")
        return redirect(url_for("index"))

    return render_template("appointment.html",
                           user_name=session.get("user_name"),
                           user_phone=session.get("user_phone"))

@app.route("/about")
@login_required
def about():
    return render_template("about.html")

@app.route("/services")
@login_required
def services():
    return render_template("services.html")

@app.route("/contact")
@login_required
def contact():
    return render_template("contact.html",
                           phone="0341858874",
                           whatsapp="03416995056")

if __name__ == "__main__":
    # Development server (for production use gunicorn + proper HTTPS)
    app.run(host="0.0.0.0", port=5000, debug=False)
