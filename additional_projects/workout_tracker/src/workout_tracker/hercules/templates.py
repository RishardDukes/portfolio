# workout_tracker/hercules/templates.py
import random

TEMPLATES = {
    "keep": [
        "Perfect. Keep {weight} and aim for {next_rep_goal} reps next set.",
        "Good. Same weight ({weight}) — try {next_rep_goal} reps next set.",
        "You're in the zone. Stay at {weight} and push for {next_rep_goal}.",
    ],
    "increase": [
        "You earned the jump. Next time bump to {next_weight} and aim for {rep_min}+ reps.",
        "Top of the range with control — go to {next_weight} next time, aim for {rep_min}+.",
    ],
    "decrease": [
        "That’s heavy for today’s target. Drop to {next_weight} next time and rebuild into the range.",
        "Under the rep floor near failure — reduce to {next_weight} and aim for {rep_min}+.",
    ],
    "tips": [
        "If you stall, take 2 deep breaths and squeeze out 1 more rep.",
        "Control the negative (2–3 seconds). That’s where the growth reps are.",
        "Keep your form tight — make the target muscle do the work.",
    ],
}

def pick(key: str) -> str:
    return random.choice(TEMPLATES[key])

def pick_tip() -> str:
    return random.choice(TEMPLATES["tips"])
