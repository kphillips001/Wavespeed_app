from pathlib import Path
import shutil

import streamlit as st

from app.config.content_paths import (
    get_premium_gallery_dir,
    get_premium_photoshoot_dir,
)

from app.ui.image_file_utils import (
    get_image_files,
    get_unique_image_path,
)


def render_premium_gallery(selected_output_dir):
    premium_gallery_dir = get_premium_gallery_dir(selected_output_dir)
    premium_photoshoot_dir = get_premium_photoshoot_dir(selected_output_dir)

    premium_gallery_dir.mkdir(parents=True, exist_ok=True)
    premium_photoshoot_dir.mkdir(parents=True, exist_ok=True)

    st.markdown("---")
    st.subheader("🖼 Premium Gallery")

    premium_images = get_image_files(
        premium_gallery_dir,
        recursive=False,
    )

    if not premium_images:
        st.warning("No images currently in Premium Gallery.")
        return

    cols = st.columns(3)

    for index, image_path in enumerate(premium_images):
        with cols[index % 3]:
            st.image(
                str(image_path),
                use_container_width=True,
            )

            action_col1, action_col2 = st.columns(2)

            with action_col1:
                if st.button(
                    "📸 Queue",
                    key=f"premium_gallery_queue_{image_path}",
                    use_container_width=True,
                ):
                    destination = get_unique_image_path(
                        premium_photoshoot_dir,
                        image_path.name,
                    )

                    shutil.move(
                        str(image_path),
                        str(destination),
                    )

                    st.session_state["save_toast_message"] = (
                        "📸 Moved image to Premium Photoshoot Queue"
                    )

                    st.rerun()

            with action_col2:
                if st.button(
                    "🗑 Delete",
                    key=f"premium_gallery_delete_{image_path}",
                    use_container_width=True,
                ):
                    junk_dir = premium_gallery_dir / "Junk-Outdated"

                    junk_dir.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    destination = get_unique_image_path(
                        junk_dir,
                        Path(image_path).name,
                    )

                    shutil.move(
                        str(image_path),
                        str(destination),
                    )

                    st.session_state["save_toast_message"] = (
                        "🗑 Moved premium image to Junk"
                    )

                    st.rerun()

            st.button(
                "📤 Export Soon",
                key=f"premium_gallery_export_{image_path}",
                use_container_width=True,
                disabled=True,
            )