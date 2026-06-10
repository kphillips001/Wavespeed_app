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


X_CAPTION_COUNT = 10
INSTAGRAM_CAPTION_COUNT = 5
CAPTION_COUNT = X_CAPTION_COUNT


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

INSTAGRAM_FALLBACK_CAPTIONS = [
    "Soft light, easy mood, and a little confidence ✨",
    "Weekend energy, even if it is only for a minute ☀️",
    "Pretty light has a way of changing the whole day 💫",
    "Keeping this one simple: good light, good mood, good moment 🤍",
    "A little sunshine and a little main-character energy ✨",
    "Some moments are too pretty not to keep 🌸",
    "Quiet confidence, soft light, and a good view ✨",
    "This felt like a save-it-for-later kind of moment 🤍",
    "Easy days, warm light, soft smile ☀️",
    "Just here for the pretty little moments 💫",
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

INSTAGRAM_CAPTION_STYLE = """
INSTAGRAM CAPTION STYLE:
- polished, cute, flirty, and natural
- lifestyle/content creator vibe
- should feel like something a real creator would post
- softer and prettier than X
- can invite comments sometimes, but not every caption needs to be a question
- short enough to feel casual and post-ready
- avoid reply-bait phrasing that feels too X/Twitter-specific
- avoid generic influencer-caption wording
- captions must be grounded in the actual image
- identify visible scene cues before writing: setting, location type, weather, lighting, outfit, vehicle, road, room, beach, water, props, and overall vibe
- if the image has a country, rural, truck, dirt road, field, golden-hour, lake, beach, city, gym, bedroom, or travel vibe, make the caption reflect that specific vibe
- do not use generic fallback lines like "soft light, easy mood" unless that is truly the strongest visual read
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


def get_caption_count(platform):
    if platform == "instagram":
        return INSTAGRAM_CAPTION_COUNT

    return X_CAPTION_COUNT


def clean_caption_list(
    captions,
    fallback_captions,
    filter_banned=False,
    caption_count=CAPTION_COUNT,
):
    if not isinstance(captions, list):
        captions = []

    cleaned_captions = []

    for caption in captions:
        if not isinstance(caption, str):
            continue

        cleaned_caption = caption.strip()

        if not cleaned_caption:
            continue

        caption_lower = cleaned_caption.lower()

        if filter_banned and any(
            banned_phrase in caption_lower
            for banned_phrase in BANNED_PHRASES
        ):
            continue

        if cleaned_caption not in cleaned_captions:
            cleaned_captions.append(
                cleaned_caption
            )

    for fallback_caption in fallback_captions:
        if len(cleaned_captions) >= caption_count:
            break

        if fallback_caption not in cleaned_captions:
            cleaned_captions.append(
                fallback_caption
            )

    return cleaned_captions[:caption_count]


def normalize_caption_response(caption_data, platforms=None):
    platforms = platforms or ["x"]

    if not isinstance(caption_data, dict):
        caption_data = {
            "image_summary": {
                "scene": "",
                "outfit": "",
                "mood": "",
                "setting": "",
            },
        }

    if "x" in platforms:
        caption_data["x"] = clean_caption_list(
            caption_data.get("x", []),
            X_FALLBACK_CAPTIONS,
            filter_banned=True,
            caption_count=X_CAPTION_COUNT,
        )
    else:
        caption_data.pop("x", None)

    if "instagram" in platforms:
        caption_data["instagram"] = clean_caption_list(
            caption_data.get("instagram", []),
            INSTAGRAM_FALLBACK_CAPTIONS,
            caption_count=INSTAGRAM_CAPTION_COUNT,
        )
    else:
        caption_data.pop("instagram", None)

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
    platforms=None,
):
    platforms = platforms or ["x"]
    base64_image = encode_image(image_path)

    platform_sections = []
    json_platform_fields = []

    if "instagram" in platforms:
        platform_sections.append(INSTAGRAM_CAPTION_STYLE)
        json_platform_fields.append(
            '"instagram": ["", "", "", "", ""]'
        )

    if "x" in platforms:
        platform_sections.append(X_CAPTION_STYLE)
        json_platform_fields.append(
            '"x": ["", "", "", "", "", "", "", "", "", ""]'
        )

    platform_style_text = "\n".join(platform_sections)
    json_platform_text = ",\n  ".join(json_platform_fields)
    platform_label = " and ".join(
        "Instagram" if platform == "instagram" else "X"
        for platform in platforms
    )

    prompt = f"""
You are creating social media captions for an AI creator/content model.

Analyze the image carefully using the attached image.
Return exactly {INSTAGRAM_CAPTION_COUNT} Instagram captions if Instagram is requested.
Return exactly {X_CAPTION_COUNT} X captions if X is requested.

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

{platform_style_text}

IMPORTANT:
- You MUST return the exact caption count requested for each platform.
- Do not return fewer captions than requested.
- Every caption must be unique.
- Every caption must be easy for a follower to answer.
- Captions should feel like something sent in a casual text conversation.
- Avoid generic influencer-caption wording.
- Avoid captions that ask viewers to rate the creator, the outfit, the look, or the vibe.
- For Instagram, at least 4 of the 5 captions must include a concrete visual cue from the image.

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
  {json_platform_text}
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
            "instagram": INSTAGRAM_FALLBACK_CAPTIONS,
        },
    )

    return normalize_caption_response(
        caption_data,
        platforms=platforms,
    )


def regenerate_platform_captions(
    image_path,
    platform="x",
    extra_instructions="",
):
    base64_image = encode_image(image_path)
    platform_key = (platform or "x").lower()

    if platform_key in ["twitter"]:
        platform_key = "x"

    if platform_key not in ["instagram", "x"]:
        platform_key = "x"

    platform_style = (
        INSTAGRAM_CAPTION_STYLE
        if platform_key == "instagram"
        else X_CAPTION_STYLE
    )

    fallback_captions = (
        INSTAGRAM_FALLBACK_CAPTIONS
        if platform_key == "instagram"
        else X_FALLBACK_CAPTIONS
    )
    caption_count = get_caption_count(platform_key)
    json_empty_items = ", ".join(
        '""'
        for _ in range(caption_count)
    )

    prompt = f"""
You are regenerating {platform_key} captions for an AI creator/content model.

Analyze the attached image carefully and create exactly {caption_count} new {platform_key} captions.

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

IMPORTANT:
- You MUST return exactly {caption_count} captions.
- Do not return fewer than {caption_count}.
- Every caption must be unique.
- Every caption must be easy for a follower to answer.
- Captions should feel like something sent in a casual text conversation.
- Avoid generic influencer-caption wording.
- Avoid captions that ask viewers to rate the creator, the outfit, the look, or the vibe.
- If regenerating Instagram captions, at least 4 of the 5 captions must include a concrete visual cue from the image.

Extra user instructions:
{extra_instructions}

Return ONLY valid JSON in this format:

{{
  "{platform_key}": [
    {json_empty_items}
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
            platform_key: fallback_captions,
        },
    )

    return normalize_caption_response(
        caption_data,
        platforms=[platform_key],
    )
