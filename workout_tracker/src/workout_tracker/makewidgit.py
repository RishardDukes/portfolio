#!/usr/bin/env python3
"""
makewidgit.py — one-shot runner for the Workout Tracker widget.
Run with: python src/workout_tracker/makewidgit.py
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent          # src/workout_tracker
ROOT = PKG_DIR.parents[1]                          # workout_tracker/
VENV = ROOT / ".venv"
REQ = ROOT / "requirements2.txt"                   
SRC = ROOT / "src"

def run(cmd, **kwargs):
    print("$", " ".join(cmd))
    subprocess.check_call(cmd, **kwargs)

def ensure_venv():
    if not VENV.exists():
        run([sys.executable, "-m", "venv", str(VENV)])
    py = VENV / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")
    return str(py)

def install_reqs(py):
    if REQ.exists():
        run([py, "-m", "pip", "install", "-U", "pip"])
        run([py, "-m", "pip", "install", "-r", str(REQ)])
    else:
        print(f"{REQ.name} not found; continuing...")

def main():
    py = ensure_venv()
    install_reqs(py)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)

    print("\nLaunching Workout Tracker widget on http://localhost:7860 ...")
    print("In Codespaces, open the forwarded port 7860.")

    run([py, "-m", "workout_tracker.widget_app"], cwd=str(ROOT), env=env)

if __name__ == "__main__":
    main()