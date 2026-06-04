from pathlib import Path
import shutil


POSTED_MAIN_DIR = Path(
    r"D:\Ava Blackthorne\Ready\Wavespeed\Posted_Main"
)

POSTED_BACKUP_DIR = Path(
    r"D:\Ava Blackthorne\Ready\Wavespeed\Posted_Backup"
)


def handle_successful_publish(
    image_path,
    published_accounts,
):
    image_path = Path(image_path)

    POSTED_MAIN_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    POSTED_BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    published_to_main = (
        "AvaBlackthorne"
        in published_accounts
    )

    published_to_backup = (
        "AvaBlackthorneX"
        in published_accounts
    )

    if (
        published_to_main
        and published_to_backup
    ):
        shutil.copy2(
            image_path,
            POSTED_MAIN_DIR
            / image_path.name,
        )

        shutil.copy2(
            image_path,
            POSTED_BACKUP_DIR
            / image_path.name,
        )

        image_path.unlink(
            missing_ok=True
        )

    elif published_to_main:
        shutil.move(
            str(image_path),
            str(
                POSTED_MAIN_DIR
                / image_path.name
            ),
        )

    elif published_to_backup:
        shutil.move(
            str(image_path),
            str(
                POSTED_BACKUP_DIR
                / image_path.name
            ),
        )