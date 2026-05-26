import streamlit as st


def render_premium_content_studio():
   
    st.subheader("Reference Image")

    if "premium_uploader_key" not in st.session_state:
        st.session_state["premium_uploader_key"] = 0

    premium_uploaded_file = st.file_uploader(
        "Upload Premium Reference Image",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"premium_uploaded_file_{st.session_state['premium_uploader_key']}",
    )

    st.subheader("Creative Tags")

    st.caption(
        "Enter ideas, not prompts. The Premium Creative Director will build the shoot."
    )

    with st.expander(
        "💡 Premium Example Ideas",
        expanded=False,
    ):
        st.markdown(
            """
- luxury bedroom
- hotel mirror
- black lingerie set
- moody window light
- soft cinematic lighting
- Fanvue teaser set
            """
        )

    if "premium_creative_tags_key" not in st.session_state:
        st.session_state["premium_creative_tags_key"] = 0

    premium_user_tags = st.text_area(
        label="",
        key=f"premium_creative_tags_{st.session_state['premium_creative_tags_key']}",
        placeholder="Type your premium creative tags here...",
        label_visibility="collapsed",
    )

    create_premium_clicked = st.button(
        "✨ Create Premium Shoot",
        use_container_width=True,
        disabled=premium_uploaded_file is None,
    )

    if premium_uploaded_file is None:
        st.caption(
            "Upload a premium reference image before creating a premium shoot."
        )

    if create_premium_clicked:
        if not premium_user_tags.strip():
            st.error("Please enter some premium creative tags.")
            st.stop()

        st.info(
            "Premium Studio UI is ready. Generation logic will be connected next."
        )