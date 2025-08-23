# Workout Tracker — Widget + CLI

A workout logger you can actually *use*... Add sets from a clean browser widget or from the terminal, store everything locally in SQLite, and visualize progress. :)

![Made with Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-3.0+-000?logo=flask) ![Matplotlib](https://img.shields.io/badge/Matplotlib-3.8+-11557c)

---

## ✨ Features
- **Two ways to use**: a **browser widget** (Flask) and a **CLI**.
- **Local-first**: data lives in `~/.workout_tracker.sqlite3` (no cloud required).
- **Simple data model**: each set = `date, exercise, weight, reps`.
- **Live chart**: filter by exercise and see your weight over time.
- **Zero fuss**: standard Python + 2 small deps (Flask, Matplotlib).

---

## 🚀 Quick Start (GitHub Codespaces)
```bash
cd additional_projects/workout_tracker
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=./src
```

### Run the Widget (UI)
```bash
python -m workout_tracker.widget_app
```
- Open the forwarded **port 7860** → the UI loads.
- Use the form to add sets; pick an exercise from the dropdown to see the chart.

### Use the CLI (optional)
```bash
# Log sets
python -m workout_tracker.cli add --date 2025-08-23 --exercise Bench --weight 135 --reps 8
python -m workout_tracker.cli add --date 2025-08-23 --exercise Bench --weight 145 --reps 6

# View & chart
python -m workout_tracker.cli list --exercise Bench --limit 10
python -m workout_tracker.cli plot --exercise Bench
```

> Tip: if you prefer `python -m workout_tracker ...`, add `src/workout_tracker/__main__.py` that calls `cli.main()`.

---

## 🧱 Project Structure
```
workout_tracker/
├─ README.md
├─ requirements.txt          # Flask + Matplotlib
└─ src/workout_tracker/
   ├─ __init__.py
   ├─ db.py                  # SQLite helpers (creates ~/.workout_tracker.sqlite3)
   ├─ cli.py                 # terminal add/list/plot
   ├─ widget_app.py          # Flask API + static site
   └─ static/
      └─ index.html          # widget UI (vanilla JS + Chart.js CDN)
```

---

## 📥 Data Model
Each set you log needs **four fields**:
- `date` — `YYYY-MM-DD`
- `exercise` — short, consistent name (e.g., `Bench`, `Squat`)
- `weight` — number (lbs or kg, just be consistent)
- `reps` — integer

Example (CLI):
```bash
python -m workout_tracker.cli add --date 2025-08-23 --exercise Squat --weight 185 --reps 5
```

---

## 🧰 Troubleshooting
- **ModuleNotFoundError (`workout_tracker`)**  
  Ensure you’re in the project folder and set:
  ```bash
  export PYTHONPATH=./src
  ```
  (or install once with an editable package if you prefer).

- **Plot not showing in Codespaces**  
  Use a headless backend:
  ```bash
  export MPLBACKEND=Agg
  python -m workout_tracker.cli plot --exercise Bench
  ```
  (We can add a “save chart to PNG” option if you want.)

- **Widget not loading**  
  Make sure port **7860** is forwarded and you ran `python -m workout_tracker.widget_app` in the same shell.

---

## 🗺️ Roadmap
- Save charts as PNG directly from the widget
- 1RM estimator & weekly volume stats
- CSV import/export
- Dark mode ✨

---

## 📄 License
MIT — use it, tweak it, ship it.
