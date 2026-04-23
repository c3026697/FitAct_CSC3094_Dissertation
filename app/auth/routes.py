"""Authentication routes for FitAct.

Handles user registration, login, logout, and registration success routes.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db, bcrypt
from app.models import User
from app.utils.validators import validate_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        error = None
        if not username or not email or not password:
            error = "All fields are required."
        elif len(username) < 3:
            error = "Username must be at least 3 characters."
        elif password != confirm_password:
            error = "Passwords do not match."
        else:
            password_errors = validate_password(password)
            if password_errors:
                error = password_errors[0]

        if not error:
            if User.query.filter_by(username=username).first():
                error = "Username already taken."
            elif User.query.filter_by(email=email).first():
                error = "An account with that email already exists."

        if error:
            flash(error, "danger")
            return render_template("auth/register.html")

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.register_success"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")
        login_user(user)
        next_page = request.args.get("next")
        if not user.current_programme_id:
            return redirect(url_for("questionnaire.questionnaire"))
        return redirect(next_page or url_for("workouts.workout_page"))
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register/success")
def register_success():
    return render_template("auth/register_success.html")