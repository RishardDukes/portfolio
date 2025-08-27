from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user
from .db import db
from .models import Workout

main = Blueprint("main", __name__)

@main.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("base.html")

@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@main.route("/tracker")
@login_required
def tracker():
    return render_template("tracker.html")

def _to_dict(w: Workout):
    return {
        "id": w.id, "user_id": w.user_id,
        "date": w.date.isoformat() if isinstance(w.date, date) else str(w.date),
        "exercise": w.exercise, "sets": w.sets, "reps": w.reps,
        "weight": w.weight, "notes": w.notes,
        "created_at": w.created_at.isoformat() if w.created_at else None,
        "updated_at": w.updated_at.isoformat() if w.updated_at else None,
    }

@main.route("/api/workouts", methods=["GET"])
@login_required
def list_workouts():
    q = Workout.query.filter_by(user_id=current_user.id)
    exercise = request.args.get("exercise")
    if exercise:
        q = q.filter(Workout.exercise.ilike(f"%{exercise}%"))
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    if date_from:
        try: q = q.filter(Workout.date >= date.fromisoformat(date_from))
        except ValueError: pass
    if date_to:
        try: q = q.filter(Workout.date <= date.fromisoformat(date_to))
        except ValueError: pass
    items = q.order_by(Workout.date.desc(), Workout.id.desc()).all()
    return jsonify([_to_dict(w) for w in items])

@main.route("/api/workouts", methods=["POST"])
@login_required
def create_workout():
    data = request.get_json(force=True, silent=True) or {}
    exercise = (data.get("exercise") or "").strip()
    if not exercise:
        return jsonify({"error": "exercise is required"}), 400
    raw_date = data.get("date")
    try: d = date.fromisoformat(raw_date) if raw_date else date.today()
    except Exception: d = date.today()
    w = Workout(
        user_id=current_user.id, date=d, exercise=exercise,
        sets=int(data.get("sets") or 0),
        reps=int(data.get("reps") or 0),
        weight=float(data.get("weight") or 0.0),
        notes=((data.get("notes") or "").strip() or None),
    )
    db.session.add(w); db.session.commit()
    return jsonify(_to_dict(w)), 201

@main.route("/api/workouts/<int:wid>", methods=["GET"])
@login_required
def get_workout(wid):
    w = Workout.query.get_or_404(wid)
    if w.user_id != current_user.id: abort(403)
    return jsonify(_to_dict(w))

@main.route("/api/workouts/<int:wid>", methods=["PATCH"])
@login_required
def update_workout(wid):
    w = Workout.query.get_or_404(wid)
    if w.user_id != current_user.id: abort(403)
    data = request.get_json(force=True, silent=True) or {}
    if data.get("date"):
        try: w.date = date.fromisoformat(data["date"])
        except Exception: pass
    if data.get("exercise"): w.exercise = data["exercise"].strip()
    if "sets" in data and data["sets"] is not None: w.sets = int(data["sets"])
    if "reps" in data and data["reps"] is not None: w.reps = int(data["reps"])
    if "weight" in data and data["weight"] is not None: w.weight = float(data["weight"])
    if "notes" in data: w.notes = (data["notes"] or "").strip() or None
    w.updated_at = datetime.utcnow(); db.session.commit()
    return jsonify(_to_dict(w))

@main.route("/api/workouts/<int:wid>", methods=["DELETE"])
@login_required
def delete_workout(wid):
    w = Workout.query.get_or_404(wid)
    if w.user_id != current_user.id: abort(403)
    db.session.delete(w); db.session.commit()
    return "", 204
