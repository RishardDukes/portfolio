# Workout Tracker — Flask Web App

**Projects you can ACTUALLY use...** A lightweight workout logger with **user accounts**, a clean web interface, and persistent storage in SQLite. Log your sets, view your history, and manage progress all in one place.

![Made with Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-3.0+-000?logo=flask) ![SQLite](https://img.shields.io/badge/SQLite-3-07405e?logo=sqlite&logoColor=white)

---

## ✨ Features
- **User accounts & login system** (via Flask-Login)
- **Workout logging**: exercise, sets, reps, weight, notes
- **Dashboard view**: add sets and view history (with number inputs + sliders)
- **JSON API**: `/api/workouts` (list, create, update, delete workouts)
- **Dark themed UI** with subtle fitness-themed background
- **SQLite-backed** — data persists locally

---

## 🚀 Quick Start (GitHub Codespaces or local)
```bash
# from repo root
cd additional_projects/workout_tracker
python -m venv .venv && source .venv/bin/activate
pip install -r requirements2.txt
```

Create a `.env` file at the repo root:
```
SECRET_KEY=dev-secret
DATABASE_URL=sqlite:///app.db
```

Run the app (from `portfolio/` repo root):
```bash
python run.py
```

Open the forwarded **port 5000** → the UI loads.

---

## 🖥️ Usage
- **Register** → create an account at `/register`
- **Login** → access your dashboard at `/login`
- **Dashboard** → log workouts (type or use sliders), view recent history
- **API** →  
  - `GET /api/workouts` → list workouts  
  - `POST /api/workouts` → create workout  
  - `PATCH /api/workouts/<id>` → update workout  
  - `DELETE /api/workouts/<id>` → delete workout  

---

## 🧱 Project Structure
```
portfolio/
├─ run.py                          # entrypoint
└─ additional_projects/workout_tracker/
   ├─ requirements.txt
   └─ src/workout_tracker/
      ├─ __init__.py               # Flask app factory
      ├─ db.py                     # SQLAlchemy setup
      ├─ models.py                 # User + Workout models
      ├─ auth.py                   # login/register/logout
      ├─ routes.py                 # dashboard, API endpoints
      ├─ templates/
      │   ├─ base.html             # dark theme, nav, bg emojis
      │   ├─ login.html
      │   ├─ register.html
      │   ├─ dashboard.html        # number + slider inputs
      │   └─ tracker.html
      └─ static/
          └─ app.js                # form submit + API + slider sync
```

---

## 📥 Data Model
### `User`
- `id` (int, PK)
- `email`
- `password_hash`
- `display_name`
- `created_at`

### `Workout`
- `id` (int, PK)
- `user_id` (FK → User)
- `date`
- `exercise`
- `sets`
- `reps`
- `weight`
- `notes`
- `created_at` / `updated_at`

---

## 🧰 Troubleshooting
- **Module not found (`workout_tracker`)**  
  Make sure you’re running from repo root (`portfolio/`) with:
  ```bash
  python run.py
  ```

- **Database errors**  
  Delete `app.db` and let the app recreate it:
  ```bash
  rm app.db
  python run.py
  ```

- **Templates not loading**  
  Ensure `templates/` is inside `src/workout_tracker/`.

---

## 🗺️ Roadmap
- Progress charts (per-exercise over time)
- Export/import workouts (CSV/Excel)
- Exercise categories (Push/Pull/Legs, etc.)
- Personal record (PR) tracking
- Dark mode toggle

---

## 📄 License
MIT — free to use, modify, and share.

