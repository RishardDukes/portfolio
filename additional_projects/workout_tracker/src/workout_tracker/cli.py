# workout_tracker/cli.py
import argparse
from .db import insert_log, fetch_logs
from .charts import plot_progress
from workout_tracker.hercules.engine import HerculesCoach, ExerciseTarget

def suggest_next_weight(rows):
    if not rows:
        return "Hercules: No history yet. Start at a comfortable weight and log your sets."

    # rows: (date, weight, reps)
    d, w, r = rows[-1]

    coach = HerculesCoach()
    target = ExerciseTarget(
        rep_min=8,
        rep_max=12,
        is_compound=True,
        is_machine=True
    )

    rec = coach.recommend_next_action(
        weight=float(w),
        reps=int(r),
        rir=None,
        target=target
    )

    return f"Hercules: {rec['message']} (next weight: {rec['next_weight']}, next rep goal: {rec['next_rep_goal']})"

def cmd_add(a):
    insert_log(a.date, a.exercise, a.weight, a.reps)
    print("Logged.")

def cmd_list(a):
    for d, w, r in fetch_logs(a.exercise, a.limit):
        print(f"{d} | {w} x {r}")

def cmd_plot(a):
    plot_progress(fetch_logs(a.exercise, None), a.exercise)

def cmd_suggest(a):
    print(suggest_next_weight(fetch_logs(a.exercise, 20)))

def main():
    p = argparse.ArgumentParser(prog="workout_tracker")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("--date", required=True)
    a.add_argument("--exercise", required=True)
    a.add_argument("--weight", type=float, required=True)
    a.add_argument("--reps", type=int, required=True)
    a.set_defaults(func=cmd_add)

    l = sub.add_parser("list")
    l.add_argument("--exercise", required=True)
    l.add_argument("--limit", type=int, default=10)
    l.set_defaults(func=cmd_list)

    g = sub.add_parser("plot")
    g.add_argument("--exercise", required=True)
    g.set_defaults(func=cmd_plot)

    s = sub.add_parser("suggest")
    s.add_argument("--exercise", required=True)
    s.set_defaults(func=cmd_suggest)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

