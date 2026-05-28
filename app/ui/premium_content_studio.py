import streamlit as st

from app.services.premium_director_service import generate_premium_prompts


def render_premium_content_studio():
    st.subheader("Reference Image")

    if "premium_uploader_key" not in st.session_state:
        st.session_state["premium_uploader_key"] = 0

    if "premium_prompts" not in st.session_state:
        st.session_state["premium_prompts"] = []

    premium_uploaded_file = st.file_uploader(
        "Upload Premium Reference Image",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"premium_uploaded_file_{st.session_state['premium_uploader_key']}",
    )

    st.subheader("Creative Tags")

    st.caption(
        "Enter ideas, not prompts. The Premium Creative Director will build the prompts."
    )

    premium_user_tags = st.text_area(
        label="",
        key="premium_creative_tags",
        placeholder="Type your premium creative tags here...",
        label_visibility="collapsed",
    )

    get_premium_prompts_clicked = st.button(
        "✨ Get Premium Prompts",
        use_container_width=True,
        disabled=premium_uploaded_file is None or not premium_user_tags.strip(),
    )

    if premium_uploaded_file is None:
        st.caption(
            "Upload a premium reference image before getting premium prompts."
        )

    if get_premium_prompts_clicked:
        with st.spinner("Generating premium prompts with Grok..."):
            premium_prompts = generate_premium_prompts(
                creative_tags=premium_user_tags,
                prompt_count=10,
            )

        st.session_state["premium_uploaded_file"] = premium_uploaded_file
        st.session_state["premium_user_tags"] = premium_user_tags

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

        st.success("Premium prompt batch generated.")

    st.subheader("Premium Renderer")

    premium_renderer = st.selectbox(
        "Choose premium render engine",
        options=[
            "Wan 2.7 Image Edit",
        ],
        index=0,
        key="premium_renderer",
        label_visibility="collapsed",
    )

    generate_premium_images_clicked = st.button(
        "🔥 Generate Premium Images",
        use_container_width=True,
        disabled=(
            premium_uploaded_file is None
            or not st.session_state["premium_prompts"]
        ),
    )

    if generate_premium_images_clicked:
        st.session_state["premium_renderer"] = premium_renderer
        st.info("WAN 2.7 image generation will connect here next.")

    if st.session_state["premium_prompts"]:
        with st.expander(
            "View Generated Premium Prompts",
            expanded=False,
        ):
            prompts_to_delete = []

            for index, prompt_data in enumerate(
                st.session_state["premium_prompts"],
                start=1,
            ):
                prompt_id = prompt_data["id"]
                prompt_text = prompt_data["text"]

                st.markdown(f"### Premium Prompt {index}")

                st.text_area(
                    label=f"Premium Prompt {index}",
                    value=prompt_text,
                    height=120,
                    label_visibility="collapsed",
                    key=f"premium_prompt_preview_{prompt_id}",
                    disabled=True,
                )

                action_col1, action_col2 = st.columns(2)

                with action_col1:
                    if st.button(
                        "📸 Add To Photoshoot",
                        key=f"add_premium_photoshoot_{prompt_id}",
                        use_container_width=True,
                    ):
                        st.info("Photoshoot queue logic will connect here later.")

                with action_col2:
                    if st.button(
                        "🗑️ Delete",
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