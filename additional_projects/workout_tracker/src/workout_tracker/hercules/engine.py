# workout_tracker/hercules/engine.py
from dataclasses import dataclass
from typing import Optional
from .templates import pick, pick_tip

@dataclass
class ExerciseTarget:
    rep_min: int
    rep_max: int
    rir_target_min: int = 0
    rir_target_max: int = 2
    is_compound: bool = True
    is_machine: bool = True

def _small_jump(weight: float, is_machine: bool) -> float:
    if is_machine:
        return 10.0 if weight >= 100 else 5.0
    return 5.0

class HerculesCoach:
    def recommend_next_action(
        self,
        weight: float,
        reps: int,
        rir: Optional[int],
        target: ExerciseTarget,
    ) -> dict:
        # Estimate RIR if not provided
        effective_rir = rir if rir is not None else (1 if reps >= target.rep_max - 1 else 2)

        compound_note = ""
        if target.is_compound:
            compound_note = " Compounds grow best near 0–2 RIR."

        # INCREASE WEIGHT
        if reps >= target.rep_max and target.rir_target_min <= effective_rir <= target.rir_target_max:
            jump = _small_jump(weight, target.is_machine)
            next_weight = weight + jump
            return {
                "coach": "Hercules",
                "status": "increase",
                "next_weight": next_weight,
                "next_rep_goal": target.rep_min,
                "message": pick("increase").format(
                    next_weight=next_weight,
                    rep_min=target.rep_min
                ) + compound_note,
            }

        # DECREASE WEIGHT
        if reps < target.rep_min and effective_rir <= 1:
            jump = _small_jump(weight, target.is_machine)
            next_weight = max(0.0, weight - jump)
            return {
                "coach": "Hercules",
                "status": "decrease",
                "next_weight": next_weight,
                "next_rep_goal": target.rep_min,
                "message": pick("decrease").format(
                    next_weight=next_weight,
                    rep_min=target.rep_min
                ) + compound_note,
            }

        # KEEP WEIGHT — PROGRESS REPS
        next_rep_goal = min(target.rep_max, reps + 1)

        return {
            "coach": "Hercules",
            "status": "keep",
            "next_weight": weight,
            "next_rep_goal": next_rep_goal,
            "message": pick("keep").format(
                weight=weight,
                next_rep_goal=next_rep_goal
            ) + " " + pick_tip(),
        }
