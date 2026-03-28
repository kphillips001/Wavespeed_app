import os
import re
import tkinter as tk
from tkinter import simpledialog, messagebox
from dotenv import load_dotenv
from openai import OpenAI


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

These prompts will always be used with the SAME reference image, so every prompt must preserve the same woman, same identity, same face, same hair, and same overall person from the reference image.

User request:
{user_request}

Requirements:
- Each prompt must be 1 single line
- No numbering
- No bullet points
- No extra explanations
- No emojis
- Every prompt must clearly imply the same woman from the reference image
- Focus on changing outfit, pose, setting, framing, expression, and lighting
- Keep the prompts photorealistic
- Keep the prompts clean and consistent for image-to-image editing
- Do not describe a completely new person
- Do not use vague phrases like "a woman" or "a female model" by themselves
- Instead, use phrasing like "the same blonde woman from the reference image" or "keep the same woman from the reference image"

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

        # Skip any accidental bullet-only lines
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

    # Save path = same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "prompts.txt")

    # Save prompts to file
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
# MAIN
# -----------------------------
def main():
    load_dotenv()

    openai_key = os.getenv("OPENAI_API_KEY")

    if not openai_key:
        raise ValueError("Missing OPENAI_API_KEY in .env")

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


if __name__ == "__main__":
    main()