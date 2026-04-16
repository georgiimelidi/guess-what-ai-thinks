from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKS_DIR = PROJECT_ROOT / "data" / "packs"

MODEL_NAME = "google/siglip2-base-patch16-224"
DEFAULT_TOP_K = 3
NUM_OPTIONS = 4
RANDOM_SEED = 42
QUESTIONS_PER_GAME = 10

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

DIFFICULTY_THRESHOLDS = {
    "easy_gap": 0.35,
    "medium_gap": 0.12,
}

VALID_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_APPROVED_VALUES = {"TRUE", "FALSE"}

FOOTER_TEXT = "Georgii Melidi · Guess What the AI Thinks"