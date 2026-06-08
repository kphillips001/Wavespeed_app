from datetime import datetime
import html
from pathlib import Path
import re
import time

import requests
import streamlit as st

from app.services.premium_director_service import (
    generate_premium_prompts,
)

from app.services.premium_render_service import (
    generate_premium_images,
)

from app.services.explicit_prompt_service import (
    enhance_explicit_tags,
    generate_explicit_prompts as generate_enhanced_explicit_prompts,
)

from app.services.premium_tag_enhancer_service import (
    enhance_premium_tags,
    surprise_premium_tags,
)

from app.ui.components.reference_image_selector import (
    render_reference_image_selector,
)

from app.ui.image_file_utils import (
    get_unique_image_path,
)


def download_image(image_url, output_path):
    response = requests.get(image_url, timeout=60)
    response.raise_for_status()

    with open(output_path, "wb") as file:
        file.write(response.content)


def save_premium_generated_images(images, output_dir):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_paths = []

    Path(output_dir).mkdir(parents=True, exist_ok=True)

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

    with st.expander("View Generated Premium Prompts", expanded=False):
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


def render_premium_generated_image_gallery(selected_output_dir):
    generated_images = st.session_state.get(
        "premium_generated_images",
        [],
    )

    if not generated_images:
        return

    st.markdown("---")
    st.subheader("Generated Images")

    cols = st.columns(3)

    for index, image_item in enumerate(generated_images):
        with cols[index % 3]:
            image_url = image_item.get(
                "url",
                image_item.get("local_path", ""),
            )

            if image_url:
                st.image(
                    image_url,
                    use_container_width=True,
                )

            with st.expander("Prompt"):
                st.write(
                    image_item.get(
                        "prompt",
                        "",
                    )
                )


def build_manual_premium_prompt(
    manual_prompt,
    additional_detail="",
):
    prompt_parts = [
        manual_prompt.strip(),
        """
Reference body lock:
Use the exact same woman from the reference image.
Preserve the exact same face, hair, skin tone, body size, body weight, and body proportions from the reference image.
Preserve her full natural D-cup breast proportions, full D-cup breast volume, visible breast projection, rounded natural breast shape, feminine hourglass body, waist-to-hip ratio, hip width, thigh thickness, leg proportions, and shoulder width.
Do not reduce breast volume.
Do not make her smaller-busted than the reference image.
Do not flatten the chest.
Do not change her body size, body weight, waist, hips, thighs, shoulders, bust-to-waist proportions, or recognizable silhouette.
Keep the body realistic and photorealistic.
""".strip(),
    ]

    if additional_detail and additional_detail.strip():
        prompt_parts.append(
            f"Additional regeneration detail: {additional_detail.strip()}"
        )

    return "\n\n".join(
        part
        for part in prompt_parts
        if part
    )


def run_single_manual_premium_generation(
    manual_prompt,
    additional_detail,
    active_premium_reference_image,
    selected_output_dir,
    premium_renderer,
    progress_callback=None,
):
    locked_prompt = build_manual_premium_prompt(
        manual_prompt=manual_prompt,
        additional_detail=additional_detail,
    )

    return generate_premium_images(
        premium_prompts=[
            {
                "id": "manual_prompt",
                "text": locked_prompt,
            }
        ],
        uploaded_file=active_premium_reference_image,
        selected_output_dir=selected_output_dir,
        premium_renderer=premium_renderer,
        progress_callback=progress_callback,
    )


