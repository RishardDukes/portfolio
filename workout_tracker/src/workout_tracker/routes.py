from datetime import datetime, date
import csv
import io
import json
from pathlib import Path
import time
import threading
import logging

logger = logging.getLogger(__name__)

# Hard timeout (seconds) for AI engine calls
_AI_TIMEOUT = 5.0

def _run_with_timeout(fn, timeout=_AI_TIMEOUT, default=None):
    """Run *fn* in a thread; return its result or *default* if it takes too long."""
    result = [default]
    exc    = [None]

    def _target():
        try:
            result[0] = fn()
        except Exception as e:      # noqa: BLE001
            exc[0] = e

    t = threading.Thread(target=_target, daemon=True)
    t0 = time.monotonic()
    t.start()
    t.join(timeout)
    elapsed = time.monotonic() - t0

    if t.is_alive():
        logger.error("Hercules AI timeout after %.1fs — returning default", timeout)
        return default, True        # (value, timed_out)
    if exc[0] is not None:
        logger.error("Hercules AI error (%.2fs): %s", elapsed, exc[0], exc_info=exc[0])
        return default, False
    logger.info("Hercules AI ok (%.2fs)", elapsed)
    return result[0], False
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, Response
from flask_login import login_required, current_user
from .db import db
from .models import (
    Workout,
    Program,
    ProgramDay,
    ProgramExercise,
    NutritionProfile,
    MealEntry,
    SavedMeal,
    BodyMetric,
    Goal,
)
from .hercules.engine import HerculesEngine, OnlineDataFetcher

main_bp = Blueprint("main", __name__)


ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


def _parse_iso_date(raw_date):
    if not raw_date:
        return date.today()
    try:
        return datetime.strptime(raw_date, "%Y-%m-%d").date()
    except ValueError:
        return None


def _serialize_profile(profile):
    return {
        "sex": profile.sex,
        "age": profile.age,
        "height_inches": profile.height_inches,
        "weight_lbs": profile.weight_lbs,
        "activity_level": profile.activity_level,
        "activity_multiplier": profile.activity_multiplier,
        "goal_type": profile.goal_type,
        "daily_calorie_adjustment": profile.daily_calorie_adjustment,
        "meals_per_day": profile.meals_per_day,
        "tdee": profile.tdee,
        "target_calories": profile.target_calories,
        "target_protein_g": profile.target_protein_g,
        "target_carbs_g": profile.target_carbs_g,
        "target_fats_g": profile.target_fats_g,
        "target_fiber_g": profile.target_fiber_g,
    }


def _serialize_meal(meal):
    return {
        "id": meal.id,
        "date": meal.date.isoformat(),
        "meal_name": meal.meal_name,
        "food_name": meal.food_name,
        "serving_size": meal.serving_size or "",
        "calories": meal.calories,
        "protein_g": meal.protein_g,
        "carbs_g": meal.carbs_g,
        "fats_g": meal.fats_g,
        "fiber_g": meal.fiber_g,
        "notes": meal.notes or "",
    }


def _serialize_saved_meal(saved_meal):
    return {
        "id": saved_meal.id,
        "name": saved_meal.name,
        "default_meal_name": saved_meal.default_meal_name,
        "food_name": saved_meal.food_name,
        "serving_size": saved_meal.serving_size or "",
        "calories": saved_meal.calories,
        "protein_g": saved_meal.protein_g,
        "carbs_g": saved_meal.carbs_g,
        "fats_g": saved_meal.fats_g,
        "fiber_g": saved_meal.fiber_g,
        "notes": saved_meal.notes or "",
    }


def _serialize_body_metric(metric):
    return {
        "id": metric.id,
        "date": metric.date.isoformat(),
        "weight_lbs": metric.weight_lbs,
        "body_fat_pct": metric.body_fat_pct,
        "waist_inches": metric.waist_inches,
        "notes": metric.notes or "",
    }


