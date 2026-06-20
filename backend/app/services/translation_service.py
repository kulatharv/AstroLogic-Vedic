import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def load_translations(lang="en"):
    file_path = (
        BASE_DIR /
        "static" /
        "locales" /
        f"{lang}.json"
    )

    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except:
        with open(
            BASE_DIR / "static" / "locales" / "en.json",
            encoding="utf-8"
        ) as f:
            return json.load(f)