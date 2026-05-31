from pathlib import Path
import os
import tempfile
import shutil
import requests
from datetime import datetime

import streamlit as st

from main import (
    upload_to_imgbb,
)

from app.services.multi_edit_service import (
    poll_multi_edit_result,
    submit_multi_edit_task,
)

from app.ui.image_file_utils import (
    get_unique_image_path,
)


wavespeed_key = os.getenv(
    "WAVESPEED_API_KEY"
)

imgbb_key = os.getenv(
    "IMGBB_API_KEY"
)

NANO_BANANA_PRO_EDIT_URL = (
    "https://api.wavespeed.ai/api/v3/google/nano-banana-pro/edit"
)

NANO_BANANA_PRO_EDIT_MULTI_URL = (
    "https://api.wavespeed.ai/api/v3/google/nano-banana-pro/edit-multi"
)

WAN_27_IMAGE_EDIT_PRO_URL = (
    "https://api.wavespeed.ai/api/v3/alibaba/wan-2.7/image-edit-pro"
)


def download_result_image(
    result_url,
    destination_path,
):
    response = requests.get(
        result_url,
        timeout=60,
    )

    response.raise_for_status()

    with open(destination_path, "wb") as file:
        file.write(response.content)


def clear_edit_state():
    st.session_state["multi_edit_result_url"] = None
    st.session_state["multi_edit_result_model"] = None
    st.session_state["multi_edit_result_prompt"] = None


def render_result_actions(
    result_url,
    source_path,
):
    st.markdown("---")
    st.markdown("### Generated Result")

    result_preview_col, _ = st.columns([5, 7])

    with result_preview_col:
        st.image(
            result_url,
            use_container_width=True,
        )

        st.caption(
            f"Generated with {st.session_state.get('multi_edit_result_model', 'selected model')}"
        )

        action_col1, action_col2, action_col3, action_col4 = st.columns(4)

        with action_col1:
            if st.button(
                "✨",
                key="edit_to_staging",
                help="Move finished image to Staging",
                use_container_width=True,
            ):
                gallery_root = source_path.parent.parent
                staged_dir = gallery_root / "Staged"

                staged_dir.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                staged_path = get_unique_image_path(
                    staged_dir,
                    f"edit_{timestamp}.png",
                )

                download_result_image(
                    result_url,
                    staged_path,
                )

                st.session_state["save_toast_message"] = (
                    "✨ Edit result moved to Staging"
                )

                clear_edit_state()
                st.session_state["show_multi_edit_studio"] = False
                st.session_state["show_staging_area"] = True
                st.rerun()

        with action_col2:
            if st.button(
                "📸",
                key="edit_to_photoshoot",
                help="Send finished image to Photoshoot Queue",
                use_container_width=True,
            ):
                photoshoot_queue_dir = (
                    source_path.parent.parent
                    / "Photoshoot"
                )

                photoshoot_queue_dir.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                photoshoot_path = get_unique_image_path(
                    photoshoot_queue_dir,
                    f"edit_photoshoot_{timestamp}.png",
                )

                download_result_image(
                    result_url,
                    photoshoot_path,
                )

                st.session_state["save_toast_message"] = (
                    "📸 Edit result sent to Photoshoot Queue"
                )

                clear_edit_state()
                st.session_state["show_multi_edit_studio"] = False
                st.session_state["show_photoshoot_queue"] = True
                st.rerun()

        with action_col3:
            if st.button(
                "↩",
                key="edit_restore_original",
                help="Move original image back to Gallery",
                use_container_width=True,
            ):
                gallery_root = source_path.parent.parent

                return_path = get_unique_image_path(
                    gallery_root,
                    source_path.name,
                )

                shutil.move(
                    str(source_path),
                    str(return_path),
                )

                st.session_state["save_toast_message"] = (
                    "↩ Original image moved back to Gallery"
                )

                st.session_state["multi_edit_source_image"] = None
                clear_edit_state()
                st.session_state["show_multi_edit_studio"] = False
                st.session_state["show_gallery"] = True
                st.rerun()

        with action_col4:
            if st.button(
                "🗑️",
                key="edit_discard_result",
                help="Discard finished image to Junk",
                use_container_width=True,
            ):
                gallery_root = source_path.parent.parent
                junk_dir = gallery_root / "Junk-Outdated"

                junk_dir.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                junk_path = get_unique_image_path(
                    junk_dir,
                    f"discarded_edit_{timestamp}.png",
                )

                download_result_image(
                    result_url,
                    junk_path,
                )

                st.session_state["save_toast_message"] = (
                    "🗑️ Edit result moved to Junk"
                )

                clear_edit_state()
                st.rerun()


