import os
import tempfile
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

from app.config.content_paths import (
    get_premium_gallery_dir,
)

from app.ui.image_file_utils import (
    get_unique_image_path,
)

from main import (
    upload_to_imgbb,
    verify_image_url,
    submit_wavespeed_task,
    poll_wavespeed_result,
)


WAN_27_IMAGE_EDIT_MODEL = {
    "name": "WAN 2.7 Image Edit",
    "endpoint": "https://api.wavespeed.ai/api/v3/alibaba/wan-2.7/image-edit",
}

SEEDREAM_45_EDIT_MODEL = {
    "name": "Seedream 4.5 Edit",
    "endpoint": "https://api.wavespeed.ai/api/v3/bytedance/seedream-v4.5/edit",
}

SEEDREAM_50_LITE_EDIT_MODEL = {
    "name": "Seedream 5.0 Lite Edit",
    "endpoint": "https://api.wavespeed.ai/api/v3/bytedance/seedream-v5.0-lite/edit",
}


PREMIUM_RENDERER_MODELS = {
    WAN_27_IMAGE_EDIT_MODEL["name"]: WAN_27_IMAGE_EDIT_MODEL,
    SEEDREAM_45_EDIT_MODEL["name"]: SEEDREAM_45_EDIT_MODEL,
    SEEDREAM_50_LITE_EDIT_MODEL["name"]: SEEDREAM_50_LITE_EDIT_MODEL,
}


PREMIUM_RENDER_BODY_LOCK = """
FINAL REFERENCE BODY LOCK - NON-NEGOTIABLE:
Use the reference image as the body-size source of truth.
Preserve the exact same woman, face, long dark hair, rich dark tan skin, body size, body weight, and recognizable silhouette from the reference image.
Her breasts must remain visibly large natural D-cup breasts in the generated image, with full D-cup breast volume, full upper and lower breast fullness, rounded natural breast shape, visible bust projection, and natural cleavage when clothing or framing allows it.
Do not reduce breast size. Do not make her smaller-busted. Do not flatten her chest. Do not make her appear B-cup or small-chested.
Preserve her feminine hourglass body, same waist-to-hip proportions, hip width, thigh proportions, shoulder width, and bust-to-waist ratio.
Keep her body large in frame with close creator-style framing by default so the D-cup bust, hourglass shape, and dark tan skin remain visually obvious, unless the prompt explicitly requests full-body, wide, environmental, or another specific framing style.
Preserve the prompt's facial expression direction. She should look emotionally alive with natural, candid warmth: subtle eye warmth, relaxed cheeks, small asymmetry, natural mouth shape, and believable in-the-moment expression. Avoid blank, bored, monotone, mannequin-like, emotionless, forced-smile, fake-grin, overly toothy, plastic, or overacted facial expressions.
""".strip()


def enforce_premium_render_body_lock(prompt_text):
    cleaned_prompt = (prompt_text or "").strip()

    if not cleaned_prompt:
        return ""

    return f"{cleaned_prompt}\n\n{PREMIUM_RENDER_BODY_LOCK}"


def save_uploaded_reference_to_temp(uploaded_file):
    if isinstance(uploaded_file, (str, Path)):
        source_path = Path(uploaded_file)

        if not source_path.exists():
            raise FileNotFoundError(
                f"Reference image not found: {source_path}"
            )

        suffix = source_path.suffix or ".png"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            with open(source_path, "rb") as source_file:
                temp_file.write(source_file.read())

            return temp_file.name

    suffix = Path(uploaded_file.name).suffix or ".png"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return temp_file.name


def download_premium_image(image_url, output_path):
    response = requests.get(
        image_url,
        timeout=120,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()

    with open(output_path, "wb") as file:
        file.write(response.content)


def get_premium_renderer_model(premium_renderer):
    return PREMIUM_RENDERER_MODELS.get(
        premium_renderer,
        WAN_27_IMAGE_EDIT_MODEL,
    )


def generate_premium_images(
    premium_prompts,
    uploaded_file,
    selected_output_dir,
    premium_renderer,
    progress_callback=None,
    target_output_dir=None,
):
    load_dotenv()

    wavespeed_key = os.getenv("WAVESPEED_API_KEY")
    imgbb_key = os.getenv("IMGBB_API_KEY")

    if not wavespeed_key:
        raise ValueError("Missing WAVESPEED_API_KEY in .env")

    if not imgbb_key:
        raise ValueError("Missing IMGBB_API_KEY in .env")

    if uploaded_file is None:
        raise ValueError("No premium reference image uploaded.")

    if not premium_prompts:
        raise ValueError("No premium prompts available.")

    premium_gallery_dir = (
        Path(target_output_dir)
        if target_output_dir
        else get_premium_gallery_dir(selected_output_dir)
    )
    output_label = (
        "Premium Photoshoot"
        if target_output_dir
        else "Premium Gallery"
    )

    Path(premium_gallery_dir).mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_reference_path = save_uploaded_reference_to_temp(
        uploaded_file
    )

    generated_images = []
    failed_images = []

    run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    total_prompts = len(
        premium_prompts
    )

    selected_model = get_premium_renderer_model(
        premium_renderer
    )

    try:
        if progress_callback:
            progress_callback(
                0,
                total_prompts,
                "Uploading reference image...",
                generated_images,
                failed_images,
            )

        reference_url = upload_to_imgbb(
            temp_reference_path,
            imgbb_key,
        )

        verify_image_url(
            reference_url
        )

        for index, prompt_data in enumerate(
            premium_prompts,
            start=1,
        ):
            prompt_text = prompt_data.get(
                "text",
                "",
            ).strip()

            if not prompt_text:
                continue

            render_prompt_text = enforce_premium_render_body_lock(
                prompt_text
            )

            if progress_callback:
                progress_callback(
                    index - 1,
                    total_prompts,
                    (
                        f"Generating premium image {index} of "
                        f"{total_prompts} with {selected_model['name']}..."
                    ),
                    generated_images,
                    failed_images,
                )

            try:
                request_id = submit_wavespeed_task(
                    prompt=render_prompt_text,
                    image_url=reference_url,
                    api_key=wavespeed_key,
                    model_url=selected_model["endpoint"],
                )

                output_url = poll_wavespeed_result(
                    request_id=request_id,
                    api_key=wavespeed_key,
                )

                image_filename = (
                    f"premium_{run_stamp}_{index:03d}.png"
                )

                local_image_path = get_unique_image_path(
                    premium_gallery_dir,
                    image_filename,
                )

                download_premium_image(
                    output_url,
                    local_image_path,
                )

                generated_images.append(
                    {
                        "id": f"premium_image_{index}",
                        "prompt": render_prompt_text,
                        "url": str(local_image_path),
                        "source_url": output_url,
                        "local_path": str(local_image_path),
                        "renderer": selected_model["name"],
                        "status": "completed",
                    }
                )

            except Exception as error:
                failed_images.append(
                    {
                        "id": f"premium_image_{index}",
                        "prompt": render_prompt_text,
                        "renderer": selected_model["name"],
                        "error": str(error),
                        "status": "failed",
                    }
                )

            if progress_callback:
                progress_callback(
                    index,
                    total_prompts,
                    (
                        f"Saved {len(generated_images)} to {output_label}, "
                        f"failed {len(failed_images)}."
                    ),
                    generated_images,
                    failed_images,
                )

        return {
            "generated_images": generated_images,
            "failed_images": failed_images,
        }

    finally:
        if os.path.exists(
            temp_reference_path
        ):
            os.remove(
                temp_reference_path
            )
