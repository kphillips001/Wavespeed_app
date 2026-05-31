import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[2]
    )
)

# =====================================
# STANDARD LIBRARY
# =====================================

import hashlib
import json
import os
import shutil
import tempfile
import time
from datetime import datetime


# =====================================
# THIRD PARTY
# =====================================

import requests
import streamlit as st

from dotenv import load_dotenv
from PIL import Image, ImageFilter


# =====================================
# APP CONFIG
# =====================================

from app.config.settings import (
    MODELS,
    PERSONA_OUTPUT_DIRS,
)


# =====================================
# PROMPTS
# =====================================

from app.prompts.generation_modes import (
    GENERATION_MODES,
)

from app.prompts.prompt_builder import (
    build_chatgpt_prompt,
)


# =====================================
# SERVICES
# =====================================

from app.services.caption_service import (
    generate_social_captions,
    regenerate_platform_captions,
)

from app.services.instagram_publish_service import (
    publish_to_instagram,
)

from app.services.instagram_phone_publish_service import (
    copy_caption_to_phone_clipboard,
)

from app.services.x_publish_service import (
    publish_to_x,
)

from app.services.social_lucky_service import generate_lucky_social_tags

from app.services.batch_state_service import (
    save_current_batch_state,
    load_current_batch_state,
    clear_current_batch_state,
)

from app.services.session_reset_service import (
    reset_social_studio_session,
)

# =====================================
# CORE
# =====================================

from main import (
    generate_prompts_with_grok,
    poll_wavespeed_result,
    submit_wavespeed_task,
    upload_to_imgbb,
    verify_image_url,
)


# =====================================
# UI HELPERS
# =====================================

from app.ui.image_file_utils import (
    IMAGE_EXTENSIONS,
    get_image_files,
    get_unique_image_path,
)

from app.ui.staging_area import (
    move_image_to_staged,
    render_staging_area,
    render_staging_sidebar_button,
)

from app.ui.premium_content_studio import (
    render_premium_content_studio,
)

from app.config.content_paths import (
    ensure_content_dirs,
    get_social_photoshoot_dir,
    get_premium_photoshoot_dir,
)

from app.ui.premium_studio_page import (
    render_premium_studio_page,
)

from app.ui.premium_gallery import (
    render_premium_gallery,
)

# =====================================
# ENVIRONMENT
# =====================================

load_dotenv()

grok_key = os.getenv(
    "GROK_API_KEY"
)

wavespeed_key = os.getenv(
    "WAVESPEED_API_KEY"
)

imgbb_key = os.getenv(
    "IMGBB_API_KEY"
)


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

def build_photoshoot_meta_prompt(prompt_count, shot_ideas=None):
    shot_ideas = shot_ideas or []

    filled_shots = [
        shot.strip()
        for shot in shot_ideas
        if shot.strip()
    ]

    shot_text = ""

    if filled_shots:
        shot_text = "\nSpecific shot ideas to include:\n"

        for i, shot in enumerate(filled_shots, start=1):
            shot_text += f"{i}. {shot}\n"

    camera_behavior = """
CAMERA / FRAMING RULES:

- creator must remain dominant in frame
- close-medium framing preferred
- realistic smartphone creator-photo feel
- avoid distant full-body landscape shots
- avoid scenery-first composition
- environment supports the creator, never dominates
- maintain visual intimacy
- body occupies approximately 60–80% of frame
- use natural handheld framing
- use subtle perspective depth
- favor waist-up, thigh-up, or close full-body compositions
- occasional close crop details are allowed
- maintain natural social-media creator energy

PHONE / SELFIE LIMITING RULES:

- visible phones should be uncommon
- most images should NOT include phones
- avoid repeated selfie compositions
- avoid repeated arm-extended camera poses
- prefer candid creator-content feel
- prefer natural posing over selfie behavior
- only occasional prompts may contain a visible phone
"""

    return f"""
Create exactly {prompt_count} image-to-image photoshoot prompts.

These prompts will use a reference image.

Every prompt must preserve:
- same woman / same identity
- same outfit
- same setting
- same environment
- same lighting
- same mood
- same personality
- same visual style
- same overall aesthetic

{camera_behavior}

Every prompt should create a new photoshoot continuation variation:
- different pose
- different camera angle
- different body position
- different expression
- natural realistic movement
- close creator-content energy
- environment stays secondary to the creator

Do NOT create:
- wide cinematic landscape shots
- tiny subject in large scenery
- scenery-first compositions
- unrelated locations
- unrelated outfits
- unrelated photoshoot concepts

Keep the images realistic, confident, attractive, social-media-ready, and high quality.

{shot_text}

If fewer shot ideas are provided than {prompt_count}, fill the remaining prompts with natural photoshoot variations that preserve the reference image aesthetic.

Return only the prompts as a numbered list.
"""

