from pathlib import Path


IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"]


def get_unique_image_path(output_dir, base_name):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    candidate_path = output_path / base_name

    if not candidate_path.exists():
        return candidate_path

    stem = candidate_path.stem
    suffix = candidate_path.suffix

    counter = 2

    while True:
        new_candidate = output_path / f"{stem}_{counter}{suffix}"

        if not new_candidate.exists():
            return new_candidate

        counter += 1


def get_image_files(folder_path, recursive=False):
    folder = Path(folder_path)

    if not folder.exists():
        return []

    if recursive:
        image_paths = [
            path
            for path in folder.rglob("*")
            if path.is_file()
            and path.suffix.lower() in IMAGE_EXTENSIONS
        ]
    else:
        image_paths = [
            path
            for path in folder.iterdir()
            if path.is_file()
            and path.suffix.lower() in IMAGE_EXTENSIONS
        ]

    return sorted(
        image_paths,
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )