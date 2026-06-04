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

from app.services.x_publish_service import (
    publish_to_x,
)

from app.services.published_image_service import (
    handle_successful_publish,
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
                        "📦",
                        key=f"stage_{safe_image_key}",
                        help="Move to Staging Area",
                        use_container_width=True,
                    ):
                        success = move_image_to_staged(
                            image_path
                        )

                        if success:
                            st.session_state["save_toast_message"] = (
                                "📦 Moved image to Staging Area"
                            )
                        else:
                            st.session_state["save_toast_message"] = (
                                "⚠️ Staging Area is full (10 images max)"
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
                        sent_to_edit_dir = selected_output_dir / "Sent-to-Edit"

                        sent_to_edit_dir.mkdir(
                            parents=True,
                            exist_ok=True,
                        )

                        sent_to_edit_path = get_unique_image_path(
                            sent_to_edit_dir,
                            image_path.name,
                        )

                        shutil.move(
                            str(image_path),
                            str(sent_to_edit_path),
                        )

                        st.session_state["multi_edit_source_image"] = str(sent_to_edit_path)
                        st.session_state["multi_edit_origin"] = "social"
                        st.session_state["show_multi_edit_studio"] = True
                        st.session_state["show_gallery"] = False
                        st.session_state["show_photoshoot_queue"] = False
                        st.session_state["show_staging_area"] = False
                        st.session_state["active_photoshoot"] = False

                        st.session_state["save_toast_message"] = (
                            "🎨 Moved image to Multi Edit Studio"
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
                    "Ready for captions"
                )

                action_col1, action_col2, action_col3, action_col4, action_col5 = st.columns(
                    [1, 1, 1, 1, 1]
                )

                with action_col1:
                    generate_captions_clicked = st.button(
                        "✍️",
                        key=f"captions_{safe_image_key}",
                        help="Generate Captions",
                        use_container_width=True,
                    )

                if generate_captions_clicked:

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
                        "📸",
                        key=f"staging_queue_{safe_image_key}",
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
                        key=f"staging_edit_{safe_image_key}",
                        help="Open Edit Studio",
                        use_container_width=True,
                    ):
                        sent_to_edit_dir = selected_output_dir / "Sent-to-Edit"

                        sent_to_edit_dir.mkdir(
                            parents=True,
                            exist_ok=True,
                        )

                        sent_to_edit_path = get_unique_image_path(
                            sent_to_edit_dir,
                            image_path.name,
                        )

                        shutil.move(
                            str(image_path),
                            str(sent_to_edit_path),
                        )

                        st.session_state["multi_edit_source_image"] = str(sent_to_edit_path)
                        st.session_state["multi_edit_origin"] = "staged"
                        st.session_state["edit_mode"] = None
                        st.session_state["show_multi_edit_studio"] = True
                        st.session_state["show_gallery"] = False
                        st.session_state["show_photoshoot_queue"] = False
                        st.session_state["show_staging_area"] = False
                        st.session_state["active_photoshoot"] = False

                        st.session_state["save_toast_message"] = (
                            "🎨 Moved staged image to Edit Studio"
                        )

                        st.rerun()

                with action_col4:
                    if st.button(
                        "↩️",
                        key=f"return_gallery_{safe_image_key}",
                        help="Move Back to Gallery",
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

                with action_col5:
                    if st.button(
                        "🗑️",
                        key=f"staging_delete_{safe_image_key}",
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
                            image_path.name,
                        )

                        shutil.move(
                            str(image_path),
                            str(destination),
                        )

                        st.session_state["save_toast_message"] = (
                            "🗑 Moved image to Junk"
                        )

                        st.rerun()

                caption_data = st.session_state.get(
                    f"captions_{image_path}"
                )

                if caption_data:

                    with st.expander(
                        "Generated X Captions",
                        expanded=True,
                    ):

                        x_captions = caption_data.get(
                            "x",
                            []
                        )

                        if x_captions:

                            st.markdown("#### Caption Options")

                            for caption_index, caption in enumerate(
                                x_captions,
                                start=1,
                            ):
                                st.markdown(
                                    f"**{caption_index}.** {caption}"
                                )

                                st.markdown("---")

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

                        st.markdown("### Publish Targets")

                        publish_main = st.checkbox(
                            "AvaBlackthorne",
                            value=True,
                            key=f"publish_main_{safe_image_key}",
                        )

                        publish_backup = st.checkbox(
                            "AvaBlackthorneX",
                            value=False,
                            key=f"publish_backup_{safe_image_key}",
                        )

                        caption_options = [
                            f"{idx}. {caption}"
                            for idx, caption in enumerate(
                                x_captions,
                                start=1,
                            )
                        ]

                        selected_main_caption = None
                        selected_backup_caption = None

                        if publish_main:

                            selected_main_caption = st.selectbox(
                                "Caption for AvaBlackthorne",
                                options=caption_options,
                                index=0,
                                key=f"main_caption_{safe_image_key}",
                            )

                        if publish_backup:

                            selected_backup_caption = st.selectbox(
                                "Caption for AvaBlackthorneX",
                                options=caption_options,
                                index=0,
                                key=f"backup_caption_{safe_image_key}",
                            )

                        publish_clicked = st.button(
                            "🚀 Publish Selected",
                            key=f"publish_x_{safe_image_key}",
                            use_container_width=True,
                        )

                        if publish_clicked:

                            published_accounts = []

                            try:
                                if publish_main and selected_main_caption:

                                    main_caption_text = selected_main_caption.split(
                                        ". ",
                                        1,
                                    )[1]

                                    publish_to_x(
                                        image_path=image_path,
                                        caption=main_caption_text,
                                        account_name="AvaBlackthorne",
                                    )

                                    published_accounts.append(
                                        "AvaBlackthorne"
                                    )

                                if publish_backup and selected_backup_caption:

                                    backup_caption_text = selected_backup_caption.split(
                                        ". ",
                                        1,
                                    )[1]

                                    publish_to_x(
                                        image_path=image_path,
                                        caption=backup_caption_text,
                                        account_name="AvaBlackthorneX",
                                    )

                                    published_accounts.append(
                                        "AvaBlackthorneX"
                                    )

                                if published_accounts:

                                    handle_successful_publish(
                                        image_path=image_path,
                                        published_accounts=published_accounts,
                                    )

                                    st.session_state["save_toast_message"] = (
                                        "🚀 Published to: "
                                        + ", ".join(published_accounts)
                                    )

                                    st.rerun()

                                else:
                                    st.warning(
                                        "Select at least one account before publishing."
                                    )

                            except Exception as error:
                                st.error(
                                    f"Publishing failed: {error}"
                                )
    render_pagination_controls("bottom")