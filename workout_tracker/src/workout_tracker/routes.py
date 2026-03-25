from datetime import datetime
from pathlib import Path
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from flask_login import login_required, current_user
from .db import db
from .models import Workout, Program, ProgramDay, ProgramExercise
from .hercules.engine import HerculesEngine

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
        Workout.query
        .filter_by(user_id=current_user.id)
        .order_by(Workout.date.desc(), Workout.id.desc())
        .all()
    )
    return jsonify([
        {
            "id": w.id,
            "date": w.date.isoformat() if hasattr(w.date, "isoformat") else w.date,
            "split": w.split,
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
    raw_date = data.get("date")
    parsed_date = None
    if raw_date:
        try:
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    w = Workout(
        user_id=current_user.id,
        date=parsed_date,
        split=(data.get("daytype") or "Push").strip(),
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

@main_bp.route("/api/hercules/coaching-tip", methods=["GET"])
@login_required
def get_coaching_tip():
    """Get a personalized coaching tip from Hercules AI."""
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    
    engine = HerculesEngine(current_user.id)
    engine.load_workouts(workouts)
    
    tip = engine.generate_coaching_tip()
    return jsonify(tip)

@main_bp.route("/api/hercules/form-cue", methods=["POST"])
@login_required
def get_form_cue():
    """Get a form cue for a specific exercise."""
    data = request.get_json(force=True) or {}
    exercise = data.get("exercise", "")
    
    if not exercise:
        return jsonify({"error": "Exercise name required"}), 400
    
    engine = HerculesEngine(current_user.id)
    cue = engine.get_form_cue(exercise)
    
    return jsonify({"exercise": exercise, "form_cue": cue})

@main_bp.route("/api/hercules/summary", methods=["GET"])
@login_required
def get_training_summary():
    """Get comprehensive training statistics and insights."""
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    
    engine = HerculesEngine(current_user.id)
    engine.load_workouts(workouts)
    
    stats = engine.generate_summary_stats()
    return jsonify(stats)


@main_bp.route("/api/music/tracks", methods=["GET"])
@login_required
def list_music_tracks():
    """Return playable audio files from the static sounds directory."""
    sounds_dir = Path(current_app.static_folder) / "sounds"
    if not sounds_dir.exists() or not sounds_dir.is_dir():
        return jsonify([])

    allowed_suffixes = {".mp3", ".wav", ".ogg", ".m4a"}
    tracks = [
        item.name
        for item in sounds_dir.iterdir()
        if item.is_file() and item.suffix.lower() in allowed_suffixes
    ]
    tracks.sort(key=str.lower)
    return jsonify(tracks)


@main_bp.route("/programs")
@login_required
def programs():
    return render_template("program.html")


@main_bp.route("/api/programs", methods=["GET"])
@login_required
def list_programs():
    progs = Program.query.filter_by(user_id=current_user.id).order_by(Program.created_at).all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "days": [
                {
                    "id": d.id,
                    "label": d.label,
                    "order": d.order,
                    "exercises": [
                        {
                            "id": e.id,
                            "exercise_name": e.exercise_name,
                            "target_sets": e.target_sets,
                            "target_reps": e.target_reps,
                            "order": e.order,
                        }
                        for e in d.exercises
                    ],
                }
                for d in p.days
            ],
        }
        for p in progs
    ])


@main_bp.route("/api/programs", methods=["POST"])
@login_required
def create_program():
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Program name required"}), 400
    p = Program(user_id=current_user.id, name=name)
    db.session.add(p)
    db.session.commit()
    return jsonify({"ok": True, "id": p.id, "name": p.name}), 201


@main_bp.route("/api/programs/<int:pid>", methods=["DELETE"])
@login_required
def delete_program(pid):
    p = Program.query.filter_by(id=pid, user_id=current_user.id).first()
    if not p:
        return jsonify({"error": "not found"}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({"ok": True})


@main_bp.route("/api/programs/<int:pid>/days", methods=["POST"])
@login_required
def add_program_day(pid):
    p = Program.query.filter_by(id=pid, user_id=current_user.id).first()
    if not p:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(force=True) or {}
    label = (data.get("label") or "").strip()
    if not label:
        return jsonify({"error": "Day label required"}), 400
    d = ProgramDay(program_id=pid, label=label, order=len(p.days))
    db.session.add(d)
    db.session.commit()
    return jsonify({"ok": True, "id": d.id, "label": d.label, "exercises": []}), 201


@main_bp.route("/api/programs/days/<int:did>", methods=["DELETE"])
@login_required
def delete_program_day(did):
    d = ProgramDay.query.join(Program).filter(
        ProgramDay.id == did,
        Program.user_id == current_user.id,
    ).first()
    if not d:
        return jsonify({"error": "not found"}), 404
    db.session.delete(d)
    db.session.commit()
    return jsonify({"ok": True})


@main_bp.route("/api/programs/days/<int:did>/exercises", methods=["POST"])
@login_required
def add_program_exercise(did):
    d = ProgramDay.query.join(Program).filter(
        ProgramDay.id == did,
        Program.user_id == current_user.id,
    ).first()
    if not d:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(force=True) or {}
    name = (data.get("exercise_name") or "").strip()
    if not name:
        return jsonify({"error": "Exercise name required"}), 400
    e = ProgramExercise(
        day_id=did,
        exercise_name=name,
        target_sets=int(data.get("target_sets") or 3),
        target_reps=int(data.get("target_reps") or 10),
        order=len(d.exercises),
    )
    db.session.add(e)
    db.session.commit()
    return jsonify({
        "ok": True, "id": e.id, "exercise_name": e.exercise_name,
        "target_sets": e.target_sets, "target_reps": e.target_reps,
    }), 201


@main_bp.route("/api/programs/exercises/<int:eid>", methods=["DELETE"])
@login_required
def delete_program_exercise(eid):
    e = ProgramExercise.query.join(ProgramDay).join(Program).filter(
        ProgramExercise.id == eid,
        Program.user_id == current_user.id,
    ).first()
    if not e:
        return jsonify({"error": "not found"}), 404
    db.session.delete(e)
    db.session.commit()
    return jsonify({"ok": True})
