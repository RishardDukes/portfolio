# run.py (repo root: /workspaces/portfolio)

import os
import sys
from pathlib import Path

# Ensure the workout_tracker package is importable when launching from repo root.
REPO_ROOT = Path(__file__).resolve().parent
WORKOUT_TRACKER_ROOT = REPO_ROOT / "workout_tracker"
if str(WORKOUT_TRACKER_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKOUT_TRACKER_ROOT))

from src.workout_tracker import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True,
    )
