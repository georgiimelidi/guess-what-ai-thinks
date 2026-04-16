from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import List

from core.config import IMAGE_EXTENSIONS, RANDOM_SEED, PROJECT_ROOT
from core.difficulty import assign_difficulty
from core.inference import score_pack_labels
from core.io import (
    get_images_dir,
    get_labels_yaml_path,
    get_metadata_csv_path,
    load_metadata_rows,
    load_pack_config,
    save_metadata_rows,
)
from core.model import load_image, load_siglip_model
from core.options import generate_options
from core.schema import MetadataRow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build metadata.csv for one content pack.")
    parser.add_argument("--pack", type=str, required=True, help="Pack name, e.g. animals")
    parser.add_argument("--approve-all", action="store_true", help="Mark new rows approved=TRUE")
    return parser.parse_args()


def list_images(images_dir: Path) -> List[Path]:
    if not images_dir.exists():
        raise FileNotFoundError(f"Images directory not found: {images_dir}")
    return [
        path for path in sorted(images_dir.iterdir())
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]


def build_image_id(pack_name: str, image_path: Path) -> str:
    return f"{pack_name}_{image_path.stem}"


def relative_image_path(image_path: Path, project_root: Path) -> str:
    return str(image_path.relative_to(project_root))


def main() -> None:
    args = parse_args()
    rng = random.Random(RANDOM_SEED)

    labels_yaml_path = get_labels_yaml_path(args.pack)
    metadata_csv_path = get_metadata_csv_path(args.pack)
    images_dir = get_images_dir(args.pack)

    if not labels_yaml_path.exists():
        raise FileNotFoundError(f"Pack labels not found: {labels_yaml_path}")

    print(f"Loading pack config: {labels_yaml_path}")
    pack_config = load_pack_config(labels_yaml_path)

    old_rows = {}
    if metadata_csv_path.exists():
        for row in load_metadata_rows(metadata_csv_path):
            old_rows[row.image_id] = row

    print("Loading model...")
    loaded_model = load_siglip_model()

    image_paths = list_images(images_dir)
    if not image_paths:
        raise ValueError(f"No images found in: {images_dir}")

    all_label_ids = [label.id for label in pack_config.labels]
    rows: List[MetadataRow] = []

    print(f"Found {len(image_paths)} image(s) in pack '{args.pack}'")

    for idx, image_path in enumerate(image_paths, start=1):
        print(f"[{idx}/{len(image_paths)}] Processing {image_path.name}")

        image = load_image(image_path)
        scored = score_pack_labels(
            loaded_model=loaded_model,
            image=image,
            pack_config=pack_config,
        )

        top1, top2, top3 = scored[:3]
        ranked_label_ids = [label_id for label_id, _, _, _ in scored]
        options = generate_options(ranked_label_ids=ranked_label_ids, all_label_ids=all_label_ids, rng=rng)

        all_scores = {
            label_id: {
                "text": label_text,
                "raw_score": raw_score,
                "probability": prob,
            }
            for label_id, label_text, raw_score, prob in scored
        }

        difficulty = assign_difficulty(top1_prob=top1[3], top2_prob=top2[3])
        image_id = build_image_id(args.pack, image_path)
        previous = old_rows.get(image_id)

        row = MetadataRow(
            image_id=image_id,
            pack_name=args.pack,
            image_path=relative_image_path(image_path, PROJECT_ROOT),
            true_label=previous.true_label if previous else None,
            ai_top1=top1[0],
            ai_score_top1=top1[3],
            ai_top2=top2[0],
            ai_score_top2=top2[3],
            ai_top3=top3[0],
            ai_score_top3=top3[3],
            all_scores_json=json.dumps(all_scores, ensure_ascii=False),
            options_json=json.dumps(options, ensure_ascii=False),
            difficulty=difficulty,
            approved=(
                previous.approved
                if previous is not None
                else ("TRUE" if args.approve_all else "FALSE")
            ),
            notes=previous.notes if previous else "",
        )
        rows.append(row)

    save_metadata_rows(metadata_csv_path, rows)
    print(f"\nSaved {len(rows)} row(s) to: {metadata_csv_path}")


if __name__ == "__main__":
    main()