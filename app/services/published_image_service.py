from pathlib import Path

from PIL import Image


POSTED_X_DIR = Path(
    r"D:\Ava Blackthorne\Ready\Wavespeed\Posted-Socials\Posted_X"
)


def strip_metadata_and_save(
    source_path,
    destination_path,
):
    source_path = Path(source_path)
    destination_path = Path(destination_path)

    with Image.open(source_path) as image:
        clean_image = Image.new(
            image.mode,
            image.size,
        )

        clean_image.putdata(
            list(image.getdata())
        )

        clean_image.save(
            destination_path,
            format="PNG",
        )


def handle_successful_publish(
    image_path,
    published_accounts,
):
    image_path = Path(image_path)

    POSTED_X_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if published_accounts:
        strip_metadata_and_save(
            image_path,
            POSTED_X_DIR
            / image_path.name,
        )

        image_path.unlink(
            missing_ok=True,
        )
