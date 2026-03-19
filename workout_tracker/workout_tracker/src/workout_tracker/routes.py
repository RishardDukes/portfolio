from __future__ import annotations

from datetime import date, datetime

from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from .db import db
from .hercules.engine import ExerciseTarget, HerculesCoach
from .models import Workout

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
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
    return render_template("tracker.html")


@main_bp.route("/api/workouts", methods=["GET"])
@login_required
def list_workouts():
    rows = (
        Workout.query.filter_by(user_id=current_user.id)
        .order_by(Workout.date.desc(), Workout.id.desc())
        .all()
    )
    return jsonify(
        [
            {
                "id": w.id,
                "date": w.date.isoformat(),
                "exercise": w.exercise,
                "sets": w.sets,
                "reps": w.reps,
                "weight": w.weight,
                "notes": w.notes or "",
                "volume": w.volume,
            }
            for w in rows
        ]
    )


@main_bp.route("/api/workouts/summary", methods=["GET"])
@login_required
def workout_summary():
    rows = Workout.query.filter_by(user_id=current_user.id).all()
    total_workouts = len(rows)
    total_volume = int(sum(w.volume for w in rows))
    unique_exercises = len({w.exercise.lower() for w in rows if w.exercise})
    recent_pr = max((w.weight for w in rows), default=0)

    return jsonify(
        {
            "total_workouts": total_workouts,
            "total_volume": total_volume,
            "unique_exercises": unique_exercises,
            "recent_pr": recent_pr,
        }
    )


@main_bp.route("/api/workouts", methods=["POST"])
@login_required
def create_workout():
    data = request.get_json(force=True) or {}

    from datetime import datetime
    raw_date = data.get("date")
    parsed_date = None

    if raw_date:
        try:
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

    exercise = (data.get("exercise") or "").strip()
    sets = int(data.get("sets") or 0)
    reps = int(data.get("reps") or 0)
    weight = float(data.get("weight") or 0)
    notes = (data.get("notes") or "").strip() or None

    from .models import Workout
    from .db import db

    w = Workout(
        user_id=current_user.id,
        date=parsed_date,
        exercise=exercise,
        sets=sets,
        reps=reps,
        weight=weight,
        notes=notes,
    )

    db.session.add(w)
    db.session.commit()

    # 🔥 HERCULES INTEGRATION
    from .hercules.engine import HerculesCoach, ExerciseTarget

    coach = HerculesCoach()
    target = ExerciseTarget(
        rep_min=8,
        rep_max=12,
        is_compound=True,
        is_machine=True
    )

    rec = coach.recommend_next_action(
        weight=weight,
        reps=reps,
        rir=None,
        target=target
    )

    return jsonify({
        "ok": True,
        "id": w.id,
        "hercules": rec["message"],
        "status": rec["status"],
        "next_weight": rec["next_weight"],
        "next_rep_goal": rec["next_rep_goal"]
    }), 201


@main_bp.route("/api/workouts/<int:wid>", methods=["DELETE"])
@login_required
def delete_workout(wid: int):
    workout = Workout.query.filter_by(id=wid, user_id=current_user.id).first()
    if not workout:
        return jsonify({"error": "Workout not found."}), 404

    db.session.delete(workout)
    db.session.commit()
    return jsonify({"ok": True})


main = main_bp
