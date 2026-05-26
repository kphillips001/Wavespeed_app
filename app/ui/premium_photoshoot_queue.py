from datetime import datetime
from pathlib import Path
import shutil

import streamlit as st

from app.config.content_paths import (
    get_premium_photoshoot_dir,
    get_premium_gallery_dir,
)

from app.ui.image_file_utils import (
    get_unique_image_path,
)


IMAGE_SUFFIXES = [".png", ".jpg", ".jpeg", ".webp"]


def render_premium_photoshoot_queue(selected_output_dir):
    premium_photoshoot_dir = get_premium_photoshoot_dir(
        selected_output_dir
    )

    premium_gallery_dir = get_premium_gallery_dir(
        selected_output_dir
    )

    premium_photoshoot_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    premium_gallery_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    st.markdown("---")
    st.subheader("📸 Premium Photoshoot Queue Manager")

    st.markdown("### ➕ Add Image To Premium Photoshoot Queue")

    if "premium_photoshoot_upload_key" not in st.session_state:
        st.session_state["premium_photoshoot_upload_key"] = 0

    uploaded_premium_photoshoot = st.file_uploader(
        "",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"premium_photoshoot_queue_upload_{st.session_state['premium_photoshoot_upload_key']}",
    )

    if uploaded_premium_photoshoot:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_suffix = Path(uploaded_premium_photoshoot.name).suffix.lower()

        save_path = premium_photoshoot_dir / f"premium_queue_{timestamp}{file_suffix}"

        with open(save_path, "wb") as file:
            file.write(uploaded_premium_photoshoot.getbuffer())

        st.session_state["premium_photoshoot_upload_key"] += 1
        st.session_state["save_toast_message"] = "📸 Added to Premium Photoshoot Queue"

        st.rerun()

    st.markdown("---")

    premium_photoshoot_images = sorted(
        [
            image_path
            for image_path in premium_photoshoot_dir.iterdir()
            if image_path.suffix.lower() in IMAGE_SUFFIXES
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not premium_photoshoot_images:
        st.warning("No images currently in Premium Photoshoot Queue.")
        return

    cols = st.columns(2)

    for index, image_path in enumerate(premium_photoshoot_images):
        image_key = image_path.stem

        with cols[index % 2]:
            st.image(
                str(image_path),
                use_container_width=True,
            )

            premium_photoshoot_count = st.number_input(
                "Number of Premium Photoshoot Images",
                min_value=1,
                max_value=25,
                value=5,
                key=f"premium_photoshoot_count_{image_key}",
            )

            with st.expander(
                "Shot Ideas Optional",
                expanded=False,
            ):
                for shot_index in range(1, premium_photoshoot_count + 1):
                    st.text_input(
                        f"Shot {shot_index}",
                        key=f"premium_shot_{image_key}_{shot_index}",
                        placeholder="Optional: mirror pose, bedroom lighting, close-up crop...",
                    )

            action_col1, action_col2 = st.columns(2)

            with action_col1:
                if st.button(
                    "🚀 Start Premium Photoshoot",
                    key=f"start_premium_photoshoot_{image_key}",
                    use_container_width=True,
                ):
                    st.info(
                        "Premium photoshoot generation will be connected next."
                    )

            with action_col2:
                if st.button(
                    "↩ Move To Premium Gallery",
                    key=f"move_premium_gallery_{image_key}",
                    use_container_width=True,
                ):
                    destination = get_unique_image_path(
                        premium_gallery_dir,
                        image_path.name,
                    )

                    shutil.move(
                        str(image_path),
                        str(destination),
                    )

                    st.session_state["save_toast_message"] = (
                        "↩ Moved image to Premium Gallery"
                    )

                    st.rerun()