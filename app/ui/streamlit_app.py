import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import os
import json
import tempfile
import time
from datetime import datetime

import requests
import streamlit as st
from dotenv import load_dotenv

from app.config.settings import MODELS, PERSONA_OUTPUT_DIRS
from app.prompts.prompt_builder import build_chatgpt_prompt
from app.prompts.generation_modes import GENERATION_MODES
from app.prompts.platform_modes import PLATFORM_MODES
from app.prompts.spice_levels import SPICE_LEVELS

from main import (
    generate_prompts_with_grok,
    upload_to_imgbb,
    verify_image_url,
    submit_wavespeed_task,
    poll_wavespeed_result,
)


load_dotenv()

grok_key = os.getenv("GROK_API_KEY")
wavespeed_key = os.getenv("WAVESPEED_API_KEY")
imgbb_key = os.getenv("IMGBB_API_KEY")


def get_unique_image_path(output_dir, base_name):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    candidate_path = output_path / base_name

    if not candidate_path.exists():
        return candidate_path

    stem = candidate_path.stem
    suffix = candidate_path.suffix

    counter = 2

    while True:
        new_candidate = output_path / f"{stem}_{counter}{suffix}"

        if not new_candidate.exists():
            return new_candidate

        counter += 1


def download_image(image_url, output_path):
    response = requests.get(image_url, timeout=60)
    response.raise_for_status()

    with open(output_path, "wb") as file:
        file.write(response.content)


def save_generated_images(
    images,
    output_dir,
    creator_name=None,
    model_name=None,
    user_tags=None,
    generation_mode=None,
    platform_mode=None,
    spice_level=None,
    uploaded_file=None,
):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_paths = []

    for index, image_item in enumerate(images, start=1):
        image_filename = f"ui_{timestamp}_{index:03d}.png"
        image_path = get_unique_image_path(output_dir, image_filename)

        download_image(image_item["url"], image_path)

        saved_paths.append(str(image_path))

    return saved_paths


st.set_page_config(
    page_title="WaveSpeed AI Studio",
    layout="wide",
)

st.title("🔥 WaveSpeed AI Studio")
st.markdown("---")

if st.session_state.get("save_toast_message"):
    st.toast(st.session_state["save_toast_message"], icon="✅")
    st.session_state["save_toast_message"] = None


# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("Creator")

persona_names = {
    data["name"]: key
    for key, data in PERSONA_OUTPUT_DIRS.items()
}

selected_creator_name = st.sidebar.selectbox(
    "Who is this batch for?",
    list(persona_names.keys()),
)

selected_persona_key = persona_names[selected_creator_name]
selected_output_dir = PERSONA_OUTPUT_DIRS[selected_persona_key]["output_dir"]

st.sidebar.caption(f"Save folder: {selected_output_dir}")

st.sidebar.markdown("---")
st.sidebar.header("Generation Settings")

generation_mode = st.sidebar.selectbox(
    "Generation Mode",
    [mode["name"] for mode in GENERATION_MODES.values()]
)

platform_mode = st.sidebar.selectbox(
    "Platform",
    list(PLATFORM_MODES.values())
)

spice_level = st.sidebar.selectbox(
    "Spice Level",
    list(SPICE_LEVELS.values())
)

prompt_count = st.sidebar.slider(
    "Number of Images",
    min_value=1,
    max_value=25,
    value=10,
)

st.sidebar.markdown("---")
st.sidebar.header("Send To Model")

send_to_nano_pro = st.sidebar.button(
    "🍌 Send to Nano Banana Pro",
    use_container_width=True,
)

st.sidebar.button(
    "🌱 Send to Seedream 4.5",
    use_container_width=True,
    disabled=True,
)

st.sidebar.button(
    "⚡ Send to Seedream 5 Lite",
    use_container_width=True,
    disabled=True,
)


# -----------------------------
# MAIN INPUTS
# -----------------------------
st.subheader("Reference Image")

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

uploaded_file = st.file_uploader(
    "Upload Reference Image",
    type=["png", "jpg", "jpeg", "webp"],
    key=f"uploaded_file_{st.session_state['uploader_key']}",
)

st.subheader("Creative Tags")

user_tags = st.text_area(
    "Creative Tags",
    key="creative_tags",
    placeholder="Example: bikini, summertime, lake"
)


# -----------------------------
# GENERATE BUTTON
# -----------------------------
generate_clicked = st.button(
    "🚀 Generate Prompt Batch",
    use_container_width=True,
    disabled=uploaded_file is None,
)

if uploaded_file is None:
    st.caption("Upload a reference image before generating prompts.")