def append_premium_render_results(render_results):
    st.session_state["premium_generated_images"].extend(
        render_results.get(
            "generated_images",
            [],
        )
    )

    st.session_state["premium_failed_images"].extend(
        render_results.get(
            "failed_images",
            [],
        )
    )

    st.session_state["premium_generation_complete"] = True

    # if (
    #     not st.session_state["premium_generated_images"]
    #     or not st.session_state.get("premium_generation_complete", False)
    # ):
    #     return

    # st.markdown("---")
    # st.subheader("Final Generated Images")

    # cols = st.columns(3)

    # for i, image_item in enumerate(st.session_state["premium_generated_images"]):
    #     image_id = image_item.get("id", f"premium_image_{i + 1}")

    #     with cols[i % 3]:
    #         st.image(image_item["url"], use_container_width=True)

    #         st.checkbox("Discard", key=f"premium_discard_{image_id}")

    #         st.checkbox(
    #             "📸 Continue Photoshoot",
    #             key=f"premium_photoshoot_{image_id}",
    #         )

    #         st.checkbox(
    #             "📖 Create Story (Coming Soon)",
    #             key=f"premium_story_{image_id}",
    #             disabled=True,
    #         )

    #         with st.expander("Prompt"):
    #             st.write(image_item["prompt"])

    # st.markdown("---")

    # discard_ids = []
    # photoshoot_ids = []

    # for image_item in st.session_state["premium_generated_images"]:
    #     image_id = image_item.get("id")

    #     if st.session_state.get(f"premium_discard_{image_id}", False):
    #         discard_ids.append(image_id)

    #     if st.session_state.get(f"premium_photoshoot_{image_id}", False):
    #         photoshoot_ids.append(image_id)

    # photoshoot_ids = [
    #     image_id
    #     for image_id in photoshoot_ids
    #     if image_id not in discard_ids
    # ]

    # button_label = (
    #     "🗑️ Discard Selected"
    #     if discard_ids
    #     else "💾 Save All Images"
    # )

    # if st.button(button_label, use_container_width=True):
    #     if discard_ids:
    #         st.session_state["premium_generated_images"] = [
    #             img
    #             for img in st.session_state["premium_generated_images"]
    #             if img["id"] not in discard_ids
    #         ]

    #         st.session_state["save_toast_message"] = (
    #             f"🗑️ Discarded {len(discard_ids)} premium image(s)"
    #         )

    #         st.rerun()

    #     else:
    #         st.session_state["save_toast_message"] = (
    #             f"✅ Saved {len(st.session_state['premium_generated_images'])} premium image(s). "
    #             f"📸 Sent {len(photoshoot_ids)} premium image(s) to Photoshoot."
    #         )

    #         st.session_state["save_toast_time"] = time.time()

    #         st.session_state["premium_generated_images"] = []
    #         st.session_state["premium_failed_images"] = []
    #         st.session_state["premium_prompts"] = []
    #         st.session_state["premium_generation_complete"] = False

    #         st.rerun()


