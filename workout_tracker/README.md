# WIP — Workout Intelligence Platform

A workout tracking web app built with Flask, SQLAlchemy, and vanilla JS. It brings together structured logging, flexible training plans, lightweight analytics, and Hercules AI coaching in one focused interface.

## Features

- User registration and login
- Log workouts by split (Push / Pull / Legs) with sets, reps, weight (lbs), and notes
- Build reusable training programs with custom day labels and planned exercises
- Load any saved program day into the tracker as a quick-fill starting point
- Analytics dashboard with volume trends and top exercises
- Hercules AI coaching tips with reasoning and research links
- PubMed Central integration for science-backed coaching context
- Persistent background music with a track picker and UI sound effects
- Seamless SPA-style navigation between Dashboard and Tracker

## Stack

- **Backend:** Python, Flask, Flask-Login, Flask-SQLAlchemy
- **Database:** SQLite (dev) — swappable via `DATABASE_URL` env var
- **Frontend:** Vanilla JS, CSS (no frameworks)

## Main Workflow

1. Create an account and log in.
2. Open `Programs` to define a training structure such as `Push Pull Legs`, `Upper / Lower`, or any custom split.
3. Add days like `Push A`, `Upper Heavy`, or `Full Body`, then add planned exercises with target sets and reps.
4. Open `Tracker` and optionally use `Load from plan` to pre-fill a session.
5. Adjust anything freely, log the workout, and review progress from the dashboard and session history.

The key design choice is flexibility: plans act as optional shortcuts, not hard schedules. Users can skip a planned day, change exercises on the fly, or log something completely new without breaking the flow.

## Hercules AI

Hercules is the app's coaching layer. It analyzes recent workout data and returns suggestions intended to be practical, lightweight, and grounded in the user's actual training patterns.

Current capabilities:

- Reviews workout history, volume, and consistency patterns
- Generates coaching tips with category and rationale
- Surfaces source information and clickable research URLs when available
- Uses PubMed Central data to strengthen the scientific context behind suggestions

See `HERCULES_AI_IMPLEMENTATION.md` for deeper implementation notes.

## Music and UI

- Background music persists across navigation
- Users can choose tracks directly from the top navigation bar
- UI interactions include lightweight audio feedback and SPA-style page transitions

## Why It Stands Out

- Balances structure and flexibility instead of forcing rigid workout schedules
- Connects training logs, planning, and coaching in the same workflow
- Uses research-backed context without turning the product into a cluttered data dump
- Feels closer to a real product than a classroom demo

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

## Development Notes

- The app auto-creates the SQLite schema on startup.
- If you change the schema during local development, reset the database with `rm app.db` and restart the app.
- Program data is stored in three related tables: `program`, `program_day`, and `program_exercise`.

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