def _get_or_create_nutrition_profile():
    profile = NutritionProfile.query.filter_by(user_id=current_user.id).first()
    if profile:
        return profile

    defaults = HerculesEngine.calculate_nutrition_targets({
        "sex": "male",
        "age": 25,
        "height_inches": 70,
        "weight_lbs": 180,
        "activity_multiplier": ACTIVITY_MULTIPLIERS["moderate"],
        "goal_type": "maintain",
        "daily_calorie_adjustment": 0,
    })
    profile = NutritionProfile(
        user_id=current_user.id,
        sex="male",
        age=25,
        height_inches=70,
        weight_lbs=180,
        activity_level="moderate",
        activity_multiplier=ACTIVITY_MULTIPLIERS["moderate"],
        goal_type="maintain",
        daily_calorie_adjustment=0,
        meals_per_day=4,
        tdee=defaults["tdee"],
        target_calories=defaults["target_calories"],
        target_protein_g=defaults["target_protein_g"],
        target_carbs_g=defaults["target_carbs_g"],
        target_fats_g=defaults["target_fats_g"],
        target_fiber_g=defaults["target_fiber_g"],
    )
    db.session.add(profile)
    db.session.commit()
    return profile

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


@main_bp.route("/nutrition")
@login_required
def nutrition():
    return render_template("nutrition.html")

@main_bp.route("/metrics")
@login_required
def metrics():
    return render_template("metrics.html")

@main_bp.route("/goals")
@login_required
def goals_page():
    return render_template("goals.html")

@main_bp.route("/history")
@login_required
def history_page():
    return render_template("history.html")

@main_bp.route("/api/workouts/calendar", methods=["GET"])
@login_required
def workouts_calendar():
    """Return a dict of date -> list of entries for a given year/month."""
    from collections import defaultdict
    year  = request.args.get("year",  type=int)
    month = request.args.get("month", type=int)
    if not year or not month:
        return jsonify({"error": "year and month required"}), 400
    rows = (
        Workout.query
        .filter_by(user_id=current_user.id)
        .filter(db.extract("year",  Workout.date) == year)
        .filter(db.extract("month", Workout.date) == month)
        .order_by(Workout.date.asc(), Workout.id.asc())
        .all()
    )
    by_date = defaultdict(list)
    for w in rows:
        key = w.date.isoformat() if hasattr(w.date, "isoformat") else w.date
        by_date[key].append({
            "id":       w.id,
            "split":    w.split,
            "exercise": w.exercise,
            "sets":     w.sets,
            "reps":     w.reps,
            "weight":   w.weight,
            "notes":    w.notes or "",
        })
    return jsonify(dict(by_date))

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


@main_bp.route("/api/workouts/performance", methods=["GET"])
@login_required
def workout_performance_cards():
    rows = (
        Workout.query
        .filter_by(user_id=current_user.id)
        .order_by(Workout.date.asc(), Workout.id.asc())
        .all()
    )
    by_exercise = {}
    for workout in rows:
        by_exercise.setdefault(workout.exercise, []).append(workout)

    cards = []
    for exercise, exercise_rows in by_exercise.items():
        latest = exercise_rows[-1]
        previous = exercise_rows[-2] if len(exercise_rows) > 1 else None
        best_weight = max(float(row.weight or 0) for row in exercise_rows)
        best_e1rm = max(float(row.weight or 0) * (1 + (float(row.reps or 0) / 30.0)) for row in exercise_rows)
        recent_window = exercise_rows[-5:]
        first_recent = recent_window[0]
        last_recent = recent_window[-1]
        trend_weight_delta = round(float(last_recent.weight or 0) - float(first_recent.weight or 0), 1)

        cards.append({
            "exercise": exercise,
            "latest_weight": float(latest.weight or 0),
            "latest_reps": int(latest.reps or 0),
            "best_weight": round(best_weight, 1),
            "best_e1rm": round(best_e1rm, 1),
            "sessions": len(exercise_rows),
            "delta_from_previous": round(float(latest.weight or 0) - float(previous.weight or 0), 1) if previous else None,
            "trend_weight_delta": trend_weight_delta,
        })

    cards.sort(key=lambda item: (item["sessions"], item["latest_weight"]), reverse=True)
    return jsonify(cards[:6])

