from datetime import datetime
from pathlib import Path
import shutil

import streamlit as st

from app.config.content_paths import (
    get_premium_gallery_dir,
)

from app.ui.image_file_utils import (
    get_unique_image_path,
)

from app.services.premium_photoshoot_service import (
    analyze_premium_reference_image,
    generate_premium_photoshoot_prompts,
)

from app.services.premium_render_service import (
    generate_premium_images,
)

IMAGE_SUFFIXES = [".png", ".jpg", ".jpeg", ".webp"]
PREMIUM_PHOTOSHOOT_RENDERER = "WAN 2.7 Image Edit"


def get_premium_queue_dir(selected_output_dir):
    return Path(selected_output_dir) / "Premium" / "Photoshoot"


class LocalImageUpload:
    def __init__(self, image_path):
        self.image_path = Path(image_path)
        self.name = self.image_path.name

    def getbuffer(self):
        return self.image_path.read_bytes()


def create_premium_photoshoot_session_dir(premium_photoshoot_dir):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = premium_photoshoot_dir / f"photoshoot_premium_{timestamp}"
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


def move_reference_to_session(image_path, session_dir):
    reference_name = f"source_reference{image_path.suffix.lower()}"
    destination = get_unique_image_path(session_dir, reference_name)
    shutil.move(str(image_path), str(destination))
    return destination


