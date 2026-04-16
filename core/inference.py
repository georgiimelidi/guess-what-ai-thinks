from __future__ import annotations

from typing import Dict, List, Tuple

import math
from PIL import Image

from core.model import LoadedModel, score_image_against_labels
from core.schema import PackConfig


def build_candidate_texts(pack_config: PackConfig) -> List[str]:
    return [label.text for label in pack_config.labels]


def build_text_to_label_id(pack_config: PackConfig) -> Dict[str, str]:
    return {label.text: label.id for label in pack_config.labels}


def softmax(values: List[float]) -> List[float]:
    max_val = max(values)
    exps = [math.exp(v - max_val) for v in values]
    total = sum(exps)
    return [x / total for x in exps]


def score_pack_labels(
    loaded_model: LoadedModel,
    image: Image.Image,
    pack_config: PackConfig,
) -> List[Tuple[str, str, float, float]]:
    """
    Returns sorted results as:
    (label_id, label_text, raw_score, probability)
    """
    candidate_texts = build_candidate_texts(pack_config)
    text_to_label_id = build_text_to_label_id(pack_config)

    raw_scores = score_image_against_labels(
        loaded=loaded_model,
        image=image,
        candidate_texts=candidate_texts,
    )

    probabilities = softmax(raw_scores)

    results: List[Tuple[str, str, float, float]] = []
    for text, raw_score, prob in zip(candidate_texts, raw_scores, probabilities):
        label_id = text_to_label_id[text]
        results.append((label_id, text, float(raw_score), float(prob)))

    results.sort(key=lambda x: x[2], reverse=True)
    return results


def top_k_results(
    scored_results: List[Tuple[str, str, float, float]],
    k: int = 3,
) -> List[Tuple[str, str, float, float]]:
    return scored_results[:k]