from app.config.settings import MODELS, PERSONA_OUTPUT_DIRS
from app.prompts.generation_modes import GENERATION_MODES
from app.prompts.platform_modes import PLATFORM_MODES
from app.prompts.spice_levels import SPICE_LEVELS


def select_persona():
    print("\n" + "=" * 80)
    print(" SELECT PERSONA")
    print("=" * 80)
    print("Press 1 for Ava Blackthorne")
    print("Press 2 for Amanda Cayne")

    while True:
        choice = input("\nEnter number (1 or 2): ").strip()

        if choice in PERSONA_OUTPUT_DIRS:
            selected = PERSONA_OUTPUT_DIRS[choice]

            print(f"\n✅ Selected: {selected['name']}")
            print(f"Final output folder: {selected['output_dir']}\n")

            return choice

        print("❌ Invalid selection. Please enter 1 or 2.")


def get_prompt_count():
    while True:
        try:
            user_input = input(
                "\nHow many prompts do you want ChatGPT/Grok to generate? "
            ).strip()

            prompt_count = int(user_input)

            if prompt_count > 0:
                return prompt_count

            print("❌ Enter a number greater than 0.")

        except ValueError:
            print("❌ Please enter a valid number.")


def select_model():
    print("\nSelect WaveSpeed Model:\n")

    print("1 for Google Nano Banana 2 Edit")
    print("2 for Google Nano Banana Pro Edit")
    print("3 for ByteDance Seedream 4.5 Edit")
    print("4 for ByteDance Seedream 5.0 Lite Edit")

    while True:
        choice = input("\nEnter number (1-4): ").strip()

        if choice in MODELS:
            selected = MODELS[choice]

            print(f"\n✅ Selected: {selected['name']}\n")

            return selected

        print("❌ Invalid selection. Try again.")


def ask_yes_no(prompt_text):
    while True:
        answer = input(f"{prompt_text} (y/n): ").strip().lower()

        if answer in {"y", "yes"}:
            return True

        if answer in {"n", "no"}:
            return False

        print("❌ Please enter y or n.")


# -----------------------------
# GENERATION MODE
# -----------------------------
def select_generation_mode():
    print("\n" + "=" * 80)
    print(" SELECT GENERATION MODE")
    print("=" * 80)

    print("1. Variety Batch Mode")
    print("   - Different settings, outfits, poses, lighting, and scenes")
    print()

    print("2. Photoshoot Set Mode")
    print("   - Same outfit and same setting, different poses and camera angles")
    print()

    print("3. Story Sequence Mode")
    print("   - Connected images that feel like a mini visual story")

    while True:
        choice = input("\nEnter number (1-3): ").strip()

        if choice in GENERATION_MODES:
            selected = GENERATION_MODES[choice]

            print(f"\n✅ Selected: {selected['name']}")
            print(f"📸 {selected['description']}\n")

            return selected

        print("❌ Invalid selection. Please enter 1-3.")


# -----------------------------
# PLATFORM MODE
# -----------------------------
def select_platform_mode():
    print("\n" + "=" * 80)
    print(" SELECT PLATFORM MODE")
    print("=" * 80)

    print("1. Social Media")
    print("2. Telegram")
    print("3. Fanvue Teaser")
    print("4. Fanvue Explicit")

    while True:
        choice = input("\nEnter number (1-4): ").strip()

        if choice in PLATFORM_MODES:
            selected = PLATFORM_MODES[choice]

            print(f"\n✅ Selected Platform: {selected}\n")

            return selected

        print("❌ Invalid selection. Please enter 1-4.")


# -----------------------------
# SPICE LEVEL
# -----------------------------
def select_spice_level():
    print("\n" + "=" * 80)
    print(" SELECT SPICE LEVEL")
    print("=" * 80)

    print("1. Social Safe")
    print("2. Glamour")
    print("3. Spicy Glamour")
    print("4. Fanvue Tease")
    print("5. Explicit")

    while True:
        choice = input("\nEnter number (1-5): ").strip()

        if choice in SPICE_LEVELS:
            selected = SPICE_LEVELS[choice]

            print(f"\n✅ Selected Spice Level: {selected}\n")

            return selected

        print("❌ Invalid selection. Please enter 1-5.")