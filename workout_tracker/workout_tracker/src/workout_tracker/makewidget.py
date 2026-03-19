#!/usr/bin/env python3
from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
ROOT = PKG_DIR.parents[1]
VENV = ROOT / ".venv"
REQ = ROOT / "requirements.txt"
if not REQ.exists():
    REQ = ROOT / "requirements2.txt"
SRC = ROOT / "src"


def run(cmd, **kwargs):
    print("$", " ".join(map(str, cmd)))
    subprocess.check_call(cmd, **kwargs)


def ensure_venv() -> str:
    if not VENV.exists():
        run([sys.executable, "-m", "venv", str(VENV)])
    return str(VENV / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python"))


def install_reqs(py: str) -> None:
    if REQ.exists():
        run([py, "-m", "pip", "install", "-U", "pip"])
        run([py, "-m", "pip", "install", "-r", str(REQ)])


def main() -> None:
    py = ensure_venv()
    install_reqs(py)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)

    print("\nLaunching Workout Tracker widget on http://localhost:7860 ...")
    print("In Codespaces, open the forwarded port 7860.")
    run([py, "-m", "workout_tracker.widget_app"], cwd=str(ROOT), env=env)


if __name__ == "__main__":
    main()