def build_photoshoot_prompt(
    shot_idea=None
):

    base_prompt = """
Create a new image from the supplied reference image.

Keep the same:

- character identity
- outfit
- location
- environment
- lighting
- personality
- facial appearance
- vibe
- energy
- aesthetics

Generate a new natural photoshoot variation.

Change:
- pose
- body position
- camera angle
- expression
- movement

Make it realistic and visually attractive.
"""

    if shot_idea and shot_idea.strip():

        base_prompt += f"""

Specific shot request:

{shot_idea}
"""

    return base_prompt

# =============================
# GALLERY HELPERS
# =============================

IMAGES_PER_PAGE = 24

def get_photoshoot_folders(photoshoot_root):
    root = Path(photoshoot_root)

    if not root.exists():
        return []

    folders = [
        path
        for path in root.iterdir()
        if path.is_dir()
    ]

    return sorted(
        folders,
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def render_gallery_image_grid(
    image_paths,
    columns=3,
    page_key="gallery",
    mode="gallery",
):
    if not image_paths:
        st.warning("No images found.")
        return

    def build_gallery_preview(image_path):
        preview_dir = Path(selected_output_dir) / "_gallery_preview_cache"

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

        max_width = 900
        max_height = 1200

        image.thumbnail(
            (max_width, max_height)
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

                action_col1, action_col2 = st.columns(2)

                with action_col1:
                    if st.button(
                        "📸 Queue",
                        key=f"gallery_queue_{page_key}_{image_path}",
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

                with action_col2:
                    if st.button(
                        "🗑 Delete",
                        key=f"gallery_delete_{page_key}_{image_path}",
                        use_container_width=True,
                    ):
                        junk_path = (
                            Path(selected_output_dir)
                            / "Junk-Outdated"
                        )

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

                if st.button(
                    "✨ Prepare",
                    key=f"prepare_stage_{page_key}_{image_path}",
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

                        # ==========================
                        # INSTAGRAM
                        # ==========================

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

                        # ==========================
                        # X
                        # ==========================

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

st.set_page_config(
    page_title="Social Content Studio",
    layout="wide",
)

if st.session_state.get("show_premium_studio", False):
    st.title("🔞 Premium Content Studio")
else:
    st.title("☀️ Social Content Studio")

st.markdown("---")

if st.session_state.get("save_toast_message"):
    st.toast(st.session_state["save_toast_message"], icon="✅")
    st.session_state["save_toast_message"] = None

if "photoshoot_queue" not in st.session_state:
    st.session_state["photoshoot_queue"] = []

if "show_photoshoot_queue" not in st.session_state:
    st.session_state["show_photoshoot_queue"] = False

if "show_gallery" not in st.session_state:
    st.session_state["show_gallery"] = False

if "show_staging_area" not in st.session_state:
    st.session_state["show_staging_area"] = False

if "selected_gallery_photoshoot" not in st.session_state:
    st.session_state["selected_gallery_photoshoot"] = None

if "active_photoshoot" not in st.session_state:
    st.session_state["active_photoshoot"] = False

if "active_photoshoot_reference" not in st.session_state:
    st.session_state["active_photoshoot_reference"] = None

if "active_photoshoot_results" not in st.session_state:
    st.session_state["active_photoshoot_results"] = []

if "approved_photoshoot_results" not in st.session_state:
    st.session_state["approved_photoshoot_results"] = []

if "photoshoot_upload_key" not in st.session_state:
    st.session_state["photoshoot_upload_key"] = 0

if "show_premium_studio" not in st.session_state:
    st.session_state["show_premium_studio"] = False



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
ensure_content_dirs(selected_output_dir)

st.sidebar.caption(
    f"Save folder: {selected_output_dir}"
)

# =====================================
# RESTORE SAVED BATCH
# =====================================

if "batch_restored" not in st.session_state:

    saved_batch = load_current_batch_state()

    if saved_batch:

        st.session_state["generated_images"] = [
            {
                "id": f"image_{i}",
                "url": image_path,
                "prompt": prompt_text,
                "status": "completed",
            }
            for i, (image_path, prompt_text)
            in enumerate(
                zip(
                    saved_batch.get(
                        "generated_image_paths",
                        []
                    ),
                    saved_batch.get(
                        "generated_prompts",
                        []
                    ),
                ),
                start=1,
            )
        ]

        st.session_state["generated_prompts"] = [
            {
                "id": f"prompt_{i}",
                "text": prompt_text,
            }
            for i, prompt_text
            in enumerate(
                saved_batch.get(
                    "generated_prompts",
                    []
                ),
                start=1,
            )
        ]

        st.session_state["last_user_tags"] = saved_batch.get(
            "creative_tags",
            "",
        )

        st.session_state["generation_complete"] = True

    st.session_state["batch_restored"] = True

# =====================================
# CREATIVE DIRECTOR
# =====================================

st.sidebar.header("🎬 Creative Director")

# Hidden defaults
# (keep existing backend working)

generation_mode = "Variety Batch Mode"
platform_mode = "Nano Banana Pro"

# =====================================
# CREATIVE MODE
# =====================================

spice_level = st.sidebar.radio(
    "Creative Mode",
    [
        "☀️ Social Safe",
        "🔥 Spicy",
    ],
    index=1,
)

# Keep backend values unchanged

if spice_level == "☀️ Social Safe":
    spice_level = "Social Safe"
elif spice_level == "🔥 Spicy":
    spice_level = "Spicy"

# =====================================
# IMAGE COUNT
# =====================================

st.sidebar.markdown("**Number of Images**")

prompt_count = st.sidebar.slider(
    "Images",
    min_value=1,
    max_value=25,
    value=10,
    label_visibility="collapsed",
)

st.sidebar.caption(
    f"Images: {prompt_count}"
)


# -----------------------------
# MAIN GENERATOR VISIBILITY
# -----------------------------
show_main_generator = (
    not st.session_state.get("show_photoshoot_queue", False)
    and not st.session_state.get("active_photoshoot", False)
    and not st.session_state.get("show_gallery", False)
    and not st.session_state.get("show_staging_area", False)
)

# -----------------------------
# MAIN INPUTS
# -----------------------------
if st.session_state.get("show_premium_studio", False):

    render_premium_studio_page(
        selected_output_dir
    )

elif show_main_generator:

    st.subheader("Reference Image")

    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 0

    uploaded_file = st.file_uploader(
        "Upload Reference Image",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"uploaded_file_{st.session_state['uploader_key']}",
    )

    st.subheader("Creative Tags")

    st.caption(
        "Enter ideas, not prompts. The Creative Director will build the shoot."
    )

    # --------------------------------
    # SESSION STATE
    # --------------------------------

    if "creative_tags_input_box" not in st.session_state:
        st.session_state["creative_tags_input_box"] = ""

    # --------------------------------
    # I FEEL LUCKY HANDLER
    # --------------------------------

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

        st.session_state["creative_tags_input_box"] = str(lucky_tags).strip()

    # --------------------------------
    # CREATIVE TAGS BOX
    # --------------------------------

    user_tags = st.text_area(
        label="Creative Tags",
        key="creative_tags_input_box",
        placeholder="Type your creative tags here...",
        label_visibility="collapsed",
    )

    # --------------------------------
    # I FEEL LUCKY
    # --------------------------------

    st.button(
        "🎲 I Feel Lucky",
        use_container_width=True,
        on_click=fill_lucky_tags,
    )

    # -----------------------------
    # GENERATE BUTTON
    # -----------------------------
    get_prompts_button_label = (
        "🔄 Get Fresh New Prompts"
        if (
            "generated_prompts" in st.session_state
            and st.session_state["generated_prompts"]
        )
        else "✨ Get Prompts"
    )

    get_prompts_clicked = st.button(
        get_prompts_button_label,
        use_container_width=True,
        disabled=uploaded_file is None,
    )

    if uploaded_file is None:
        st.caption("Upload a reference image before creating a shoot.")

    # -----------------------------
    # GENERATE PROMPTS
    # -----------------------------
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

        refresh_nonce = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

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

        # Clear old prompt text widgets so Streamlit does not reuse stale values
        for key in list(st.session_state.keys()):
            if key.startswith("text_prompt_"):
                del st.session_state[key]

        # Give each prompt batch a unique ID
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
        st.session_state["review_mode"] = "review"

        st.success("Prompt batch generated.")

        st.rerun()


    # -----------------------------
    # GENERATED PROMPTS DISPLAY
    # -----------------------------
    if (
        "generated_prompts" in st.session_state
        and st.session_state["generated_prompts"]
    ):

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

        st.markdown("### User Tags")
        st.code(st.session_state.get("last_user_tags", user_tags))


    # -----------------------------
    # CREATE SHOOT WITH NANO BANANA PRO
    # -----------------------------
    create_shoot_clicked = st.button(
        "🍌 Create Shoot",
        use_container_width=True,
        disabled=(
            "generated_prompts" not in st.session_state
            or not st.session_state["generated_prompts"]
            or uploaded_file is None
        ),
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

        if (
            "generated_prompts" not in st.session_state
            or not st.session_state["generated_prompts"]
        ):
            st.error("Get prompts first before creating a shoot.")
            st.stop()

        if not uploaded_file:
            st.error("Please upload a reference image before creating a shoot.")
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
            f"Creating {total_prompts} image(s) with {selected_model['name']}. This will use WaveSpeed credits."
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

        with st.spinner("Uploading reference image to ImgBB..."):
            image_url = upload_to_imgbb(
                temp_image_path,
                imgbb_key
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
            start=1
        ):

            prompt_text = prompt_item["text"]

            completed_count = len(st.session_state["generated_images"])
            failed_count = len(st.session_state["failed_images"])

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

                st.session_state["generated_images"].append(
                    {
                        "id": f"image_{index}",
                        "prompt": prompt_text,
                        "url": output_url,
                        "status": "completed",
                    }
                )

                save_current_batch_state(
                    creator_name=selected_creator_name,
                    creative_tags=st.session_state.get("last_user_tags", ""),
                    generated_prompts=[
                        item["text"]
                        for item in st.session_state.get(
                            "generated_prompts",
                            []
                        )
                    ],
                    generated_image_paths=[
                        item["url"]
                        for item in st.session_state.get(
                            "generated_images",
                            []
                        )
                    ],
                )

                with live_gallery.container():
                    st.markdown("---")
                    st.subheader("Live Generated Images")

                    current_images = list(
                        reversed(st.session_state["generated_images"])
                    )

                    cols = st.columns(2)

                    for i, image_item in enumerate(current_images):
                        with cols[i % 2]:
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

        live_gallery.empty()

        st.rerun()

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

    cols = st.columns(3)

    for i, image_item in enumerate(st.session_state["generated_images"]):
        image_id = image_item.get("id", f"image_{i + 1}")

        with cols[i % 3]:

            st.image(image_item["url"], use_container_width=True)

            st.checkbox("Discard", key=f"discard_{image_id}")

            st.checkbox(
                "📸 Continue Photoshoot",
                key=f"photoshoot_{image_id}",
            )

            st.checkbox(
                "📖 Create Story (Coming Soon)",
                key=f"story_{image_id}",
                disabled=True,
            )

            with st.expander("Prompt"):
                st.write(image_item["prompt"])

    st.markdown("---")

    discard_ids = []
    photoshoot_ids = []

    for image_item in st.session_state["generated_images"]:
        image_id = image_item.get("id")

        if st.session_state.get(f"discard_{image_id}", False):
            discard_ids.append(image_id)

        if st.session_state.get(f"photoshoot_{image_id}", False):
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

            st.session_state["generated_images"] = [
                img for img in st.session_state["generated_images"]
                if img["id"] not in discard_ids
            ]

            st.session_state["save_toast_message"] = (
                f"🗑️ Discarded {len(discard_ids)} image(s)"
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
                        []
                    )
                ],
                generated_image_paths=[
                    item["url"]
                    for item in st.session_state.get(
                        "generated_images",
                        []
                    )
                ],
            )

            st.rerun()

        else:

            normal_save_images = []
            photoshoot_save_images = []

            for image_item in st.session_state["generated_images"]:
                image_id = image_item.get("id")

                if image_id in photoshoot_ids:
                    photoshoot_save_images.append(image_item)
                else:
                    normal_save_images.append(image_item)

            selected_model = MODELS["2"]

            normal_saved_count = 0
            photoshoot_saved_count = 0

            if normal_save_images:
                save_generated_images(
                    images=normal_save_images,
                    output_dir=selected_output_dir,
                    creator_name=selected_creator_name,
                    model_name=selected_model["name"],
                    user_tags=st.session_state.get("last_user_tags", user_tags),
                    generation_mode=st.session_state.get("last_generation_mode", generation_mode),
                    platform_mode=st.session_state.get("last_platform_mode", platform_mode),
                    spice_level=st.session_state.get("last_spice_level", spice_level),
                    uploaded_file=uploaded_file,
                )

                normal_saved_count = len(normal_save_images)

            photoshoot_output_dir = r"D:\Ava Blackthorne\Ready\Wavespeed\Photoshoot"

            if photoshoot_save_images:
                save_generated_images(
                    images=photoshoot_save_images,
                    output_dir=photoshoot_output_dir,
                    creator_name=selected_creator_name,
                    model_name=selected_model["name"],
                    user_tags=st.session_state.get("last_user_tags", user_tags),
                    generation_mode=st.session_state.get("last_generation_mode", generation_mode),
                    platform_mode=st.session_state.get("last_platform_mode", platform_mode),
                    spice_level=st.session_state.get("last_spice_level", spice_level),
                    uploaded_file=uploaded_file,
                )

                photoshoot_saved_count = len(photoshoot_save_images)

            st.session_state["save_toast_message"] = (
                f"✅ Saved {normal_saved_count} image(s). "
                f"📸 Sent {photoshoot_saved_count} image(s) to Photoshoot."
            )

            st.session_state["save_toast_time"] = time.time()

            clear_current_batch_state()
            st.session_state["generated_images"] = []
            st.session_state["failed_images"] = []
            st.session_state["generated_prompts"] = []
            st.session_state["discard_happened"] = False
            st.session_state["last_saved_folder"] = None
            st.session_state["generation_complete"] = False
            st.session_state["generation_status"] = ""

            st.session_state["uploader_key"] += 1
            
            st.rerun()

# -----------------------------
# PHOTOSHOOT QUEUE DISPLAY
# -----------------------------
photoshoot_output_dir = Path(
    r"D:\Ava Blackthorne\Ready\Wavespeed\Photoshoot"
)

photoshoot_output_dir.mkdir(
    parents=True,
    exist_ok=True
)

photoshoot_images = sorted(
    [
        image_path
        for image_path in photoshoot_output_dir.iterdir()
        if image_path.suffix.lower()
        in [".png", ".jpg", ".jpeg", ".webp"]
    ],
    key=lambda path: path.stat().st_mtime,
    reverse=True,
)

# ==========================
# SIDEBAR PHOTOSHOOT SECTION
# ==========================

st.sidebar.markdown("---")
st.sidebar.header("Photoshoot")

st.sidebar.caption(
    f"{len(photoshoot_images)} image(s) queued"
)

if st.sidebar.button(
    "📸 Enter Photoshoot Queue",
    use_container_width=True
):
    st.session_state["show_photoshoot_queue"] = True
    st.session_state["show_gallery"] = False
    st.session_state["selected_gallery_photoshoot"] = None
    st.session_state["active_photoshoot"] = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("Gallery")

if st.sidebar.button(
    "🖼 Browse Gallery",
    use_container_width=True,
):
    st.session_state["show_gallery"] = True
    st.session_state["show_photoshoot_queue"] = False
    st.session_state["active_photoshoot"] = False
    st.session_state["selected_gallery_photoshoot"] = None
    st.rerun()

render_staging_sidebar_button()

st.sidebar.markdown("---")

st.sidebar.subheader(
    "🔞 Premium"
)

if st.sidebar.button(
    "Enter Premium Studio",
    use_container_width=True,
):
    st.session_state["show_premium_studio"] = True
    st.session_state["show_photoshoot_queue"] = False
    st.session_state["show_gallery"] = False
    st.session_state["show_staging_area"] = False
    st.session_state["active_photoshoot"] = False
    st.rerun()

# ==========================
# MAIN PAGE GALLERY VIEW
# ==========================

if st.session_state.get("show_gallery", False):
    gallery_root = Path(selected_output_dir)
    photoshoot_root = gallery_root / "Photoshoot"

    header_col1, header_col2 = st.columns([8, 2])

    with header_col1:
        st.subheader("🖼 Gallery")

    with header_col2:
        if st.button(
            "⬅ Back",
            key="back_from_gallery",
            use_container_width=True,
        ):
            st.session_state["show_gallery"] = False
            st.session_state["selected_gallery_photoshoot"] = None
            st.rerun()

    gallery_tab, photoshoot_tab = st.tabs(
        [
            "All Content",
            "Photoshoots",
        ]
    )

    with gallery_tab:
        st.markdown("### All Content")
        st.caption(f"Showing images directly inside: {gallery_root}")

        root_images = get_image_files(
            gallery_root,
            recursive=False,
        )

        render_gallery_image_grid(
            root_images,
            columns=3,
            page_key="all_content_gallery",
            mode="gallery",
        )

    with photoshoot_tab:
        selected_folder = st.session_state.get(
            "selected_gallery_photoshoot"
        )

        if selected_folder:
            selected_folder_path = Path(selected_folder)

            top_col1, top_col2 = st.columns([8, 2])

            with top_col1:
                st.markdown(f"### 📁 {selected_folder_path.name}")

            with top_col2:
                if st.button(
                    "⬅ Photoshoots",
                    key="back_to_photoshoot_folders",
                    use_container_width=True,
                ):
                    st.session_state["selected_gallery_photoshoot"] = None
                    st.rerun()

            photoshoot_images = get_image_files(
                selected_folder_path,
                recursive=False,
            )

            render_gallery_image_grid(
                photoshoot_images,
                columns=3,
                page_key=f"photoshoot_gallery_{selected_folder_path.name}",
            )
        else:
            st.markdown("### Photoshoot Albums")
            st.caption(f"Showing folders inside: {photoshoot_root}")

            photoshoot_folders = get_photoshoot_folders(
                photoshoot_root,
            )

            if not photoshoot_folders:
                st.warning("No photoshoot folders found.")
            else:
                cols = st.columns(3)

                for index, folder_path in enumerate(photoshoot_folders):
                    folder_images = get_image_files(
                        folder_path,
                        recursive=False,
                    )

                    with cols[index % 3]:
                        if folder_images:
                            st.image(
                                str(folder_images[0]),
                                use_container_width=True,
                            )
                        else:
                            st.info("No images")

                        st.markdown(f"**📁 {folder_path.name}**")
                        st.caption(f"{len(folder_images)} image(s)")

                        if st.button(
                            "Open Photoshoot",
                            key=f"open_gallery_folder_{folder_path.name}",
                            use_container_width=True,
                        ):
                            st.session_state["selected_gallery_photoshoot"] = str(folder_path)
                            st.rerun()

# ==========================
# STAGING AREA
# ==========================

if st.session_state.get(
    "show_staging_area",
    False
):

    if st.session_state.get(
        "publish_review_image"
    ):

        st.subheader("📲 Confirm Publishing")

        review_image_path = Path(
            st.session_state["publish_review_image"]
        )

        ig_caption = st.session_state.get(
            "publish_review_instagram_caption",
            ""
        )

        x_caption = st.session_state.get(
            "publish_review_x_caption",
            ""
        )

        preview_col, publish_col = st.columns(
            [4, 8]
        )

        with preview_col:

            st.image(
                str(review_image_path),
                use_container_width=True,
            )

        with publish_col:

            st.markdown("## Captions")

            st.markdown("### Instagram")

            st.info(
                ig_caption
            )

            st.markdown("### X")

            st.info(
                x_caption
            )

            post_col, copy_col, spacer_col = st.columns(
                [2, 2, 8]
            )

            with post_col:

                if st.button(
                    "🚀 Publish",
                    key="confirm_publish_all_button",
                    help="Publish to Instagram and X",
                    use_container_width=True,
                ):

                    instagram_success = False
                    x_success = False

                    try:

                        publish_to_x(
                            image_path=str(review_image_path),
                            caption=x_caption,
                        )

                        x_success = True

                    except Exception as error:

                        st.error(
                            f"X post failed: {error}"
                        )

                    try:

                        instagram_success = publish_to_instagram(
                            image_path=str(review_image_path),
                            caption=ig_caption,
                        )

                    except Exception as error:

                        st.error(
                            f"Instagram publish failed: {error}"
                        )

                    if instagram_success and x_success:

                        posted_socials_dir = (
                            review_image_path.parent.parent
                            / "Posted-Socials"
                        )

                        posted_socials_dir.mkdir(
                            parents=True,
                            exist_ok=True,
                        )

                        posted_image_path = get_unique_image_path(
                            posted_socials_dir,
                            review_image_path.name,
                        )

                        if review_image_path.exists():

                            shutil.move(
                                str(review_image_path),
                                str(posted_image_path),
                            )

                        st.session_state[
                            "save_toast_message"
                        ] = "🚀 Published to Instagram + X and moved to Posted-Socials"

                        st.session_state[
                            "publish_review_image"
                        ] = None

                        st.session_state[
                            "publish_review_instagram_caption"
                        ] = ""

                        st.session_state[
                            "publish_review_x_caption"
                        ] = ""

                        st.session_state[
                            "show_staging_area"
                        ] = False

                        st.rerun()

                    elif instagram_success:

                        st.success(
                            "Instagram sent to phone, but X failed."
                        )

                    elif x_success:

                        st.success(
                            "Posted to X, but Instagram failed."
                        )

            with copy_col:

                if st.button(
                    "📋 Copy IG",
                    key="copy_ig_caption_to_phone",
                    help="Copy Instagram caption to phone",
                    use_container_width=True,
                ):

                    copy_caption_to_phone_clipboard(
                        ig_caption
                    )

                    st.toast(
                        "📋 Instagram caption copied to phone",
                        icon="✅",
                    )

        st.markdown("---")

        if st.button(
            "⬅ Back To Captions",
            key="back_to_caption_selection",
            use_container_width=True,
        ):

            st.session_state[
                "publish_review_image"
            ] = None

            st.session_state[
                "publish_review_instagram_caption"
            ] = ""

            st.session_state[
                "publish_review_x_caption"
            ] = ""

            st.rerun()

        st.stop()

    render_staging_area(
        render_gallery_image_grid
    )

    st.stop()

# ==========================
# MAIN PAGE PHOTOSHOOT VIEW
# ==========================

if (
    st.session_state.get("show_photoshoot_queue", False)
    and not st.session_state.get("active_photoshoot", False)
):
    
    if "photoshoot_upload_key" not in st.session_state:
        st.session_state["photoshoot_upload_key"] = 0

    header_col1, header_col2 = st.columns([8, 2])

    with header_col1:
        st.subheader("📸 Photoshoot Queue Manager")

    with header_col2:
        if st.button(
            "⬅ Back",
            key="back_generator",
            use_container_width=True
        ):
            st.session_state["show_photoshoot_queue"] = False
            st.rerun()

    st.markdown("### ➕ Add Image To Photoshoot Queue")

    uploaded_photoshoot = st.file_uploader(
        "",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"photoshoot_queue_upload_{st.session_state['photoshoot_upload_key']}"
    )

    if uploaded_photoshoot:

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_suffix = Path(uploaded_photoshoot.name).suffix.lower()

        save_path = photoshoot_output_dir / f"queue_{timestamp}{file_suffix}"

        with open(save_path, "wb") as f:
            f.write(uploaded_photoshoot.getbuffer())

        st.session_state["photoshoot_upload_key"] += 1
        st.session_state["save_toast_message"] = "📸 Added to Photoshoot Queue"

        st.rerun()

    st.markdown("---")

    photoshoot_images = sorted(
        [
            image_path
            for image_path in photoshoot_output_dir.iterdir()
            if image_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not photoshoot_images:

        st.warning("No images currently in Photoshoot Queue.")

    else:

        cols = st.columns(2)

        for i, image_path in enumerate(photoshoot_images):

            image_key = image_path.stem

            with cols[i % 2]:

                st.image(
                    str(image_path),
                    use_container_width=True
                )

                photoshoot_count = st.number_input(
                    "Number of Photoshoot Images",
                    min_value=1,
                    max_value=25,
                    value=5,
                    key=f"photoshoot_count_{image_key}",
                )

                shot_ideas = []

                with st.expander(
                    "Shot Ideas Optional",
                    expanded=False
                ):

                    for shot_index in range(1, photoshoot_count + 1):

                        shot_text = st.text_input(
                            f"Shot {shot_index}",
                            key=f"shot_{image_key}_{shot_index}",
                            placeholder="Optional: sitting on rock, walking trail, leaning on tree...",
                        )

                        shot_ideas.append(shot_text)

                action_col1, action_col2 = st.columns(2)

                with action_col1:

                    start_photoshoot_clicked = st.button(
                        "🚀 Start Photoshoot",
                        key=f"start_photoshoot_{image_key}",
                        use_container_width=True,
                    )

                with action_col2:

                    move_gallery_clicked = st.button(
                        "↩ Move To Gallery",
                        key=f"move_gallery_{image_key}",
                        use_container_width=True,
                    )

                    if move_gallery_clicked:

                        gallery_path = selected_output_dir

                        destination = get_unique_image_path(
                            gallery_path,
                            Path(image_path).name,
                        )

                        shutil.move(
                            str(image_path),
                            str(destination),
                        )
                        
                        st.session_state["save_toast_message"] = (
                            "↩ Moved image back to Gallery"
                        )

                        st.rerun()
           

                if start_photoshoot_clicked:

                    if not grok_key:
                        st.error("Missing GROK_API_KEY in .env")
                        st.stop()

                    if not wavespeed_key:
                        st.error("Missing WAVESPEED_API_KEY in .env")
                        st.stop()

                    if not imgbb_key:
                        st.error("Missing IMGBB_API_KEY in .env")
                        st.stop()

                    st.session_state["active_photoshoot"] = True
                    st.session_state["show_photoshoot_queue"] = False
                    st.session_state["active_photoshoot_reference"] = str(image_path)
                    st.session_state["active_photoshoot_count"] = photoshoot_count
                    st.session_state["active_photoshoot_shot_ideas"] = shot_ideas
                    st.session_state["active_photoshoot_results"] = []
                    st.session_state["approved_photoshoot_results"] = []

                    selected_model = MODELS["2"]

                    status_box = st.empty()
                    progress_bar = st.progress(0)
                    live_gallery = st.empty()

                    photoshoot_meta_prompt = build_photoshoot_meta_prompt(
                        prompt_count=photoshoot_count,
                        shot_ideas=shot_ideas,
                    )

                    photoshoot_prompts = generate_prompts_with_grok(
                        photoshoot_meta_prompt,
                        grok_key,
                    )

                    with st.spinner("Uploading photoshoot reference image..."):

                        image_url = upload_to_imgbb(
                            str(image_path),
                            imgbb_key,
                        )

                        verify_image_url(image_url)

                    completed_count = 0
                    failed_count = 0

                    for index, prompt_text in enumerate(
                        photoshoot_prompts[:photoshoot_count],
                        start=1
                    ):

                        remaining_count = (
                            photoshoot_count
                            - completed_count
                            - failed_count
                        )

                        status_box.info(
                            f"Photoshoot image {index} of {photoshoot_count}: processing... "
                            f"✅ {completed_count} completed "
                            f"❌ {failed_count} failed "
                            f"⏳ {remaining_count} remaining"
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

                            st.session_state["active_photoshoot_results"].append(
                                {
                                    "id": f"photoshoot_{index}",
                                    "prompt": prompt_text,
                                    "url": output_url,
                                    "status": "completed",
                                }
                            )

                            completed_count += 1

                            completed_images = [
                                result["url"]
                                for result in st.session_state["active_photoshoot_results"]
                                if result.get("status") == "completed"
                            ]

                            with live_gallery.container():

                                st.markdown("---")
                                st.subheader("Live Photoshoot Images")

                                live_cols = st.columns(3)

                                for img_index, img_url in enumerate(completed_images):

                                    with live_cols[img_index % 3]:

                                        st.image(
                                            img_url,
                                            use_container_width=True
                                        )

                        except Exception as error:

                            st.session_state["active_photoshoot_results"].append(
                                {
                                    "id": f"photoshoot_{index}",
                                    "prompt": prompt_text,
                                    "error": str(error),
                                    "status": "failed",
                                }
                            )

                            failed_count += 1

                        progress_bar.progress(index / photoshoot_count)

                    status_box.success(
                        f"Photoshoot complete "
                        f"✅ {completed_count} completed "
                        f"❌ {failed_count} failed"
                    )

                    live_gallery.empty()

                    st.rerun()


# ==========================
# ACTIVE PHOTOSHOOT
# ==========================

if (
    st.session_state.get("active_photoshoot", False)
    and st.session_state.get("active_photoshoot_results")
):

    st.markdown("---")
    st.subheader("📸 Photoshoot Results")

    st.markdown(
        """
        <style>
        [data-testid="stImage"] img {
            height: 420px;
            width: 100%;
            object-fit: contain;
            border-radius: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    reference_path = st.session_state.get("active_photoshoot_reference")

    if reference_path:

        st.markdown("### Source Reference Image")

        st.image(
            reference_path,
            width=400,
        )

    completed_results = [
        result
        for result in st.session_state.get("active_photoshoot_results", [])
        if result.get("status") == "completed"
    ]

    if completed_results:

        st.markdown("### Generated Photoshoot Images")

        cols = st.columns(3)

        for i, result_item in enumerate(completed_results):

            result_id = result_item.get(
                "id",
                f"photoshoot_{i + 1}"
            )

            with cols[i % 3]:

                st.image(
                    result_item["url"],
                    use_container_width=True,
                    clamp=True,
                )

                st.checkbox(
                    "Discard",
                    key=f"discard_photoshoot_{result_id}",
                )

                with st.expander("Prompt"):
                    st.write(result_item["prompt"])

        st.markdown("---")

        discard_ids = []

        for result_item in completed_results:

            result_id = result_item.get("id")

            if st.session_state.get(
                f"discard_photoshoot_{result_id}",
                False
            ):
                discard_ids.append(result_id)

        if discard_ids:
            photoshoot_button_label = "🗑️ Discard Selected"
        else:
            photoshoot_button_label = "✅ Approve All Photoshoot Images"

        if st.button(
            photoshoot_button_label,
            use_container_width=True,
        ):

            if discard_ids:

                st.session_state["active_photoshoot_results"] = [
                    result
                    for result in st.session_state["active_photoshoot_results"]
                    if result.get("id") not in discard_ids
                ]

                st.session_state["save_toast_message"] = (
                    f"🗑️ Discarded {len(discard_ids)} photoshoot image(s)"
                )

                st.rerun()

            else:

                photoshoot_root_dir = Path(
                    r"D:\Ava Blackthorne\Ready\Wavespeed\Photoshoot"
                )

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                completed_folder = (
                    photoshoot_root_dir
                    / f"photoshoot_{timestamp}"
                )

                completed_folder.mkdir(
                    parents=True,
                    exist_ok=True
                )

                reference_source_path = Path(
                    st.session_state["active_photoshoot_reference"]
                )

                reference_target_path = (
                    completed_folder
                    / "source_reference.png"
                )

                if reference_source_path.exists():

                    reference_source_path.replace(
                        reference_target_path
                    )

                save_generated_images(
                    images=completed_results,
                    output_dir=completed_folder,
                )

                st.session_state["save_toast_message"] = (
                    f"✅ Photoshoot saved to {completed_folder}"
                )

                st.session_state["active_photoshoot"] = False
                st.session_state["active_photoshoot_reference"] = None
                st.session_state["active_photoshoot_results"] = []
                st.session_state["approved_photoshoot_results"] = []

                st.rerun()