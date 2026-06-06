from datetime import datetime

import requests
import streamlit as st

from app.config.settings import MODELS
from app.prompts.generation_modes import GENERATION_MODES
from app.prompts.prompt_builder import build_chatgpt_prompt
from app.services.batch_state_service import save_current_batch_state
from app.services.session_reset_service import reset_social_studio_session
from app.services.social_lucky_service import generate_lucky_social_tags
from app.ui.components.reference_image_selector import (
    render_reference_image_selector,
)
from app.ui.image_file_utils import get_unique_image_path

from main import (
    generate_prompts_with_grok,
    poll_wavespeed_result,
    submit_wavespeed_task,
    upload_to_imgbb,
    verify_image_url,
)


def save_generated_image_now(
    image_url,
    output_dir,
    index,
):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f"ui_{timestamp}_{index:03d}.png"

    image_path = get_unique_image_path(
        output_dir,
        image_filename,
    )

    response = requests.get(
        image_url,
        timeout=60,
    )

    response.raise_for_status()

    with open(image_path, "wb") as file:
        file.write(response.content)

    return str(image_path)


def render_social_content_studio(
    selected_output_dir,
    selected_creator_name,
    reference_images_dir,
    generation_mode,
    platform_mode,
    spice_level,
    prompt_count,
    grok_key,
    wavespeed_key,
    imgbb_key,
):
    selected_reference_image = render_reference_image_selector(
        reference_dir=reference_images_dir,
        session_key="social_selected_reference_image",
        title="Reference Image Library",
        columns=6,
    )

    has_reference_image = selected_reference_image is not None

    if not has_reference_image:
        st.markdown(
            """
            <p style="
                color:#dc2626;
                font-weight:600;
                margin-bottom:0;
            ">
            ⚠️ Reference Image Must Be Selected before continuing.
            </p>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    def fill_lucky_tags():
        lucky_tags = generate_lucky_social_tags(
            prompt_count=prompt_count
        )

        if isinstance(lucky_tags, list):
            lucky_tags = ", ".join(
                str(tag).strip()
                for tag in lucky_tags
                if str(tag).strip()
            )

        st.session_state["creative_tags_input_box"] = str(
            lucky_tags
        ).strip()

    title_col, lucky_col = st.columns([8, 2])

    with title_col:
        st.subheader("Creative Tags")

    with lucky_col:
        st.markdown(
            "<div style='height: 18px;'></div>",
            unsafe_allow_html=True,
        )

        lucky_clicked = st.button(
            "🎲 I Feel Lucky",
            key="social_lucky_tags",
            use_container_width=True,
            disabled=not has_reference_image,
        )

        if lucky_clicked:
            fill_lucky_tags()

    st.caption(
        "Enter ideas, not prompts. The Creative Director will build the shoot."
    )

    if "creative_tags_input_box" not in st.session_state:
        st.session_state["creative_tags_input_box"] = ""

    user_tags = st.text_area(
        label="Creative Tags",
        key="creative_tags_input_box",
        placeholder=(
            "Select a reference image before entering creative tags..."
            if not has_reference_image
            else "Type your creative tags here..."
        ),
        label_visibility="collapsed",
        disabled=not has_reference_image,
    )

    get_prompts_button_label = (
        "🔄 Get Fresh New Prompts"
        if st.session_state.get("generated_prompts")
        else "✨ Get Prompts"
    )

    get_prompts_clicked = st.button(
        get_prompts_button_label,
        use_container_width=True,
        disabled=not has_reference_image,
    )

    if get_prompts_clicked:
        if not user_tags.strip():
            st.error("Please enter some creative tags.")
            st.stop()

        if not grok_key:
            st.error("Missing GROK_API_KEY in .env")
            st.stop()

        st.info("Generating prompts with Grok...")

        selected_generation_mode = None

        for mode in GENERATION_MODES.values():
            if mode["name"] == generation_mode:
                selected_generation_mode = mode
                break

        meta_prompt = build_chatgpt_prompt(
            prompt_count=prompt_count,
            user_request=user_tags,
            generation_mode=selected_generation_mode,
            platform_mode=platform_mode,
            spice_level=spice_level,
        )

        refresh_nonce = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )

        meta_prompt += f"""

IMPORTANT FRESHNESS RULE:

This is a regeneration request.

Create a completely new prompt batch.

Do not repeat:
- previous poses
- previous camera angles
- previous framing
- previous body positions
- previous scene compositions
- previous wording

Keep the same creative tags, but make the ideas feel fresh.

Fresh request ID: {refresh_nonce}
"""

        prompts = generate_prompts_with_grok(
            meta_prompt,
            grok_key,
        )

        for key in list(st.session_state.keys()):
            if key.startswith("text_prompt_"):
                del st.session_state[key]

        if "prompt_batch_id" not in st.session_state:
            st.session_state["prompt_batch_id"] = 0

        st.session_state["prompt_batch_id"] += 1
        prompt_batch_id = st.session_state["prompt_batch_id"]

        st.session_state["generated_prompts"] = [
            {
                "id": f"prompt_{prompt_batch_id}_{i}",
                "text": prompt,
            }
            for i, prompt in enumerate(prompts, start=1)
        ]

        st.session_state["last_generation_mode"] = generation_mode
        st.session_state["last_platform_mode"] = platform_mode
        st.session_state["last_spice_level"] = spice_level
        st.session_state["last_prompt_count"] = prompt_count
        st.session_state["last_user_tags"] = user_tags
        st.session_state["generated_images"] = []
        st.session_state["failed_images"] = []
        st.session_state["generation_complete"] = False
        st.session_state["review_mode"] = "review"

        st.success("Prompt batch generated.")
        st.rerun()

    if st.session_state.get("generated_prompts"):
        with st.expander("View Generated Prompts", expanded=False):
            for i, prompt_item in enumerate(
                st.session_state["generated_prompts"],
                start=1,
            ):
                prompt_id = prompt_item["id"]
                prompt_text = prompt_item["text"]

                st.markdown(f"### Prompt {i}")

                st.text_area(
                    label=f"Prompt {i}",
                    value=prompt_text,
                    height=120,
                    key=f"text_{prompt_id}",
                    label_visibility="collapsed",
                )

                if st.button(
                    f"🗑️ Delete Prompt {i}",
                    key=f"delete_{prompt_id}",
                ):
                    st.session_state["generated_prompts"] = [
                        item
                        for item in st.session_state["generated_prompts"]
                        if item["id"] != prompt_id
                    ]

                    st.rerun()

        st.info(
            f"{len(st.session_state['generated_prompts'])} prompt(s) currently selected for future image generation."
        )

        st.markdown("### User Tags")
        st.code(
            st.session_state.get(
                "last_user_tags",
                user_tags,
            )
        )

    render_col1, render_col2 = st.columns(2)

    with render_col1:
        create_nano_clicked = st.button(
            "🍌 Generate with Nano Pro",
            use_container_width=True,
            disabled=(
                not has_reference_image
                or not st.session_state.get("generated_prompts")
            ),
        )

    with render_col2:
        create_wan_clicked = st.button(
            "🔥 Generate with WAN 2.7",
            use_container_width=True,
            disabled=(
                not has_reference_image
                or not st.session_state.get("generated_prompts")
            ),
        )

    create_shoot_clicked = (
        create_nano_clicked
        or create_wan_clicked
    )

    has_resettable_state = (
        bool(st.session_state.get("generated_prompts"))
        or bool(st.session_state.get("generated_images"))
        or bool(st.session_state.get("failed_images"))
        or bool(st.session_state.get("generation_status"))
        or bool(st.session_state.get("generation_complete"))
        or bool(st.session_state.get("last_user_tags"))
    )

    if has_resettable_state:
        reset_clicked = st.button(
            "🔴 Reset Session",
            use_container_width=True,
        )

        if reset_clicked:
            reset_social_studio_session()
            st.rerun()

    if create_shoot_clicked:
        if not st.session_state.get("generated_prompts"):
            st.error("Get prompts first before creating a shoot.")
            st.stop()

        if not has_reference_image:
            st.error(
                "Please upload or select a reference image before creating a shoot."
            )
            st.stop()

        if not wavespeed_key:
            st.error("Missing WAVESPEED_API_KEY in .env")
            st.stop()

        if not imgbb_key:
            st.error("Missing IMGBB_API_KEY in .env")
            st.stop()

        if create_nano_clicked:
            selected_model = MODELS["2"]

        else:
            selected_model = MODELS["WAN_2_7"]
        
        total_prompts = len(st.session_state["generated_prompts"])

        st.warning(
            f"Creating {total_prompts} image(s) with {selected_model['name']}. This will use WaveSpeed credits."
        )

        status_box = st.empty()
        progress_bar = st.progress(0)
        live_gallery = st.empty()

        with st.spinner("Uploading reference image to ImgBB..."):
            image_url = upload_to_imgbb(
                selected_reference_image,
                imgbb_key,
            )

            verify_image_url(image_url)

        st.session_state["generated_images"] = []
        st.session_state["failed_images"] = []
        st.session_state["review_mode"] = "review"
        st.session_state["discard_happened"] = False
        st.session_state["last_saved_folder"] = None
        st.session_state["generation_status"] = ""
        st.session_state["generation_complete"] = False

        for index, prompt_item in enumerate(
            st.session_state["generated_prompts"],
            start=1,
        ):
            prompt_text = prompt_item["text"]

            completed_count = len(st.session_state["generated_images"])
            failed_count = len(st.session_state["failed_images"])
            remaining_count = total_prompts - completed_count - failed_count

            st.session_state["generation_status"] = (
                f"Image {index} of {total_prompts}: processing...   "
                f"✅ {completed_count} completed   "
                f"❌ {failed_count} failed   "
                f"⏳ {remaining_count} remaining"
            )

            status_box.info(st.session_state["generation_status"])

            try:
                request_id = submit_wavespeed_task(
                    prompt=prompt_text,
                    image_url=image_url,
                    api_key=wavespeed_key,
                    model_url=selected_model["endpoint"],
                )

                output_url = poll_wavespeed_result(
                    request_id=request_id,
                    api_key=wavespeed_key,
                )

                saved_image_path = save_generated_image_now(
                    image_url=output_url,
                    output_dir=selected_output_dir,
                    index=index,
                )

                st.session_state["generated_images"].append(
                    {
                        "id": f"image_{index}",
                        "prompt": prompt_text,
                        "url": output_url,
                        "saved_path": saved_image_path,
                        "status": "completed",
                    }
                )

                save_current_batch_state(
                    creator_name=selected_creator_name,
                    creative_tags=st.session_state.get(
                        "last_user_tags",
                        "",
                    ),
                    generated_prompts=[
                        item["text"]
                        for item in st.session_state.get(
                            "generated_prompts",
                            [],
                        )
                    ],
                    generated_image_paths=[
                        item.get("saved_path", item.get("url"))
                        for item in st.session_state.get(
                            "generated_images",
                            [],
                        )
                    ],
                )

                with live_gallery.container():
                    st.markdown("---")
                    st.subheader("Live Generated Images")

                    current_images = list(
                        reversed(
                            st.session_state["generated_images"]
                        )
                    )

                    cols = st.columns(3)

                    for i, image_item in enumerate(current_images):
                        with cols[i % 3]:
                            st.image(
                                image_item["url"],
                                use_container_width=True,
                            )

            except Exception as error:
                st.session_state["failed_images"].append(
                    {
                        "id": f"image_{index}",
                        "prompt": prompt_text,
                        "error": str(error),
                        "status": "failed",
                    }
                )

            completed_count = len(st.session_state["generated_images"])
            failed_count = len(st.session_state["failed_images"])
            remaining_count = total_prompts - completed_count - failed_count

            st.session_state["generation_status"] = (
                f"Image {index} of {total_prompts}: processing...   "
                f"✅ {completed_count} completed   "
                f"❌ {failed_count} failed   "
                f"⏳ {remaining_count} remaining"
            )

            status_box.info(st.session_state["generation_status"])
            progress_bar.progress(index / total_prompts)

        completed_count = len(st.session_state["generated_images"])
        failed_count = len(st.session_state["failed_images"])

        st.session_state["generation_complete"] = True

        st.session_state["generation_status"] = (
            f"Generation complete. "
            f"✅ {completed_count} completed   "
            f"❌ {failed_count} failed"
        )

        if failed_count == 0:
            status_box.success(st.session_state["generation_status"])
        else:
            status_box.warning(st.session_state["generation_status"])

        st.success(
            f"Saved {completed_count} generated image(s) directly to gallery folder."
        )

    if (
        st.session_state.get("generation_complete", False)
        and st.session_state.get("generated_images")
    ):
        open_content_gallery_clicked = st.button(
            "Open Content Gallery",
            use_container_width=True,
            key="open_content_gallery_after_generation",
        )

        if open_content_gallery_clicked:
            st.session_state["show_gallery"] = True
            st.session_state["show_photoshoot_queue"] = False
            st.session_state["show_staging_area"] = False
            st.session_state["active_photoshoot"] = False
            st.session_state["show_premium_studio"] = False
            st.rerun()
