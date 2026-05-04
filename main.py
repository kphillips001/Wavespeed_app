import os
import re
import time
import base64
import requests
import tkinter as tk
from datetime import datetime
from tkinter import simpledialog, messagebox, filedialog

from dotenv import load_dotenv
from openai import OpenAI


# -----------------------------
# CONFIG
# -----------------------------
WAVESPEED_RESULT_URL = "https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"

MODELS = {
    "1": {
        "name": "Google Nano Banana 2 Edit",
        "endpoint": "https://api.wavespeed.ai/api/v3/google/nano-banana-2/edit",
    },
    "2": {
        "name": "Google Nano Banana Pro Edit",
        "endpoint": "https://api.wavespeed.ai/api/v3/google/nano-banana-pro/edit",
    },
    "3": {
        "name": "ByteDance Seedream 4.5 Edit",
        "endpoint": "https://api.wavespeed.ai/api/v3/bytedance/seedream-v4.5/edit",
    },
    "4": {
        "name": "ByteDance Seedream 5.0 Lite Edit",
        "endpoint": "https://api.wavespeed.ai/api/v3/bytedance/seedream-v5.0-lite/edit",
    },
}

PERSONA_OUTPUT_DIRS = {
    "1": {
        "name": "Ava Blackthorne",
        "output_dir": r"D:\Ava Blackthorne\Ready\Wavespeed",
    },
    "2": {
        "name": "Amanda Cayne",
        "output_dir": r"D:\Amanda Cayne\Ready\Wavespeed",
    },
}


# -----------------------------
# PATH HELPERS
# -----------------------------
def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_prompts_file_path():
    return os.path.join(get_script_dir(), "prompts.txt")


def get_outputs_dir(persona_choice):
    return PERSONA_OUTPUT_DIRS[persona_choice]["output_dir"]


def create_run_stamp():
    return datetime.now().strftime("run_%Y%m%d_%H%M%S")


def get_failed_prompts_file_path(run_stamp):
    return os.path.join(get_script_dir(), f"failed_prompts_{run_stamp}.txt")


# -----------------------------
# PERSONA SELECTION
# -----------------------------
def select_persona():
    print("\n" + "=" * 80)
    print("🎭 SELECT PERSONA")
    print("=" * 80)
    print("Press 1 for Ava Blackthorne")
    print("Press 2 for Amanda Cayne")

    while True:
        choice = input("\nEnter number (1 or 2): ").strip()

        if choice in PERSONA_OUTPUT_DIRS:
            selected = PERSONA_OUTPUT_DIRS[choice]
            print(f"\n✅ Selected: {selected['name']}")
            print(f"📂 Final output folder: {selected['output_dir']}\n")
            return choice

        print("❌ Invalid selection. Please enter 1 or 2.")


# -----------------------------
# GET PROMPT COUNT
# -----------------------------
def get_prompt_count():
    while True:
        try:
            user_input = input("\nHow many prompts do you want ChatGPT to generate? ").strip()
            prompt_count = int(user_input)

            if prompt_count > 0:
                return prompt_count

            print("❌ Enter a number greater than 0.")
        except ValueError:
            print("❌ Please enter a valid number.")


# -----------------------------
# INPUT BOX FOR META REQUEST
# -----------------------------
def get_meta_prompt_request():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    user_request = simpledialog.askstring(
        title="Prompt Request",
        prompt=(
            "Enter what you want ChatGPT to generate.\n\n"
            "Example:\n"
            "Sexy spring outfits, tight clothing, indoor/outdoor, teasing poses"
        ),
        parent=root
    )

    root.destroy()
    return user_request


