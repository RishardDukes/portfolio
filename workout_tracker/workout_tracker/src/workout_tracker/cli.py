from __future__ import annotations

import argparse

from .db import fetch_logs, insert_log
from .hercules.engine import ExerciseTarget, HerculesCoach


def suggest_next_weight(rows):
    if not rows:
        return "Hercules: No history yet. Start at a comfortable weight and log your first set."

    _, weight, reps = rows[-1]
    coach = HerculesCoach()
    target = ExerciseTarget(rep_min=8, rep_max=12, is_compound=True, is_machine=True)
    rec = coach.recommend_next_action(weight=float(weight), reps=int(reps), rir=None, target=target)
    return f"Hercules: {rec['message']}"


def cmd_add(args):
    insert_log(args.date, args.exercise, args.weight, args.reps)
    print("Logged.")


def cmd_list(args):
    for d, w, r in fetch_logs(args.exercise, args.limit):
        print(f"{d} | {w} x {r}")


def cmd_suggest(args):
    print(suggest_next_weight(fetch_logs(args.exercise, 20)))


def main():
    parser = argparse.ArgumentParser(prog="workout_tracker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    add_p = sub.add_parser("add")
    add_p.add_argument("--date", required=True)
    add_p.add_argument("--exercise", required=True)
    add_p.add_argument("--weight", type=float, required=True)
    add_p.add_argument("--reps", type=int, required=True)
    add_p.set_defaults(func=cmd_add)

    list_p = sub.add_parser("list")
    list_p.add_argument("--exercise", required=True)
    list_p.add_argument("--limit", type=int, default=10)
    list_p.set_defaults(func=cmd_list)

    suggest_p = sub.add_parser("suggest")
    suggest_p.add_argument("--exercise", required=True)
    suggest_p.set_defaults(func=cmd_suggest)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
