from pathlib import Path


def get_wavespeed_root(output_dir):
    return Path(output_dir)


def get_social_gallery_dir(output_dir):
    return get_wavespeed_root(output_dir)


def get_social_photoshoot_dir(output_dir):
    return get_wavespeed_root(output_dir) / "Photoshoot"


def get_social_staged_dir(output_dir):
    return get_wavespeed_root(output_dir) / "Staged"


def get_premium_root_dir(output_dir):
    return get_wavespeed_root(output_dir) / "Premium"


def get_premium_gallery_dir(output_dir):
    return get_premium_root_dir(output_dir) / "Gallery"


def get_premium_photoshoot_dir(output_dir):
    return get_premium_root_dir(output_dir) / "Photoshoot"


def get_premium_staged_dir(output_dir):
    return get_premium_root_dir(output_dir) / "Staged"


def get_premium_identity_dir(output_dir):
    return get_premium_root_dir(output_dir) / "Identity"


def get_premium_export_dir(output_dir):
    return get_premium_root_dir(output_dir) / "Export_To_FanvueChatbot"


def ensure_content_dirs(output_dir):
    folders = [
        get_social_gallery_dir(output_dir),
        get_social_photoshoot_dir(output_dir),
        get_social_staged_dir(output_dir),
        get_premium_gallery_dir(output_dir),
        get_premium_photoshoot_dir(output_dir),
        get_premium_staged_dir(output_dir),
        get_premium_identity_dir(output_dir),
        get_premium_export_dir(output_dir),
    ]

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
