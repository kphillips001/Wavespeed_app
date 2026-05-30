import os
import re

from dotenv import load_dotenv

from main import generate_prompts_with_grok

load_dotenv()


def split_numbered_prompts(raw_text):
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
    session_count,
    session_direction="",
):
    return f"""
You are the Premium Photoshoot Director for a GFE image system.

Generate exactly {session_count} WAN 2.7 image-edit prompts.

The uploaded reference image is the seed image for the session.

CORE GOAL:
Create a continuity-locked Girlfriend Experience premium session.

This is NOT social content.
This is NOT luxury content.
This is NOT editorial photography.
This is NOT a random prompt batch.
This is NOT a professional photoshoot.

The product is connection, access, intimacy, warmth, and emotional escalation.

CONTINUITY LOCK:
Every prompt must preserve:
- same woman
- same face
- same hair
- same body
- same skin tone
- same room
- same couch/bed/furniture
- same lighting
- same time of day
- same outfit state or same level of coverage as the reference image
- same realistic candid atmosphere

Do NOT change location.
Do NOT add luxury villas, yachts, penthouses, pools, resorts, or unrelated locations.
Do NOT create a story sequence.
Do NOT describe where she went earlier.
Do NOT make it look polished, staged, editorial, or fashion-model styled.

SESSION STYLE:
The images should feel like a private GFE chatting session.
The viewer should feel like they are spending time with her in the same room.
Each image should feel more connected, more intimate, and more emotionally engaging than the previous one.

POSE VARIATION IS MANDATORY:

Every image must use a noticeably different pose.

Do not repeat the pose from the previous image.

Do not keep the woman seated in the same position throughout the session.

The woman should naturally change positions as if spending time in the room.

Examples include:

- sitting cross-legged
- sitting sideways
- reclining on couch
- lying across cushions
- kneeling on couch
- standing beside couch
- standing near window
- sitting on floor against couch
- leaning on armrest
- walking toward camera
- turning over shoulder
- resting on stomach
- resting on side

Each image must create obvious visual variety while preserving continuity.

ESCALATION SYSTEM:
Treat the entire session as a progressive emotional intimacy ladder.

The escalation must occur regardless of whether the session contains
5, 10, 15, 20, or 25 images.

Early Stage (0-20%):
- relaxed
- comfortable
- inviting
- warm eye contact
- natural posture
- approachable girlfriend energy

Flirty Stage (20-40%):
- playful smiles
- teasing expressions
- stronger viewer engagement
- increased confidence
- subtle flirtation

Teasing Stage (40-60%):
- more suggestive body language
- closer framing
- stronger eye contact
- more intimate posture
- heightened anticipation

Intimate Stage (60-80%):
- private subscriber-only feeling
- emotionally connected
- stronger confidence
- inviting posture
- increased romantic tension

Peak Tension Stage (80-100%):
- highest emotional intimacy level of the session
- strongest viewer connection
- most private feeling
- most confident body language
- strongest romantic anticipation

IMPORTANT:
Each prompt must feel like a natural continuation of the previous image.

Every escalation step must include BOTH:

1. Increased intimacy
2. New body positioning

Expression changes alone are not sufficient.

The viewer should immediately recognize a different pose when comparing adjacent images.

The woman should frequently change posture, orientation, camera relationship, and position within the room while preserving continuity.

The woman should appear progressively more comfortable,
more playful,
more flirtatious,
and more emotionally connected to the viewer as the session progresses.

Never reset the escalation.
Never jump backward.
Every prompt should build naturally upon the previous one.

SESSION CONTINUITY RULE:
The viewer should feel like all images were taken within
the same 10-minute period.

Maintain:
- same room
- same furniture
- same lighting
- same atmosphere
- same camera style
- same woman
- same appearance

Only posture, expression, body language, framing,
and emotional intimacy level should evolve.

POSE EVOLUTION RULE:

Every prompt MUST introduce a clearly different pose.

Do NOT generate prompts that differ only by:
- facial expression
- eye contact
- smile intensity
- camera distance

The woman's physical position must evolve
throughout the session.

Examples of acceptable progression:
- sitting normally
- legs tucked beneath her
- cross-legged
- reclining sideways
- leaning forward
- resting against cushions
- seated at edge of couch
- laying across couch
- curled into couch
- stretched comfortably along couch

Each image should feel like a different moment
from the same private session.

Do NOT generate multiple prompts with essentially
the same sitting position.

Each image should feel like a new moment from
the same private session.

Examples:
- sitting cross-legged
- leaning back into cushions
- reclining sideways
- resting against armrest
- kneeling on couch
- legs tucked beneath her
- seated at edge of couch
- leaning forward
- curled comfortably into cushions
- laying across couch

The pose progression should evolve naturally
throughout the session while preserving
the same environment and continuity.

PROMPT STYLE:
Keep the wording visual and image-generation friendly.
Avoid poetic filler.
Avoid repeating the same sentence structure.
Avoid luxury language.
Avoid professional photography language.

Use candid phrases like:
- relaxed on the couch
- leaning closer
- playful teasing grin
- soft direct eye contact
- natural body language
- intimate in-the-moment feeling
- private subscriber-only atmosphere
- warm realistic room lighting
- comfortable girlfriend energy
- quiet romantic tension
- subtle playful confidence

Optional user direction:
{session_direction}

OUTPUT FORMAT:
Return only a numbered list of prompts.
No titles.
No explanations.
No markdown.
""".strip()


def generate_premium_photoshoot_prompts(
    session_count,
    session_direction="",
):
    api_key = os.getenv("GROK_API_KEY")

    if not api_key:
        raise ValueError("Missing GROK_API_KEY in .env")

    prompt_instruction = build_premium_photoshoot_prompt(
        session_count=session_count,
        session_direction=session_direction,
    )

    raw_response = generate_prompts_with_grok(
        prompt_instruction,
        api_key,
    )

    prompts = split_numbered_prompts(raw_response)

    return prompts[:session_count]