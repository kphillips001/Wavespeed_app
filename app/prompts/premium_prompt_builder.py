from app.prompts.shot_types import SHOT_TYPES



def build_premium_shot_type_context():
    formatted_shot_types = "\n".join(
        f"- {shot_type}"
        for shot_type in SHOT_TYPES
    )

    return f"""
SHOT INTELLIGENCE:
Use a natural mix of creator photography shot types.

Suggested shot types:
{formatted_shot_types}

IMPORTANT:
- These are not rigid rules.
- Adapt shot types naturally to the user's creative tags.
- Avoid repeating the same framing repeatedly.
- Vary visual energy across the batch.
- Build visually different creator moments.

Use these to vary:
- pose
- framing
- camera distance
- body orientation
- body-leading composition
- perspective
- camera height
- emotional tone
- closeups vs full-body shots
- environmental interaction
- storytelling energy
"""



def build_premium_grok_prompt(
    creative_tags: str,
    prompt_count: int = 10,
) -> str:

    shot_type_context = build_premium_shot_type_context()

    return f"""
I need a list of {prompt_count} high-quality WAN 2.7 image-edit prompts.

These prompts always use the SAME reference image.

Every prompt MUST preserve:
- same woman
- same face
- same hair
- same body
- same identity from the reference image
- same general skin tone
- same creator aesthetic
- same overall attractiveness

USER CREATIVE TAGS:
{creative_tags}

PREMIUM CREATIVE DIRECTOR MODE:

The user is NOT writing full prompts.
The user is only providing creative signals.

Your job is to become a Premium AI Creative Director.

Turn short premium tags into complete cinematic WAN 2.7 image-edit prompts.

These prompts are intended for premium creator-content generation.

IMPORTANT:
The images should feel:
- seductive
- intimate
- realistic
"""