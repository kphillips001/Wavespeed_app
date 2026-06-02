from datetime import datetime
from pathlib import Path
import time

import requests
import streamlit as st

from app.config.content_paths import (
    get_premium_gallery_dir,
    get_premium_photoshoot_dir,
)

from app.services.premium_director_service import (
    generate_premium_prompts,
    generate_explicit_prompts,
)

from app.services.premium_render_service import (
    generate_premium_images,
)

from app.ui.image_file_utils import (
    get_unique_image_path,
)

from app.services.premium_tag_enhancer_service import (
    enhance_premium_tags,
    surprise_premium_tags,
)


def download_image(image_url, output_path):
    response = requests.get(image_url, timeout=60)
    response.raise_for_status()

    with open(output_path, "wb") as file:
        file.write(response.content)


def save_premium_generated_images(
    images,
    output_dir,
):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_paths = []

    Path(output_dir).mkdir(
        parents=True,
        exist_ok=True,
    )

    for index, image_item in enumerate(images, start=1):
        image_filename = f"premium_{timestamp}_{index:03d}.png"

        image_path = get_unique_image_path(
            output_dir,
            image_filename,
        )

        download_image(
            image_item["url"],
            image_path,
        )

        saved_paths.append(str(image_path))

    return saved_paths


def render_premium_prompt_expander():
    if not st.session_state["premium_prompts"]:
        return

    with st.expander(
        "View Generated Premium Prompts",
        expanded=True,
    ):
        prompts_to_delete = []

        for index, prompt_data in enumerate(
            st.session_state["premium_prompts"],
            start=1,
        ):
            prompt_id = prompt_data["id"]

            st.markdown(f"### Premium Prompt {index}")

            updated_prompt_text = st.text_area(
                label=f"Premium Prompt {index}",
                value=prompt_data["text"],
                height=140,
                label_visibility="collapsed",
                key=f"premium_prompt_edit_{prompt_id}",
            )

            prompt_data["text"] = updated_prompt_text

            if st.button(
                "🗑️ Delete This Prompt",
                key=f"delete_premium_prompt_{prompt_id}",
                use_container_width=True,
            ):
                prompts_to_delete.append(prompt_id)

            st.divider()

        if prompts_to_delete:
            st.session_state["premium_prompts"] = [
                prompt_data
                for prompt_data in st.session_state["premium_prompts"]
                if prompt_data["id"] not in prompts_to_delete
            ]

            st.rerun()


def render_premium_generated_image_gallery(
    selected_output_dir,
):
    if (
        not st.session_state["premium_generated_images"]
        or not st.session_state.get("premium_generation_complete", False)
    ):
        return

    st.markdown("---")
    st.subheader("Final Generated Images")

    cols = st.columns(3)

    for i, image_item in enumerate(st.session_state["premium_generated_images"]):
        image_id = image_item.get("id", f"premium_image_{i + 1}")

        with cols[i % 3]:

            st.image(image_item["url"], use_container_width=True)

            st.checkbox("Discard", key=f"premium_discard_{image_id}")

            st.checkbox(
                "📸 Continue Photoshoot",
                key=f"premium_photoshoot_{image_id}",
            )

            st.checkbox(
                "📖 Create Story (Coming Soon)",
                key=f"premium_story_{image_id}",
                disabled=True,
            )

            with st.expander("Prompt"):
                st.write(image_item["prompt"])

    st.markdown("---")

    discard_ids = []
    photoshoot_ids = []

    for image_item in st.session_state["premium_generated_images"]:
        image_id = image_item.get("id")

        if st.session_state.get(f"premium_discard_{image_id}", False):
            discard_ids.append(image_id)

        if st.session_state.get(f"premium_photoshoot_{image_id}", False):
            photoshoot_ids.append(image_id)

    photoshoot_ids = [
        image_id for image_id in photoshoot_ids
        if image_id not in discard_ids
    ]

    if discard_ids:
        button_label = "🗑️ Discard Selected"
    else:
        button_label = "💾 Save All Images"

    if st.button(button_label, use_container_width=True):

        if discard_ids:

            st.session_state["premium_generated_images"] = [
                img for img in st.session_state["premium_generated_images"]
                if img["id"] not in discard_ids
            ]

            st.session_state["save_toast_message"] = (
                f"🗑️ Discarded {len(discard_ids)} premium image(s)"
            )

            st.rerun()

        else:

            st.session_state["save_toast_message"] = (
                f"✅ Saved {len(st.session_state['premium_generated_images'])} premium image(s). "
                f"📸 Sent {len(photoshoot_ids)} premium image(s) to Photoshoot."
            )

            st.session_state["save_toast_time"] = time.time()

            st.session_state["premium_generated_images"] = []
            st.session_state["premium_failed_images"] = []
            st.session_state["premium_prompts"] = []
            st.session_state["premium_generation_complete"] = False

            st.session_state["premium_uploader_key"] += 1

            st.rerun()


