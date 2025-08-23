# Ping Checker 2.0

# 1) go to the project
cd /workspaces/portfolio/additional_projects/ping_checker_2

# 2) (optional) create a venv
python -m venv .venv
source .venv/bin/activate

# 3) point Python at src/ (because this is a src/ layout)
export PYTHONPATH=./src

# 4) collect some data (Google + Cloudflare)
python -m ping_checker_2.monitor --hosts google.com 1.1.1.1 --interval 2 --cycles 10

# 5) build the HTML report
python -m ping_checker_2.report --out report.html

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Async host checks with historical logging (SQLite) and a static HTML report.  
**No external deps** — stdlib only (`asyncio`, `sqlite3`, `argparse`, `pathlib`).

## Project Structure
```
ping_checker_2/
├─ README.md
├─ requirements.txt   # empty on purpose
└─ src/ping_checker_2/
   ├─ __init__.py
   ├─ monitor.py      # async TCP checks (port 80)
   ├─ report.py       # builds HTML report
   └─ storage.py      # SQLite helpers
```

## Quick Start (Codespaces)
```bash
cd additional_projects/ping_checker_2
python -m venv .venv && source .venv/bin/activate
export PYTHONPATH=./src
python -m ping_checker_2.monitor --hosts google.com 1.1.1.1 --interval 2 --cycles 10
python -m ping_checker_2.report --out report.html
```

**View the report**
```bash
python -m http.server 8000   # then open the forwarded port and go to /report.html
```
_(Or right-click `report.html` → Open with Live Preview.)_

## Usage
```bash
# monitor multiple hosts
python -m ping_checker_2.monitor --hosts google.com 1.1.1.1 github.com --interval 5 --cycles 60

# build HTML from history
python -m ping_checker_2.report --out report.html
```
Data is stored at `~/.ping_checker.sqlite3`.

## Common Issues & Fixes
- **ModuleNotFoundError (`ping_checker_2`)**  
  Set `PYTHONPATH=./src` (as above) _or_ install once:
  ```bash
  # optional: install package to avoid PYTHONPATH
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
  Fixed by using `string.Template` in `report.py` (no action needed if you’re on this repo).