# -----------------------------
# BUILD META PROMPT
# -----------------------------
def build_chatgpt_prompt(prompt_count, user_request):

    # 🔥 SFW SEXY OUTFIT BIAS
    outfit_bias = """
low-cut tops, deep V-neck tops, plunging necklines, bikinis, string bikinis,
bikini tops, denim shorts, daisy duke shorts, crop tops, tight tank tops,
push-up bras under visible tops, fitted lingerie-inspired outfits, open jackets,
unzipped hoodies, partially open shirts, off-shoulder tops, tight mini dresses,
bodycon dresses with deep neckline, tight athletic tops, tight gym sets,
tight leggings, fitted summer outfits, teasing but SFW social media outfits
"""

    base_style = f"""Glamorous, photorealistic, SFW social-media-ready feminine styling designed to attract male attention, strong curvy silhouette, sexy fitted outfits, revealing but non-explicit clothing, confident playful body language, flirtatious but safe-for-social-media posing, natural candid positioning, indoor and outdoor environments, soft warm lighting, high visual appeal, scroll-stopping attraction, OUTFIT PRIORITY: {outfit_bias}"""

    combined_request = f"{base_style}, {user_request}"

    return f"""I need a list of {prompt_count} high-quality image-to-image editing prompts.

These prompts will always be used with the SAME reference image, so every prompt MUST preserve the exact same woman.

User request:
{combined_request}

--------------------------------------------------
🔥 PRIMARY PURPOSE / SOCIAL MEDIA LAYER (CRITICAL)
--------------------------------------------------

These prompts are for SFW social media images designed to attract male attention and drive curiosity toward a link.

Every image MUST be:
- Sexy
- SFW
- Scroll-stopping
- Visually attractive to men
- Flirty, confident, and attention-grabbing
- Teasing without nudity or explicit sexual content

Do NOT generate:
- plain outfits
- conservative or modest styling
- boring or low-attraction visuals

--------------------------------------------------
🔥 KEYWORD INTERPRETATION SYSTEM (CRITICAL)
--------------------------------------------------

The user's input defines the PRIMARY outfit direction.

1. SPECIFIC ITEM (e.g. "denim shorts", "bikini top"):
   - MUST appear in EVERY prompt
   - DO NOT replace or remove it

2. GENERAL STYLE (e.g. "tight clothing", "sexy attire"):
   - Generate variety within the theme
   - NEVER drift outside the theme

3. MULTIPLE ITEMS:
   - ALL must appear in EVERY prompt

--------------------------------------------------
🔥 SEX APPEAL ENFORCEMENT (CRITICAL)
--------------------------------------------------

Every prompt MUST be designed to attract male attention.

- Outfits must be tight, fitted, and curve-enhancing
- Emphasize waist, hips, chest framing, and legs
- Use teasing, revealing (but SFW) styling
- Expressions must be confident, playful, or seductive
- Poses must feel inviting, natural, and engaging

Avoid:
- baggy clothing
- neutral poses
- low-energy expressions
- anything that hides the body

--------------------------------------------------
🔥 SETTING + ENVIRONMENT SYSTEM (CRITICAL)
--------------------------------------------------

Each prompt MUST include a strong, attractive setting.

Use a wide variety:

INDOOR:
- bedroom (bed edge, sheets)
- couch / living room
- kitchen counter
- mirror selfie (bathroom)
- doorway / hallway
- window lighting scenes

OUTDOOR:
- beach
- poolside
- balcony
- patio
- stairs
- street-style candid
- car setting

ACTIVE:
- gym mirror
- walking outdoors
- casual lifestyle scenes

RULES:
- Every prompt should use a DIFFERENT setting
- No generic environments ("indoors", "outside")
- Setting must enhance pose + outfit
- Must feel Instagram-ready and realistic

--------------------------------------------------
🔥 POSE + CAMERA ENFORCEMENT (CRITICAL)
--------------------------------------------------

- Use leaning, seated, reclining, walking, or over-the-shoulder poses
- Use mirror selfies where appropriate
- Use angled torso or forward lean
- Camera must highlight chest, waist, hips, legs

NEVER:
- stiff poses
- flat posture
- hidden body angles

--------------------------------------------------
🔥 POSE DIVERSITY RULES
--------------------------------------------------

- Every prompt must feel different
- Mix pose types across prompts
- Avoid repetition

--------------------------------------------------
STRICT IDENTITY RULES
--------------------------------------------------

- SAME woman always
- SAME face, hair, body

--------------------------------------------------
PROMPT STRUCTURE
--------------------------------------------------

Each prompt MUST start with:
"The exact same woman from the reference image with identical face, hair, and body,"

--------------------------------------------------
CONTENT RULES
--------------------------------------------------

- One line per prompt
- No numbering
- No explanations
- No emojis
- Photorealistic
- SFW only
- No other people

Return ONLY the list of prompts."""