@main_bp.route("/api/hercules/coaching-tip", methods=["GET"])
@login_required
def get_coaching_tip():
    """Get up to three personalised coaching tips from Hercules AI."""
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    goals    = Goal.query.filter_by(user_id=current_user.id, achieved=False).all()
    engine   = HerculesEngine(current_user.id)
    engine.load_workouts(workouts)
    engine.load_goals(goals)
    tips, _ = _run_with_timeout(lambda: engine.generate_coaching_tips(3), default=[])
    return jsonify(tips or ["Keep pushing — great things take consistency."])


@main_bp.route("/api/hercules/weekly-summary", methods=["GET"])
@login_required
def get_weekly_summary():
    """Get a structured weekly training check-in."""
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    goals    = Goal.query.filter_by(user_id=current_user.id, achieved=False).all()
    engine   = HerculesEngine(current_user.id)
    engine.load_workouts(workouts)
    engine.load_goals(goals)
    summary, _ = _run_with_timeout(engine.generate_weekly_summary,
                                   default={"status": "unavailable", "message": "Summary temporarily unavailable."})
    return jsonify(summary)

@main_bp.route("/api/hercules/form-cue", methods=["POST"])
@login_required
def get_form_cue():
    """Get a form cue for a specific exercise."""
    data = request.get_json(force=True) or {}
    exercise = data.get("exercise", "")
    
    if not exercise:
        return jsonify({"error": "Exercise name required"}), 400
    
    engine = HerculesEngine(current_user.id)
    cue, _  = _run_with_timeout(lambda: engine.get_form_cue(exercise),
                                default="Focus on quality movement throughout the set.")
    return jsonify({"exercise": exercise, "form_cue": cue})

@main_bp.route("/api/hercules/summary", methods=["GET"])
@login_required
def get_training_summary():
    """Get comprehensive training statistics and insights."""
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    
    engine = HerculesEngine(current_user.id)
    engine.load_workouts(workouts)
    
    stats, _ = _run_with_timeout(engine.generate_summary_stats, default={})
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


@main_bp.route("/api/nutrition/profile", methods=["GET"])
@login_required
def get_nutrition_profile():
    profile = _get_or_create_nutrition_profile()
    return jsonify(_serialize_profile(profile))


@main_bp.route("/api/nutrition/profile", methods=["POST"])
@login_required
def save_nutrition_profile():
    profile = _get_or_create_nutrition_profile()
    data = request.get_json(force=True) or {}

    profile.sex = (data.get("sex") or profile.sex or "male").lower()
    profile.age = max(int(data.get("age") or profile.age or 25), 14)
    profile.height_inches = max(float(data.get("height_inches") or profile.height_inches or 70), 48)
    profile.weight_lbs = max(float(data.get("weight_lbs") or profile.weight_lbs or 180), 50)
    profile.activity_level = (data.get("activity_level") or profile.activity_level or "moderate").lower()
    profile.activity_multiplier = ACTIVITY_MULTIPLIERS.get(profile.activity_level, 1.55)
    profile.goal_type = (data.get("goal_type") or profile.goal_type or "maintain").lower()
    profile.daily_calorie_adjustment = int(data.get("daily_calorie_adjustment") or profile.daily_calorie_adjustment or 0)
    profile.meals_per_day = max(int(data.get("meals_per_day") or profile.meals_per_day or 4), 1)

    targets = HerculesEngine.calculate_nutrition_targets({
        "sex": profile.sex,
        "age": profile.age,
        "height_inches": profile.height_inches,
        "weight_lbs": profile.weight_lbs,
        "activity_multiplier": profile.activity_multiplier,
        "goal_type": profile.goal_type,
        "daily_calorie_adjustment": profile.daily_calorie_adjustment,
    })
    profile.tdee = targets["tdee"]
    profile.target_calories = int(targets["target_calories"])
    profile.target_protein_g = targets["target_protein_g"]
    profile.target_carbs_g = targets["target_carbs_g"]
    profile.target_fats_g = targets["target_fats_g"]
    profile.target_fiber_g = targets["target_fiber_g"]

    db.session.add(profile)
    db.session.commit()
    payload = _serialize_profile(profile)
    payload["bmr"] = targets["bmr"]
    return jsonify(payload)


