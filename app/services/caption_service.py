import base64
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def encode_image(image_path):
    image_path = Path(image_path)

    with open(image_path, "rb") as image_file:
        return base64.b64encode(
            image_file.read()
        ).decode("utf-8")


def safe_json_loads(raw_text, fallback):
    try:
        return json.loads(raw_text)

    except json.JSONDecodeError:
        print("Caption service returned invalid JSON:")
        print(raw_text)

        return fallback


def generate_social_captions(
    image_path,
    extra_instructions="",
):
    base64_image = encode_image(image_path)

    prompt = f"""
You are creating social media captions for an AI creator/content model.

Analyze the image and return captions for BOTH Instagram and X.

GENERAL STYLE:
- flirty but social-media safe
- confident
- playful
- short
- engagement-focused
- every caption MUST include emojis
- use 1–3 emojis per caption
- emojis should feel natural, flirty, sunny, playful, or platform-appropriate
- no hashtags for now
- no explicit sexual language
- no mention of AI
- no mention that this is generated
- avoid sounding like an ad

INSTAGRAM CAPTION STYLE:
- polished
- cute
- flirty but natural
- lifestyle/content creator vibe
- should feel like something a real creator would post
- can be slightly softer and prettier than X
- should still invite comments sometimes, but not every caption needs to be a question

X CAPTION STYLE:
- slightly flirtier than Instagram
- more interactive
- designed to spark replies, quotes, and reactions
- use playful tension and curiosity
- ask easy-to-answer questions
- use reply-bait formats like:
  - "be honest..."
  - "pick one..."
  - "what was your first thought?"
  - "would you..."
  - "rate this..."
  - "cute or trouble?"
  - "you vs me?"
- captions should feel casual, bold, and reactive
- every X caption should make the viewer want to reply

Extra user instructions:
{extra_instructions}

Return ONLY valid JSON in this format:

{{
  "image_summary": {{
    "scene": "",
    "outfit": "",
    "mood": "",
    "setting": ""
  }},
  "instagram": [
    "",
    "",
    "",
    "",
    ""
  ],
  "x": [
    "",
    "",
    "",
    "",
    ""
  ]
}}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ],
    )

    raw_text = response.output_text

    return safe_json_loads(
        raw_text,
        fallback={
            "image_summary": {
                "scene": "",
                "outfit": "",
                "mood": "",
                "setting": "",
            },
            "instagram": [
                "Weekend mood unlocked ☀️✨",
                "Just a little sunshine and confidence 😌💫",
                "This view felt too good not to share 🌊✨",
                "Soft smiles, pretty light, good energy 💕",
                "Some days just need a little extra sparkle ✨",
            ],
            "x": [
                "Be honest... what was the first thing you noticed? 👀✨",
                "Cute or trouble? Choose carefully 😇😈",
                "Would you sit next to me or pretend not to stare? 😂👀",
                "Rate the vibe... but I’m judging your answer 😏✨",
                "Pick one: the view, the outfit, or the smile? 👀",
            ],
        },
    )


def regenerate_platform_captions(
    image_path,
    platform,
    extra_instructions="",
):
    base64_image = encode_image(image_path)

    platform_key = platform.lower()

    if platform_key in ["twitter"]:
        platform_key = "x"

    if platform_key not in ["instagram", "x"]:
        platform_key = "instagram"

    if platform_key == "x":
        platform_style = """
X CAPTION STYLE:
- slightly flirtier than Instagram
- interactive / reply-bait focused
- designed to spark replies, quotes, and reactions
- use playful questions
- use casual, bold, short phrasing
- use phrases like:
  - "be honest..."
  - "pick one..."
  - "what was your first thought?"
  - "would you..."
  - "rate this..."
  - "cute or trouble?"
  - "you vs me?"
- every caption should make the viewer want to reply
"""
    else:
        platform_style = """
INSTAGRAM CAPTION STYLE:
- polished
- cute
- flirty but natural
- lifestyle/content creator vibe
- short and pretty
- slightly softer than X
- can invite comments, but should not feel forced
"""

    prompt = f"""
You are regenerating {platform_key} captions for an AI creator/content model.

Analyze the image and create 5 new {platform_key} captions.

GENERAL STYLE:
- flirty but social-media safe
- confident
- playful
- short
- engagement-focused
- every caption MUST include emojis
- use 1–3 emojis per caption
- emojis should feel natural, flirty, sunny, playful, or platform-appropriate
- no hashtags
- no explicit sexual language
- no mention of AI
- no mention that this is generated
- avoid sounding like an ad

{platform_style}

Extra user instructions:
{extra_instructions}

Return ONLY valid JSON in this format:

{{
  "{platform_key}": [
    "",
    "",
    "",
    "",
    ""
  ]
}}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ],
    )

    raw_text = response.output_text

    fallback_captions = {
        "instagram": [
            "Weekend mood unlocked ☀️✨",
            "Just a little sunshine and confidence 😌💫",
            "This view felt too good not to share 🌊✨",
            "Soft smiles, pretty light, good energy 💕",
            "Some days just need a little extra sparkle ✨",
        ],
        "x": [
            "Be honest... what was the first thing you noticed? 👀✨",
            "Cute or trouble? Choose carefully 😇😈",
            "Would you sit next to me or pretend not to stare? 😂👀",
            "Rate the vibe... but I’m judging your answer 😏✨",
            "Pick one: the view, the outfit, or the smile? 👀",
        ],
    }

    return safe_json_loads(
        raw_text,
        fallback={
            platform_key: fallback_captions.get(
                platform_key,
                fallback_captions["instagram"],
            )
        },
    )