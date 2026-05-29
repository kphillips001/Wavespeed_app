import streamlit as st

from app.ui.premium_content_studio import (
    render_premium_content_studio,
)

from app.ui.premium_photoshoot_queue import (
    render_premium_photoshoot_queue,
)

from app.ui.premium_gallery import (
    render_premium_gallery,
)


def render_premium_studio_page(selected_output_dir):

    # -----------------------------
    # SESSION STATES
    # -----------------------------

    if "show_premium_photoshoot_queue" not in st.session_state:
        st.session_state["show_premium_photoshoot_queue"] = False

    if "show_premium_gallery" not in st.session_state:
        st.session_state["show_premium_gallery"] = False

    # -----------------------------
    # PREMIUM PHOTOSHOOT QUEUE PAGE
    # -----------------------------

    if st.session_state["show_premium_photoshoot_queue"]:

        if st.button("← Return To Premium Studio"):
            st.session_state["show_premium_photoshoot_queue"] = False
            st.rerun()

        render_premium_photoshoot_queue(
            selected_output_dir
        )

        return

    # -----------------------------
    # PREMIUM GALLERY PAGE
    # -----------------------------

    if st.session_state["show_premium_gallery"]:

        if st.button("← Return To Premium Studio"):
            st.session_state["show_premium_gallery"] = False
            st.rerun()

        render_premium_gallery(
            selected_output_dir
        )

        return

    # -----------------------------
    # MAIN PREMIUM PAGE
    # -----------------------------

    if st.button(
        "← Return to Social Studio",
        use_container_width=False,
    ):
        st.session_state["show_premium_studio"] = False
        st.session_state["show_premium_photoshoot_queue"] = False
        st.session_state["show_premium_gallery"] = False
        st.rerun()

    st.markdown("---")

    render_premium_content_studio(
        selected_output_dir=selected_output_dir,
    )

    st.markdown("---")

    st.subheader("📸 Premium Photoshoot Queue")

    if st.button(
        "Enter Premium Photoshoot Queue",
        use_container_width=True,
    ):
        st.session_state["show_premium_photoshoot_queue"] = True
        st.session_state["show_premium_gallery"] = False
        st.rerun()

    st.markdown("---")

    st.subheader("🖼 Premium Gallery")

    if st.button(
        "Browse Premium Gallery",
        use_container_width=True,
    ):
        st.session_state["show_premium_gallery"] = True
        st.session_state["show_premium_photoshoot_queue"] = False
        st.rerun()

    st.markdown("---")

    st.subheader("📤 Export To FanvueChatbot")

    st.info("Export workflow coming next.")