# -----------------------------
# CALL CHATGPT
# -----------------------------
def generate_prompts_with_grok(meta_prompt, api_key):
    import requests

    url = "https://api.x.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "grok-3-mini",
        "messages": [
            {"role": "user", "content": meta_prompt}
        ],
        "temperature": 0.9
    }

    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()

    data = response.json()

    content = data["choices"][0]["message"]["content"].strip()

    prompts = []
    for line in content.split("\n"):
        line = line.strip()

        if not line:
            continue

        line = re.sub(r"^\d+[\.\)]\s*", "", line)

        if line in {"-", "*", "•"}:
            continue

        prompts.append(line)

    return prompts


# -----------------------------
# SHOW RESULT + SAVE TO FILE
# -----------------------------
def show_result(prompts):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    file_path = get_prompts_file_path()

    with open(file_path, "w", encoding="utf-8") as f:
        for p in prompts:
            f.write(p + "\n")

    messagebox.showinfo(
        "Prompts Generated",
        f"{len(prompts)} prompts generated.\n\nSaved to:\n{file_path}",
        parent=root
    )

    root.destroy()

    print("\n" + "=" * 80)
    print("🔥 GENERATED PROMPTS:")
    print("=" * 80)

    for i, p in enumerate(prompts, 1):
        print(f"{i}. {p}")

    print("=" * 80)
    print(f"📁 Saved to: {file_path}\n")


# -----------------------------
# MODEL SELECTION
# -----------------------------
def select_model():
    print("\n🎯 Select WaveSpeed Model:\n")
    print("1 for Google Nano Banana 2 Edit")
    print("2 for Google Nano Banana Pro Edit")
    print("3 for ByteDance Seedream 4.5 Edit")
    print("4 for ByteDance Seedream 5.0 Lite Edit")

    while True:
        choice = input("\nEnter number (1-4): ").strip()

        if choice == "1":
            selected = MODELS["1"]
        elif choice == "2":
            selected = MODELS["2"]
        elif choice == "3":
            selected = MODELS["3"]
        elif choice == "4":
            selected = MODELS["4"]
        else:
            print("❌ Invalid selection. Try again.")
            continue

        print(f"\n✅ Selected: {selected['name']}\n")
        return selected


# -----------------------------
# LOAD PROMPTS FROM FILE
# -----------------------------
def load_prompts_from_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"prompts.txt not found: {file_path}")

    prompts = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                prompts.append(line)

    if not prompts:
        raise ValueError("prompts.txt exists, but it is empty.")

    return prompts


# -----------------------------
# ASK TO SEND TO WAVESPEED
# -----------------------------
def ask_yes_no(prompt_text):
    while True:
        answer = input(f"{prompt_text} (y/n): ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("❌ Please enter y or n.")


# -----------------------------
# FILE PICKER FOR REFERENCE IMAGE
# -----------------------------
def select_reference_image():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    file_path = filedialog.askopenfilename(
        parent=root,
        title="Select Reference Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")]
    )

    root.destroy()
    return file_path


# -----------------------------
# IMGBB HELPERS
# -----------------------------
def choose_best_imgbb_url(data):
    """
    Try the most direct/public image URL fields first.
    Falls back through several candidates safely.
    """
    candidates = [
        data.get("data", {}).get("image", {}).get("url"),
        data.get("data", {}).get("url"),
        data.get("data", {}).get("display_url"),
        data.get("data", {}).get("medium", {}).get("url"),
        data.get("data", {}).get("thumb", {}).get("url"),
    ]

    for url in candidates:
        if isinstance(url, str) and url.strip():
            return url.strip()

    raise ValueError(f"Could not find a usable ImgBB URL in response: {data}")


