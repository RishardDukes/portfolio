# additional_projects/workout_tracker/src/workout_tracker/widget_app.py
from flask import Flask, request, jsonify, send_from_directory
from workout_tracker.db import get_conn, insert_log

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
    with get_conn() as conn:
        if exercise:
            cur = conn.execute(
                "SELECT date, weight, reps FROM logs WHERE exercise=? ORDER BY date",
                (exercise,),
            )
            rows = cur.fetchall()
            rows = rows[-limit:] if limit else rows
            return jsonify([{"date": d, "weight": w, "reps": r} for d, w, r in rows])
        else:
            cur = conn.execute(
                "SELECT date, exercise, weight, reps FROM logs ORDER BY date"
            )
            rows = cur.fetchall()
            return jsonify(
                [{"date": d, "exercise": e, "weight": w, "reps": r} for d, e, w, r in rows]
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

if __name__ == "__main__":
    # Codespaces-friendly host/port
    app.run(host="0.0.0.0", port=7860, debug=True)
