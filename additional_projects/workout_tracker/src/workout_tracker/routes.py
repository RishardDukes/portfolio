# src/workout_tracker/routes.py
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user
from .db import db

# If you already created a Workout model elsewhere, import it.
# Otherwise, see the inline "Fallback Workout model" below.
try:
    from .models import Workout  # type: ignore
except Exception:
    Workout = None  # will define a minimal fallback below

main = Blueprint("main", __name__)

# ---------- HTML PAGES ----------

@main.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    # Keep it simple; you can swap to a proper template later.
    return render_template("base.html")

@main.route("/dashboard")
@login_required
def dashboard():
    # show a quick summary; you can replace with a real template
    total = db.session.query(FallbackWorkout if Workout is None else Workout)\
                      .filter_by(user_id=current_user.id).count()
    return f"Welcome {current_user.display_name or current_user.email}! You have {total} logged workouts."

@main.route("/tracker")
@login_required
def tracker():
    # render your tracker UI; replace with an actual template if you like
    return "Tracker UI goes here. (Make a nice template later!)"


# ---------- JSON API (CRUD for workouts) ----------

def _workout_to_dict(w):
    return {
        "id": w.id,
        "user_id": w.user_id,
        "date": (w.date.isoformat() if isinstance(w.date, datetime) else str(w.date)),
        "exercise": w.exercise,
        "sets": w.sets,
        "reps": w.reps,
        "weight": w.weight,
        "notes": w.notes,
        "created_at": w.created_at.isoformat() if w.created_at else None,
        "updated_at": w.updated_at.isoformat() if w.updated_at else None,
    }

# List current user's workouts (optional filters: exercise, date_from, date_to)
@main.route("/api/workouts", methods=["GET"])
@login_required
def list_workouts():
    Model = FallbackWorkout if Workout is None else Workout
    q = Model.query.filter_by(user_id=current_user.id)

    exercise = request.args.get("exercise")
    if exercise:
        q = q.filter(Model.exercise.ilike(f"%{exercise}%"))

    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    if date_from:
        q = q.filter(Model.date >= date_from)
    if date_to:
        q = q.filter(Model.date <= date_to)

    items = q.order_by(Model.date.desc(), Model.id.desc()).all()
    return jsonify([_workout_to_dict(w) for w in items])

# Create a workout (JSON body)
@main.route("/api/workouts", methods=["POST"])
@login_required
def create_workout():
    Model = FallbackWorkout if Workout is None else Workout
    data = request.get_json(force=True, silent=True) or {}

    # minimal validation
    exercise = (data.get("exercise") or "").strip()
    if not exercise:
        return jsonify({"error": "exercise is required"}), 400

    w = Model(
        user_id=current_user.id,
        date=data.get("date") or datetime.utcnow().date(),
        exercise=exercise,
        sets=int(data.get("sets") or 0),
        reps=int(data.get("reps") or 0),
        weight=float(data.get("weight") or 0),
        notes=(data.get("notes") or "").strip() or None,
    )
    db.session.add(w)
    db.session.commit()
    return jsonify(_workout_to_dict(w)), 201

# Read one workout
@main.route("/api/workouts/<int:wid>", methods=["GET"])
@login_required
def get_workout(wid):
    Model = FallbackWorkout if Workout is None else Workout
    w = Model.query.get_or_404(wid)
    if w.user_id != current_user.id:
        abort(403)
    return jsonify(_workout_to_dict(w))

# Partial update
@main.route("/api/workouts/<int:wid>", methods=["PATCH"])
@login_required
def update_workout(wid):
    Model = FallbackWorkout if Workout is None else Workout
    w = Model.query.get_or_404(wid)
    if w.user_id != current_user.id:
        abort(403)

    data = request.get_json(force=True, silent=True) or {}
    if "date" in data and data["date"]:
        w.date = data["date"]
    if "exercise" in data and data["exercise"]:
        w.exercise = data["exercise"].strip()
    if "sets" in data and data["sets"] is not None:
        w.sets = int(data["sets"])
    if "reps" in data and data["reps"] is not None:
        w.reps = int(data["reps"])
    if "weight" in data and data["weight"] is not None:
        w.weight = float(data["weight"])
    if "notes" in data:
        w.notes = (data["notes"] or "").strip() or None

    w.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_workout_to_dict(w))

# Delete
@main.route("/api/workouts/<int:wid>", methods=["DELETE"])
@login_required
def delete_workout(wid):
    Model = FallbackWorkout if Workout is None else Workout
    w = Model.query.get_or_404(wid)
    if w.user_id != current_user.id:
        abort(403)
    db.session.delete(w)
    db.session.commit()
    return "", 204


# ---------- Fallback Workout model (only used if you haven't made one yet) ----------

if Workout is None:
    from sqlalchemy.sql import func
    from sqlalchemy import Date

    class FallbackWorkout(db.Model):
        """
        Minimal workouts table scoped to a user.
        If you already created a Workout model in models.py, this class is ignored.
        """
        __tablename__ = "workouts"

        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

        # Basic training fields
        date = db.Column(Date, nullable=False, default=func.current_date())
        exercise = db.Column(db.String(120), nullable=False)
        sets = db.Column(db.Integer, default=0)
        reps = db.Column(db.Integer, default=0)
        weight = db.Column(db.Float, default=0.0)
        notes = db.Column(db.Text)

        created_at = db.Column(db.DateTime, server_default=func.now())
        updated_at = db.Column(db.DateTime, onupdate=func.now())
