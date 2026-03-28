import os
import sys
import base64
import time
import requests
import tkinter as tk
from tkinter import filedialog
from dotenv import load_dotenv


# -----------------------------
# CONFIG
# -----------------------------
MODEL_URL = "https://api.wavespeed.ai/api/v3/bytedance/seedream-v5.0-lite/edit"


# -----------------------------
# FILE PICKER
# -----------------------------
def select_image():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select Reference Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")]
    )

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
        }
    )

    response.raise_for_status()
    return response.json()["data"]["url"]


# -----------------------------
# SEND TO WAVESPEED
# -----------------------------
def generate_image(prompt, image_url, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "images": [image_url],
        "output_format": "jpeg"
    }

    response = requests.post(MODEL_URL, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()


# -----------------------------
# POLL RESULT
# -----------------------------
def poll_result(task_id, api_key):
    url = f"https://api.wavespeed.ai/api/v3/predictions/{task_id}/result"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    while True:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        status = data.get("data", {}).get("status")

        print(f"Status: {status}")

        if status == "completed":
            return data
        elif status == "failed":
            raise Exception("Generation failed")

        time.sleep(3)


# -----------------------------
# MAIN
# -----------------------------
def main():
    load_dotenv()

    wavespeed_key = os.getenv("WAVESPEED_API_KEY")
    imgbb_key = os.getenv("IMGBB_API_KEY")

    if not wavespeed_key:
        raise ValueError("Missing WAVESPEED_API_KEY in .env")

    if not imgbb_key:
        raise ValueError("Missing IMGBB_API_KEY in .env")

    # Step 1: pick image
    image_path = select_image()

    if not image_path:
        print("No image selected.")
        return

    print(f"\nSelected image: {image_path}")

    # Step 2: upload to ImgBB
    print("\nUploading image to ImgBB...")
    image_url = upload_to_imgbb(image_path, imgbb_key)
    print(f"Image URL: {image_url}")

    # Step 3: send to WaveSpeed
    print("\nSending to WaveSpeed...")
    result = generate_image(
        prompt="Keep same woman, change outfit to tight black dress, soft lighting, photorealistic",
        image_url=image_url,
        api_key=wavespeed_key
    )

    task_id = result.get("data", {}).get("id")

    print(f"\nTask ID: {task_id}")

    # Step 4: poll result
    print("\nWaiting for result...")
    final_result = poll_result(task_id, wavespeed_key)

    output_url = final_result.get("data", {}).get("outputs", [None])[0]

    print("\n🔥 DONE")
    print(f"Generated Image URL: {output_url}")


if __name__ == "__main__":
    main()