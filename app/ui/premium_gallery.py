from pathlib import Path
import hashlib
import shutil

import streamlit as st
from PIL import Image

from app.config.content_paths import (
    get_premium_gallery_dir,
    get_premium_photoshoot_dir,
    )

from app.ui.image_file_utils import (
    get_image_files,
    get_unique_image_path,
)


IMAGES_PER_PAGE = 24


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

    def build_premium_preview(image_path):
        preview_dir = premium_gallery_dir / "_premium_gallery_preview_cache"

        preview_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        cache_name = hashlib.md5(
            f"{image_path}_{image_path.stat().st_mtime}".encode()
        ).hexdigest()

        preview_path = preview_dir / f"{cache_name}.jpg"

        if preview_path.exists():
            return preview_path

        image = Image.open(image_path).convert("RGB")

        image.thumbnail(
            (900, 1200)
        )

        image.save(
            preview_path,
            quality=95,
        )

        return preview_path

    st.markdown(
        """
        <style>
        [data-testid="stImage"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
            border-radius: 0 !important;
            overflow: hidden !important;
            box-shadow: none !important;
        }

        [data-testid="stImage"] img {
            width: 100% !important;
            display: block !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            border-radius: 12px !important;
            box-shadow: none !important;
        }

        div[data-testid="column"] {
            margin-bottom: 12px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    total_images = len(premium_images)

    total_pages = max(
        1,
        (total_images + IMAGES_PER_PAGE - 1) // IMAGES_PER_PAGE,
    )

    page_key = "premium_gallery_page"

    if page_key not in st.session_state:
        st.session_state[page_key] = 1

    current_page = st.session_state[page_key]

    if current_page > total_pages:
        current_page = total_pages
        st.session_state[page_key] = current_page

    def render_pagination_controls(location):
        nav_col1, nav_col2, nav_col3 = st.columns([6, 1, 1])

        with nav_col1:
            st.caption(
                f"Page {current_page} of {total_pages} • {total_images} image(s)"
            )

        with nav_col2:
            if st.button(
                "← Prev",
                key=f"premium_gallery_prev_{location}",
                use_container_width=True,
                disabled=current_page <= 1,
            ):
                st.session_state[page_key] = current_page - 1
                st.rerun()

        with nav_col3:
            if st.button(
                "Next →",
                key=f"premium_gallery_next_{location}",
                use_container_width=True,
                disabled=current_page >= total_pages,
            ):
                st.session_state[page_key] = current_page + 1
                st.rerun()

    render_pagination_controls("top")

    start_index = (current_page - 1) * IMAGES_PER_PAGE
    end_index = start_index + IMAGES_PER_PAGE

    visible_images = premium_images[start_index:end_index]

    cols = st.columns(3)

    for index, image_path in enumerate(visible_images):
        with cols[index % 3]:
            preview_path = build_premium_preview(
                image_path
            )

            safe_image_key = hashlib.md5(
                f"premium_gallery_{index}_{image_path}_{image_path.stat().st_mtime}".encode()
            ).hexdigest()

            st.image(
                str(preview_path),
                use_container_width=True,
            )

            action_col1, action_col2, action_col3, action_col4, action_col5 = st.columns(
                [1, 1, 1, 1, 1]
            )

            with action_col1:
                if st.button(
                    "✨",
                    key=f"premium_gallery_prepare_{safe_image_key}",
                    help="Prepare for Premium Publishing",
                    use_container_width=True,
                ):
                    st.toast("✨ Premium publishing prep coming soon!")

            with action_col2:
                if st.button(
                    "📸",
                    key=f"premium_gallery_queue_{safe_image_key}",
                    help="Add to Premium Photoshoot Queue",
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

            with action_col3:
                if st.button(
                    "🎨",
                    key=f"premium_gallery_multi_edit_{safe_image_key}",
                    help="Open in Multi Edit Studio",
                    use_container_width=True,
                ):
                    st.toast("🎨 Premium Multi Edit coming soon!")

            with action_col4:
                if st.button(
                    "🎬",
                    key=f"premium_gallery_video_{safe_image_key}",
                    help="Video Studio Coming Soon",
                    use_container_width=True,
                ):
                    st.toast("🎬 Video Studio coming soon!")

            with action_col5:
                if st.button(
                    "🗑️",
                    key=f"premium_gallery_delete_{safe_image_key}",
                    help="Move to Junk",
                    use_container_width=True,
                ):
                    junk_dir = Path(selected_output_dir) / "Junk-Outdated"

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
                        "🗑️ Moved premium image to Junk"
                    )

                    st.rerun()
         

    render_pagination_controls("bottom")