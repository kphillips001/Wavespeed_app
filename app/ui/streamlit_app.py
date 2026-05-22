import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import os

import streamlit as st
from dotenv import load_dotenv

from app.prompts.prompt_builder import build_chatgpt_prompt
from app.prompts.generation_modes import GENERATION_MODES
from app.prompts.platform_modes import PLATFORM_MODES
from app.prompts.spice_levels import SPICE_LEVELS
from main import generate_prompts_with_grok


load_dotenv()

grok_key = os.getenv("GROK_API_KEY")


st.set_page_config(
    page_title="WaveSpeed AI Studio",
    layout="wide",
)

st.title("🔥 WaveSpeed AI Studio")

st.markdown("---")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("Generation Settings")

generation_mode = st.sidebar.selectbox(
    "Generation Mode",
    [
        mode["name"]
        for mode in GENERATION_MODES.values()
    ]
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

# -----------------------------
# MAIN INPUTS
# -----------------------------
st.subheader("Reference Image")

uploaded_file = st.file_uploader(
    "Upload Reference Image",
    type=["png", "jpg", "jpeg", "webp"]
)

st.subheader("Creative Tags")

user_tags = st.text_area(
    "Enter tags, outfits, scenes, vibes, locations, etc.",
    placeholder="Example: bikini, summertime, lake",
    height=120,
)

# -----------------------------
# GENERATE BUTTON
# -----------------------------
generate_clicked = st.button(
    "🚀 Generate Prompt Batch",
    use_container_width=True,
)

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