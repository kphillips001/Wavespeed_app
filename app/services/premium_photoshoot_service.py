import os
import re

from dotenv import load_dotenv

from main import generate_prompts_with_grok

load_dotenv()


def split_numbered_prompts(raw_text) -> list[str]:
    if not raw_text:
        return []

    if isinstance(raw_text, list):
        return [
            str(item).strip()
            for item in raw_text
            if str(item).strip()
        ]

    parts = re.split(
        r"\n\s*\d+[\.\)]\s+",
        "\n" + str(raw_text).strip(),
    )

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def build_premium_photoshoot_prompt(
    session_count: int,
    session_direction: str = "",
) -> str:
    return f"""
You are the Premium Photoshoot Director for a GFE adult-content image system.

Generate exactly {session_count} WAN 2.7 image-edit prompts.

The uploaded reference image is the seed image for the session.

Core objective:
Create a continuity-locked premium GFE session.

This is NOT social content.
This is NOT luxury content.
This is NOT editorial fashion photography.
This is NOT a random prompt batch.

The goal is:
same woman, same setting, same room, same lighting, same outfit state, same atmosphere,
with the session gradually becoming more intimate, more teasing, more inviting, and more emotionally charged.

Important continuity rules:
- Keep the exact same environment from the reference image.
- Keep the same furniture, room style, lighting, camera realism, and time of day.
- Keep the same outfit state as the reference image.
- Keep the same identity, face, hair, skin tone, body type, and proportions.
- Do not change locations.
- Do not create a storyline.
- Do not introduce new rooms, luxury villas, pools, yachts, penthouses, or unrelated settings.
- Do not make the images look professional, staged, editorial, or fashion-shoot styled.

Session progression:
- Image 1 should feel relaxed, warm, comfortable, and inviting.
- Middle images should become more flirtatious, teasing, and emotionally intimate.
- Final images should feel the most intense, private, and premium.

Use:
- natural body language
- warm eye contact
- soft expressions
- subtle confidence
- couch/bedroom/living-room realism when appropriate
- believable GFE intimacy
- private subscriber-only atmosphere
- candid in-the-moment energy

Avoid:
- luxury language
- polished magazine language
- professional photoshoot language
- random scene changes
- repetitive wording
- overly poetic wording

Optional user direction:
{session_direction}

Output format:
Return only a numbered list of prompts.
No titles.
No explanations.
No markdown.
""".strip()


def generate_premium_photoshoot_prompts(
    session_count: int,
    session_direction: str = "",
) -> list[str]:
    api_key = os.getenv("GROK_API_KEY")

    if not api_key:
        raise ValueError("Missing GROK_API_KEY in .env")

    instruction_prompt = build_premium_photoshoot_prompt(
        session_count=session_count,
        session_direction=session_direction,
    )

    raw_response = generate_prompts_with_grok(
        instruction_prompt,
        api_key,
    )

    prompts = split_numbered_prompts(raw_response)

    return prompts[:session_count]