import os
import re

from dotenv import load_dotenv

from main import generate_prompts_with_grok


load_dotenv()

QUALITY_SUFFIX = "soft even studio lighting, photorealistic 8k"


IDENTITY_LOCK_RULES = """
REFERENCE IDENTITY LOCK

Every generated prompt must preserve the reference woman exactly:
- same face
- same facial structure
- same hair color
- same hairstyle
- same skin tone
- same body
- same body proportions
- same bust size
- full natural D-cup breast proportions
- full natural D-cup breast volume
- same overall identity from the reference image

Do not change her hair color.
Do not make her red-haired.
Do not make her auburn-haired.
Do not make her ginger-haired.
Do not make her blonde if the reference is not blonde.
Do not make her brunette if the reference is not brunette.
Do not invent any hair color different from the reference image.
"""


TOPLESS_VISIBILITY_RULES = """
TOPLESS / NUDE VISIBILITY RULES

If topless, bare breasts, nude, naked, or upper body uncovered content is requested:
- every topless prompt must clearly preserve bare breasts
- nipples must be visible
- nipples must be perky and visible
- do not hide nipples with hair
- do not hide nipples with arms
- do not hide nipples with hands
- do not hide nipples with furniture, sheets, pillows, towels, steam, shadows, or props
- do not replace toplessness with lingerie, bra, bikini top, crop top, shirt, robe, towel, or covered chest
- keep the presentation realistic and consistent with the reference woman's body
- preserve full natural D-cup breast proportions
- preserve full natural D-cup breast volume
"""


NUDITY_GROOMING_RULES = """
NUDITY GROOMING RULES

If nude, naked, fully nude, lower body visible, or pubic area visible content is requested:
- no pubic hair
- no visible pubic hair
- keep the pubic area fully smooth
- do not add a landing strip
- do not add stubble
- do not add natural pubic hair
"""


USER_TAG_PRESERVATION_RULES = """
USER TAG PRESERVATION RULES

All user-supplied Explicit Tags are mandatory anchor concepts.

The AI may:
- expand user concepts
- enrich them with supporting visual details
- add setting details
- add lighting details
- add camera/framing details
- add mood and realism details

The AI must not:
- ignore user concepts
- replace user concepts with unrelated concepts
- remove the requested setting if the user supplied one
- drift into a different scene when a specific setting is supplied
"""


SETTING_RULES = """
OPTIONAL SETTING RULES

If the Optional Setting field is blank:
- AI should choose varied settings automatically.
- Generated prompts should avoid repeating the same setting.
- Use a balanced mix of indoor, outdoor, urban, nightlife, travel, and luxury settings.

If the Optional Setting field contains one setting:
- All generated prompts should remain centered on that setting.
- Variation should come from camera angle, framing, pose, lighting, and micro-location.

If the Optional Setting field contains multiple comma-separated settings:
- Rotate through those settings across the prompt batch.
- Avoid repeating the exact same micro-location or composition.
"""


PROMPT_DIVERSITY_RULES = """
PROMPT DIVERSITY RULES

For a batch of prompts:
- Every prompt must begin from a different visual concept.
- Do not reuse the same room, corner, furniture piece, or micro-location twice.
- Vary shot distance: close-up, medium close-up, waist-up, full-body, detail shot.
- Vary camera angle: eye-level, low angle, overhead, side angle, rear angle, mirror angle, POV.
- Vary framing: chest-up, head-to-hips, waist-up, tight crop, environmental shot.
- Vary mood and expression.
- Maintain the same reference woman across the full batch.
- Keep creator-phone realism unless the user explicitly asks for studio/editorial style.
"""


TOPLESS_TERMS = [
    "topless",
    "bare breasts",
    "bare breast",
    "nude",
    "nudity",
    "naked",
    "upper body uncovered",
    "no upper-body clothing",
    "no bra",
    "no top",
]


NUDE_LOWER_BODY_TERMS = [
    "nude",
    "nudity",
    "naked",
    "fully nude",
    "completely nude",
    "bare body",
    "lower body visible",
    "pubic area",
]


NIPPLE_VISIBILITY_PHRASE = (
    "topless with bare breasts and perky visible nipples unobstructed"
)


NUDITY_GROOMING_PHRASE = (
    "no pubic hair, fully smooth pubic area"
)


def normalize_prompt_suffix(prompt: str, suffix: str = QUALITY_SUFFIX) -> str:
    cleaned_prompt = (prompt or "").strip()

    if not cleaned_prompt:
        return ""

    cleaned_prompt = cleaned_prompt.rstrip(" ,.")
    normalized_suffix = suffix.strip().rstrip(" ,.")

    if cleaned_prompt.lower().endswith(normalized_suffix.lower()):
        return cleaned_prompt

    return f"{cleaned_prompt}, {normalized_suffix}"


def references_topless_content(text: str) -> bool:
    text_lower = (text or "").lower()

    return any(
        term in text_lower
        for term in TOPLESS_TERMS
    )


def references_nude_lower_body_content(text: str) -> bool:
    text_lower = (text or "").lower()

    return any(
        term in text_lower
        for term in NUDE_LOWER_BODY_TERMS
    )


def normalize_topless_visibility(prompt: str) -> str:
    cleaned_prompt = (prompt or "").strip()

    if not cleaned_prompt:
        return ""

    if not references_topless_content(cleaned_prompt):
        return cleaned_prompt

    if "visible nipple" in cleaned_prompt.lower():
        return cleaned_prompt

    cleaned_prompt = cleaned_prompt.rstrip(" ,.")

    return f"{cleaned_prompt}, {NIPPLE_VISIBILITY_PHRASE}"