def get_image_files(folder_path):
    return sorted(
        [
            image_path
            for image_path in folder_path.iterdir()
            if image_path.is_file()
            and image_path.suffix.lower() in IMAGE_SUFFIXES
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def get_completed_session_dirs(premium_photoshoot_dir):
    return sorted(
        [
            folder_path
            for folder_path in premium_photoshoot_dir.iterdir()
            if folder_path.is_dir()
            and folder_path.name.startswith("photoshoot_premium_")
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def get_unique_folder_path(parent_dir, folder_name):
    parent_path = Path(parent_dir)
    candidate_path = parent_path / folder_name

    if not candidate_path.exists():
        return candidate_path

    counter = 2

    while True:
        numbered_path = parent_path / f"{folder_name}_{counter}"

        if not numbered_path.exists():
            return numbered_path

        counter += 1


def get_premium_photoshoot_junk_dir(premium_photoshoot_dir):
    junk_dir = premium_photoshoot_dir / "_Junk_Premium_Photoshoots"
    junk_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    return junk_dir


def move_path_to_junk(path_to_move, junk_root, folder_name=None):
    path_to_move = Path(path_to_move)
    junk_root = Path(junk_root)

    if folder_name:
        target_parent = junk_root / folder_name
        target_parent.mkdir(
            parents=True,
            exist_ok=True,
        )
    else:
        target_parent = junk_root

    if path_to_move.is_dir():
        destination = get_unique_folder_path(
            target_parent,
            path_to_move.name,
        )
    else:
        destination = get_unique_image_path(
            target_parent,
            path_to_move.name,
        )

    shutil.move(
        str(path_to_move),
        str(destination),
    )

    return destination


def render_completed_premium_sessions(premium_photoshoot_dir):
    session_dirs = get_completed_session_dirs(
        premium_photoshoot_dir
    )

    if not session_dirs:
        return

    st.markdown("---")
    st.subheader("Completed Premium Photoshoots")

    junk_dir = get_premium_photoshoot_junk_dir(
        premium_photoshoot_dir
    )

    for session_dir in session_dirs:
        session_images = get_image_files(
            session_dir
        )

        if not session_images:
            continue

        with st.expander(
            f"{session_dir.name} - {len(session_images)} image(s)",
            expanded=(
                st.session_state.get("open_premium_photoshoot_session")
                == session_dir.name
            ),
        ):
            st.caption(
                str(session_dir)
            )

            delete_session_key = f"delete_premium_session_confirm_{session_dir.name}"

            st.checkbox(
                "Confirm delete entire photoshoot",
                key=delete_session_key,
            )

            if st.button(
                "Delete Entire Photoshoot",
                key=f"delete_premium_session_{session_dir.name}",
                use_container_width=True,
                disabled=not st.session_state.get(delete_session_key, False),
            ):
                if session_dir.parent == premium_photoshoot_dir:
                    move_path_to_junk(
                        session_dir,
                        junk_dir,
                    )
                    st.session_state["save_toast_message"] = (
                        f"Moved premium photoshoot {session_dir.name} to junk"
                    )
                    st.session_state["open_premium_photoshoot_session"] = None
                    st.rerun()

            cols = st.columns(4)

            for image_index, image_path in enumerate(session_images):
                with cols[image_index % 4]:
                    st.image(
                        str(image_path),
                        use_container_width=True,
                    )

                    if st.button(
                        "Delete Image",
                        key=(
                            "delete_premium_session_image_"
                            f"{session_dir.name}_{image_path.name}"
                        ),
                        use_container_width=True,
                    ):
                        move_path_to_junk(
                            image_path,
                            junk_dir,
                            folder_name=session_dir.name,
                        )
                        st.session_state["open_premium_photoshoot_session"] = (
                            session_dir.name
                        )
                        st.session_state["save_toast_message"] = (
                            f"Moved {image_path.name} to junk"
                        )
                        st.rerun()


def render_premium_photoshoot_queue(selected_output_dir):
    premium_photoshoot_dir = get_premium_queue_dir(selected_output_dir)
    premium_gallery_dir = get_premium_gallery_dir(selected_output_dir)

    premium_photoshoot_dir.mkdir(parents=True, exist_ok=True)
    premium_gallery_dir.mkdir(parents=True, exist_ok=True)

    st.markdown("---")
    st.subheader("🔥 Premium Photoshoot Queue Manager")

    st.caption(
        "Build small GFE session sets from one winning image. "
        "Same setting. Same atmosphere. Escalating intimacy."
    )

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
        st.session_state["save_toast_message"] = "🔥 Added to Premium Photoshoot Queue"
        st.rerun()

    st.markdown("---")

    premium_photoshoot_images = get_image_files(
        premium_photoshoot_dir
    )

    if not premium_photoshoot_images:
        st.warning("No images currently in Premium Photoshoot Queue.")
        render_completed_premium_sessions(
            premium_photoshoot_dir
        )
        return

    cols = st.columns(2)

    for index, image_path in enumerate(premium_photoshoot_images):
        image_key = image_path.stem
        prompts_key = f"premium_session_prompts_{image_key}"

        with cols[index % 2]:
            st.image(str(image_path), use_container_width=True)

            st.markdown("#### 🔥 Premium Session Setup")

            session_count = st.selectbox(
                "How many premium session images?",
                options=[5, 10],
                index=0,
                key=f"premium_session_count_{image_key}",
            )

            session_direction = st.text_area(
                "Optional session direction",
                placeholder=(
                    "Optional: keep night pool setting, closer angles, "
                    "more playful expressions, same coverage..."
                ),
                height=80,
                key=f"premium_session_direction_{image_key}",
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "✨ Generate Session Prompts",
                    key=f"generate_session_prompts_{image_key}",
                    use_container_width=True,
                ):
                    with st.spinner("Analyzing reference and building continuity-locked session prompts..."):
                        reference_context = analyze_premium_reference_image(
                            image_path
                        )

                        session_prompts = generate_premium_photoshoot_prompts(
                            session_count=session_count,
                            session_direction=session_direction,
                            reference_context=reference_context,
                        )

                    st.session_state[prompts_key] = [
                        {
                            "id": f"premium_session_prompt_{prompt_index}",
                            "text": prompt,
                        }
                        for prompt_index, prompt in enumerate(session_prompts, start=1)
                    ]

                    st.success(
                        f"Generated {len(st.session_state[prompts_key])} session prompts."
                    )

            with col2:
                generate_disabled = not st.session_state.get(prompts_key)

                if st.button(
                    "🔥 Generate Images",
                    key=f"generate_session_images_{image_key}",
                    use_container_width=True,
                    disabled=generate_disabled,
                ):
                    progress_bar = st.progress(0)
                    status_placeholder = st.empty()
                    live_gallery = st.empty()

                    def update_progress(
                        current,
                        total,
                        message,
                        generated_images=None,
                        failed_images=None,
                    ):
                        progress_value = 0

                        if total > 0:
                            progress_value = int((current / total) * 100)

                        progress_bar.progress(progress_value)

                        completed_count = len(generated_images or [])
                        failed_count = len(failed_images or [])
                        remaining_count = total - completed_count - failed_count

                        status_placeholder.info(
                            f"{message} "
                            f"✅ {completed_count} completed "
                            f"❌ {failed_count} failed "
                            f"⏳ {remaining_count} remaining"
                        )

                        if generated_images:
                            with live_gallery.container():
                                st.markdown("---")
                                st.subheader("Live Premium Session Images")

                                live_cols = st.columns(3)

                                for image_index, image_item in enumerate(generated_images):
                                    with live_cols[image_index % 3]:
                                        st.image(
                                            image_item["url"],
                                            use_container_width=True,
                                        )

                    session_dir = create_premium_photoshoot_session_dir(
                        premium_photoshoot_dir
                    )

                    with st.spinner("Generating Premium Photoshoot Session with WAN 2.7..."):
                        render_results = generate_premium_images(
                            premium_prompts=st.session_state[prompts_key],
                            uploaded_file=LocalImageUpload(image_path),
                            selected_output_dir=selected_output_dir,
                            premium_renderer=PREMIUM_PHOTOSHOOT_RENDERER,
                            progress_callback=update_progress,
                            target_output_dir=session_dir,
                        )

                    generated_count = len(render_results.get("generated_images", []))
                    failed_count = len(render_results.get("failed_images", []))
                    st.session_state["last_premium_session_dir"] = str(session_dir)

                    if failed_count == 0:
                        move_reference_to_session(image_path, session_dir)
                        st.success(
                            f"Premium session complete. "
                            f"{generated_count} completed. Saved to {session_dir}"
                        )
                    else:
                        st.warning(
                            f"Premium session complete. "
                            f"{generated_count} completed, {failed_count} failed. "
                            f"Saved to {session_dir}"
                        )

            if st.session_state.get(prompts_key):
                with st.expander("View / Edit Premium Session Prompts", expanded=False):
                    edited_prompts = []

                    for prompt_index, prompt_data in enumerate(
                        st.session_state[prompts_key],
                        start=1,
                    ):
                        edited_text = st.text_area(
                            f"Session Prompt {prompt_index}",
                            value=prompt_data["text"],
                            height=130,
                            key=f"edit_premium_session_prompt_{image_key}_{prompt_index}",
                        )

                        edited_prompts.append(
                            {
                                "id": prompt_data["id"],
                                "text": edited_text,
                            }
                        )

                    if st.button(
                        "💾 Save Edited Session Prompts",
                        key=f"save_session_prompts_{image_key}",
                        use_container_width=True,
                    ):
                        st.session_state[prompts_key] = edited_prompts
                        st.success("Edited session prompts saved.")
                    
                    if st.button(
                        "🔥 Generate Premium Session",
                        key=f"generate_saved_premium_session_{image_key}",
                        use_container_width=True,
                    ):
                        progress_bar = st.progress(0)
                        status_placeholder = st.empty()
                        live_gallery = st.empty()

                        def update_progress(
                            current,
                            total,
                            message,
                            generated_images=None,
                            failed_images=None,
                        ):
                            progress_value = 0

                            if total > 0:
                                progress_value = int((current / total) * 100)

                            progress_bar.progress(progress_value)

                            completed_count = len(generated_images or [])
                            failed_count = len(failed_images or [])
                            remaining_count = total - completed_count - failed_count

                            status_placeholder.info(
                                f"{message} "
                                f"✅ {completed_count} completed "
                                f"❌ {failed_count} failed "
                                f"⏳ {remaining_count} remaining"
                            )

                            if generated_images:
                                with live_gallery.container():
                                    st.markdown("---")
                                    st.subheader("Live Premium Session Images")

                                    live_cols = st.columns(3)

                                    for image_index, image_item in enumerate(generated_images):
                                        with live_cols[image_index % 3]:
                                            st.image(
                                                image_item["url"],
                                                use_container_width=True,
                                            )

                        session_dir = create_premium_photoshoot_session_dir(
                            premium_photoshoot_dir
                        )

                        with st.spinner("Generating Premium Session with WAN 2.7..."):
                            render_results = generate_premium_images(
                                premium_prompts=st.session_state[prompts_key],
                                uploaded_file=LocalImageUpload(image_path),
                                selected_output_dir=selected_output_dir,
                                premium_renderer=PREMIUM_PHOTOSHOOT_RENDERER,
                                progress_callback=update_progress,
                                target_output_dir=session_dir,
                            )

                        generated_count = len(render_results.get("generated_images", []))
                        failed_count = len(render_results.get("failed_images", []))
                        st.session_state["last_premium_session_dir"] = str(session_dir)

                        if failed_count == 0:
                            move_reference_to_session(image_path, session_dir)
                            st.success(
                                f"Premium session complete. "
                                f"{generated_count} completed. Saved to {session_dir}"
                            )
                        else:
                            st.warning(
                                f"Premium session complete. "
                                f"{generated_count} completed, {failed_count} failed. "
                                f"Saved to {session_dir}"
                            )
                                        

            st.markdown("---")

            action_col1, action_col2 = st.columns(2)

            with action_col1:
                if st.button(
                    "↩ Move To Premium Gallery",
                    key=f"move_premium_gallery_{image_key}",
                    use_container_width=True,
                ):
                    destination = get_unique_image_path(
                        premium_gallery_dir,
                        image_path.name,
                    )

                    shutil.move(str(image_path), str(destination))

                    st.session_state["save_toast_message"] = (
                        "↩ Moved image to Premium Gallery"
                    )

                    st.rerun()

            with action_col2:
                if st.button(
                    "🗑️ Remove From Queue",
                    key=f"remove_premium_queue_{image_key}",
                    use_container_width=True,
                ):
                    image_path.unlink(missing_ok=True)
                    st.session_state["save_toast_message"] = (
                        "Removed from Premium Photoshoot Queue"
                    )
                    st.rerun()

    render_completed_premium_sessions(
        premium_photoshoot_dir
    )
