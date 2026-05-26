import subprocess
import time

import uiautomator2 as u2


PHONE_SERIAL = "RFCN90JL1LP"
INSTAGRAM_PACKAGE = "com.instagram.android"
PHONE_IMAGE_FOLDER = "/sdcard/Pictures/Wavespeed/"


def push_image_to_phone(
    image_path,
):

    print("\n==============================")
    print("PUSH IMAGE TO PHONE")
    print("==============================")

    subprocess.run(
        [
            "adb",
            "-s",
            PHONE_SERIAL,
            "shell",
            "mkdir",
            "-p",
            PHONE_IMAGE_FOLDER,
        ],
        check=True,
    )

    subprocess.run(
        [
            "adb",
            "-s",
            PHONE_SERIAL,
            "push",
            str(image_path),
            PHONE_IMAGE_FOLDER,
        ],
        check=True,
    )

    subprocess.run(
        [
            "adb",
            "-s",
            PHONE_SERIAL,
            "shell",
            "am",
            "broadcast",
            "-a",
            "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
            "-d",
            f"file://{PHONE_IMAGE_FOLDER}",
        ],
        check=True,
    )

    time.sleep(2)

    print("Image pushed to phone.")

    return True


def open_instagram_on_phone():

    print("\n==============================")
    print("PHONE INSTAGRAM PUBLISH TEST")
    print("==============================")

    d = u2.connect_usb(
        PHONE_SERIAL
    )

    print(
        f"Connected to phone: {PHONE_SERIAL}"
    )

    print("Closing Instagram...")

    d.app_stop(
        INSTAGRAM_PACKAGE
    )

    time.sleep(2)

    print("Opening Instagram...")

    d.app_start(
        INSTAGRAM_PACKAGE
    )

    time.sleep(3)

    print("Instagram opened on phone.")

    return True

def start_instagram_create_post():

    d = u2.connect_usb(
        PHONE_SERIAL
    )

    print("\nStarting Instagram create flow...")

    #
    # Tap top-left + button
    #

    d.click(
        34,
        123
    )

    time.sleep(3)

    print("Tapped Instagram create button.")

    return True

def copy_caption_to_phone_clipboard(
    caption,
):

    import pyperclip

    pyperclip.copy(
        caption
    )

    print(
        "Instagram caption copied to Windows clipboard."
    )

    return True