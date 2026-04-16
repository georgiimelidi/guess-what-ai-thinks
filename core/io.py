import csv
from pathlib import Path
from typing import List

import yaml

from core.schema import LabelEntry, MetadataRow, PackConfig


def load_pack_config(labels_yaml_path: Path) -> PackConfig:
    with labels_yaml_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    labels = [
        LabelEntry(
            id=item["id"],
            text=item["text"],
            aliases=item.get("aliases", []),
        )
        for item in raw["labels"]
    ]

    return PackConfig(
        pack_name=raw["pack_name"],
        display_name=raw["display_name"],
        description=raw["description"],
        labels=labels,
    )


def load_metadata_rows(metadata_csv_path: Path) -> List[MetadataRow]:
    if not metadata_csv_path.exists():
        return []

    rows: List[MetadataRow] = []
    with metadata_csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row["image_id"]:
                continue

            rows.append(
                MetadataRow(
                    image_id=row["image_id"],
                    pack_name=row["pack_name"],
                    image_path=row["image_path"],
                    true_label=row.get("true_label") or None,
                    ai_top1=row["ai_top1"],
                    ai_score_top1=float(row["ai_score_top1"]),
                    ai_top2=row["ai_top2"],
                    ai_score_top2=float(row["ai_score_top2"]),
                    ai_top3=row["ai_top3"],
                    ai_score_top3=float(row["ai_score_top3"]),
                    all_scores_json=row["all_scores_json"],
                    options_json=row["options_json"],
                    difficulty=row["difficulty"],
                    approved=row["approved"],
                    notes=row.get("notes", ""),
                )
            )
    return rows


def save_metadata_rows(metadata_csv_path: Path, rows: List[MetadataRow]) -> None:
    fieldnames = [
        "image_id",
        "pack_name",
        "image_path",
        "true_label",
        "ai_top1",
        "ai_score_top1",
        "ai_top2",
        "ai_score_top2",
        "ai_top3",
        "ai_score_top3",
        "all_scores_json",
        "options_json",
        "difficulty",
        "approved",
        "notes",
    ]

    metadata_csv_path.parent.mkdir(parents=True, exist_ok=True)

    with metadata_csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "image_id": row.image_id,
                    "pack_name": row.pack_name,
                    "image_path": row.image_path,
                    "true_label": row.true_label or "",
                    "ai_top1": row.ai_top1,
                    "ai_score_top1": row.ai_score_top1,
                    "ai_top2": row.ai_top2,
                    "ai_score_top2": row.ai_score_top2,
                    "ai_top3": row.ai_top3,
                    "ai_score_top3": row.ai_score_top3,
                    "all_scores_json": row.all_scores_json,
                    "options_json": row.options_json,
                    "difficulty": row.difficulty,
                    "approved": row.approved,
                    "notes": row.notes or "",
                }
            )


def get_pack_dir(pack_name: str) -> Path:
    from core.config import PACKS_DIR
    return PACKS_DIR / pack_name


def get_labels_yaml_path(pack_name: str) -> Path:
    return get_pack_dir(pack_name) / "labels.yaml"


def get_metadata_csv_path(pack_name: str) -> Path:
    return get_pack_dir(pack_name) / "metadata.csv"


def get_images_dir(pack_name: str) -> Path:
    return get_pack_dir(pack_name) / "images"

def load_approved_metadata_rows(metadata_csv_path: Path) -> List[MetadataRow]:
    rows = load_metadata_rows(metadata_csv_path)
    return [row for row in rows if row.approved == "TRUE"]

def update_metadata_row(metadata_csv_path: Path, updated_row: MetadataRow) -> None:
    rows = load_metadata_rows(metadata_csv_path)

    replaced = False
    for i, row in enumerate(rows):
        if row.image_id == updated_row.image_id:
            rows[i] = updated_row
            replaced = True
            break

    if not replaced:
        rows.append(updated_row)

    save_metadata_rows(metadata_csv_path, rows)