import os
import re
import time
import base64
import shutil
import requests
import tkinter as tk
from datetime import datetime
from tkinter import simpledialog, messagebox, filedialog

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image


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

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

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


def get_temp_root_dir():
    return os.path.join(get_script_dir(), "temp")


def create_temp_run_dir():
    run_stamp = datetime.now().strftime("run_%Y%m%d_%H%M%S")
    temp_run_dir = os.path.join(get_temp_root_dir(), run_stamp)
    os.makedirs(temp_run_dir, exist_ok=True)
    return temp_run_dir, run_stamp


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
    return f"""I need a list of {prompt_count} high-quality image-to-image editing prompts.

These prompts will always be used with the SAME reference image, so every prompt MUST preserve the exact same woman.

User request:
{user_request}

STRICT IDENTITY RULES (VERY IMPORTANT):
- Every prompt MUST preserve the EXACT same woman from the reference image
- Maintain identical facial features, bone structure, and identity
- Maintain the SAME hair color, hairstyle, and hair length (DO NOT change hair color)
- Maintain the SAME body type and proportions
- Maintain the SAME breast size and shape
- Do NOT change ethnicity, face, or physical identity in any way

POSE DIVERSITY RULES (VERY IMPORTANT):
- Distribute the prompts across clearly different pose categories
- Include a balanced mix of seated poses, leaning poses, laying or reclining poses, walking or movement poses, over-the-shoulder poses, and environment-interaction poses
- Do NOT let multiple prompts feel like the same stance with only outfit changes
- Do NOT use hands on hips
- Do NOT use stiff straight-on standing poses unless explicitly requested
- Each prompt must describe the pose clearly and specifically
- Prioritize natural, candid, seductive, varied body language

PROMPT STRUCTURE:
- Each prompt MUST start with:
  "The exact same woman from the reference image with identical face, hair, and body,"

CONTENT RULES:
- Each prompt must be 1 single line
- No numbering
- No bullet points
- No extra explanations
- No emojis
- Each prompt should be clearly different
- Focus ONLY on changing outfit, pose, setting, framing, expression, and lighting
- Keep prompts photorealistic and realistic
- Do NOT introduce a new person
- Do NOT use vague phrases like "a woman" or "a female model"

Return ONLY the list of prompts."""


# -----------------------------
# CALL CHATGPT
# -----------------------------
def generate_prompts_with_gpt(meta_prompt, api_key):
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": meta_prompt}
        ],
        temperature=0.9
    )

    content = response.choices[0].message.content.strip()

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


def get_run_count(max_count):
    while True:
        try:
            user_input = input(
                f"\nHow many prompts do you want to send to WaveSpeed? (1-{max_count}): "
            ).strip()
            run_count = int(user_input)

            if 1 <= run_count <= max_count:
                return run_count

            print(f"❌ Enter a number between 1 and {max_count}.")
        except ValueError:
            print("❌ Please enter a valid number.")


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
    return data["data"]["url"]


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
    response = requests.get(url, timeout=120)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(response.content)


# -----------------------------
# METADATA STRIPPING HELPERS
# -----------------------------
def strip_metadata_and_save(input_path, output_path):
    with Image.open(input_path) as img:
        cleaned = Image.new(img.mode, img.size)
        cleaned.putdata(list(img.getdata()))

        save_kwargs = {}
        ext = os.path.splitext(output_path)[1].lower()

        if cleaned.mode == "P" and ext in {".jpg", ".jpeg"}:
            cleaned = cleaned.convert("RGB")

        if cleaned.mode == "RGBA" and ext in {".jpg", ".jpeg"}:
            cleaned = cleaned.convert("RGB")

        if ext in {".jpg", ".jpeg"}:
            save_kwargs["format"] = "JPEG"
            save_kwargs["quality"] = 95
            save_kwargs["optimize"] = True
        elif ext == ".png":
            save_kwargs["format"] = "PNG"
        elif ext == ".webp":
            save_kwargs["format"] = "WEBP"
            save_kwargs["quality"] = 95

        cleaned.save(output_path, **save_kwargs)


def get_final_output_path(outputs_dir, run_stamp, index):
    filename = f"{run_stamp}_{index:03d}.png"
    return os.path.join(outputs_dir, filename)


def clean_temp_images_to_final(temp_run_dir, outputs_dir, run_stamp):
    os.makedirs(outputs_dir, exist_ok=True)

    raw_files = []
    for name in sorted(os.listdir(temp_run_dir)):
        path = os.path.join(temp_run_dir, name)
        if not os.path.isfile(path):
            continue

        ext = os.path.splitext(name)[1].lower()
        if ext in SUPPORTED_IMAGE_EXTENSIONS:
            raw_files.append(path)

    if not raw_files:
        return []

    print("\n" + "=" * 80)
    print("🧼 STARTING METADATA CLEANING")
    print("=" * 80)
    print(f"📂 Temp run folder: {temp_run_dir}")
    print(f"📂 Final output folder: {outputs_dir}\n")

    cleaned_paths = []

    for index, raw_path in enumerate(raw_files, start=1):
        final_path = get_final_output_path(outputs_dir, run_stamp, index)

        print(f"🧼 Cleaning image {index}/{len(raw_files)}")
        print(f"    RAW   : {raw_path}")
        print(f"    FINAL : {final_path}")

        strip_metadata_and_save(raw_path, final_path)
        cleaned_paths.append(final_path)

        print("    ✅ Metadata stripped and saved to final directory\n")

    return cleaned_paths