def verify_image_url(image_url):
    """
    Try to verify the URL, but DO NOT crash the script if it fails.
    Returns True if verified, False otherwise.
    """
    print("🔎 Verifying reference image URL...")

    try:
        response = requests.get(
            image_url,
            timeout=20,
            allow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()

        if not content_type.startswith("image/"):
            print("⚠️ Warning: URL did not return an image.")
            print(f"⚠️ Content-Type: {content_type}")
            print("⚠️ Continuing anyway...\n")
            return False

        print("✅ Reference URL verified")
        print(f"🔗 URL: {image_url}")
        print(f"🖼️ Content-Type: {content_type}\n")

        return True

    except requests.exceptions.RequestException as e:
        print("⚠️ Warning: Could not verify reference image URL.")
        print(f"⚠️ Reason: {e}")
        print("⚠️ Continuing anyway and letting WaveSpeed try the URL...\n")

        return False


# -----------------------------
# UPLOAD TO IMGBB
# -----------------------------
def upload_to_imgbb(image_path, api_key):
    with open(image_path, "rb") as file:
        encoded = base64.b64encode(file.read())

    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={
            "key": api_key,
            "image": encoded
        },
        timeout=120
    )
    response.raise_for_status()

    data = response.json()

    image_url = choose_best_imgbb_url(data)

    print("\n" + "=" * 80)
    print("☁️ IMGBB UPLOAD COMPLETE")
    print("=" * 80)
    print(f"🔗 Selected reference URL: {image_url}")
    print("=" * 80 + "\n")

    return image_url


# -----------------------------
# WAVESPEED SUBMIT TASK
# -----------------------------
def submit_wavespeed_task(prompt, image_url, api_key, model_url):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "images": [image_url],
        "output_format": "png"
    }

    response = requests.post(
        model_url,
        headers=headers,
        json=payload,
        timeout=120
    )
    response.raise_for_status()

    data = response.json()
    request_id = data.get("data", {}).get("id")

    if not request_id:
        raise ValueError(f"No task ID returned from WaveSpeed. Response: {data}")

    return request_id


