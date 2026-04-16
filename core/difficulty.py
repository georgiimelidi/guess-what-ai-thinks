from core.config import DIFFICULTY_THRESHOLDS


def assign_difficulty(top1_prob: float, top2_prob: float) -> str:
    gap = top1_prob - top2_prob

    if gap >= DIFFICULTY_THRESHOLDS["easy_gap"]:
        return "easy"
    if gap >= DIFFICULTY_THRESHOLDS["medium_gap"]:
        return "medium"
    return "hard"