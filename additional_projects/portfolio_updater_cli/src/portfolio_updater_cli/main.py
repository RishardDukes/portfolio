import argparse, datetime
from pathlib import Path

README_TEMPLATE = "# {name}\n\n{desc}\n"
LICENSE_MIT = "MIT License\n\nCopyright (c) {year} {author}\n"
GITIGNORE = "__pycache__/\n*.py[cod]\n.venv/\n.env\n*.egg-info/\n*.log\n"
CI_YML = "name: Python CI\n"

def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")

def init_project(args):
    root = Path(args.name)
    root.mkdir(exist_ok=True)
    write(root / "README.md", README_TEMPLATE.format(name=args.name, desc=args.desc))
    write(root / "LICENSE", LICENSE_MIT.format(year=datetime.datetime.now().year, author=args.author))
    write(root / ".gitignore", GITIGNORE)
    write(root / "requirements.txt", "")
    if args.ci:
        write(root / ".github/workflows/ci.yml", CI_YML)
    pkg = root / "src" / args.name.replace('-', '_')
    write(pkg / "__init__.py", "")
    print(f"Initialized project at {root.resolve()}")

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init")
    i.add_argument("name")
    i.add_argument("--desc", default="Project description.")
    i.add_argument("--author", default="Your Name")
    i.add_argument("--ci", action="store_true")
    i.set_defaults(func=init_project)
    a = p.parse_args()
    a.func(a)

if __name__ == "__main__":
    main()
