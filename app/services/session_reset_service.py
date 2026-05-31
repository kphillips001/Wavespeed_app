import streamlit as st

from app.services.batch_state_service import (
    clear_current_batch_state,
)


def reset_social_studio_session():
    clear_current_batch_state()

    keys_to_clear = [
        "generated_prompts",
        "generated_images",
        "failed_images",
        "generation_complete",
        "generation_status",
        "review_mode",
        "discard_happened",
        "last_saved_folder",
        "last_user_tags",
        "last_generation_mode",
        "last_platform_mode",
        "last_spice_level",
        "last_prompt_count",
        "creative_tags_input_box",
        "cancel_generation",
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    for key in list(st.session_state.keys()):
        if (
            key.startswith("text_prompt_")
            or key.startswith("delete_prompt_")
            or key.startswith("discard_image_")
            or key.startswith("photoshoot_image_")
            or key.startswith("story_image_")
        ):
            del st.session_state[key]

    st.session_state["generated_prompts"] = []
    st.session_state["generated_images"] = []
    st.session_state["failed_images"] = []
    st.session_state["generation_complete"] = False
    st.session_state["generation_status"] = ""
    st.session_state["creative_tags_input_box"] = ""
    st.session_state["last_user_tags"] = ""

    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 0

    st.session_state["uploader_key"] += 1