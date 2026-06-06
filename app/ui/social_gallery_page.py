from pathlib import Path

import streamlit as st

from app.ui.image_file_utils import (
    get_image_files,
)

from app.ui.social_gallery import (
    render_gallery_image_grid,
)


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


def render_social_gallery_page(selected_output_dir):
    gallery_root = Path(selected_output_dir)
    photoshoot_root = gallery_root / "Photoshoot"

    header_col1, header_col2 = st.columns([8, 2])

    with header_col1:
        st.subheader("Gallery")

    with header_col2:
        if st.button(
            "Back",
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
            selected_output_dir=selected_output_dir,
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
                st.markdown(f"### {selected_folder_path.name}")

            with top_col2:
                if st.button(
                    "Photoshoots",
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
                selected_output_dir=selected_output_dir,
                columns=3,
                page_key=f"photoshoot_gallery_{selected_folder_path.name}",
                mode="gallery",
            )

        else:
            st.markdown("### Photoshoot Albums")
            st.caption(f"Showing folders inside: {photoshoot_root}")

            photoshoot_folders = get_photoshoot_folders(
                photoshoot_root,
            )

            if not photoshoot_folders:
                st.warning("No photoshoot folders found.")
                return

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

                    st.markdown(f"**{folder_path.name}**")
                    st.caption(f"{len(folder_images)} image(s)")

                    if st.button(
                        "Open Photoshoot",
                        key=f"open_gallery_folder_{folder_path.name}",
                        use_container_width=True,
                    ):
                        st.session_state["selected_gallery_photoshoot"] = str(
                            folder_path
                        )
                        st.rerun()