def render_premium_content_studio_legacy(selected_output_dir):
    # -----------------------------
    # SESSION STATE
    # -----------------------------

    if "premium_prompts" not in st.session_state:
        st.session_state["premium_prompts"] = []

    if "premium_generated_images" not in st.session_state:
        st.session_state["premium_generated_images"] = []

    if "premium_failed_images" not in st.session_state:
        st.session_state["premium_failed_images"] = []

    if "premium_generation_complete" not in st.session_state:
        st.session_state["premium_generation_complete"] = False

    # -----------------------------
    # PREMIUM REFERENCE LIBRARY
    # -----------------------------

    premium_reference_dir = (
        Path(selected_output_dir)
        / "NSFW Reference Images"
    )

    selected_reference_image = render_reference_image_selector(
        reference_dir=str(premium_reference_dir),
        session_key="premium_reference_image",
        title="Reference Image Library",
        columns=6,
    )

    active_premium_reference_image = selected_reference_image

    has_premium_reference_image = active_premium_reference_image is not None

    if not has_premium_reference_image:
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

    with st.expander(
        "🎨 Creative Director",
        expanded=False,
    ):
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

        if "premium_enhanced_explicit_tags_value" not in st.session_state:
            st.session_state["premium_enhanced_explicit_tags_value"] = ""

        if "premium_tags_have_been_enhanced" not in st.session_state:
            st.session_state["premium_tags_have_been_enhanced"] = False

        if "premium_tags_have_been_surprised" not in st.session_state:
            st.session_state["premium_tags_have_been_surprised"] = False

        if "premium_explicit_tags_have_been_enhanced" not in st.session_state:
            st.session_state["premium_explicit_tags_have_been_enhanced"] = False

        if "premium_selected_tag_source" not in st.session_state:
            st.session_state["premium_selected_tag_source"] = "Original Tags"

        if "premium_prompt_count" not in st.session_state:
            st.session_state["premium_prompt_count"] = 10

        # -----------------------------
        # ORIGINAL TAGS
        # -----------------------------

        premium_user_tags = st.text_area(
            label="Original Creative Tags",
            key="premium_creative_tags",
            placeholder="Example: nude, night, pool",
            height=90,
        )

        premium_explicit_tags = st.text_area(
            label="Explicit Tags",
            key="premium_explicit_tags",
            placeholder="Enter explicit/adult concepts to preserve as mandatory anchors...",
            height=90,
        )

        premium_explicit_optional_setting = st.text_input(
            label="Optional Setting",
            key="premium_explicit_optional_setting",
            placeholder=(
                "Optional: rooftop, club bathroom, hotel suite, dark alley. "
                "Leave blank for varied settings."
            ),
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

        explicit_enhance_button_label = (
            "Re-Enhance Explicit Tags"
            if st.session_state["premium_explicit_tags_have_been_enhanced"]
            else "Enhance Explicit Tags"
        )

        tag_action_col1, tag_action_col2, tag_action_col3 = st.columns(3)

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

        with tag_action_col3:
            enhance_explicit_tags_clicked = st.button(
                explicit_enhance_button_label,
                use_container_width=True,
                disabled=not premium_explicit_tags.strip(),
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
        # ENHANCE EXPLICIT TAGS
        # -----------------------------

        if enhance_explicit_tags_clicked:
            with st.spinner("Enhancing explicit tags with Grok..."):
                enhanced_explicit_tags = enhance_explicit_tags(
                    raw_explicit_tags=premium_explicit_tags,
                    optional_setting=premium_explicit_optional_setting,
                )

            st.session_state["premium_enhanced_explicit_tags_value"] = enhanced_explicit_tags
            st.session_state["premium_enhanced_explicit_tags_input"] = enhanced_explicit_tags
            st.session_state["premium_explicit_tags_have_been_enhanced"] = True
            st.session_state["premium_selected_tag_source"] = "Enhanced Explicit Tags"

            st.success("Enhanced explicit tags created.")
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
            disabled=True,
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
            disabled=True,
        )

        st.session_state["premium_surprise_tags_value"] = premium_surprise_tags

        # -----------------------------
        # ENHANCED EXPLICIT TAG BOX
        # -----------------------------

        premium_enhanced_explicit_tags = st.text_area(
            label="Enhanced Explicit Tags",
            value=st.session_state["premium_enhanced_explicit_tags_value"],
            key="premium_enhanced_explicit_tags_input",
            placeholder="Enhanced explicit tags will appear here...",
            height=90,
            disabled=True,
        )

        st.session_state[
            "premium_enhanced_explicit_tags_value"
        ] = premium_enhanced_explicit_tags

        # -----------------------------
        # TAG SOURCE SELECTION
        # -----------------------------

        selected_tag_source = st.radio(
            "Choose tags to send to Grok",
            options=[
                "Original Tags",
                "Enhanced Tags",
                "Surprise Me Tags",
                "Enhanced Explicit Tags",
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

        elif selected_tag_source == "Enhanced Explicit Tags":
            tags_for_prompt_generation = st.session_state[
                "premium_enhanced_explicit_tags_value"
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

        st.markdown("### Number of Prompts")

        premium_prompt_count = st.slider(
            "Number of Prompts",
            min_value=1,
            max_value=25,
            value=st.session_state["premium_prompt_count"],
            key="premium_prompt_count",
            label_visibility="collapsed",
        )

        st.caption(
            f"Prompts: {premium_prompt_count}"
        )

        st.markdown("### Explicitness Level")

           
        enhanced_explicit_tags_for_prompt = st.session_state[
            "premium_enhanced_explicit_tags_value"
        ].strip()

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
                disabled=not enhanced_explicit_tags_for_prompt,
            )

        if get_explicit_prompts_clicked:
            with st.spinner("Generating explicit prompts with Grok..."):
                explicit_prompts = generate_enhanced_explicit_prompts(
                    enhanced_explicit_tags=st.session_state["premium_enhanced_explicit_tags_value"].strip(),
                    prompt_count=premium_prompt_count,
                    optional_setting=premium_explicit_optional_setting,
                )
            st.session_state["premium_reference_image"] = active_premium_reference_image
            st.session_state["premium_user_tags"] = premium_user_tags
            st.session_state["premium_tags_used_for_prompts"] = st.session_state["premium_enhanced_explicit_tags_value"].strip()
            st.session_state["premium_tag_source_used_for_prompts"] = "Enhanced Explicit Tags"
            st.session_state["premium_prompt_mode"] = "explicit"
            st.session_state["premium_prompts"] = [
                {
                    "id": f"explicit_prompt_{index}",
                    "text": prompt,
                }
                for index, prompt in enumerate(explicit_prompts, start=1)
            ]
            st.session_state["premium_generated_images"] = []
            st.session_state["premium_failed_images"] = []
            st.session_state["premium_generation_complete"] = False
            st.success("Explicit prompt batch generated.")
            st.rerun()

            st.session_state["premium_generated_images"] = []
            st.session_state["premium_failed_images"] = []
            st.session_state["premium_generation_complete"] = False

            st.success("Explicit prompt batch generated.")

        if not active_premium_reference_image:
            st.caption(
                "Select or upload a reference image before generating premium images."
            )

        if get_premium_prompts_clicked:
            with st.spinner("Generating premium prompts with Grok..."):
                premium_prompts = generate_premium_prompts(
                    creative_tags=tags_for_prompt_generation,
                    prompt_count=premium_prompt_count,
                )

            st.session_state["premium_reference_image"] = active_premium_reference_image
            st.session_state["premium_user_tags"] = premium_user_tags
            st.session_state["premium_tags_used_for_prompts"] = tags_for_prompt_generation
            st.session_state["premium_tag_source_used_for_prompts"] = selected_tag_source
            st.session_state["premium_prompt_mode"] = "premium"

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

        render_premium_prompt_expander()

    with st.expander(
        "✍️ Manual Prompt",
        expanded=False,
    ):

        manual_prompt = st.text_area(
            "Prompt",
            height=250,
            key="premium_manual_prompt",
            placeholder=(
                "Enter your own prompt and bypass "
                "Creative Director mode."
            ),
        )
        
    st.subheader("Premium Renderer")

    premium_renderer = st.selectbox(
        "Choose premium render engine",
        options=[
            "WAN 2.7 Image Edit",
            "Seedream 4.5 Edit",
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
            active_premium_reference_image is None
            or (
                not st.session_state["premium_prompts"]
                and not manual_prompt.strip()
            )
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
                progress_value = int((current / total) * 100)

            progress_bar.progress(progress_value)

            completed_count = len(generated_images or [])
            failed_count = len(failed_images or [])
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

                    for image_index, image_item in enumerate(generated_images):
                        with cols[image_index % 3]:
                            st.image(
                                image_item["url"],
                                use_container_width=True,
                            )

                            with st.expander("Prompt"):
                                st.write(image_item["prompt"])

        with st.spinner(f"Generating premium images with {premium_renderer}..."):
            prompts_to_generate = st.session_state["premium_prompts"]

            if manual_prompt.strip():
                prompts_to_generate = [
                    {
                        "id": "manual_prompt",
                        "text": manual_prompt.strip(),
                    }
                ]
            render_results = generate_premium_images(
                premium_prompts=prompts_to_generate,
                uploaded_file=active_premium_reference_image,
                selected_output_dir=selected_output_dir,
                premium_renderer=premium_renderer,
                progress_callback=update_premium_progress,
            )

        st.session_state["premium_generated_images"] = render_results.get(
            "generated_images",
            [],
        )

        st.session_state["premium_failed_images"] = render_results.get(
            "failed_images",
            [],
        )

        st.session_state["premium_generation_complete"] = True

        completed_count = len(st.session_state["premium_generated_images"])
        failed_count = len(st.session_state["premium_failed_images"])

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
        open_premium_gallery_clicked = st.button(
            "🖼 Open Premium Gallery",
            use_container_width=True,
            key="open_premium_gallery_after_generation",
        )

        if open_premium_gallery_clicked:
            st.session_state["show_premium_gallery"] = True
            st.session_state["show_premium_photoshoot_queue"] = False
            st.rerun()

        return True

    return False


def init_premium_content_state():
    defaults = {
        "premium_prompts": [],
        "premium_generated_images": [],
        "premium_failed_images": [],
        "premium_generation_complete": False,
        "premium_enhanced_tags_value": "",
        "premium_surprise_tags_value": "",
        "premium_enhanced_explicit_tags_value": "",
        "premium_tags_have_been_enhanced": False,
        "premium_tags_have_been_surprised": False,
        "premium_explicit_tags_have_been_enhanced": False,
        "premium_selected_tag_source": "Original Tags",
        "premium_prompt_count": 10,
        "show_premium_reference_library": False,
        "premium_manual_prompt_saved": "",
        "premium_last_manual_prompt_base": "",
        "premium_manual_regenerate_detail": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_premium_generation_results():
    st.session_state["premium_generated_images"] = []
    st.session_state["premium_failed_images"] = []
    st.session_state["premium_generation_complete"] = False


def set_premium_prompt_batch(
    prompts,
    prompt_id_prefix,
    prompt_mode,
    tags_used,
    tag_source,
    premium_user_tags,
    active_reference_image,
):
    st.session_state["premium_reference_image"] = active_reference_image
    st.session_state["premium_user_tags"] = premium_user_tags
    st.session_state["premium_tags_used_for_prompts"] = tags_used
    st.session_state["premium_tag_source_used_for_prompts"] = tag_source
    st.session_state["premium_prompt_mode"] = prompt_mode

    st.session_state["premium_prompts"] = [
        {
            "id": f"{prompt_id_prefix}_{index}",
            "text": prompt,
        }
        for index, prompt in enumerate(
            prompts,
            start=1,
        )
    ]

    clear_premium_generation_results()


def get_tags_for_source(
    selected_tag_source,
    premium_user_tags,
):
    if selected_tag_source == "Original Tags":
        return premium_user_tags.strip()

    if selected_tag_source == "Enhanced Tags":
        return st.session_state["premium_enhanced_tags_value"].strip()

    if selected_tag_source == "Surprise Me Tags":
        return st.session_state["premium_surprise_tags_value"].strip()

    if selected_tag_source == "Enhanced Explicit Tags":
        return st.session_state["premium_enhanced_explicit_tags_value"].strip()

    return ""


def render_premium_reference_section(selected_output_dir):
    premium_reference_dir = (
        Path(selected_output_dir)
        / "NSFW Reference Images"
    )

    active_reference_image = st.session_state.get(
        "premium_reference_image"
    )

    has_reference_image = bool(active_reference_image)

    st.subheader("Reference Image")

    if has_reference_image:
        selected_preview_col, selected_info_col = st.columns([2, 10])

        with selected_preview_col:
            st.image(
                str(active_reference_image),
                use_container_width=True,
            )

        with selected_info_col:
            st.success("Selected reference image")
            st.caption(str(active_reference_image))

    else:
        st.warning("Reference Image Must Be Selected before continuing.")

    selected_reference_image = render_reference_image_selector(
        reference_dir=str(premium_reference_dir),
        session_key="premium_reference_image",
        title="Reference Image Library",
        columns=6,
    )

    if selected_reference_image:
        active_reference_image = selected_reference_image

    return active_reference_image


def render_tag_output(label, value):
    st.markdown(f"**{label}**")

    if value:
        normalized_value = re.sub(
            r"[\r\n;]+",
            ", ",
            str(value),
        )

        normalized_value = re.sub(
            r"\s*[-•]\s+",
            ", ",
            normalized_value,
        )

        normalized_value = re.sub(
            r"\s*,\s*",
            ", ",
            normalized_value,
        ).strip(" ,")

        wrapped_value = ", ".join(
            tag.strip()
            for tag in normalized_value.split(",")
            if tag.strip()
        )

        escaped_value = html.escape(
            wrapped_value
        )

        st.markdown(
            f"""
            <div style="
                width: 100%;
                max-height: 220px;
                overflow-y: auto;
                overflow-x: hidden;
                white-space: normal;
                overflow-wrap: anywhere;
                word-break: normal;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 12px 14px;
                background: #f8fafc;
                color: #111827;
                font-size: 14px;
                line-height: 1.55;
            ">
                {escaped_value}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.caption("No generated output yet.")


def render_premium_creative_director(
    active_premium_reference_image,
):
    with st.expander(
        "Creative Director",
        expanded=True,
    ):
        st.caption(
            "Enter simple ideas first. Then enhance them into premium-ready tags."
        )

        with st.form(
            "premium_creative_director_form",
            clear_on_submit=False,
        ):
            premium_user_tags = st.text_area(
                label="Original Creative Tags",
                key="premium_creative_tags",
                placeholder="Example: nude, night, pool",
                height=90,
            )

            premium_explicit_tags = st.text_area(
                label="Explicit Tags",
                key="premium_explicit_tags",
                placeholder="Enter explicit/adult concepts to preserve as mandatory anchors...",
                height=90,
            )

            premium_explicit_optional_setting = st.text_input(
                label="Optional Setting",
                key="premium_explicit_optional_setting",
                placeholder=(
                    "Optional: rooftop, club bathroom, hotel suite, dark alley. "
                    "Leave blank for varied settings."
                ),
            )

            tag_action_col1, tag_action_col2, tag_action_col3 = st.columns(3)

            with tag_action_col1:
                enhance_tags_clicked = st.form_submit_button(
                    "Enhance Tags",
                    use_container_width=True,
                )

            with tag_action_col2:
                surprise_tags_clicked = st.form_submit_button(
                    "Surprise Me",
                    use_container_width=True,
                )

            with tag_action_col3:
                enhance_explicit_tags_clicked = st.form_submit_button(
                    "Enhance Explicit Tags",
                    use_container_width=True,
                )

            if enhance_tags_clicked:
                if not premium_user_tags.strip():
                    st.error("Original Creative Tags are required.")
                else:
                    with st.spinner("Enhancing premium tags with Grok..."):
                        enhanced_tags = enhance_premium_tags(
                            simple_tags=premium_user_tags,
                        )

                    st.session_state["premium_enhanced_tags_value"] = enhanced_tags
                    st.session_state["premium_tags_have_been_enhanced"] = True
                    st.session_state["premium_selected_tag_source"] = "Enhanced Tags"
                    st.success("Enhanced tags created.")

            if surprise_tags_clicked:
                if not premium_user_tags.strip():
                    st.error("Original Creative Tags are required.")
                else:
                    with st.spinner("Creating surprise premium tags with Grok..."):
                        surprise_tags = surprise_premium_tags(
                            simple_tags=premium_user_tags,
                        )

                    st.session_state["premium_surprise_tags_value"] = surprise_tags
                    st.session_state["premium_tags_have_been_surprised"] = True
                    st.session_state["premium_selected_tag_source"] = "Surprise Me Tags"
                    st.success("Surprise tags created.")

            if enhance_explicit_tags_clicked:
                if not premium_explicit_tags.strip():
                    st.error("Explicit Tags are required.")
                else:
                    with st.spinner("Enhancing explicit tags with Grok..."):
                        enhanced_explicit_tags = enhance_explicit_tags(
                            raw_explicit_tags=premium_explicit_tags,
                            optional_setting=premium_explicit_optional_setting,
                        )

                    st.session_state[
                        "premium_enhanced_explicit_tags_value"
                    ] = enhanced_explicit_tags
                    st.session_state[
                        "premium_explicit_tags_have_been_enhanced"
                    ] = True
                    st.session_state[
                        "premium_selected_tag_source"
                    ] = "Enhanced Explicit Tags"
                    st.success("Enhanced explicit tags created.")

            st.markdown("---")

            render_tag_output(
                "Enhanced Premium Tags",
                st.session_state["premium_enhanced_tags_value"],
            )

            render_tag_output(
                "Surprise Me Tags",
                st.session_state["premium_surprise_tags_value"],
            )

            render_tag_output(
                "Enhanced Explicit Tags",
                st.session_state["premium_enhanced_explicit_tags_value"],
            )

            selected_tag_source = st.radio(
                "Choose tags to send to Grok",
                options=[
                    "Original Tags",
                    "Enhanced Tags",
                    "Surprise Me Tags",
                    "Enhanced Explicit Tags",
                ],
                key="premium_selected_tag_source",
                horizontal=True,
            )

            tags_for_prompt_generation = get_tags_for_source(
                selected_tag_source,
                premium_user_tags,
            )

            if tags_for_prompt_generation:
                st.caption(
                    f"Using {selected_tag_source}: {tags_for_prompt_generation}"
                )
            else:
                st.caption(
                    f"{selected_tag_source} is empty. Select another tag source or generate tags first."
                )

            st.markdown("### Number of Prompts")

            premium_prompt_count = st.slider(
                "Number of Prompts",
                min_value=1,
                max_value=25,
                value=st.session_state["premium_prompt_count"],
                key="premium_prompt_count",
                label_visibility="collapsed",
            )

            st.caption(
                f"Prompts: {premium_prompt_count}"
            )

            enhanced_explicit_tags_for_prompt = st.session_state[
                "premium_enhanced_explicit_tags_value"
            ].strip()

            prompt_col1, prompt_col2 = st.columns(2)

            with prompt_col1:
                get_premium_prompts_clicked = st.form_submit_button(
                    "Get Premium Prompts",
                    use_container_width=True,
                )

            with prompt_col2:
                get_explicit_prompts_clicked = st.form_submit_button(
                    "Get Explicit Prompts",
                    use_container_width=True,
                )

            if get_explicit_prompts_clicked:
                if not enhanced_explicit_tags_for_prompt:
                    st.error("Enhanced Explicit Tags are required first.")
                else:
                    with st.spinner("Generating explicit prompts with Grok..."):
                        explicit_prompts = generate_enhanced_explicit_prompts(
                            enhanced_explicit_tags=enhanced_explicit_tags_for_prompt,
                            prompt_count=premium_prompt_count,
                            optional_setting=premium_explicit_optional_setting,
                        )

                    set_premium_prompt_batch(
                        prompts=explicit_prompts,
                        prompt_id_prefix="explicit_prompt",
                        prompt_mode="explicit",
                        tags_used=enhanced_explicit_tags_for_prompt,
                        tag_source="Enhanced Explicit Tags",
                        premium_user_tags=premium_user_tags,
                        active_reference_image=active_premium_reference_image,
                    )

                    st.success("Explicit prompt batch generated.")

            if get_premium_prompts_clicked:
                if not tags_for_prompt_generation:
                    st.error("Choose or generate tags before requesting prompts.")
                else:
                    with st.spinner("Generating premium prompts with Grok..."):
                        premium_prompts = generate_premium_prompts(
                            creative_tags=tags_for_prompt_generation,
                            prompt_count=premium_prompt_count,
                        )

                    set_premium_prompt_batch(
                        prompts=premium_prompts,
                        prompt_id_prefix="premium_prompt",
                        prompt_mode="premium",
                        tags_used=tags_for_prompt_generation,
                        tag_source=selected_tag_source,
                        premium_user_tags=premium_user_tags,
                        active_reference_image=active_premium_reference_image,
                    )

                    st.success("Premium prompt batch generated.")

        if not active_premium_reference_image:
            st.caption(
                "Select or upload a reference image before generating premium images."
            )

        render_premium_prompt_expander()


def render_premium_content_studio(selected_output_dir):
    init_premium_content_state()

    active_premium_reference_image = render_premium_reference_section(
        selected_output_dir
    )

    has_premium_reference_image = active_premium_reference_image is not None

    st.markdown("---")

    render_premium_creative_director(
        active_premium_reference_image=active_premium_reference_image,
    )

    st.markdown("---")

    with st.expander(
        "Manual Prompt",
        expanded=False,
    ):
        manual_prompt = st.text_area(
            "Manual Prompt",
            height=180,
            key="premium_manual_prompt_saved",
            placeholder=(
                "Enter your own prompt and bypass Creative Director mode."
            ),
        )

    st.subheader("Premium Renderer")

    with st.form(
        "premium_renderer_form",
        clear_on_submit=False,
    ):
        premium_renderer = st.selectbox(
            "Choose premium render engine",
            options=[
                "WAN 2.7 Image Edit",
                "Seedream 4.5 Edit",
                "Seedream 5.0 Lite Edit",
            ],
            index=0,
            key="premium_renderer",
            label_visibility="collapsed",
        )

        generate_premium_images_clicked = st.form_submit_button(
            "Generate Premium Images",
            use_container_width=True,
        )

    if generate_premium_images_clicked:
        if not has_premium_reference_image:
            st.error("Select a premium reference image before generating.")
            st.stop()

        if not st.session_state["premium_prompts"] and not manual_prompt.strip():
            st.error("Generate prompts or enter a manual prompt first.")
            st.stop()

        clear_premium_generation_results()

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
                progress_value = int((current / total) * 100)

            progress_bar.progress(progress_value)

            completed_count = len(generated_images or [])
            failed_count = len(failed_images or [])
            remaining_count = total - completed_count - failed_count

            status_placeholder.info(
                f"{message}  "
                f"completed {completed_count}  "
                f"failed {failed_count}  "
                f"remaining {remaining_count}"
            )

            if generated_images:
                with live_gallery.container():
                    st.markdown("---")
                    st.subheader("Live Generated Images")

                    cols = st.columns(3)

                    for image_index, image_item in enumerate(generated_images):
                        with cols[image_index % 3]:
                            st.image(
                                image_item["url"],
                                use_container_width=True,
                            )

        with st.spinner(f"Generating premium images with {premium_renderer}..."):
            if manual_prompt.strip():
                st.session_state[
                    "premium_last_manual_prompt_base"
                ] = manual_prompt.strip()

                render_results = run_single_manual_premium_generation(
                    manual_prompt=manual_prompt,
                    additional_detail="",
                    active_premium_reference_image=active_premium_reference_image,
                    selected_output_dir=selected_output_dir,
                    premium_renderer=premium_renderer,
                    progress_callback=update_premium_progress,
                )

                append_premium_render_results(
                    render_results
                )

            else:
                st.session_state["premium_last_manual_prompt_base"] = ""
                st.session_state["premium_manual_regenerate_detail"] = ""

                render_results = generate_premium_images(
                    premium_prompts=st.session_state["premium_prompts"],
                    uploaded_file=active_premium_reference_image,
                    selected_output_dir=selected_output_dir,
                    premium_renderer=premium_renderer,
                    progress_callback=update_premium_progress,
                )

                st.session_state["premium_generated_images"] = render_results.get(
                    "generated_images",
                    [],
                )

                st.session_state["premium_failed_images"] = render_results.get(
                    "failed_images",
                    [],
                )

                st.session_state["premium_generation_complete"] = True

        completed_count = len(st.session_state["premium_generated_images"])
        failed_count = len(st.session_state["premium_failed_images"])

        if failed_count == 0:
            st.success(
                f"Generation complete. {completed_count} completed"
            )
        else:
            st.warning(
                f"Generation complete. {completed_count} completed, {failed_count} failed"
            )

    render_premium_generated_image_gallery(
        selected_output_dir=selected_output_dir,
    )

    if (
        st.session_state.get("premium_last_manual_prompt_base")
        and st.session_state.get("premium_generated_images")
    ):
        with st.form(
            "premium_manual_regenerate_form",
            clear_on_submit=False,
        ):
            regenerate_detail = st.text_area(
                "Additional detail for regeneration",
                key="premium_manual_regenerate_detail",
                height=100,
                placeholder=(
                    "Optional: add a small change, detail, pose adjustment, "
                    "lighting tweak, or framing note."
                ),
            )

            regenerate_clicked = st.form_submit_button(
                "Regenerate Another Image",
                use_container_width=True,
            )

        if regenerate_clicked:
            if not has_premium_reference_image:
                st.error("Select a premium reference image before regenerating.")
                st.stop()

            progress_bar = st.progress(0)
            status_placeholder = st.empty()

            def update_regenerate_progress(
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

                status_placeholder.info(
                    f"{message}  "
                    f"completed {completed_count}  "
                    f"failed {failed_count}"
                )

            with st.spinner("Regenerating another premium image..."):
                regenerate_results = run_single_manual_premium_generation(
                    manual_prompt=st.session_state[
                        "premium_last_manual_prompt_base"
                    ],
                    additional_detail=regenerate_detail,
                    active_premium_reference_image=active_premium_reference_image,
                    selected_output_dir=selected_output_dir,
                    premium_renderer=premium_renderer,
                    progress_callback=update_regenerate_progress,
                )

            append_premium_render_results(
                regenerate_results
            )

            st.session_state["save_toast_message"] = (
                "Regenerated image added for comparison."
            )

            st.rerun()

    if (
        st.session_state.get("premium_generation_complete", False)
        and st.session_state.get("premium_generated_images")
    ):
        open_premium_gallery_clicked = st.button(
            "Open Premium Gallery",
            use_container_width=True,
            key="open_premium_gallery_after_generation",
        )

        if open_premium_gallery_clicked:
            st.session_state["show_premium_gallery"] = True
            st.session_state["show_premium_photoshoot_queue"] = False
            st.rerun()

        return True

    return False
