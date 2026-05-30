from datetime import datetime
from pathlib import Path

import os
import shutil
import streamlit as st

from app.config.content_paths import (
    get_premium_photoshoot_dir,
    get_premium_gallery_dir,
)

from app.ui.image_file_utils import (
    get_unique_image_path,
)

from app.services.premium_photoshoot_service import (
    generate_premium_photoshoot_prompts,
)

from main import (
    upload_to_imgbb,
    verify_image_url,
    submit_wavespeed_task,
    poll_wavespeed_result,
    download_image,
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

        prompts_key = f"premium_session_prompts_{image_key}"
        count_key = f"premium_session_count_{image_key}"
        direction_key = f"premium_session_direction_{image_key}"

        with cols[index % 2]:
            st.image(
                str(image_path),
                use_container_width=True,
            )

            st.markdown("#### 🔥 Premium Session Setup")

            premium_session_count = st.selectbox(
                "How many premium session images?",
                options=[5, 10],
                index=0,
                key=count_key,
            )

            session_direction = st.text_area(
                "Optional session direction",
                placeholder=(
                    "Example: keep this as a warm couch session, "
                    "girlfriend experience, increasing tension, same room..."
                ),
                key=direction_key,
                height=80,
            )

            generate_prompt_col, generate_image_col = st.columns(2)

            with generate_prompt_col:
                if st.button(
                    "✨ Generate Session Prompts",
                    key=f"generate_premium_session_prompts_{image_key}",
                    use_container_width=True,
                ):
                    with st.spinner("Building continuity-locked GFE session prompts..."):
                        session_prompts = generate_premium_photoshoot_prompts(
                            session_count=premium_session_count,
                            session_direction=session_direction,
                        )

                    st.session_state[prompts_key] = session_prompts
                    st.success(
                        f"Generated {len(session_prompts)} premium session prompts."
                    )

            with generate_image_col:
                generate_images_disabled = not st.session_state.get(prompts_key)

                if st.button(
                    "🔥 Generate Images",
                    key=f"generate_premium_session_images_{image_key}",
                    use_container_width=True,
                    disabled=generate_images_disabled,
                ):
                    wavespeed_key = os.getenv("WAVESPEED_API_KEY")
                    imgbb_key = os.getenv("IMGBB_API_KEY")
                    wan_endpoint = os.getenv("WAN_27_IMAGE_EDIT_ENDPOINT")

                    if not wavespeed_key:
                        st.error("Missing WAVESPEED_API_KEY in .env")
                        return

                    if not imgbb_key:
                        st.error("Missing IMGBB_API_KEY in .env")
                        return

                    if not wan_endpoint:
                        st.error(
                            "Missing WAN_27_IMAGE_EDIT_ENDPOINT in .env. "
                            "Add your WAN 2.7 image-edit endpoint before generating."
                        )
                        return

                    session_output_dir = premium_gallery_dir / f"premium_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    session_output_dir.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    prompts = st.session_state.get(prompts_key, [])

                    with st.spinner("Uploading seed image and generating premium session..."):
                        image_url = upload_to_imgbb(
                            str(image_path),
                            imgbb_key,
                        )

                        verify_image_url(image_url)

                        saved_count = 0

                        for prompt_index, prompt in enumerate(prompts, start=1):
                            try:
                                request_id = submit_wavespeed_task(
                                    prompt=prompt,
                                    image_url=image_url,
                                    api_key=wavespeed_key,
                                    model_url=wan_endpoint,
                                )

                                output_url = poll_wavespeed_result(
                                    request_id,
                                    wavespeed_key,
                                )

                                final_path = session_output_dir / f"premium_session_{prompt_index:03d}.png"

                                download_image(
                                    output_url,
                                    str(final_path),
                                )

                                saved_count += 1

                            except Exception as error:
                                st.warning(
                                    f"Prompt {prompt_index} failed and was skipped: {error}"
                                )

                    st.success(
                        f"Premium session complete. Saved {saved_count}/{len(prompts)} images."
                    )

            if st.session_state.get(prompts_key):
                with st.expander(
                    "View Premium Session Prompts",
                    expanded=False,
                ):
                    edited_prompts = []

                    for prompt_index, prompt in enumerate(
                        st.session_state[prompts_key],
                        start=1,
                    ):
                        edited_prompt = st.text_area(
                            f"Session Prompt {prompt_index}",
                            value=prompt,
                            height=130,
                            key=f"premium_session_prompt_edit_{image_key}_{prompt_index}",
                        )

                        edited_prompts.append(edited_prompt)

                    if st.button(
                        "💾 Save Edited Session Prompts",
                        key=f"save_edited_premium_session_prompts_{image_key}",
                        use_container_width=True,
                    ):
                        st.session_state[prompts_key] = edited_prompts
                        st.success("Edited premium session prompts saved.")

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

                    shutil.move(
                        str(image_path),
                        str(destination),
                    )

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
                    st.session_state["save_toast_message"] = "Removed from Premium Photoshoot Queue"
                    st.rerun()