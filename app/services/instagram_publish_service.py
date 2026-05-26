from pathlib import Path
import pyperclip

from PIL import Image

from app.services.instagram_phone_publish_service import (
    open_instagram_on_phone,
    push_image_to_phone,
)


POSTED_SOCIALS_DIR = Path(
    r"D:\Ava Blackthorne\Ready\Wavespeed\Posted-Socials"
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


def publish_to_instagram(
    image_path,
    caption,
):

    image_path = Path(image_path)

    POSTED_SOCIALS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_destination = (
        POSTED_SOCIALS_DIR /
        image_path.name
    )

    #
    # 1. Strip EXIF / metadata and save clean image only
    #

    strip_metadata_and_save(
        image_path,
        image_destination,
    )

    #
    # 2. Copy caption to Windows clipboard
    #

    pyperclip.copy(
        caption
    )

    #
    # 3. Push clean published image to phone
    #

    push_image_to_phone(
        image_destination
    )

    #
    # 4. Open Instagram
    #

    open_instagram_on_phone()

    #
    # 5. Remove original staged image
    #

    if image_path.exists():

        image_path.unlink()

    print("\n====================")
    print("INSTAGRAM PUBLISH")
    print("====================")
    print(f"Clean image saved:\n{image_destination}")
    print("Clean image pushed to phone")
    print("Original staged image removed")
    print("Caption copied to Windows clipboard")

    return True