# additional_projects/workout_tracker/src/workout_tracker/widget_app.py
from flask import Flask, request, jsonify, send_from_directory
from workout_tracker.db import get_conn, insert_log, fetch_logs_with_id, delete_log

app = Flask(__name__, static_folder="static", static_url_path="/static")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.get("/api/exercises")
def exercises():
    with get_conn() as conn:
        cur = conn.execute("SELECT DISTINCT exercise FROM logs ORDER BY exercise")
        return jsonify([r[0] for r in cur.fetchall()])

@app.get("/api/logs")
def logs():
    exercise = request.args.get("exercise")
    limit = int(request.args.get("limit", "50"))
    if exercise:
        rows = fetch_logs_with_id(exercise, limit)
        return jsonify([{"id": i, "date": d, "weight": w, "reps": r} for i, d, w, r in rows])
    else:
        with get_conn() as conn:
            cur = conn.execute(
                "SELECT id, date, exercise, weight, reps FROM logs ORDER BY date"
            )
            rows = cur.fetchall()
        return jsonify(
            [{"id": i, "date": d, "exercise": e, "weight": w, "reps": r} for i, d, e, w, r in rows]
        )

@app.post("/api/add")
def add():
    data = request.get_json(force=True)
    for k in ("date", "exercise", "weight", "reps"):
        if k not in data:
            return jsonify({"error": f"Missing field {k}"}), 400
    try:
        weight = float(data["weight"])
        reps = int(data["reps"])
    except ValueError:
        return jsonify({"error": "Invalid weight or reps"}), 400
    insert_log(data["date"], data["exercise"], weight, reps)
    return jsonify({"status": "ok"})

@app.post("/api/delete")
def delete():
    data = request.get_json(force=True)
    try:
        row_id = int(data["id"])
    except Exception:
        return jsonify({"error": "Missing or invalid id"}), 400
    delete_log(row_id)
    return jsonify({"status": "deleted", "id": row_id})


if __name__ == "__main__":
    # Codespaces-friendly host/port
    app.run(host="0.0.0.0", port=7860, debug=True)
