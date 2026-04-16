from __future__ import annotations

from dataclasses import dataclass
from typing import List

import torch
from PIL import Image
from transformers import AutoModel, AutoProcessor

from core.config import MODEL_NAME


def get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


@dataclass
class LoadedModel:
    model: AutoModel
    processor: AutoProcessor
    device: torch.device


def load_siglip_model(model_name: str = MODEL_NAME) -> LoadedModel:
    device = get_device()

    processor = AutoProcessor.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    model.to(device)

    return LoadedModel(
        model=model,
        processor=processor,
        device=device,
    )


def load_image(image_path: str | bytes | "os.PathLike[str]") -> Image.Image:
    image = Image.open(image_path).convert("RGB")
    return image


@torch.no_grad()
def score_image_against_labels(
    loaded: LoadedModel,
    image: Image.Image,
    candidate_texts: List[str],
) -> List[float]:
    """
    Returns one score per candidate text.
    Higher means more compatible with the image.
    """
    inputs = loaded.processor(
        text=candidate_texts,
        images=image,
        padding="max_length",
        return_tensors="pt",
    )

    inputs = {k: v.to(loaded.device) for k, v in inputs.items()}

    outputs = loaded.model(**inputs)

    if not hasattr(outputs, "logits_per_image"):
        raise ValueError("Model output does not contain logits_per_image.")

    logits_per_image = outputs.logits_per_image
    scores = logits_per_image[0].detach().cpu().tolist()
    return scores