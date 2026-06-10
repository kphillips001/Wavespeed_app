import os
import re
import base64

from dotenv import load_dotenv
from openai import OpenAI

from main import generate_prompts_with_grok

load_dotenv()


openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


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


def encode_reference_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(
            image_file.read()
        ).decode("utf-8")


def analyze_premium_reference_image(image_path):
    if not os.getenv("OPENAI_API_KEY"):
        return ""

    base64_image = encode_reference_image(image_path)

    prompt = """
Analyze this premium photoshoot reference image for scene continuity.

Return a concise visual description that can be reused as source-image context
for image-edit prompts.

Focus only on:
- location and setting
- water/pool/bed/room/outdoor details if visible
- clothing or coverage state
- lighting and time-of-day feel
- pose/body position
- framing/camera distance
- mood/expression

Do not invent missing details.
Do not make it safer or less revealing than the image.
Do not change the location.
Return plain text only.
""".strip()

    response = openai_client.responses.create(
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

    return response.output_text.strip()


def build_premium_photoshoot_prompt(
    session_count,
    session_direction="",
    reference_context="",
):
    reference_context = reference_context.strip() or (
        "No automatic image context was available. Preserve the uploaded "
        "reference image exactly, including its location, outfit or coverage, "
        "lighting, mood, and framing."
    )

    return f"""
You are the Premium Photoshoot Director for a GFE image system.

Generate exactly {session_count} WAN 2.7 image-edit prompts.

The uploaded reference image is the seed image for the session.
The following source-image context is authoritative and must be followed:

SOURCE IMAGE CONTEXT:
{reference_context}

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
- same exact location and visible environment from SOURCE IMAGE CONTEXT
- same visible props, surfaces, water, furniture, or background elements from SOURCE IMAGE CONTEXT
- same lighting and time-of-day feel from SOURCE IMAGE CONTEXT
- same outfit state or same level of coverage as the reference image
- same realistic candid atmosphere

Do NOT change location.
Do NOT add couches, beds, rooms, pools, resorts, or unrelated locations unless they are clearly present in SOURCE IMAGE CONTEXT or explicitly requested by the user.
Do NOT replace a pool/water scene with an indoor couch scene.
Do NOT replace topless, nude, bikini, lingerie, or clothed coverage with a different coverage level unless explicitly requested by the user.
Do NOT create a story sequence.
Do NOT describe where she went earlier.
Do NOT make it look polished, staged, editorial, or fashion-model styled.

SESSION STYLE:
The images should feel like a private GFE chatting session.
The viewer should feel like they are spending time with her in the same setting.
Each image should feel more connected, more intimate, and more emotionally engaging than the previous one.

POSE VARIATION IS MANDATORY:

Every image must use a noticeably different pose.

Do not repeat the pose from the previous image.

Do not keep the woman seated in the same position throughout the session.

The woman should naturally change positions as if spending time in the room.
If the source image is outdoors, in water, at a pool, in a shower, on a bed, in a bedroom, or any other specific setting,
all pose changes must remain physically plausible inside that same setting.

Examples include:

- leaning closer toward camera
- turning over shoulder
- resting on one elbow
- sitting or kneeling where the source setting allows
- reclining where the source setting allows
- standing or half-standing where the source setting allows
- shifting weight naturally
- changing arm placement
- changing gaze direction
- changing torso angle

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
- same exact source-image setting
- same visible environment details
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
- relaxed starting posture matching the source image
- leaning slightly closer
- turning shoulder or hip angle
- shifting arm placement
- changing gaze and expression
- reclining or sitting only if plausible in the source setting
- standing or kneeling only if plausible in the source setting
- moving closer to the camera while keeping the same environment

Each image should feel like a different moment
from the same private session.

Do NOT generate multiple prompts with essentially
the same sitting position.
Do NOT generate couch, bed, floor, window, or room poses unless those details exist in SOURCE IMAGE CONTEXT or the user requested them.

Each image should feel like a new moment from
the same private session.

Examples:
- same source location, slightly different pose
- same source lighting, closer gaze
- same source environment, different torso angle
- same source coverage, different arm placement
- same source scene, more intimate framing

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
- leaning closer
- playful teasing grin
- soft direct eye contact
- natural body language
- intimate in-the-moment feeling
- private subscriber-only atmosphere
- realistic source-matched lighting
- comfortable girlfriend energy
- quiet romantic tension
- subtle playful confidence

Optional user direction:
{session_direction}

USER DIRECTION RULE:
If Optional user direction is blank, do not invent a new location or setup.
If Optional user direction conflicts with SOURCE IMAGE CONTEXT, follow the user direction only for the specific detail requested and preserve the rest of the source context.

OUTPUT FORMAT:
Return only a numbered list of prompts.
No titles.
No explanations.
No markdown.
""".strip()


def generate_premium_photoshoot_prompts(
    session_count,
    session_direction="",
    reference_context="",
):
    api_key = os.getenv("GROK_API_KEY")

    if not api_key:
        raise ValueError("Missing GROK_API_KEY in .env")

    prompt_instruction = build_premium_photoshoot_prompt(
        session_count=session_count,
        session_direction=session_direction,
        reference_context=reference_context,
    )

    raw_response = generate_prompts_with_grok(
        prompt_instruction,
        api_key,
    )

    prompts = split_numbered_prompts(raw_response)

    return prompts[:session_count]
