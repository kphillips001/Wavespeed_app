import os
import re
import csv
import time
import base64
import requests
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from dotenv import load_dotenv
from openai import OpenAI


# -----------------------------
# CONFIG
# -----------------------------
WAVESPEED_MODEL_URL = "https://api.wavespeed.ai/api/v3/bytedance/seedream-v5.0-lite/edit"
WAVESPEED_RESULT_URL = "https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"


# -----------------------------
# PATH HELPERS
# -----------------------------
def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_prompts_file_path():
    return os.path.join(get_script_dir(), "prompts.txt")


def get_outputs_dir():
    return r"D:\Amanda Cayne\Ready\Wavespeed"


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

        # Remove numbering like "1. " or "2) "
        line = re.sub(r"^\d+[\.\)]\s*", "", line)

        # Skip accidental bullet-only lines
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
def submit_wavespeed_task(prompt, image_url, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "images": [image_url],
        "output_format": "jpeg"
    }

    response = requests.post(
        WAVESPEED_MODEL_URL,
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
            raise RuntimeError(f"WaveSpeed task failed. Response: {data}")

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
# SAVE MANIFEST
# -----------------------------
def save_manifest(rows):
    manifest_path = os.path.join(get_outputs_dir(), "manifest.csv")

    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["index", "prompt", "request_id", "wavespeed_url", "saved_path"]
        )
        writer.writeheader()
        writer.writerows(rows)

    return manifest_path


# -----------------------------
# RUN WAVESPEED LOOP
# -----------------------------
def run_wavespeed(prompts, wavespeed_key, imgbb_key):
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
    print(f"✅ Reference image URL ready.\n")

    outputs_dir = get_outputs_dir()
    os.makedirs(outputs_dir, exist_ok=True)

    manifest_rows = []

    for index, prompt in enumerate(prompts_to_run, start=1):
        print("-" * 80)
        print(f"🎨 Generating image {index}/{run_count}")
        print(f"Prompt: {prompt}")

        request_id = submit_wavespeed_task(prompt, image_url, wavespeed_key)
        print(f"    Task ID: {request_id}")

        output_url = poll_wavespeed_result(request_id, wavespeed_key)

        save_path = os.path.join(outputs_dir, f"{index:03d}.jpg")
        download_image(output_url, save_path)

        print(f"    ✅ Saved: {save_path}")

        manifest_rows.append({
            "index": index,
            "prompt": prompt,
            "request_id": request_id,
            "wavespeed_url": output_url,
            "saved_path": save_path
        })

    manifest_path = save_manifest(manifest_rows)

    print("\n" + "=" * 80)
    print("🔥 WAVESPEED RUN COMPLETE")
    print("=" * 80)
    print(f"Images saved to: {outputs_dir}")
    print(f"Manifest saved to: {manifest_path}")
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

    if not ask_yes_no("Send these prompts to WaveSpeed now?"):
        print("Okay — prompts were generated and saved, but no WaveSpeed run was started.")
        return

    prompts_from_file = load_prompts_from_file(get_prompts_file_path())
    run_wavespeed(prompts_from_file, wavespeed_key, imgbb_key)


if __name__ == "__main__":
    main()