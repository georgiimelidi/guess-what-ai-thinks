import random
from typing import List, Sequence

from core.config import NUM_OPTIONS


def generate_options(
    ranked_label_ids: Sequence[str],
    all_label_ids: Sequence[str],
    rng: random.Random,
) -> List[str]:
    """
    Build exactly NUM_OPTIONS distinct answer options.

    Strategy:
    - always include top1, top2, top3 if available
    - fill remaining slots with random labels from same pack
    - shuffle final options
    """
    chosen: List[str] = []

    for label_id in ranked_label_ids[:3]:
        if label_id not in chosen:
            chosen.append(label_id)

    remaining_pool = [label for label in all_label_ids if label not in chosen]
    rng.shuffle(remaining_pool)

    while len(chosen) < NUM_OPTIONS and remaining_pool:
        chosen.append(remaining_pool.pop())

    if len(chosen) < NUM_OPTIONS:
        raise ValueError(
            f"Could not generate {NUM_OPTIONS} unique options from labels: {all_label_ids}"
        )

    rng.shuffle(chosen)
    return chosen