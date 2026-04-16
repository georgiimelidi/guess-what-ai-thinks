from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LabelEntry:
    id: str
    text: str
    aliases: List[str] = field(default_factory=list)


@dataclass
class PackConfig:
    pack_name: str
    display_name: str
    description: str
    labels: List[LabelEntry]


@dataclass
class MetadataRow:
    image_id: str
    pack_name: str
    image_path: str
    true_label: Optional[str]
    ai_top1: str
    ai_score_top1: float
    ai_top2: str
    ai_score_top2: float
    ai_top3: str
    ai_score_top3: float
    all_scores_json: str
    options_json: str
    difficulty: str
    approved: str
    notes: Optional[str] = ""