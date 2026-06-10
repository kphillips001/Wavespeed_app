import os
import re
import base64

from dotenv import load_dotenv
from openai import OpenAI

from main import generate_prompts_with_grok

from app.prompts.nsfw_progression import build_nsfw_photoshoot_escalation

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
You are analyzing a reference image for an escalating NSFW premium photoshoot.

Return a concise but precise visual description focused on continuity and current state.

Focus especially on:
- exact location / room / environment (floor, walls, lighting, background elements)
- current clothing or nudity state in detail (e.g. "fully clothed", "wearing lingerie", "topless wearing only black thong", "completely nude", "sheer robe open", etc.)
- which body parts are visible (breasts visible? nipples? lower body covered?)
- current pose and body position
- lighting and time-of-day
- framing / camera distance

Be direct and accurate about nudity/coverage level. Do not soften or censor.
Do not invent details that are not visible.
Do not change the location or setting.
Return only plain text description, no labels or bullet points.
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
You are the Premium Photoshoot Director for an escalating NSFW GFE image system.

Generate exactly {session_count} WAN 2.7 image-edit prompts.

The uploaded reference image is the seed image for the session.
The following source-image context is authoritative and must be followed:

SOURCE IMAGE CONTEXT:
{reference_context}

================================================================================
AUTOMATIC NSFW EVOLUTION MODE (HIGHEST PRIORITY - OVERRIDES OTHER RULES)
================================================================================

Read the SOURCE IMAGE CONTEXT above to determine the woman's **current coverage / nudity state**.

Then generate a clear, gradual erotic progression across all {session_count} prompts, starting from exactly the state described in the reference.

Typical progression ladder (adapt the starting point based on what the reference actually shows):

1. Start extremely close to the reference: same pose, same clothing/coverage level, same environment.
2. Increase sensuality: hands exploring breasts, squeezing, playing with nipples (if topless or becoming topless).
3. Lower body touch: hand between legs, rubbing over panties/thong, visible arousal/wetness.
4. Progressive clothing removal: sliding panties down, partial removal, more skin revealed.
5. Full removal: panties/thong completely off, full nudity, legs naturally opening/spreading.
6. Explicit self-pleasure: fingers on clit, fingering, masturbation poses, intimate self-touch.
7. Peak: arched back, eyes closed in pleasure, biting lip, moaning expressions, intense intimate moments.

MANDATORY RULES FOR THIS SESSION:
- Stay in the **EXACT same environment** for every prompt: same floor, same walls, same lighting, same background, same furniture, same room. Do NOT change location or add new props/rooms.
- Never add clothing back or reduce the nudity level compared to previous steps.
- Perfect continuity: same woman, same face, same hair, same rich dark tan skin, same body, same full natural D-cup breasts with visible nipples when exposed.
- Increase explicitness and intimacy **gradually and naturally** across the batch.
- Use natural, sensual, private-creator-moment language.
- The batch must feel like one continuous private moment that slowly escalates in real time.

If the reference is already quite nude, start the ladder from that point and escalate further into self-touch and peak pleasure.
If the reference is clothed or lightly covered, the progression should still move toward increasing nudity and explicit acts, but do it gradually.

This NSFW evolution takes priority over general variety or emotional-only escalation.

================================================================================

CORE GOAL:
Create a continuity-locked escalating NSFW premium photoshoot that feels like a private GFE moment unfolding.

This is NOT a random batch.
This is NOT a professional photoshoot.
This is a private, intimate, progressively more explicit session with the same woman in the same place.

CONTINUITY LOCK (adjusted for NSFW escalation):
Every prompt must preserve:
- same woman
- same face
- same hair
- same body proportions and skin tone
- same exact location and visible environment from SOURCE IMAGE CONTEXT (floor, walls, lighting, background — this is non-negotiable)
- same lighting and time-of-day feel from SOURCE IMAGE CONTEXT

The outfit / coverage level is **allowed and expected to change** as part of the NSFW progression (clothing removal is the point of the escalation).

Do NOT change the physical location or major environment.
Do NOT invent new rooms, beds, pools, or furniture that are not in the SOURCE IMAGE CONTEXT.

SESSION STYLE (NSFW Photoshoot):
The images should feel like one continuous private NSFW moment with her in the exact same place.
The viewer should feel like they are watching a real, intimate escalation unfold in real time.

The core of this session is **gradual NSFW progression** (as defined in the high-priority block above), combined with natural pose and framing variety inside the locked environment.

POSE & FRAMING VARIATION (inside the fixed environment):
Every image must feel visually distinct through:
- different poses and body positions (plausible in the source setting)
- different camera angles and distances (while staying intimate)
- different hand placement and micro-actions that support the current escalation step
- varying framing (close-up, medium, upper-thigh, etc.) as the explicitness increases

Do not repeat the exact same pose or framing consecutively.

All changes must stay physically inside the environment described in SOURCE IMAGE CONTEXT.

NSFW ESCALATION IS THE PRIMARY DRIVER:
The sexual progression defined earlier (clothing removal → touching → explicit self-pleasure) must be clearly visible and advancing across the batch.

Emotional connection, eye contact, and expressions should support the sexual escalation (pleasure faces, inviting looks, biting lip, etc.) rather than replace it.

SESSION CONTINUITY RULE:
The viewer should feel like all images were taken within the same short private session in one location.

Maintain strictly:
- same exact physical environment and all visible details from SOURCE IMAGE CONTEXT
- same lighting
- same woman, face, hair, body, skin tone
- same overall candid / private atmosphere

Only the following are allowed to evolve:
- clothing coverage (decreasing as per the NSFW ladder)
- pose and body position
- hand actions and self-touch
- explicitness level
- facial expression / pleasure response
- framing and camera angle (while staying in the same room)

Do NOT generate prompts that only change expression or eye contact while keeping the same coverage and pose.

The woman's physical state (how covered or how she is touching herself) must advance with the progression.

ENVIRONMENT LOCK (CRITICAL):
The single most important rule after identity continuity is:
**Never change the room, floor, walls, lighting, or major background elements.**

Every single prompt must be obviously happening in the exact same physical space as the reference image.

PROMPT STYLE:
Keep the wording visual, concrete, and directly usable for WAN 2.7 image editing.
Be explicit about nudity, body contact, and actions once the progression reaches those stages.
Match the tone of authentic private creator content.

Use natural, in-the-moment phrases such as:
- still in the same spot on the wooden floor
- slowly sliding her thong down her thighs
- hand between her legs, fingers moving
- back slightly arched
- fingers circling her clit
- eyes closed, biting her lower lip
- natural light on her skin
- legs parted

Optional user direction:
{session_direction}

USER DIRECTION RULE:
Optional direction can emphasize certain steps or add flavor, but the core NSFW progression, environment lock, and identity continuity from the source context must be respected.

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
