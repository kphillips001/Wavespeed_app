import hashlib
import shutil
from pathlib import Path

import streamlit as st
from PIL import Image

from app.services.caption_service import (
    generate_social_captions,
    regenerate_platform_captions,
)

from app.ui.image_file_utils import (
    get_unique_image_path,
)

from app.ui.staging_area import (
    move_image_to_staged,
)


IMAGES_PER_PAGE = 24


def render_gallery_image_grid(
    image_paths,
    selected_output_dir,
    columns=3,
    page_key="gallery",
    mode="gallery",
):
    if not image_paths:
        st.warning("No images found.")
        return

    selected_output_dir = Path(selected_output_dir)

    def build_gallery_preview(image_path):
        preview_dir = selected_output_dir / "_gallery_preview_cache"

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

    total_images = len(image_paths)

    total_pages = max(
        1,
        (total_images + IMAGES_PER_PAGE - 1) // IMAGES_PER_PAGE,
    )

    current_page_key = f"{page_key}_page"

    if current_page_key not in st.session_state:
        st.session_state[current_page_key] = 1

    current_page = st.session_state[current_page_key]

    if current_page > total_pages:
        current_page = total_pages
        st.session_state[current_page_key] = current_page

    def render_pagination_controls(location):
        nav_col1, nav_col2, nav_col3 = st.columns([6, 1, 1])

        with nav_col1:
            st.caption(
                f"Page {current_page} of {total_pages} • {total_images} image(s)"
            )

        with nav_col2:
            if st.button(
                "← Prev",
                key=f"{page_key}_prev_{location}",
                use_container_width=True,
                disabled=current_page <= 1,
            ):
                st.session_state[current_page_key] = current_page - 1
                st.rerun()

        with nav_col3:
            if st.button(
                "Next →",
                key=f"{page_key}_next_{location}",
                use_container_width=True,
                disabled=current_page >= total_pages,
            ):
                st.session_state[current_page_key] = current_page + 1
                st.rerun()

    render_pagination_controls("top")

    start_index = (current_page - 1) * IMAGES_PER_PAGE
    end_index = start_index + IMAGES_PER_PAGE

    visible_images = image_paths[start_index:end_index]

    photoshoot_queue_dir = Path(
        r"D:\Ava Blackthorne\Ready\Wavespeed\Photoshoot"
    )

    photoshoot_queue_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    cols = st.columns(columns)

    for index, image_path in enumerate(visible_images):
        with cols[index % columns]:
            preview_path = build_gallery_preview(
                image_path
            )

            safe_image_key = hashlib.md5(
                f"{page_key}_{mode}_{index}_{image_path}_{image_path.stat().st_mtime}".encode()
            ).hexdigest()

            if mode == "gallery":

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
                        key=f"prepare_stage_{page_key}_{image_path}",
                        help="Prepare for Publishing",
                        use_container_width=True,
                    ):
                        success = move_image_to_staged(
                            image_path
                        )

                        if success:
                            st.session_state["save_toast_message"] = (
                                "✨ Moved image to Staged"
                            )
                        else:
                            st.session_state["save_toast_message"] = (
                                "⚠️ Staged area is full"
                            )

                        st.rerun()

                with action_col2:
                    if st.button(
                        "📸",
                        key=f"gallery_queue_{page_key}_{image_path}",
                        help="Add to Photoshoot Queue",
                        use_container_width=True,
                    ):
                        queue_path = get_unique_image_path(
                            photoshoot_queue_dir,
                            image_path.name,
                        )

                        shutil.move(
                            str(image_path),
                            str(queue_path),
                        )

                        st.session_state["save_toast_message"] = (
                            "📸 Added image to Photoshoot Queue"
                        )

                        st.rerun()

                with action_col3:
                    if st.button(
                        "🎨",
                        key=f"gallery_multi_edit_{page_key}_{image_path}",
                        help="Open in Multi Edit Studio",
                        use_container_width=True,
                    ):
                        st.session_state["multi_edit_source_image"] = str(image_path)
                        st.session_state["multi_edit_origin"] = "social"
                        st.session_state["show_multi_edit_studio"] = True
                        st.session_state["show_gallery"] = False
                        st.session_state["show_photoshoot_queue"] = False
                        st.session_state["show_staging_area"] = False
                        st.session_state["active_photoshoot"] = False

                        st.session_state["save_toast_message"] = (
                            "🎨 Sent image to Multi Edit Studio"
                        )

                        st.rerun()

                with action_col4:
                    if st.button(
                        "🎬",
                        key=f"gallery_video_{page_key}_{image_path}",
                        help="Video Studio (Coming Soon)",
                        use_container_width=True,
                    ):
                        st.toast(
                            "🎬 Video Studio coming soon!"
                        )

                with action_col5:
                    if st.button(
                        "🗑️",
                        key=f"gallery_delete_{page_key}_{image_path}",
                        help="Move to Junk",
                        use_container_width=True,
                    ):
                        junk_path = selected_output_dir / "Junk-Outdated"

                        junk_path.mkdir(
                            parents=True,
                            exist_ok=True,
                        )

                        destination = get_unique_image_path(
                            junk_path,
                            Path(image_path).name,
                        )

                        shutil.move(
                            str(image_path),
                            str(destination),
                        )

                        st.session_state["save_toast_message"] = (
                            "🗑 Moved image to Junk"
                        )

                        st.rerun()

            elif mode == "staged":

                st.image(
                    str(preview_path),
                    use_container_width=True,
                )

                st.caption(
                    "Ready for captions, reels, and publishing."
                )

                action_col1, action_col2 = st.columns(2)

                with action_col1:

                    if st.button(
                        "✍ Captions",
                        key=f"captions_{safe_image_key}",
                        use_container_width=True,
                    ):

                        with st.spinner(
                            "Generating captions..."
                        ):

                            captions = generate_social_captions(
                                image_path=image_path,
                            )

                        st.session_state[
                            f"captions_{image_path}"
                        ] = captions

                        st.rerun()

                with action_col2:

                    if st.button(
                        "↩ Gallery",
                        key=f"return_gallery_{safe_image_key}",
                        use_container_width=True,
                    ):

                        destination = get_unique_image_path(
                            selected_output_dir,
                            image_path.name,
                        )

                        shutil.move(
                            str(image_path),
                            str(destination),
                        )

                        st.session_state[
                            "save_toast_message"
                        ] = (
                            "↩ Moved image back to Gallery"
                        )

                        st.rerun()

                caption_data = st.session_state.get(
                    f"captions_{image_path}"
                )

                if caption_data:

                    with st.expander(
                        "Generated Captions",
                        expanded=True,
                    ):

                        st.markdown("### Instagram")

                        instagram_captions = caption_data.get(
                            "instagram",
                            []
                        )

                        selected_ig_caption = ""

                        if instagram_captions:

                            selected_ig_caption = st.radio(
                                "Select Instagram Caption",
                                instagram_captions,
                                key=f"selected_ig_caption_{safe_image_key}",
                            )

                        else:

                            st.warning(
                                "No Instagram captions available."
                            )

                        ig_guidance = st.text_input(
                            "Instagram guidance",
                            placeholder="Example: softer, cuter, lake weekend, less flirty...",
                            key=f"ig_guidance_{safe_image_key}",
                        )

                        if st.button(
                            "🔄 Regenerate Instagram Captions",
                            key=f"regen_ig_{safe_image_key}",
                            use_container_width=True,
                        ):

                            with st.spinner(
                                "Regenerating Instagram captions..."
                            ):

                                new_ig = regenerate_platform_captions(
                                    image_path=image_path,
                                    platform="instagram",
                                    extra_instructions=ig_guidance,
                                )

                            caption_data["instagram"] = new_ig.get(
                                "instagram",
                                [],
                            )

                            st.session_state[
                                f"captions_{image_path}"
                            ] = caption_data

                            st.rerun()

                        st.markdown("---")

                        st.markdown("### X")

                        x_captions = caption_data.get(
                            "x",
                            []
                        )

                        selected_x_caption = ""

                        if x_captions:

                            selected_x_caption = st.radio(
                                "Select X Caption",
                                x_captions,
                                key=f"selected_x_caption_{safe_image_key}",
                            )

                        else:

                            st.warning(
                                "No X captions available."
                            )

                        x_guidance = st.text_input(
                            "X guidance",
                            placeholder="Example: more flirty, more interactive, ask a question...",
                            key=f"x_guidance_{safe_image_key}",
                        )

                        if st.button(
                            "🔄 Regenerate X Captions",
                            key=f"regen_x_{safe_image_key}",
                            use_container_width=True,
                        ):

                            with st.spinner(
                                "Regenerating X captions..."
                            ):

                                new_x = regenerate_platform_captions(
                                    image_path=image_path,
                                    platform="x",
                                    extra_instructions=x_guidance,
                                )

                            caption_data["x"] = new_x.get(
                                "x",
                                [],
                            )

                            st.session_state[
                                f"captions_{image_path}"
                            ] = caption_data

                            st.rerun()

                        st.markdown("---")

                        if st.button(
                            "➡ Continue",
                            key=f"review_selected_captions_{safe_image_key}",
                            use_container_width=True,
                        ):

                            st.session_state[
                                "publish_review_image"
                            ] = str(image_path)

                            st.session_state[
                                "publish_review_instagram_caption"
                            ] = selected_ig_caption

                            st.session_state[
                                "publish_review_x_caption"
                            ] = selected_x_caption

                            st.rerun()

    render_pagination_controls("bottom")