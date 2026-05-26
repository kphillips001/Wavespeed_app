import os

import tweepy


def publish_to_x(
    image_path,
    caption,
):
    auth = tweepy.OAuth1UserHandler(
        os.getenv(
            "X_CONSUMER_KEY"
        ),
        os.getenv(
            "X_CONSUMER_SECRET"
        ),
        os.getenv(
            "X_ACCESS_TOKEN"
        ),
        os.getenv(
            "X_ACCESS_TOKEN_SECRET"
        ),
    )

    api = tweepy.API(
        auth
    )

    client = tweepy.Client(
        consumer_key=os.getenv(
            "X_CONSUMER_KEY"
        ),
        consumer_secret=os.getenv(
            "X_CONSUMER_SECRET"
        ),
        access_token=os.getenv(
            "X_ACCESS_TOKEN"
        ),
        access_token_secret=os.getenv(
            "X_ACCESS_TOKEN_SECRET"
        ),
    )

    media = api.media_upload(
        str(image_path)
    )

    tweet = client.create_tweet(
        text=caption,
        media_ids=[
            media.media_id
        ]
    )

    print(
        "\n================="
    )
    print(
        "POSTED TO X"
    )
    print(
        "================="
    )

    print(
        tweet.data
    )

    return True