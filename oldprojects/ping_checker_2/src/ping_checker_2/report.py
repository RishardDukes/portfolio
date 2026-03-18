import argparse
from collections import defaultdict
from string import Template
from .storage import get_history

HTML_TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8"><title>Ping Checker Report</title>
<style>body{font-family:system-ui,Arial;margin:24px} table{border-collapse:collapse} td,th{border:1px solid #ccc;padding:6px 10px}</style>
</head><body>
<h1>Ping Checker Report</h1>
<p>Generated from local SQLite history.</p>
<table>
<tr><th>Host</th><th>Uptime %</th><th>Checks</th><th>Avg Latency (ms)</th></tr>
$rows
</table>
</body></html>"""

def compute_stats():
    data = get_history()
    stats = defaultdict(lambda: {"ok": 0, "total": 0, "lat_sum": 0.0, "lat_n": 0})
    for ts, host, ok, lat in data:
        s = stats[host]
        s["total"] += 1
        if ok:
            s["ok"] += 1
            if lat is not None:
                s["lat_sum"] += lat
                s["lat_n"] += 1
    rows = []
    for host, s in stats.items():
        uptime = (s["ok"] / s["total"]) * 100 if s["total"] else 0
        avg = (s["lat_sum"] / s["lat_n"]) if s["lat_n"] else 0
        rows.append((host, uptime, s["total"], avg))
    return sorted(rows)

def to_html(rows):
    tr = "\n".join(
        f"<tr><td>{h}</td><td>{uptime:.1f}</td><td>{n}</td><td>{avg:.1f}</td></tr>"
        for h, uptime, n, avg in rows
    )
    return Template(HTML_TEMPLATE).substitute(rows=tr)

def main():
    p = argparse.ArgumentParser(prog="ping_checker_2.report")
    p.add_argument("--out", default="report.html")
    a = p.parse_args()
    html = to_html(compute_stats())
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {a.out}")

if __name__ == "__main__":
    main()