def render_premium_content_studio(
    selected_output_dir,
):
    st.subheader("Reference Image")

    if "premium_uploader_key" not in st.session_state:
        st.session_state["premium_uploader_key"] = 0

    if "premium_prompts" not in st.session_state:
        st.session_state["premium_prompts"] = []

    if "premium_generated_images" not in st.session_state:
        st.session_state["premium_generated_images"] = []

    if "premium_failed_images" not in st.session_state:
        st.session_state["premium_failed_images"] = []

    if "premium_generation_complete" not in st.session_state:
        st.session_state["premium_generation_complete"] = False

    premium_uploaded_file = st.file_uploader(
        "Upload Premium Reference Image",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"premium_uploaded_file_{st.session_state['premium_uploader_key']}",
    )

    active_premium_uploaded_file = (
        premium_uploaded_file
        or st.session_state.get("premium_uploaded_file")
    )

    st.subheader("Creative Tags")

    st.caption(
        "Enter simple ideas first. Then enhance them into premium-ready tags."
    )

    # -----------------------------
    # TAG SESSION STATE
    # -----------------------------

    if "premium_enhanced_tags_value" not in st.session_state:
        st.session_state["premium_enhanced_tags_value"] = ""

    if "premium_surprise_tags_value" not in st.session_state:
        st.session_state["premium_surprise_tags_value"] = ""

    if "premium_tags_have_been_enhanced" not in st.session_state:
        st.session_state["premium_tags_have_been_enhanced"] = False

    if "premium_tags_have_been_surprised" not in st.session_state:
        st.session_state["premium_tags_have_been_surprised"] = False

    if "premium_selected_tag_source" not in st.session_state:
        st.session_state["premium_selected_tag_source"] = "Original Tags"

    # -----------------------------
    # ORIGINAL TAGS
    # -----------------------------

    premium_user_tags = st.text_area(
        label="Original Creative Tags",
        key="premium_creative_tags",
        placeholder="Example: nude, night, pool",
        height=90,
    )

    enhance_button_label = (
        "🔁 Re-Enhance Tags"
        if st.session_state["premium_tags_have_been_enhanced"]
        else "✨ Enhance Tags"
    )

    surprise_button_label = (
        "🎲 Surprise Me Again"
        if st.session_state["premium_tags_have_been_surprised"]
        else "🎲 Surprise Me"
    )

    tag_action_col1, tag_action_col2 = st.columns(2)

    with tag_action_col1:
        enhance_tags_clicked = st.button(
            enhance_button_label,
            use_container_width=True,
            disabled=not premium_user_tags.strip(),
        )

    with tag_action_col2:
        surprise_tags_clicked = st.button(
            surprise_button_label,
            use_container_width=True,
            disabled=not premium_user_tags.strip(),
        )

    # -----------------------------
    # ENHANCE TAGS
    # -----------------------------

    if enhance_tags_clicked:
        with st.spinner("Enhancing premium tags with Grok..."):
            enhanced_tags = enhance_premium_tags(
                simple_tags=premium_user_tags,
            )

        st.session_state["premium_enhanced_tags_value"] = enhanced_tags
        st.session_state["premium_enhanced_tags_input"] = enhanced_tags
        st.session_state["premium_tags_have_been_enhanced"] = True
        st.session_state["premium_selected_tag_source"] = "Enhanced Tags"

        st.success("Enhanced tags created.")
        st.rerun()

    # -----------------------------
    # SURPRISE TAGS
    # -----------------------------

    if surprise_tags_clicked:
        with st.spinner("Creating surprise premium tags with Grok..."):
            surprise_tags = surprise_premium_tags(
                simple_tags=premium_user_tags,
            )

        st.session_state["premium_surprise_tags_value"] = surprise_tags
        st.session_state["premium_surprise_tags_input"] = surprise_tags
        st.session_state["premium_tags_have_been_surprised"] = True
        st.session_state["premium_selected_tag_source"] = "Surprise Me Tags"

        st.success("Surprise tags created.")
        st.rerun()

    # -----------------------------
    # ENHANCED TAG BOX
    # -----------------------------

    premium_enhanced_tags = st.text_area(
        label="Enhanced Premium Tags",
        value=st.session_state["premium_enhanced_tags_value"],
        key="premium_enhanced_tags_input",
        placeholder="Enhanced premium tags will appear here...",
        height=90,
    )

    st.session_state["premium_enhanced_tags_value"] = premium_enhanced_tags

    # -----------------------------
    # SURPRISE TAG BOX
    # -----------------------------

    premium_surprise_tags = st.text_area(
        label="Surprise Me Tags",
        value=st.session_state["premium_surprise_tags_value"],
        key="premium_surprise_tags_input",
        placeholder="Surprise Me tags will appear here...",
        height=90,
    )

    st.session_state["premium_surprise_tags_value"] = premium_surprise_tags

    # -----------------------------
    # TAG SOURCE SELECTION
    # -----------------------------

    selected_tag_source = st.radio(
        "Choose tags to send to Grok",
        options=[
            "Original Tags",
            "Enhanced Tags",
            "Surprise Me Tags",
        ],
        key="premium_selected_tag_source",
        horizontal=True,
    )

    if selected_tag_source == "Original Tags":
        tags_for_prompt_generation = premium_user_tags.strip()

    elif selected_tag_source == "Enhanced Tags":
        tags_for_prompt_generation = st.session_state[
            "premium_enhanced_tags_value"
        ].strip()

    elif selected_tag_source == "Surprise Me Tags":
        tags_for_prompt_generation = st.session_state[
            "premium_surprise_tags_value"
        ].strip()

    else:
        tags_for_prompt_generation = ""

    if tags_for_prompt_generation:
        st.caption(
            f"Using {selected_tag_source}: {tags_for_prompt_generation}"
        )
    else:
        st.caption(
            f"{selected_tag_source} is empty. Select another tag source or generate tags first."
        )

    # -----------------------------
    # GET PREMIUM PROMPTS
    # -----------------------------

    prompt_button_col1, prompt_button_col2 = st.columns(2)

    with prompt_button_col1:
        prompt_button_col1, prompt_button_col2 = st.columns(2)

        with prompt_button_col1:
            get_premium_prompts_clicked = st.button(
                "✨ Get Premium Prompts",
                use_container_width=True,
                disabled=not tags_for_prompt_generation,
            )

        with prompt_button_col2:
            get_explicit_prompts_clicked = st.button(
                "🔥 Get Explicit Prompts",
                use_container_width=True,
                disabled=not tags_for_prompt_generation,
            )

    if get_explicit_prompts_clicked:
        with st.spinner("Generating bold premium prompts with Grok..."):
            explicit_prompts = generate_explicit_prompts(
                creative_tags=tags_for_prompt_generation,
                prompt_count=10,
            )

        st.session_state["premium_uploaded_file"] = premium_uploaded_file
        st.session_state["premium_user_tags"] = premium_user_tags
        st.session_state["premium_tags_used_for_prompts"] = (
            tags_for_prompt_generation
        )
        st.session_state["premium_tag_source_used_for_prompts"] = (
            selected_tag_source
        )
        st.session_state["premium_prompt_mode"] = "explicit"

        st.session_state["premium_prompts"] = [
            {
                "id": f"explicit_prompt_{index}",
                "text": prompt,
            }
            for index, prompt in enumerate(
                explicit_prompts,
                start=1,
            )
        ]

        st.session_state["premium_generated_images"] = []
        st.session_state["premium_failed_images"] = []
        st.session_state["premium_generation_complete"] = False

        st.success("Bold premium prompt batch generated.")

    if premium_uploaded_file is None:
        st.caption(
            "You can generate prompts now, but upload a premium reference image before generating images."
        )

    if get_premium_prompts_clicked:
        with st.spinner("Generating premium prompts with Grok..."):
            premium_prompts = generate_premium_prompts(
                creative_tags=tags_for_prompt_generation,
                prompt_count=10,
            )

        st.session_state["premium_uploaded_file"] = premium_uploaded_file
        st.session_state["premium_user_tags"] = premium_user_tags
        st.session_state["premium_tags_used_for_prompts"] = (
            tags_for_prompt_generation
        )
        st.session_state["premium_tag_source_used_for_prompts"] = (
            selected_tag_source
        )

        st.session_state["premium_prompts"] = [
            {
                "id": f"premium_prompt_{index}",
                "text": prompt,
            }
            for index, prompt in enumerate(
                premium_prompts,
                start=1,
            )
        ]

        st.session_state["premium_generated_images"] = []
        st.session_state["premium_failed_images"] = []
        st.session_state["premium_generation_complete"] = False

        st.success("Premium prompt batch generated.")

        if get_explicit_prompts_clicked:
            with st.spinner("Generating explicit prompts with Grok..."):
                explicit_prompts = generate_explicit_prompts(
                    creative_tags=tags_for_prompt_generation,
                    prompt_count=10,
                )

            st.session_state["premium_uploaded_file"] = premium_uploaded_file
            st.session_state["premium_user_tags"] = premium_user_tags
            st.session_state["premium_tags_used_for_prompts"] = (
                tags_for_prompt_generation
            )
            st.session_state["premium_tag_source_used_for_prompts"] = (
                selected_tag_source
            )
            st.session_state["premium_prompt_mode"] = "explicit"

            st.session_state["premium_prompts"] = [
                {
                    "id": f"explicit_prompt_{index}",
                    "text": prompt,
                }
                for index, prompt in enumerate(
                    explicit_prompts,
                    start=1,
                )
            ]

            st.session_state["premium_generated_images"] = []
            st.session_state["premium_failed_images"] = []
            st.session_state["premium_generation_complete"] = False

            st.success("Explicit prompt batch generated.")

    render_premium_prompt_expander()

    st.subheader("Premium Renderer")

    premium_renderer = st.selectbox(
        "Choose premium render engine",
        options=[
            "WAN 2.7 Image Edit",
            "Seedream 5.0 Lite Edit",
        ],
        index=0,
        key="premium_renderer",
        label_visibility="collapsed",
    )

    generate_premium_images_clicked = st.button(
        "🔥 Generate Premium Images",
        use_container_width=True,
        disabled=(
            active_premium_uploaded_file is None
            or not st.session_state["premium_prompts"]
        ),
    )

    if generate_premium_images_clicked:

        st.session_state["premium_generated_images"] = []
        st.session_state["premium_failed_images"] = []
        st.session_state["premium_generation_complete"] = False

        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        live_gallery = st.empty()

        def update_premium_progress(
            current,
            total,
            message,
            generated_images=None,
            failed_images=None,
        ):
            progress_value = 0

            if total > 0:
                progress_value = int(
                    (current / total) * 100
                )

            progress_bar.progress(progress_value)

            completed_count = len(
                generated_images or []
            )

            failed_count = len(
                failed_images or []
            )

            remaining_count = total - completed_count - failed_count

            status_placeholder.info(
                f"{message}  "
                f"✅ {completed_count} completed "
                f"❌ {failed_count} failed "
                f"⏳ {remaining_count} remaining"
            )

            if generated_images:
                with live_gallery.container():
                    st.markdown("---")
                    st.subheader("Live Generated Images")

                    cols = st.columns(3)

                    for image_index, image_item in enumerate(
                        generated_images
                    ):
                        with cols[image_index % 3]:
                            st.image(
                                image_item["url"],
                                use_container_width=True,
                            )

                            with st.expander("Prompt"):
                                st.write(
                                    image_item["prompt"]
                                )

        with st.spinner(f"Generating premium images with {premium_renderer}..."):

            render_results = generate_premium_images(
                premium_prompts=st.session_state["premium_prompts"],
                uploaded_file=active_premium_uploaded_file,
                selected_output_dir=selected_output_dir,
                premium_renderer=premium_renderer,
                progress_callback=update_premium_progress,
            )

        st.session_state["premium_generated_images"] = (
            render_results.get("generated_images", [])
        )

        st.session_state["premium_failed_images"] = (
            render_results.get("failed_images", [])
        )

        st.session_state["premium_generation_complete"] = True

        completed_count = len(
            st.session_state["premium_generated_images"]
        )

        failed_count = len(
            st.session_state["premium_failed_images"]
        )

        if failed_count == 0:
            st.success(
                f"Generation complete. ✅ {completed_count} completed"
            )
        else:
            st.warning(
                f"Generation complete. ✅ {completed_count} completed ❌ {failed_count} failed"
            )

    render_premium_generated_image_gallery(
        selected_output_dir=selected_output_dir,
    )

    if (
        st.session_state.get("premium_generation_complete", False)
        and st.session_state.get("premium_generated_images")
    ):
        return True

    return False