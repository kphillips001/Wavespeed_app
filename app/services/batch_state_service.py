import json
from pathlib import Path
from datetime import datetime


BATCH_STATE_DIR = Path("outputs")
BATCH_STATE_FILE = BATCH_STATE_DIR / "current_batch.json"


def save_current_batch_state(
    creator_name="",
    reference_image_path="",
    creative_tags="",
    generated_prompts=None,
    generated_image_paths=None,
    discarded_image_paths=None,
):
    BATCH_STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    batch_state = {
        "creator_name": creator_name,
        "reference_image_path": str(reference_image_path),
        "creative_tags": creative_tags,
        "generated_prompts": generated_prompts or [],
        "generated_image_paths": [
            str(path)
            for path in (generated_image_paths or [])
        ],
        "discarded_image_paths": [
            str(path)
            for path in (discarded_image_paths or [])
        ],
        "saved_at": datetime.now().isoformat(timespec="seconds"),
    }

    with open(
        BATCH_STATE_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            batch_state,
            file,
            indent=4,
        )

    return batch_state


def load_current_batch_state():
    if not BATCH_STATE_FILE.exists():
        return None

    try:
        with open(
            BATCH_STATE_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except json.JSONDecodeError:
        return None


def clear_current_batch_state():
    if BATCH_STATE_FILE.exists():
        BATCH_STATE_FILE.unlink()