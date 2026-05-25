from pathlib import Path
import shutil

import streamlit as st

from app.ui.image_file_utils import (
    get_image_files,
    get_unique_image_path,
)

STAGED_DIR = Path(
    r"D:\Ava Blackthorne\Ready\Wavespeed\Staged"
)

MAX_STAGED_ITEMS = 10


def ensure_staged_dir():
    STAGED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def get_staged_images():
    ensure_staged_dir()

    return get_image_files(
        STAGED_DIR,
        recursive=False,
    )


def get_staged_count():
    return len(
        get_staged_images()
    )


def move_image_to_staged(image_path):
    ensure_staged_dir()

    staged_count = get_staged_count()

    if staged_count >= MAX_STAGED_ITEMS:
        return False

    destination = get_unique_image_path(
        STAGED_DIR,
        Path(image_path).name,
    )

    shutil.move(
        str(image_path),
        str(destination),
    )

    return True


def render_staging_sidebar_button():
    staged_count = get_staged_count()

    st.sidebar.markdown("---")
    st.sidebar.header("Staging")

    st.sidebar.caption(
        f"{staged_count}/{MAX_STAGED_ITEMS} item(s) staged"
    )

    if st.sidebar.button(
        f"📦 Enter Staging Area",
        use_container_width=True,
    ):
        st.session_state["show_staging_area"] = True
        st.session_state["show_gallery"] = False
        st.session_state["show_photoshoot_queue"] = False
        st.session_state["active_photoshoot"] = False
        st.rerun()


def render_staging_area(render_gallery_image_grid):
    staged_images = get_staged_images()

    header_col1, header_col2 = st.columns([8, 2])

    with header_col1:
        st.subheader(
            f"📦 Staging Area ({len(staged_images)}/{MAX_STAGED_ITEMS})"
        )

    with header_col2:
        if st.button(
            "⬅ Back",
            key="back_from_staging_area",
            use_container_width=True,
        ):
            st.session_state["show_staging_area"] = False
            st.rerun()

    st.caption(
        "Images here are prepared for captions, reels, and publishing."
    )

    if not staged_images:
        st.info("No images currently staged.")
        return

    render_gallery_image_grid(
        staged_images,
        columns=3,
        page_key="staging_area",
        mode="staged",
    )