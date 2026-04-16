from __future__ import annotations

import argparse
from pathlib import Path

from core.inference import score_pack_labels, top_k_results
from core.io import get_labels_yaml_path, load_pack_config
from core.model import load_image, load_siglip_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview model scores for one image against one pack."
    )
    parser.add_argument(
        "--pack",
        type=str,
        required=True,
        help="Pack name, e.g. animals",
    )
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Path to image file",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="How many top results to display",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    labels_yaml_path = get_labels_yaml_path(args.pack)
    if not labels_yaml_path.exists():
        raise FileNotFoundError(f"Pack labels not found: {labels_yaml_path}")

    print(f"Loading pack: {args.pack}")
    pack_config = load_pack_config(labels_yaml_path)

    print("Loading model...")
    loaded_model = load_siglip_model()

    print(f"Loading image: {image_path}")
    image = load_image(image_path)

    print("Scoring labels...")
    scored = score_pack_labels(
        loaded_model=loaded_model,
        image=image,
        pack_config=pack_config,
    )

    top_results = top_k_results(scored, k=args.top_k)

    print("\nTop results:")
    for rank, (label_id, label_text, raw_score, prob) in enumerate(top_results, start=1):
        print(
            f"{rank}. {label_id} ({label_text}) -> raw={raw_score:.4f}, prob={100*prob:.2f}%"
        )

    print("\nAll results:")
    for label_id, label_text, raw_score, prob in scored:
        print(f"- {label_id:<20} raw={raw_score:>8.4f}   prob={100*prob:>6.2f}%")


if __name__ == "__main__":
    main()