@main_bp.route("/api/nutrition/meals", methods=["GET"])
@login_required
def list_meals():
    selected_date = _parse_iso_date(request.args.get("date"))
    if selected_date is None:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    rows = (
        MealEntry.query
        .filter_by(user_id=current_user.id, date=selected_date)
        .order_by(MealEntry.created_at.asc(), MealEntry.id.asc())
        .all()
    )
    return jsonify([_serialize_meal(row) for row in rows])


@main_bp.route("/api/nutrition/meals", methods=["POST"])
@login_required
def create_meal():
    data = request.get_json(force=True) or {}
    selected_date = _parse_iso_date(data.get("date"))
    if selected_date is None:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    food_name = (data.get("food_name") or "").strip()
    if not food_name:
        return jsonify({"error": "Food name required"}), 400

    meal = MealEntry(
        user_id=current_user.id,
        date=selected_date,
        meal_name=(data.get("meal_name") or "Breakfast").strip(),
        food_name=food_name,
        serving_size=(data.get("serving_size") or "").strip() or None,
        calories=float(data.get("calories") or 0),
        protein_g=float(data.get("protein_g") or 0),
        carbs_g=float(data.get("carbs_g") or 0),
        fats_g=float(data.get("fats_g") or 0),
        fiber_g=float(data.get("fiber_g") or 0),
        notes=(data.get("notes") or "").strip() or None,
    )
    db.session.add(meal)
    db.session.commit()
    return jsonify({"ok": True, "meal": _serialize_meal(meal)}), 201


@main_bp.route("/api/nutrition/meals/<int:meal_id>", methods=["DELETE"])
@login_required
def delete_meal(meal_id):
    meal = MealEntry.query.filter_by(id=meal_id, user_id=current_user.id).first()
    if not meal:
        return jsonify({"error": "not found"}), 404
    db.session.delete(meal)
    db.session.commit()
    return jsonify({"ok": True})


@main_bp.route("/api/nutrition/saved-meals", methods=["GET"])
@login_required
def list_saved_meals():
    rows = (
        SavedMeal.query
        .filter_by(user_id=current_user.id)
        .order_by(SavedMeal.created_at.desc(), SavedMeal.id.desc())
        .all()
    )
    return jsonify([_serialize_saved_meal(row) for row in rows])


@main_bp.route("/api/nutrition/saved-meals", methods=["POST"])
@login_required
def create_saved_meal():
    data = request.get_json(force=True) or {}
    food_name = (data.get("food_name") or "").strip()
    if not food_name:
        return jsonify({"error": "Food name required"}), 400

    name = (data.get("name") or food_name).strip()
    saved_meal = SavedMeal(
        user_id=current_user.id,
        name=name,
        default_meal_name=(data.get("default_meal_name") or data.get("meal_name") or "Meal").strip(),
        food_name=food_name,
        serving_size=(data.get("serving_size") or "").strip() or None,
        calories=float(data.get("calories") or 0),
        protein_g=float(data.get("protein_g") or 0),
        carbs_g=float(data.get("carbs_g") or 0),
        fats_g=float(data.get("fats_g") or 0),
        fiber_g=float(data.get("fiber_g") or 0),
        notes=(data.get("notes") or "").strip() or None,
    )
    db.session.add(saved_meal)
    db.session.commit()
    return jsonify({"ok": True, "saved_meal": _serialize_saved_meal(saved_meal)}), 201