# -----------------------------
# WAVESPEED POLL RESULT
# -----------------------------
def poll_wavespeed_result(request_id, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    result_url = WAVESPEED_RESULT_URL.format(request_id=request_id)

    while True:
        response = requests.get(result_url, headers=headers, timeout=120)
        response.raise_for_status()

        data = response.json()
        status = data.get("data", {}).get("status")

        print(f"    Status: {status}")

        if status == "completed":
            outputs = data.get("data", {}).get("outputs", [])
            if not outputs:
                raise ValueError(f"Task completed but no outputs returned. Response: {data}")

            first_output = outputs[0]
            if isinstance(first_output, str):
                return first_output
            if isinstance(first_output, dict):
                url = first_output.get("url")
                if url:
                    return url

            raise ValueError(f"Unexpected outputs format: {outputs}")

        if status == "failed":
            error_message = data.get("data", {}).get("error", "Unknown WaveSpeed error")
            raise RuntimeError(f"WaveSpeed task failed: {error_message}")

        time.sleep(3)


# -----------------------------
# DOWNLOAD IMAGE
# -----------------------------
def download_image(url, save_path):
    response = requests.get(
        url,
        timeout=120,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )
    response.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(response.content)


# -----------------------------
# FINAL OUTPUT HELPERS
# -----------------------------
def get_final_output_path(outputs_dir, run_stamp, index):
    filename = f"{run_stamp}_{index:03d}.png"
    return os.path.join(outputs_dir, filename)


def save_failed_prompts_report(run_stamp, failed_prompts):
    if not failed_prompts:
        return None

    file_path = get_failed_prompts_file_path(run_stamp)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("Failed WaveSpeed Prompts\n")
        f.write("=" * 80 + "\n\n")

        for item in failed_prompts:
            f.write(f"Prompt Number: {item['index']}\n")
            f.write(f"Reason: {item['reason']}\n")
            f.write(f"Prompt: {item['prompt']}\n")
            f.write("-" * 80 + "\n")

    return file_path


# -----------------------------
# RUN WAVESPEED LOOP
# -----------------------------
def run_wavespeed(prompts, wavespeed_key, imgbb_key, selected_model, persona_choice):
    prompts_to_run = prompts
    run_count = len(prompts_to_run)

    print(f"\n🚀 Sending ALL {run_count} prompts to WaveSpeed...\n")

    print("👉 Press Enter to select your reference image...")
    input()

    image_path = select_reference_image()
    if not image_path:
        print("No reference image selected.")
        return

    print(f"\n🖼️ Reference image selected: {image_path}")
    print("☁️ Uploading reference image once to ImgBB...")

    image_url = upload_to_imgbb(image_path, imgbb_key)
    verify_image_url(image_url)

    print("✅ Reference image URL ready.\n")

    outputs_dir = get_outputs_dir(persona_choice)
    os.makedirs(outputs_dir, exist_ok=True)

    run_stamp = create_run_stamp()

    print("=" * 80)
    print("📁 RUN PATHS")
    print("=" * 80)
    print(f"🎭 Persona         : {PERSONA_OUTPUT_DIRS[persona_choice]['name']}")
    print(f"📦 Final output    : {outputs_dir}")
    print(f"🏷️ Run stamp       : {run_stamp}")
    print("=" * 80 + "\n")

    saved_paths = []
    failed_prompts = []

    for index, prompt in enumerate(prompts_to_run, start=1):
        print("-" * 80)
        print(f"🎨 Generating image {index}/{run_count}")
        print(f"Model: {selected_model['name']}")
        print(f"Prompt: {prompt}")

        try:
            request_id = submit_wavespeed_task(
                prompt=prompt,
                image_url=image_url,
                api_key=wavespeed_key,
                model_url=selected_model["endpoint"]
            )
            print(f"    Task ID: {request_id}")

            output_url = poll_wavespeed_result(request_id, wavespeed_key)

            final_save_path = get_final_output_path(outputs_dir, run_stamp, index)
            download_image(output_url, final_save_path)
            saved_paths.append(final_save_path)

            print(f"    ✅ Saved to final: {final_save_path}")

        except Exception as e:
            failure_reason = str(e)
            failed_prompts.append({
                "index": index,
                "prompt": prompt,
                "reason": failure_reason,
            })

            print("\n" + "=" * 80)
            print("⚠️ WAVESPEED PROMPT FAILED — SKIPPING TO NEXT")
            print("=" * 80)
            print(f"Prompt {index} failed.")
            print(f"Reason: {failure_reason}")
            print("Continuing with the remaining prompts...")
            print("=" * 80 + "\n")
            continue

    failed_report_path = save_failed_prompts_report(run_stamp, failed_prompts)

    print("\n" + "=" * 80)
    if failed_prompts:
        print("⚠️ WAVESPEED RUN COMPLETED WITH SOME FAILURES")
    else:
        print("🔥 WAVESPEED RUN COMPLETE")
    print("=" * 80)
    print(f"🎭 Persona              : {PERSONA_OUTPUT_DIRS[persona_choice]['name']}")
    print(f"✅ Images saved to final: {len(saved_paths)}")
    print(f"❌ Failed prompts       : {len(failed_prompts)}")
    print(f"📂 Final output folder  : {outputs_dir}")

    if failed_prompts:
        failed_numbers = ", ".join(str(item["index"]) for item in failed_prompts)
        print(f"📝 Failed prompt numbers: {failed_numbers}")
        if failed_report_path:
            print(f"📄 Failed prompts file  : {failed_report_path}")

    print("=" * 80 + "\n")


# -----------------------------
# MAIN
# -----------------------------
def main():
    load_dotenv()

    grok_key = os.getenv("GROK_API_KEY")
    wavespeed_key = os.getenv("WAVESPEED_API_KEY")
    imgbb_key = os.getenv("IMGBB_API_KEY")

    if not grok_key:
        raise ValueError("Missing GROK_API_KEY in .env")
    if not wavespeed_key:
        raise ValueError("Missing WAVESPEED_API_KEY in .env")
    if not imgbb_key:
        raise ValueError("Missing IMGBB_API_KEY in .env")

    persona_choice = select_persona()
    prompt_count = get_prompt_count()

    print(f"\n✅ You want {prompt_count} prompts.")
    print("👉 Press Enter to continue and open the input box...")
    input()

    user_request = get_meta_prompt_request()

    if not user_request or not user_request.strip():
        print("No request entered.")
        return

    meta_prompt = build_chatgpt_prompt(prompt_count, user_request.strip())

    print("\n🤖 Generating prompts with ChatGPT...\n")
    prompts = generate_prompts_with_grok(meta_prompt, grok_key)
    show_result(prompts)

    selected_model = select_model()

    if not ask_yes_no("Send these prompts to WaveSpeed now?"):
        print("Okay — prompts were generated and saved, but no WaveSpeed run was started.")
        return

    prompts_from_file = load_prompts_from_file(get_prompts_file_path())

    run_wavespeed(
        prompts=prompts_from_file,
        wavespeed_key=wavespeed_key,
        imgbb_key=imgbb_key,
        selected_model=selected_model,
        persona_choice=persona_choice
    )


if __name__ == "__main__":
    main()