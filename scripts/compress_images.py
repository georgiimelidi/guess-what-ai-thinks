from PIL import Image
import os

ROOT = "data/packs"
MAX_SIZE = 512
QUALITY = 80

for pack in os.listdir(ROOT):
    img_dir = os.path.join(ROOT, pack, "images")

    if not os.path.isdir(img_dir):
        continue

    for file in os.listdir(img_dir):
        path = os.path.join(img_dir, file)

        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        try:
            img = Image.open(path).convert("RGB")

            # Resize
            img.thumbnail((MAX_SIZE, MAX_SIZE))

            # Save compressed (overwrite)
            img.save(path, "JPEG", quality=QUALITY, optimize=True)

            print("compressed:", path)

        except Exception as e:
            print("error:", path, e)