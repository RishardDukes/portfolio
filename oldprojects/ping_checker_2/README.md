# Ping Checker 2.0 — Async uptime & HTML report (stdlib-only)

A tiny uptime monitor you can actually use... It checks hosts asynchronously, logs results to SQLite, and builds a clean static **HTML report**.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white) ![Stdlib Only](https://img.shields.io/badge/Deps-Stdlib%20Only-2ea44f)

---

## ✨ Features
- **No external packages** — just `asyncio`, `sqlite3`, `argparse`, `pathlib`.
- **Async checks** via TCP connect (port 80 by default).
- **SQLite history** at `~/.ping_checker.sqlite3`.
- **HTML report** with uptime %, total checks, and avg latency.
- **Codespaces-friendly**.

---

## 🚀 Quick Start (GitHub Codespaces)
```bash
cd additional_projects/ping_checker_2
python -m venv .venv && source .venv/bin/activate
export PYTHONPATH=./src    # because this uses a src/ layout

# collect some data
python -m ping_checker_2.monitor --hosts google.com 1.1.1.1 --interval 2 --cycles 10

# build the static report
python -m ping_checker_2.report --out report.html

# (view) serve the folder and open the forwarded port
python -m http.server 8000   # then visit /report.html
```
*(Or right‑click `report.html` → **Open with Live Preview** in Codespaces.)*

---

## 🧱 Project Structure
```
ping_checker_2/
├─ README.md
├─ requirements.txt          # empty on purpose (stdlib only)
└─ src/ping_checker_2/
   ├─ __init__.py
   ├─ monitor.py             # async TCP checks
   ├─ report.py              # builds HTML from DB
   └─ storage.py             # SQLite helpers & schema
```

---

## 🛠️ Usage
**Monitor multiple hosts:**
```bash
python -m ping_checker_2.monitor --hosts google.com 1.1.1.1 github.com --interval 5 --cycles 60
```
- `--hosts` space‑separated list of domains/IPs  
- `--interval` seconds between checks  
- `--cycles` number of loops (omit to run indefinitely)

**Generate report:**
```bash
python -m ping_checker_2.report --out report.html
```

**Stop the monitor:** `Ctrl + C` (or `pkill -f "python -m ping_checker_2.monitor"`).

---

## 🧰 Troubleshooting
- **ModuleNotFoundError (`ping_checker_2`)**  
  This project uses a `src/` layout. Either set `PYTHONPATH=./src` (as above) **or** install once:

  ```bash
  # optional: make it permanent
  cat > pyproject.toml << 'EOF'
  [build-system]
  requires = ["setuptools>=61.0"]
  build-backend = "setuptools.build_meta"

  [project]
  name = "ping_checker_2"
  version = "0.1.0"
  requires-python = ">=3.9"

  [tool.setuptools]
  package-dir = {"" = "src"}
  packages = ["ping_checker_2"]
  EOF

  pip install -e .
  ```

- **KeyError: 'font-family' when generating HTML**  
  Fixed by switching to `string.Template` in `report.py` so CSS braces don’t confuse `str.format`.

- **Can’t see report**  
  Serve locally: `python -m http.server 8000` → open the forwarded port → go to `/report.html`.

---

## 🗺️ Roadmap
- Config file (hosts, interval)  
- Pretty console output (`rich`)  
- Downtime alerts (Slack/email)  
- Latency charts in the HTML

---

## 📄 License
MIT