# -----------------------------
# FINALIZE PARTIAL OR FULL RUN
# -----------------------------
def finalize_downloaded_images(temp_run_dir, outputs_dir, run_stamp, raw_downloaded):
    if not raw_downloaded:
        return []

    cleaned_paths = clean_temp_images_to_final(
        temp_run_dir=temp_run_dir,
        outputs_dir=outputs_dir,
        run_stamp=run_stamp
    )

    shutil.rmtree(temp_run_dir, ignore_errors=True)
    return cleaned_paths


# -----------------------------
# RUN WAVESPEED LOOP
# -----------------------------
def run_wavespeed(prompts, wavespeed_key, imgbb_key, selected_model, persona_choice):
    run_count = get_run_count(len(prompts))
    prompts_to_run = prompts[:run_count]

    print("\n👉 Press Enter to select your reference image...")
    input()

    image_path = select_reference_image()
    if not image_path:
        print("No reference image selected.")
        return

    print(f"\n🖼️ Reference image selected: {image_path}")
    print("☁️ Uploading reference image once to ImgBB...")
    image_url = upload_to_imgbb(image_path, imgbb_key)
    print("✅ Reference image URL ready.\n")

    outputs_dir = get_outputs_dir(persona_choice)
    os.makedirs(outputs_dir, exist_ok=True)

    temp_run_dir, run_stamp = create_temp_run_dir()

    print("=" * 80)
    print("📁 RUN PATHS")
    print("=" * 80)
    print(f"🎭 Persona         : {PERSONA_OUTPUT_DIRS[persona_choice]['name']}")
    print(f"🧪 Temp run folder : {temp_run_dir}")
    print(f"📦 Final output    : {outputs_dir}")
    print(f"🏷️ Run stamp       : {run_stamp}")
    print("=" * 80 + "\n")

    raw_downloaded = []
    failure_reason = None
    failed_prompt_index = None

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

            raw_save_path = os.path.join(temp_run_dir, f"{index:03d}.png")
            download_image(output_url, raw_save_path)
            raw_downloaded.append(raw_save_path)

            print(f"    ✅ RAW saved to temp: {raw_save_path}")

        except Exception as e:
            failure_reason = str(e)
            failed_prompt_index = index

            print("\n" + "=" * 80)
            print("⚠️ WAVESPEED STOPPED EARLY")
            print("=" * 80)
            print(f"Prompt {index} failed.")
            print(f"Reason: {failure_reason}")
            print("The script will now clean and save any images that were already completed.")
            print("=" * 80 + "\n")
            break

    cleaned_paths = finalize_downloaded_images(
        temp_run_dir=temp_run_dir,
        outputs_dir=outputs_dir,
        run_stamp=run_stamp,
        raw_downloaded=raw_downloaded
    )

    if failure_reason:
        print("\n" + "=" * 80)
        print("⚠️ WAVESPEED RUN PARTIALLY COMPLETED")
        print("=" * 80)
        print(f"🎭 Persona               : {PERSONA_OUTPUT_DIRS[persona_choice]['name']}")
        print(f"✅ Raw images downloaded : {len(raw_downloaded)}")
        print(f"✅ Images cleaned        : {len(cleaned_paths)}")
        print(f"❌ Failed on prompt      : {failed_prompt_index}/{run_count}")
        print(f"📝 Failure reason        : {failure_reason}")
        print(f"📂 Final output folder   : {outputs_dir}")
        print("🗑️ Temp folder deleted")
        print("=" * 80 + "\n")
        return

    print("\n" + "=" * 80)
    print("🔥 WAVESPEED RUN COMPLETE")
    print("=" * 80)
    print(f"🎭 Persona               : {PERSONA_OUTPUT_DIRS[persona_choice]['name']}")
    print(f"✅ Raw images downloaded : {len(raw_downloaded)}")
    print(f"✅ Images cleaned        : {len(cleaned_paths)}")
    print(f"📂 Final output folder   : {outputs_dir}")
    print("🗑️ Temp folder deleted")
    print("=" * 80 + "\n")


# -----------------------------
# MAIN
# -----------------------------
def main():
    load_dotenv()

    openai_key = os.getenv("OPENAI_API_KEY")
    wavespeed_key = os.getenv("WAVESPEED_API_KEY")
    imgbb_key = os.getenv("IMGBB_API_KEY")

    if not openai_key:
        raise ValueError("Missing OPENAI_API_KEY in .env")
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
    prompts = generate_prompts_with_gpt(meta_prompt, openai_key)
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