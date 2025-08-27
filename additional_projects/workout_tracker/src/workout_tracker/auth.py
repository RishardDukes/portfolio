# src/workout_tracker/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .db import db

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    # Already logged in? Send them to their dashboard.
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        display_name = (request.form.get("display_name") or "").strip() or None
        password = request.form.get("password") or ""

        # minimal validation
        if not email or not password:
            flash("Email and password are required.", "warning")
            return redirect(url_for("auth.register"))
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "warning")
            return redirect(url_for("auth.register"))

        # unique email
        if User.query.filter_by(email=email).first():
            flash("That email is already registered. Try logging in.", "info")
            return redirect(url_for("auth.login"))

        user = User(email=email, display_name=display_name)
        user.set_password(password)  # securely hash
        db.session.add(user)
        db.session.commit()

        login_user(user, remember=True)
        flash("Welcome! Account created.", "success")
        # If you have a different landing page, change 'dashboard' below.
        return redirect(url_for('main.dashboard'))

    # GET
    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)

            # support ?next=/some/protected/page
            next_url = request.args.get("next")
            flash("Logged in successfully.", "success")
            return redirect(next_url or url_for('main.dashboard'))

        flash("Invalid email or password.", "danger")

    # GET
    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))
