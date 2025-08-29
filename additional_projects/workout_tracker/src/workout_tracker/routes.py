from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .db import db
from .models import Workout

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    # Redirect signed-in users to dashboard; guests go to login
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))

@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@main_bp.route("/tracker")
@login_required
def tracker():
    # If you don't have tracker.html yet, you can reuse dashboard.html
    return render_template("tracker.html")

# -------- API: newest first --------
@main_bp.route("/api/workouts", methods=["GET"])
@login_required
def list_workouts():
    rows = (
        Workout.query
        .filter_by(user_id=current_user.id)
        .order_by(Workout.date.desc(), Workout.id.desc())
        .all()
    )
    return jsonify([
        {
            "id": w.id,
            "date": w.date.isoformat() if hasattr(w.date, "isoformat") else w.date,
            "exercise": w.exercise,
            "sets": w.sets,
            "reps": w.reps,
            "weight": w.weight,
            "notes": w.notes or "",
        }
        for w in rows
    ])

@main_bp.route("/api/workouts", methods=["POST"])
@login_required
def create_workout():
    data = request.get_json(force=True) or {}
    w = Workout(
        user_id=current_user.id,
        date=data.get("date"),
        exercise=(data.get("exercise") or "").strip(),
        sets=int(data.get("sets") or 0),
        reps=int(data.get("reps") or 0),
        weight=float(data.get("weight") or 0),
        notes=(data.get("notes") or "").strip() or None,
    )
    db.session.add(w)
    db.session.commit()
    return jsonify({"ok": True, "id": w.id}), 201

@main_bp.route("/api/workouts/<int:wid>", methods=["DELETE"])
@login_required
def delete_workout(wid):
    w = Workout.query.filter_by(id=wid, user_id=current_user.id).first()
    if not w:
        return jsonify({"error": "not found"}), 404
    db.session.delete(w)
    db.session.commit()
    return jsonify({"ok": True})

# Back-compat alias if something imports `main`
main = main_bp
