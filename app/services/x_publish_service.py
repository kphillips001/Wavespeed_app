import os
import tempfile
from pathlib import Path

from PIL import Image
import tweepy


X_ACCOUNT_CREDENTIALS = {
    "AvaBlackthorne": {
        "consumer_key": "X_CONSUMER_KEY",
        "consumer_secret": "X_CONSUMER_SECRET",
        "access_token": "X_ACCESS_TOKEN",
        "access_token_secret": "X_ACCESS_TOKEN_SECRET",
    },
    "AvaBlackthorneX": {
        "consumer_key": "X_AVABLACKTHORNEX_CONSUMER_KEY",
        "consumer_secret": "X_AVABLACKTHORNEX_CONSUMER_SECRET",
        "access_token": "X_AVABLACKTHORNEX_ACCESS_TOKEN",
        "access_token_secret": "X_AVABLACKTHORNEX_ACCESS_TOKEN_SECRET",
    },
}


def get_x_credentials(account_name):
    account_config = X_ACCOUNT_CREDENTIALS.get(account_name)

    if not account_config:
        raise ValueError(
            f"Unknown X account: {account_name}"
        )

    credentials = {
        key: os.getenv(env_name)
        for key, env_name in account_config.items()
    }

    missing_credentials = [
        env_name
        for key, env_name in account_config.items()
        if not credentials.get(key)
    ]

    if missing_credentials:
        raise ValueError(
            "Missing X credentials: "
            + ", ".join(missing_credentials)
        )

    return credentials


def strip_metadata_to_temp_image(image_path):
    image_path = Path(image_path)

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".png",
    )

    temp_path = Path(temp_file.name)
    temp_file.close()

    with Image.open(image_path) as image:
        clean_image = Image.new(
            image.mode,
            image.size,
        )

        clean_image.putdata(
            list(image.getdata())
        )

        clean_image.save(
            temp_path,
            format="PNG",
        )

    return temp_path


def publish_to_x(
    image_path,
    caption,
    account_name="AvaBlackthorne",
):
    credentials = get_x_credentials(
        account_name
    )

    auth = tweepy.OAuth1UserHandler(
        credentials["consumer_key"],
        credentials["consumer_secret"],
        credentials["access_token"],
        credentials["access_token_secret"],
    )

    api = tweepy.API(
        auth
    )

    client = tweepy.Client(
        consumer_key=credentials["consumer_key"],
        consumer_secret=credentials["consumer_secret"],
        access_token=credentials["access_token"],
        access_token_secret=credentials["access_token_secret"],
    )

    clean_image_path = strip_metadata_to_temp_image(
        image_path
    )

    try:
        media = api.media_upload(
            str(clean_image_path)
        )

    finally:
        clean_image_path.unlink(
            missing_ok=True
        )

    tweet = client.create_tweet(
        text=caption,
        media_ids=[
            media.media_id
        ],
    )

    print("\n=================")
    print(f"POSTED TO X: {account_name}")
    print("=================")
    print(tweet.data)

    return True
