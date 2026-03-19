# Workout Tracker

A polished Flask workout logger with authentication, a responsive dashboard, recent workout history, and **Hercules Coach** built directly into the main logging flow.

## What’s improved
- Hercules is now wired into the primary dashboard flow instead of only the legacy widget path.
- Dashboard has summary stats, a coach panel, and a more polished UI.
- Background music now has a mute toggle and remembers the mute state.
- Success sound can overlap correctly with background music.
- Database paths are more stable and stored in the app's `instance/` directory.
- Legacy widget utilities now run again instead of referencing missing helpers.

## Project structure
```text
workout_tracker/
├── README.md
├── requirements.txt
├── requirements2.txt
└── src/
    ├── instance/
    │   ├── app.db
    │   └── widget_logs.sqlite3
    └── workout_tracker/
        ├── __init__.py
        ├── auth.py
        ├── cli.py
        ├── db.py
        ├── makewidget.py
        ├── makewidgit.py
        ├── models.py
        ├── routes.py
        ├── run.py
        ├── widget_app.py
        ├── hercules/
        ├── static/
        └── templates/
```

## Run the main app
From the `workout_tracker/` folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m workout_tracker.run
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m workout_tracker.run
```

Then open `http://127.0.0.1:5000`.

## Run the legacy widget
```bash
PYTHONPATH=src python -m workout_tracker.widget_app
```

Or use:

```bash
python src/workout_tracker/makewidget.py
```

## Environment variables
Optional `.env`:

```env
SECRET_KEY=replace-me
DATABASE_URL=sqlite:///custom.db
FLASK_DEBUG=true
```

If `DATABASE_URL` is omitted, the app uses `src/instance/app.db`.

## Hercules Coach behavior
Hercules returns a recommendation after each logged workout:
- **Increase** weight when you hit the top of the rep range with enough control
- **Keep** weight and push reps when you’re still in range
- **Decrease** weight when you miss the rep floor near failure

## Next good upgrades
- Per-exercise charts on `/tracker`
- Edit existing workout entries
- Tags like Push / Pull / Legs
- Personal records page
- Hosted deployment with Postgres
