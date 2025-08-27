# run.py (repo root: /workspaces/portfolio)

from additional_projects.workout_tracker.src.workout_tracker import create_app

app = create_app()

if __name__ == "__main__":
    import os
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