@main_bp.route("/api/nutrition/saved-meals/<int:saved_meal_id>/log", methods=["POST"])
@login_required
def log_saved_meal(saved_meal_id):
    saved_meal = SavedMeal.query.filter_by(id=saved_meal_id, user_id=current_user.id).first()
    if not saved_meal:
        return jsonify({"error": "not found"}), 404

    data = request.get_json(force=True) or {}
    selected_date = _parse_iso_date(data.get("date"))
    if selected_date is None:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    meal = MealEntry(
        user_id=current_user.id,
        date=selected_date,
        meal_name=(data.get("meal_name") or saved_meal.default_meal_name or "Meal").strip(),
        food_name=saved_meal.food_name,
        serving_size=saved_meal.serving_size,
        calories=saved_meal.calories,
        protein_g=saved_meal.protein_g,
        carbs_g=saved_meal.carbs_g,
        fats_g=saved_meal.fats_g,
        fiber_g=saved_meal.fiber_g,
        notes=saved_meal.notes,
    )
    db.session.add(meal)
    db.session.commit()
    return jsonify({"ok": True, "meal": _serialize_meal(meal)}), 201


@main_bp.route("/api/nutrition/saved-meals/<int:saved_meal_id>", methods=["DELETE"])
@login_required
def delete_saved_meal(saved_meal_id):
    saved_meal = SavedMeal.query.filter_by(id=saved_meal_id, user_id=current_user.id).first()
    if not saved_meal:
        return jsonify({"error": "not found"}), 404
    db.session.delete(saved_meal)
    db.session.commit()
    return jsonify({"ok": True})


@main_bp.route("/api/nutrition/body-metrics", methods=["GET"])
@login_required
def list_body_metrics():
    rows = (
        BodyMetric.query
        .filter_by(user_id=current_user.id)
        .order_by(BodyMetric.date.desc(), BodyMetric.id.desc())
        .limit(60)
        .all()
    )
    return jsonify([_serialize_body_metric(row) for row in rows])


@main_bp.route("/api/nutrition/body-metrics", methods=["POST"])
@login_required
def create_body_metric():
    data = request.get_json(force=True) or {}
    selected_date = _parse_iso_date(data.get("date"))
    if selected_date is None:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    weight_lbs_raw = data.get("weight_lbs")
    if weight_lbs_raw in (None, ""):
        return jsonify({"error": "Weight is required"}), 400

    metric = BodyMetric(
        user_id=current_user.id,
        date=selected_date,
        weight_lbs=float(weight_lbs_raw),
        body_fat_pct=float(data.get("body_fat_pct")) if data.get("body_fat_pct") not in (None, "") else None,
        waist_inches=float(data.get("waist_inches")) if data.get("waist_inches") not in (None, "") else None,
        notes=(data.get("notes") or "").strip() or None,
    )
    db.session.add(metric)
    db.session.commit()
    return jsonify({"ok": True, "metric": _serialize_body_metric(metric)}), 201


@main_bp.route("/api/nutrition/body-metrics/<int:metric_id>", methods=["DELETE"])
@login_required
def delete_body_metric(metric_id):
    metric = BodyMetric.query.filter_by(id=metric_id, user_id=current_user.id).first()
    if not metric:
        return jsonify({"error": "not found"}), 404
    db.session.delete(metric)
    db.session.commit()
    return jsonify({"ok": True})


