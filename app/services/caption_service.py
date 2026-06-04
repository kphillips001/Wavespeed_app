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


CAPTION_COUNT = 10


X_FALLBACK_CAPTIONS = [
    "Be honest... are you answering texts right away or letting them sit for a little drama? 😂📱👇",
    "Okay but what's one thing that instantly puts you in a better mood? ✨👇",
    "If we were both ignoring responsibilities right now, what are we doing instead? 😌👇",
    "Pick one: cozy night in, spontaneous drive, or somewhere quiet with a view? 🚗🌙👇",
    "Tell me your ideal way to end a long day... music, snacks, or no notifications? 😌👇",
    "You get one lazy afternoon with zero plans... what are we doing first? ☀️👇",
    "Be honest... are you the planner or the 'let's see where the night goes' type? 😂👇",
    "If I texted you 'come over' right now, what would your excuse be? 😏📱👇",
    "What's your go-to move when you want to disappear from the world for a bit? 👀👇",
    "Current mood: phone in hand, plans undecided, trouble optional 😌🔥👇",
]


X_CAPTION_STYLE = """
X CAPTION STYLE:
- conversational girlfriend-energy captions
- flirty, warm, playful, and easy to answer
- designed to make the viewer feel like she is talking directly to them
- captions should feel like a text message, not an influencer post
- ask questions about the viewer’s choices, mood, weekend, plans, stories, habits, texting style, routines, or opinions
- create imagined interaction, like hanging out, relaxing together, taking a drive, watching a movie, sitting by the water, or winding down
- use natural openers like:
  - "Be honest..."
  - "Okay but..."
  - "Pick one..."
  - "Tell me..."
  - "If we were..."
  - "You get one choice..."
  - "Current mood..."
- every X caption should invite a reply
- every X caption should feel specific to the image mood, setting, outfit, or vibe
- prefer questions that make the viewer talk about themselves
- at least 8 of the 10 captions must focus on the viewer, not the creator
- no more than 2 captions may reference the creator’s appearance, outfit, look, body, pose, or vibe
- avoid validation-seeking captions
- avoid captions that only focus on her appearance
- avoid generic thirst-trap captions
- do NOT use "rate this", "rate me", "rate this look", "cute or trouble", "can’t stop staring", "can't stop staring", "would you date me", "you vs me", "what was your first thought", "spill it", or "who’s stalking my phone" phrasing
"""


BANNED_PHRASES = [
    "rate this",
    "rate me",
    "rate this look",
    "cute or trouble",
    "you vs me",
    "first thought",
    "what was your first thought",
    "can’t stop staring",
    "can't stop staring",
    "would you date me",
    "spill it",
    "stalking my phone",
    "who’s stalking my phone",
    "who's stalking my phone",
]


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


def normalize_x_caption_response(caption_data):
    if not isinstance(caption_data, dict):
        caption_data = {
            "image_summary": {
                "scene": "",
                "outfit": "",
                "mood": "",
                "setting": "",
            },
            "x": [],
        }

    x_captions = caption_data.get(
        "x",
        [],
    )

    if not isinstance(x_captions, list):
        x_captions = []

    cleaned_captions = []

    for caption in x_captions:
        if not isinstance(caption, str):
            continue

        cleaned_caption = caption.strip()

        if not cleaned_caption:
            continue

        caption_lower = cleaned_caption.lower()

        if any(
            banned_phrase in caption_lower
            for banned_phrase in BANNED_PHRASES
        ):
            continue

        if cleaned_caption not in cleaned_captions:
            cleaned_captions.append(
                cleaned_caption
            )

    for fallback_caption in X_FALLBACK_CAPTIONS:
        if len(cleaned_captions) >= CAPTION_COUNT:
            break

        if fallback_caption not in cleaned_captions:
            cleaned_captions.append(
                fallback_caption
            )

    caption_data["x"] = cleaned_captions[:CAPTION_COUNT]

    caption_data.pop(
        "instagram",
        None,
    )

    if "image_summary" not in caption_data:
        caption_data["image_summary"] = {
            "scene": "",
            "outfit": "",
            "mood": "",
            "setting": "",
        }

    return caption_data


def generate_social_captions(
    image_path,
    extra_instructions="",
):
    base64_image = encode_image(image_path)

    prompt = f"""
You are creating X captions for an AI creator/content model.

Analyze the image and return exactly {CAPTION_COUNT} captions for X only.

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

{X_CAPTION_STYLE}

IMPORTANT:
- You MUST return exactly {CAPTION_COUNT} captions.
- Do not return fewer than {CAPTION_COUNT}.
- Every caption must be unique.
- Every caption must be easy for a follower to answer.
- Captions should feel like something sent in a casual text conversation.
- Avoid generic influencer-caption wording.
- Avoid captions that ask viewers to rate the creator, the outfit, the look, or the vibe.

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
  "x": [
    "",
    "",
    "",
    "",
    "",
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

    caption_data = safe_json_loads(
        raw_text,
        fallback={
            "image_summary": {
                "scene": "",
                "outfit": "",
                "mood": "",
                "setting": "",
            },
            "x": X_FALLBACK_CAPTIONS,
        },
    )

    return normalize_x_caption_response(
        caption_data
    )


def regenerate_platform_captions(
    image_path,
    platform="x",
    extra_instructions="",
):
    base64_image = encode_image(image_path)

    prompt = f"""
You are regenerating X captions for an AI creator/content model.

Analyze the image and create exactly {CAPTION_COUNT} new X captions.

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

{X_CAPTION_STYLE}

IMPORTANT:
- You MUST return exactly {CAPTION_COUNT} captions.
- Do not return fewer than {CAPTION_COUNT}.
- Every caption must be unique.
- Every caption must be easy for a follower to answer.
- Captions should feel like something sent in a casual text conversation.
- Avoid generic influencer-caption wording.
- Avoid captions that ask viewers to rate the creator, the outfit, the look, or the vibe.

Extra user instructions:
{extra_instructions}

Return ONLY valid JSON in this format:

{{
  "x": [
    "",
    "",
    "",
    "",
    "",
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

    caption_data = safe_json_loads(
        raw_text,
        fallback={
            "x": X_FALLBACK_CAPTIONS,
        },
    )

    return normalize_x_caption_response(
        caption_data
    )