def normalize_nudity_grooming(prompt: str) -> str:
    cleaned_prompt = (prompt or "").strip()

    if not cleaned_prompt:
        return ""

    if not references_nude_lower_body_content(cleaned_prompt):
        return cleaned_prompt

    if "no pubic hair" in cleaned_prompt.lower():
        return cleaned_prompt

    cleaned_prompt = cleaned_prompt.rstrip(" ,.")

    return f"{cleaned_prompt}, {NUDITY_GROOMING_PHRASE}"


def split_user_tags(raw_tags: str) -> list[str]:
    if not raw_tags:
        return []

    return [
        tag.strip()
        for tag in raw_tags.split(",")
        if tag.strip()
    ]


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


def build_explicit_enhancer_instruction(
    raw_explicit_tags: str,
    optional_setting: str | None = None,
) -> str:
    setting_text = (optional_setting or "").strip()
    setting_instruction = (
        f"The user supplied this optional setting: {setting_text}. "
        "Preserve it as a mandatory setting anchor."
        if setting_text
        else "No setting was supplied. Add varied setting ideas automatically."
    )

    return f"""
You are expanding user-supplied adult-content tags for an image generation workflow.

Raw user tags:
{raw_explicit_tags}

{setting_instruction}

Return only a comma-separated tag list.
Do not number the response.
Do not include explanations.

{USER_TAG_PRESERVATION_RULES}

{IDENTITY_LOCK_RULES}

{TOPLESS_VISIBILITY_RULES}

{NUDITY_GROOMING_RULES}

Add supporting visual details for:
- environment
- camera angle
- framing
- lighting
- realism
- mood
- body/pose composition
- rendering quality

Make the result detailed enough for a downstream prompt builder.
""".strip()


def build_explicit_prompt_instruction(
    enhanced_explicit_tags: str,
    prompt_count: int,
    optional_setting: str | None = None,
) -> str:
    setting_text = (optional_setting or "").strip()
    setting_instruction = (
        f"Optional setting supplied by user: {setting_text}. "
        "Treat this as mandatory and keep all prompts centered on it."
        if setting_text
        else "No setting supplied by user. Choose varied settings automatically."
    )

    return f"""
Generate exactly {prompt_count} image prompts from the enhanced adult-content tags below.

Enhanced tags:
{enhanced_explicit_tags}

{setting_instruction}

Output requirements:
- Return exactly {prompt_count} numbered prompts.
- Each prompt must be one paragraph.
- Each prompt must be substantially different.
- Preserve every user-supplied core concept from the tags.
- Maintain the same reference woman across the full batch.
- Preserve full natural D-cup breast proportions in every prompt.
- Preserve the exact same hair color and hairstyle from the reference image.
- Never make her red-haired, auburn-haired, ginger-haired, or any hair color different from the reference image.
- End every prompt with: {QUALITY_SUFFIX}

{IDENTITY_LOCK_RULES}

{TOPLESS_VISIBILITY_RULES}

{NUDITY_GROOMING_RULES}

{SETTING_RULES}

{PROMPT_DIVERSITY_RULES}

Do not include commentary before or after the prompts.
""".strip()


def get_grok_api_key() -> str:
    api_key = os.getenv("GROK_API_KEY")

    if not api_key:
        raise ValueError("Missing GROK_API_KEY in .env")

    return api_key


def enhance_explicit_tags(
    raw_explicit_tags: str,
    optional_setting: str | None = None,
) -> str:
    if not raw_explicit_tags or not raw_explicit_tags.strip():
        raise ValueError("Explicit Tags are required.")

    instruction = build_explicit_enhancer_instruction(
        raw_explicit_tags=raw_explicit_tags,
        optional_setting=optional_setting,
    )

    response = generate_prompts_with_grok(
        instruction,
        get_grok_api_key(),
    )

    if isinstance(response, list):
        return ", ".join(
            tag
            for item in response
            for tag in split_user_tags(str(item))
        )

    return str(response).strip()


def generate_explicit_prompts(
    enhanced_explicit_tags: str,
    prompt_count: int,
    optional_setting: str | None = None,
) -> list[str]:
    if not enhanced_explicit_tags or not enhanced_explicit_tags.strip():
        raise ValueError("Enhanced Explicit Tags are required.")

    instruction = build_explicit_prompt_instruction(
        enhanced_explicit_tags=enhanced_explicit_tags,
        prompt_count=prompt_count,
        optional_setting=optional_setting,
    )

    raw_response = generate_prompts_with_grok(
        instruction,
        get_grok_api_key(),
    )

    prompts = split_numbered_prompts(
        raw_response
    )

    force_topless_visibility = references_topless_content(
        enhanced_explicit_tags
    )

    force_nudity_grooming = references_nude_lower_body_content(
        enhanced_explicit_tags
    )

    normalized_prompts = []

    for prompt in prompts:
        if not prompt.strip():
            continue

        if force_topless_visibility:
            prompt = (
                f"{prompt.rstrip(' ,.')}, "
                f"{NIPPLE_VISIBILITY_PHRASE}"
            )
        else:
            prompt = normalize_topless_visibility(
                prompt
            )

        if force_nudity_grooming:
            prompt = (
                f"{prompt.rstrip(' ,.')}, "
                f"{NUDITY_GROOMING_PHRASE}"
            )
        else:
            prompt = normalize_nudity_grooming(
                prompt
            )

        normalized_prompts.append(
            normalize_prompt_suffix(prompt)
        )

    return normalized_prompts[:prompt_count]