@main_bp.route("/api/nutrition/summary", methods=["GET"])
@login_required
def nutrition_summary():
    selected_date = _parse_iso_date(request.args.get("date"))
    if selected_date is None:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    profile = _get_or_create_nutrition_profile()
    meals = MealEntry.query.filter_by(user_id=current_user.id, date=selected_date).all()
    totals = HerculesEngine.summarize_meals(meals)
    targets = _serialize_profile(profile)
    balance = {
        "calories": round(profile.target_calories - totals["calories"], 1),
        "protein_g": round(profile.target_protein_g - totals["protein_g"], 1),
        "carbs_g": round(profile.target_carbs_g - totals["carbs_g"], 1),
        "fats_g": round(profile.target_fats_g - totals["fats_g"], 1),
        "fiber_g": round(profile.target_fiber_g - totals["fiber_g"], 1),
    }
    remaining = {
        "calories": round(max(balance["calories"], 0), 1),
        "protein_g": round(max(balance["protein_g"], 0), 1),
        "carbs_g": round(max(balance["carbs_g"], 0), 1),
        "fats_g": round(max(balance["fats_g"], 0), 1),
        "fiber_g": round(max(balance["fiber_g"], 0), 1),
    }
    return jsonify({
        "date": selected_date.isoformat(),
        "profile": targets,
        "totals": totals,
        "balance": balance,
        "remaining": remaining,
    })


@main_bp.route("/api/nutrition/food-search", methods=["GET"])
@login_required
def nutrition_food_search():
    query = (request.args.get("query") or "").strip()
    if not query:
        return jsonify([])
    foods = OnlineDataFetcher.fetch_food_options(query, max_results=6)
    return jsonify(foods)


@main_bp.route("/api/hercules/nutrition-tip", methods=["POST"])
@login_required
def get_nutrition_tip():
    data = request.get_json(force=True) or {}
    selected_date = _parse_iso_date(data.get("date"))
    if selected_date is None:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    meal_name = (data.get("meal_name") or "Next Meal").strip()

    profile = _get_or_create_nutrition_profile()
    meals = MealEntry.query.filter_by(user_id=current_user.id, date=selected_date).all()
    engine = HerculesEngine(current_user.id)
    tip = engine.generate_nutrition_tip(_serialize_profile(profile), meals, meal_name=meal_name)
    return jsonify(tip)


# ── Data Export ───────────────────────────────────────────────────────────────

@main_bp.route("/api/export/workouts.csv")
@login_required
def export_workouts_csv():
    """Download all workouts as a CSV file."""
    workouts = (
        Workout.query
        .filter_by(user_id=current_user.id)
        .order_by(Workout.date.desc(), Workout.id.desc())
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "date", "split", "exercise", "sets", "reps", "weight_lbs", "notes"])
    for w in workouts:
        writer.writerow([w.id, w.date.isoformat(), w.split, w.exercise,
                         w.sets, w.reps, w.weight, w.notes or ""])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=hercules_workouts.csv"},
    )


@main_bp.route("/api/export/workouts.json")
@login_required
def export_workouts_json():
    """Download all workouts as a JSON file."""
    workouts = (
        Workout.query
        .filter_by(user_id=current_user.id)
        .order_by(Workout.date.desc(), Workout.id.desc())
        .all()
    )
    data = [
        {
            "id": w.id,
            "date": w.date.isoformat(),
            "split": w.split,
            "exercise": w.exercise,
            "sets": w.sets,
            "reps": w.reps,
            "weight_lbs": w.weight,
            "notes": w.notes or "",
        }
        for w in workouts
    ]
    return Response(
        json.dumps({"exported_at": datetime.utcnow().isoformat(), "workouts": data}, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=hercules_workouts.json"},
    )


@main_bp.route("/api/export/metrics.csv")
@login_required
def export_metrics_csv():
    """Download all body metrics as a CSV file."""
    metrics = (
        BodyMetric.query
        .filter_by(user_id=current_user.id)
        .order_by(BodyMetric.date.desc(), BodyMetric.id.desc())
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "date", "weight_lbs", "body_fat_pct", "waist_inches", "notes"])
    for m in metrics:
        writer.writerow([
            m.id, m.date.isoformat(), m.weight_lbs,
            m.body_fat_pct if m.body_fat_pct is not None else "",
            m.waist_inches if m.waist_inches is not None else "",
            m.notes or "",
        ])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=hercules_metrics.csv"},
    )