# -----------------------------
# GENERATE PROMPTS
# -----------------------------
if generate_clicked:

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

    prompts = generate_prompts_with_grok(
        meta_prompt,
        grok_key,
    )

    st.session_state["generated_prompts"] = [
        {
            "id": f"prompt_{i}",
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
    st.session_state["review_mode"] = "review"

    st.success("Prompt batch generated.")


# -----------------------------
# GENERATED PROMPTS DISPLAY
# -----------------------------
if "generated_prompts" in st.session_state and st.session_state["generated_prompts"]:

    with st.expander("View Generated Prompts", expanded=False):

        for i, prompt_item in enumerate(
            st.session_state["generated_prompts"],
            start=1
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

    st.write(
        f"**Generation Mode:** {st.session_state.get('last_generation_mode', generation_mode)}"
    )
    st.write(
        f"**Platform:** {st.session_state.get('last_platform_mode', platform_mode)}"
    )
    st.write(
        f"**Spice Level:** {st.session_state.get('last_spice_level', spice_level)}"
    )
    st.write(
        f"**Prompt Count:** {len(st.session_state['generated_prompts'])}"
    )

    st.markdown("### User Tags")
    st.code(st.session_state.get("last_user_tags", user_tags))


# -----------------------------
# SEND TO NANO BANANA PRO
# -----------------------------
if send_to_nano_pro:

    if "generated_prompts" not in st.session_state or not st.session_state["generated_prompts"]:
        st.error("Generate prompts first before sending to Nano Banana Pro.")
        st.stop()

    if not uploaded_file:
        st.error("Please upload a reference image before sending to Nano Banana Pro.")
        st.stop()

    if not wavespeed_key:
        st.error("Missing WAVESPEED_API_KEY in .env")
        st.stop()

    if not imgbb_key:
        st.error("Missing IMGBB_API_KEY in .env")
        st.stop()

    selected_model = MODELS["2"]
    total_prompts = len(st.session_state["generated_prompts"])

    st.warning(
        f"Sending {total_prompts} prompt(s) to {selected_model['name']}. This will use WaveSpeed credits."
    )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=Path(uploaded_file.name).suffix
    ) as temp_file:

        temp_file.write(uploaded_file.getvalue())
        temp_image_path = temp_file.name

    status_box = st.empty()
    progress_bar = st.progress(0)
    live_gallery = st.empty()

    with st.spinner(
        "Uploading reference image to ImgBB..."
    ):
        image_url = upload_to_imgbb(
            temp_image_path,
            imgbb_key
        )

        verify_image_url(
            image_url
        )

    st.session_state["generated_images"] = []
    st.session_state["failed_images"] = []
    st.session_state["review_mode"] = "review"
    st.session_state["discard_happened"] = False
    st.session_state["last_saved_folder"] = None
    st.session_state["generation_status"] = ""
    st.session_state["generation_complete"] = False

    for index, prompt_item in enumerate(
        st.session_state["generated_prompts"],
        start=1
    ):

        prompt_text = prompt_item["text"]

        completed_count = len(
            st.session_state["generated_images"]
        )

        failed_count = len(
            st.session_state["failed_images"]
        )

        remaining_count = (
            total_prompts
            - completed_count
            - failed_count
        )

        st.session_state["generation_status"] = (
            f"Image {index} of {total_prompts}: processing...   "
            f"✅ {completed_count} completed   "
            f"❌ {failed_count} failed   "
            f"⏳ {remaining_count} remaining"
        )

        status_box.info(
            st.session_state["generation_status"]
        )

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

            st.session_state["generated_images"].append(
                {
                    "id":f"image_{index}",
                    "prompt":prompt_text,
                    "url":output_url,
                    "status":"completed",
                }
            )

            # ======================
            # LIVE IMAGE UPDATE
            # ======================

            with live_gallery.container():

                st.markdown("---")
                st.subheader("Live Generated Images")

                current_images = list(
                    reversed(
                        st.session_state["generated_images"]
                    )
                )

                cols = st.columns(2)

                for i, image_item in enumerate(current_images):

                    with cols[i % 2]:

                        st.image(
                            image_item["url"],
                            use_container_width=True,
                        )

        except Exception as error:

            st.session_state[
                "failed_images"
            ].append(
                {
                    "id": f"image_{index}",
                    "prompt": prompt_text,
                    "error": str(error),
                    "status": "failed",
                }
            )

        completed_count = len(
            st.session_state["generated_images"]
        )

        failed_count = len(
            st.session_state["failed_images"]
        )

        remaining_count = (
            total_prompts
            - completed_count
            - failed_count
        )

        st.session_state["generation_status"] = (
            f"Image {index} of {total_prompts}: processing...   "
            f"✅ {completed_count} completed   "
            f"❌ {failed_count} failed   "
            f"⏳ {remaining_count} remaining"
        )

        status_box.info(
            st.session_state["generation_status"]
        )

        progress_bar.progress(
            index / total_prompts
        )

    completed_count = len(
        st.session_state["generated_images"]
    )

    failed_count = len(
        st.session_state["failed_images"]
    )

    st.session_state["generation_complete"] = True

    st.session_state["generation_status"] = (
        f"Generation complete. "
        f"✅ {completed_count} completed   "
        f"❌ {failed_count} failed"
    )

    if failed_count == 0:
        status_box.success(
            st.session_state["generation_status"]
        )
    else:
        status_box.warning(
            st.session_state["generation_status"]
        )

    live_gallery.empty()

# -----------------------------
# GENERATED IMAGE GALLERY
# -----------------------------
if (
    "generated_images" in st.session_state
    and st.session_state["generated_images"]
    and st.session_state.get("generation_complete", False)
):

    st.markdown("---")
    st.subheader("Final Generated Images")

    cols = st.columns(2)

    for i, image_item in enumerate(st.session_state["generated_images"]):
        image_id = image_item.get("id", f"image_{i + 1}")

        with cols[i % 2]:

            st.image(image_item["url"], use_container_width=True)

            st.checkbox(
                "Mark for discard",
                key=f"discard_{image_id}",
            )

            with st.expander("Prompt"):
                st.write(image_item["prompt"])

    st.markdown("---")

    # =====================================
    # DETERMINE DISCARDS
    # =====================================

    discard_ids = []

    for i, image_item in enumerate(st.session_state["generated_images"]):
        image_id = image_item.get("id", f"image_{i + 1}")

        if st.session_state.get(f"discard_{image_id}", False):
            discard_ids.append(image_id)

    # =====================================
    # BUTTON LABEL LOGIC
    # =====================================

    if discard_ids:
        button_label = "🗑️ Discard Selected"

    elif st.session_state.get("discard_happened", False):
        button_label = "💾 Save Remaining Images"

    else:
        button_label = "💾 Save All Images"

    # =====================================
    # MAIN ACTION BUTTON
    # =====================================

    if st.button(button_label, use_container_width=True):

        # =================================
        # DISCARD MODE
        # =================================

        if discard_ids:

            st.session_state["generated_images"] = [
                image_item
                for image_item in st.session_state["generated_images"]
                if image_item.get("id") not in discard_ids
            ]

            st.session_state["discard_happened"] = True

            st.success(
                f"Discarded {len(discard_ids)} image(s)."
            )

            st.rerun()

                # =================================
        # SAVE MODE
        # =================================

        else:

            selected_model = MODELS["2"]

            saved_paths = save_generated_images(
                images=st.session_state["generated_images"],
                output_dir=selected_output_dir,
                creator_name=selected_creator_name,
                model_name=selected_model["name"],
                user_tags=st.session_state.get("last_user_tags", user_tags),
                generation_mode=st.session_state.get("last_generation_mode", generation_mode),
                platform_mode=st.session_state.get("last_platform_mode", platform_mode),
                spice_level=st.session_state.get("last_spice_level", spice_level),
                uploaded_file=uploaded_file,
            )

            saved_count = len(st.session_state["generated_images"])

            # Single temporary success toast
            st.session_state["save_toast_message"] = (
                f"✅ Saved {saved_count} image(s) to: {selected_output_dir}"
            )

            st.session_state["save_toast_time"] = time.time()

            # Reset everything for next generation
            st.session_state["generated_images"] = []
            st.session_state["failed_images"] = []
            st.session_state["generated_prompts"] = []
            st.session_state["discard_happened"] = False
            st.session_state["last_saved_folder"] = None
            st.session_state["generation_complete"] = False
            st.session_state["generation_status"] = ""

            # Reset reference image
            st.session_state["uploader_key"] += 1

            # Reset creative tags
            st.session_state["creative_tags"] = ""

            st.rerun()
    
# -----------------------------
# UPLOADED IMAGE PREVIEW
# -----------------------------
if uploaded_file:
    st.markdown("### Uploaded Reference Image")
    st.image(uploaded_file, width=300)


# -----------------------------
# FUTURE SECTION
# -----------------------------
st.markdown("---")

st.subheader("Future Workflow")

st.markdown(
    """
Future UI flow:

1. Generate Variety Batch
2. Display generated images
3. Select favorite image
4. Generate:
   - Photoshoot Set
   - Story Sequence
   - Caption Packs
5. Send to:
   - Instagram
   - X
   - Telegram
   - Fanvue
"""
)