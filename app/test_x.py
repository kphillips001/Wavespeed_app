from pathlib import Path

from dotenv import load_dotenv

from app.services.x_publish_service import (
    publish_to_x,
)

load_dotenv(
    override=True
)

publish_to_x(
    Path(
        r"D:\Ava Blackthorne\Ready\Wavespeed\Staged\image_003.png"
    ),
    "Testing Wavespeed X publishing 🚀"
)