@main_bp.route("/api/export/nutrition.csv")
@login_required
def export_nutrition_csv():
    """Download all meal entries as a CSV file."""
    meals = (
        MealEntry.query
        .filter_by(user_id=current_user.id)
        .order_by(MealEntry.date.desc(), MealEntry.id.desc())
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "date", "meal_name", "food_name", "serving_size",
                     "calories", "protein_g", "carbs_g", "fats_g", "fiber_g", "notes"])
    for m in meals:
        writer.writerow([
            m.id, m.date.isoformat(), m.meal_name, m.food_name,
            m.serving_size or "", m.calories, m.protein_g, m.carbs_g,
            m.fats_g, m.fiber_g, m.notes or "",
        ])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=hercules_nutrition.csv"},
    )


# ── Goals ─────────────────────────────────────────────────────────────────────

def _serialize_goal(g):
    return {
        "id": g.id,
        "goal_type": g.goal_type,
        "exercise": g.exercise or "",
        "target_weight": g.target_weight,
        "target_date": g.target_date.isoformat() if g.target_date else None,
        "note": g.note or "",
        "achieved": g.achieved,
        "created_at": g.created_at.isoformat(),
    }


@main_bp.route("/api/goals", methods=["GET"])
@login_required
def list_goals():
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.created_at.desc()).all()
    return jsonify([_serialize_goal(g) for g in goals])


@main_bp.route("/api/goals", methods=["POST"])
@login_required
def create_goal():
    data = request.get_json(force=True) or {}
    goal_type = (data.get("goal_type") or "lift").lower()
    if goal_type not in ("lift", "bodyweight"):
        return jsonify({"error": "goal_type must be 'lift' or 'bodyweight'"}), 400

    target = data.get("target_weight")
    if target is None:
        return jsonify({"error": "target_weight is required"}), 400

    exercise = (data.get("exercise") or "").strip() or None
    if goal_type == "lift" and not exercise:
        return jsonify({"error": "exercise is required for lift goals"}), 400

    raw_date = data.get("target_date")
    target_date = None
    if raw_date:
        target_date = _parse_iso_date(raw_date)
        if target_date is None:
            return jsonify({"error": "Invalid target_date format. Use YYYY-MM-DD."}), 400

    g = Goal(
        user_id=current_user.id,
        goal_type=goal_type,
        exercise=exercise,
        target_weight=float(target),
        target_date=target_date,
        note=(data.get("note") or "").strip() or None,
    )
    db.session.add(g)
    db.session.commit()
    return jsonify({"ok": True, "goal": _serialize_goal(g)}), 201


@main_bp.route("/api/goals/<int:gid>", methods=["PATCH"])
@login_required
def update_goal(gid):
    g = Goal.query.filter_by(id=gid, user_id=current_user.id).first()
    if not g:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(force=True) or {}
    if "achieved" in data:
        g.achieved = bool(data["achieved"])
    if "note" in data:
        g.note = (data["note"] or "").strip() or None
    if "target_date" in data:
        td = _parse_iso_date(data["target_date"])
        if td is None and data["target_date"]:
            return jsonify({"error": "Invalid target_date format"}), 400
        g.target_date = td
    if "target_weight" in data:
        g.target_weight = float(data["target_weight"])
    db.session.commit()
    return jsonify({"ok": True, "goal": _serialize_goal(g)})


@main_bp.route("/api/goals/<int:gid>", methods=["DELETE"])
@login_required
def delete_goal(gid):
    g = Goal.query.filter_by(id=gid, user_id=current_user.id).first()
    if not g:
        return jsonify({"error": "not found"}), 404
    db.session.delete(g)
    db.session.commit()
    return jsonify({"ok": True})

