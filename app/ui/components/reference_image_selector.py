from datetime import datetime
from pathlib import Path

import streamlit as st


IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}


def get_reference_images(reference_dir):
    reference_path = Path(reference_dir)

    reference_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return sorted(
        [
            image_path
            for image_path in reference_path.iterdir()
            if (
                image_path.is_file()
                and image_path.suffix.lower() in IMAGE_EXTENSIONS
            )
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def get_unique_reference_path(reference_dir, filename):
    reference_path = Path(reference_dir)
    original_path = reference_path / filename

    if not original_path.exists():
        return original_path

    stem = original_path.stem
    suffix = original_path.suffix

    counter = 1

    while True:
        candidate = reference_path / f"{stem}_{counter}{suffix}"

        if not candidate.exists():
            return candidate

        counter += 1


def save_uploaded_reference_image(uploaded_file, reference_dir):
    reference_path = Path(reference_dir)

    reference_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    suffix = Path(uploaded_file.name).suffix.lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"reference_{timestamp}{suffix}"

    save_path = get_unique_reference_path(
        reference_path,
        safe_filename,
    )

    with open(save_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return str(save_path)


def render_reference_image_selector(
    reference_dir,
    session_key,
    title="Reference Image Library",
    columns=5,
):
    reference_images = get_reference_images(reference_dir)

    upload_key_state = f"{session_key}_library_upload_key"

    if upload_key_state not in st.session_state:
        st.session_state[upload_key_state] = 0

    st.markdown(f"### {title}")

    st.markdown(
        """
        <style>
        div[data-testid="stFileUploader"] {
            margin-top: 0rem !important;
        }

        div[data-testid="stFileUploader"] section {
            height: 280px !important;
            border: 1px dashed #c9ced6 !important;
            border-radius: 12px !important;
            background: #f8fafc !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0rem !important;
            margin-bottom: 14px !important;
        }

        div[data-testid="stFileUploader"] section > div {
            width: 100% !important;
            height: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            flex-direction: column !important;
        }

        div[data-testid="stFileUploader"] button {
            display: none !important;
        }

        div[data-testid="stFileUploader"] small {
            display: none !important;
        }

        div[data-testid="stFileUploaderDropzoneInstructions"] {
            width: 100% !important;
            height: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
        }

        div[data-testid="stFileUploaderDropzoneInstructions"] div {
            width: 100% !important;
            text-align: center !important;
        }

        div[data-testid="stFileUploaderDropzoneInstructions"] div span {
            display: none !important;
        }

        div[data-testid="stFileUploaderDropzoneInstructions"] div::before {
            content: "➕\\A\\A Add Reference\\A\\A Drag & drop image here";
            white-space: pre;
            display: block;
            text-align: center;
            font-size: 16px;
            font-weight: 600;
            color: #6b7280;
            line-height: 1.6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    card_items = reference_images + ["upload_card"]
    cols = st.columns(columns)

    for index, item in enumerate(card_items):

        with cols[index % columns]:

            if item == "upload_card":

                uploaded_reference = st.file_uploader(
                    "Upload Reference Image",
                    type=["png", "jpg", "jpeg", "webp"],
                    key=(
                        f"{session_key}_library_upload_"
                        f"{st.session_state[upload_key_state]}"
                    ),
                    label_visibility="collapsed",
                )

                if uploaded_reference is not None:

                    saved_path = save_uploaded_reference_image(
                        uploaded_file=uploaded_reference,
                        reference_dir=reference_dir,
                    )

                    st.session_state[session_key] = saved_path
                    st.session_state[upload_key_state] += 1

                    st.toast("✅ Reference image added and selected")
                    st.rerun()

                continue

            image_path = item
            image_path_str = str(image_path)

            selected_path = st.session_state.get(session_key)
            is_selected = selected_path == image_path_str

            st.image(
                image_path_str,
                use_container_width=True,
            )

            button_label = (
                "✅ Selected"
                if is_selected
                else "Use Reference"
            )

            if st.button(
                button_label,
                key=f"{session_key}_{image_path.stem}_{index}",
                use_container_width=True,
            ):
                st.session_state[session_key] = image_path_str
                st.rerun()

    return st.session_state.get(session_key)