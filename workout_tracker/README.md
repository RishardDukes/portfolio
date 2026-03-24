# WIP — Workout Intelligence Platform

A futuristic workout tracking web app built with Flask, SQLAlchemy, and vanilla JS.

## Features

- User registration and login
- Log workouts by split (Push / Pull / Legs) with sets, reps, weight (lbs), and notes
- Analytics dashboard with volume trends and top exercises
- Hercules AI coaching tips
- Persistent background music with futuristic UI sound effects
- Seamless SPA-style navigation between Dashboard and Tracker

## Stack

- **Backend:** Python, Flask, Flask-Login, Flask-SQLAlchemy
- **Database:** SQLite (dev) — swappable via `DATABASE_URL` env var
- **Frontend:** Vanilla JS, CSS (no frameworks)

## Getting Started

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python run.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Configuration

Set these environment variables to override defaults:

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | `dev-secret` | Flask session signing key — **change this in production** |
| `DATABASE_URL` | `sqlite:///app.db` | Database connection string |

```bash
# Example .env (never commit this file)
SECRET_KEY=your-strong-random-key
DATABASE_URL=sqlite:///app.db
```