def render_edit_landing(
    source_path,
):
    st.markdown("### Choose Edit Type")

    st.image(
        str(source_path),
        width=420,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ✏️ Single Edit")
        st.caption(
            "Use text instructions only. Example: change her skirt to black denim."
        )

        if st.button(
            "Open Single Edit",
            use_container_width=True,
        ):
            st.session_state["edit_mode"] = "single"
            clear_edit_state()
            st.rerun()

    with col2:
        st.markdown("#### 🎨 Multi Edit")
        st.caption(
            "Upload a reference asset. Example: swap in a shirt, purse, lingerie set, or prop."
        )

        if st.button(
            "Open Multi Edit",
            use_container_width=True,
        ):
            st.session_state["edit_mode"] = "multi"
            clear_edit_state()
            st.rerun()


def render_single_edit(
    source_path,
):
    st.markdown("### ✏️ Single Edit")

    source_col, control_col = st.columns([5, 7])

    with source_col:
        st.markdown("#### Source Image")

        st.image(
            str(source_path),
            use_container_width=True,
        )

    with control_col:
        st.markdown("#### Edit Instructions")

        instructions = st.text_area(
            "Describe the edit",
            placeholder="Example: Change her denim skirt to black denim. Keep everything else the same.",
            height=140,
            key="single_edit_instructions",
        )

        selected_model = st.radio(
            "Choose generation model",
            [
                "Nano Banana Pro Edit",
                "WAN 2.7 Image Edit Pro",
            ],
            index=0,
            key="single_edit_model_choice",
        )

        generate_clicked = st.button(
            "🎨 Generate Single Edit",
            use_container_width=True,
            disabled=not instructions.strip(),
        )

    if generate_clicked:

        if not wavespeed_key:
            st.error("Missing WAVESPEED_API_KEY in .env")
            st.stop()

        if not imgbb_key:
            st.error("Missing IMGBB_API_KEY in .env")
            st.stop()

        with st.spinner(
            "Uploading source image..."
        ):
            source_image_url = upload_to_imgbb(
                str(source_path),
                imgbb_key,
            )

        st.toast(
            "Source image uploaded successfully.",
            icon="✅",
        )

        if selected_model == "Nano Banana Pro Edit":
            model_url = NANO_BANANA_PRO_EDIT_URL
        else:
            model_url = WAN_27_IMAGE_EDIT_PRO_URL

        final_prompt = instructions.strip()

        with st.spinner(
            f"Generating with {selected_model}..."
        ):
            request_id = submit_multi_edit_task(
                api_key=wavespeed_key,
                model_url=model_url,
                prompt=final_prompt,
                image_urls=[
                    source_image_url,
                ],
            )

            output_url = poll_multi_edit_result(
                api_key=wavespeed_key,
                request_id=request_id,
            )

        st.session_state["multi_edit_result_url"] = output_url
        st.session_state["multi_edit_result_model"] = selected_model
        st.session_state["multi_edit_result_prompt"] = final_prompt

        st.rerun()


def render_multi_reference_edit(
    source_path,
):
    st.markdown("### 🎨 Multi Edit")

    source_col, reference_col = st.columns(2)

    with source_col:
        st.markdown("#### Source Image")

        st.image(
            str(source_path),
            use_container_width=True,
        )

    with reference_col:
        st.markdown("#### Reference Asset")

        asset_upload = st.file_uploader(
            "Upload clothing, product, prop, or style reference",
            type=["png", "jpg", "jpeg", "webp"],
            key="multi_edit_asset_upload",
        )

        if asset_upload is not None:
            st.image(
                asset_upload,
                use_container_width=True,
            )
        else:
            st.info(
                "Upload a shirt, purse, lingerie set, product, prop, accessory, or style reference."
            )

    st.markdown("### Edit Instructions")

    instructions = st.text_area(
        "Describe the edit",
        placeholder="Example: Only replace the shirt in image 1 with the shirt from image 2. Keep everything else the same.",
        height=140,
        key="multi_edit_instructions",
    )

    st.markdown("### Model")

    selected_model = st.radio(
        "Choose generation model",
        [
            "Nano Banana Pro Edit Multi",
            "WAN 2.7 Image Edit Pro",
        ],
        index=0,
        key="multi_edit_model_choice",
    )

    generate_clicked = st.button(
        "🎨 Generate Multi Edit",
        use_container_width=True,
        disabled=asset_upload is None or not instructions.strip(),
    )

    if generate_clicked:

        if not wavespeed_key:
            st.error("Missing WAVESPEED_API_KEY in .env")
            st.stop()

        if not imgbb_key:
            st.error("Missing IMGBB_API_KEY in .env")
            st.stop()

        with st.spinner(
            "Uploading images..."
        ):
            source_image_url = upload_to_imgbb(
                str(source_path),
                imgbb_key,
            )

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".png",
            ) as temp_file:
                temp_file.write(
                    asset_upload.getbuffer()
                )

                asset_path = temp_file.name

            reference_image_url = upload_to_imgbb(
                asset_path,
                imgbb_key,
            )

        st.toast(
            "Images uploaded successfully.",
            icon="✅",
        )

        if selected_model == "Nano Banana Pro Edit Multi":
            model_url = NANO_BANANA_PRO_EDIT_MULTI_URL
        else:
            model_url = WAN_27_IMAGE_EDIT_PRO_URL

        final_prompt = instructions.strip()

        with st.spinner(
            f"Generating with {selected_model}..."
        ):
            request_id = submit_multi_edit_task(
                api_key=wavespeed_key,
                model_url=model_url,
                prompt=final_prompt,
                image_urls=[
                    source_image_url,
                    reference_image_url,
                ],
            )

            output_url = poll_multi_edit_result(
                api_key=wavespeed_key,
                request_id=request_id,
            )

        st.session_state["multi_edit_result_url"] = output_url
        st.session_state["multi_edit_result_model"] = selected_model
        st.session_state["multi_edit_result_prompt"] = final_prompt

        st.rerun()


def render_multi_edit_studio():
    st.subheader("🎨 Edit Studio")

    source_image = st.session_state.get(
        "multi_edit_source_image"
    )

    if not source_image:
        st.warning("No source image selected yet.")
        return

    source_path = Path(source_image)

    top_col1, top_col2 = st.columns([8, 2])

    with top_col1:
        st.caption(
            "Choose Single Edit for text-only changes, or Multi Edit to use a reference asset."
        )

    with top_col2:
        if st.button(
            "⬅ Back",
            use_container_width=True,
        ):
            st.session_state["edit_mode"] = None
            st.session_state["show_multi_edit_studio"] = False
            st.session_state["show_gallery"] = True
            st.rerun()

    st.markdown("---")

    result_url = st.session_state.get(
        "multi_edit_result_url"
    )

    if result_url:
        render_result_actions(
            result_url,
            source_path,
        )
        return

    edit_mode = st.session_state.get(
        "edit_mode"
    )

    if edit_mode == "single":
        render_single_edit(
            source_path,
        )

    elif edit_mode == "multi":
        render_multi_reference_edit(
            source_path,
        )

    else:
        render_edit_landing(
            source_path,
        )