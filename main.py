import os
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
    return f"""I need a list of {prompt_count} high-quality image generation prompts.

User request:
{user_request}

Requirements:
- Each prompt should be 1 single line
- No numbering
- No bullet points
- No extra explanations
- No emojis
- Each prompt should be slightly different
- Photorealistic style
- Keep prompts clean and consistent

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

    # Split into list by line
    prompts = [line.strip() for line in content.split("\n") if line.strip()]

    return prompts


# -----------------------------
# SHOW RESULT
# -----------------------------
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