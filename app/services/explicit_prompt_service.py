import os
import re
from dotenv import load_dotenv
from main import generate_prompts_with_grok

load_dotenv()

QUALITY_SUFFIX = "soft warm bedroom lighting, messy bedsheets, photorealistic, ultra-detailed skin texture, realistic anatomy, glistening fluids, 8k, masterpiece, best quality"

# ==================== EXPLICITNESS LEVELS ====================
EXPLICITNESS_LEVELS = {
    1: "mild sensual nudity, tasteful and artistic",
    3: "moderately explicit, detailed but elegant",
    5: "strongly explicit, detailed anatomy and arousal",
    7: "hardcore explicit, graphic sexual action",
    10: "maximum vulgar, extremely dirty hardcore porn style with no limits"
}

# ==================== STRONGER EXPLICIT RULES ====================
EXPLICIT_ACTION_RULES = """
EXTREME EXPLICIT ACTION RULES - HARDCORE PORN STYLE
When the user mentions dildo, toy, masturbating, insertion, riding, spreading, pussy, fucking herself, or similar:
- Be extremely graphic, vulgar, and pornographic
- Use direct sexual language: deep vaginal insertion, thick purple translucent dildo stretching her pussy, riding the dildo vigorously, thrusting, pumping, creaming on the toy
- Describe wetness and fluids in detail: glistening arousal fluids, dripping wet pussy, creamy juices coating the dildo, soaked sheets
- Show explicit anatomy: spread labia, swollen clit, stretched pussy lips wrapped tightly around the thick dildo, visible inner pink folds
- Strong arousal expressions: moaning in ecstasy, eyes rolled back, biting lip, heavy breathing, face flushed with lust
- Vary explicit poses: legs spread wide open, squatting and riding, on all fours reaching back to fuck herself, lying on back with legs in the air, etc.

CLOSE FRAMING EMPHASIS:
- Frequently include close-up and tight framing on the explicit action (pussy, dildo insertion, breasts, face + body)
- Use terms like: extreme close-up, tight close-up on pussy, detailed insertion shot, macro view of stretched pussy, etc.
"""

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
"""

TOPLESS_VISIBILITY_RULES = """
TOPLESS / NUDE VISIBILITY RULES
If topless, bare breasts, nude, naked, or upper body uncovered content is requested:
- every topless prompt must clearly preserve bare breasts
- nipples must be visible
- nipples must be perky and visible
- do not hide nipples with hair, arms, hands, furniture, sheets, pillows, or props
- preserve full natural D-cup breast proportions and volume
"""

NUDITY_GROOMING_RULES = """
NUDITY GROOMING RULES
If nude, naked, fully nude, lower body visible, or pubic area visible content is requested:
- no pubic hair
- keep the pubic area fully smooth
- do not add landing strip or stubble
"""

USER_TAG_PRESERVATION_RULES = """
USER TAG PRESERVATION RULES
All user-supplied Explicit Tags are mandatory anchor concepts.
The AI may expand and enrich them but must not ignore or replace them.
"""

SETTING_RULES = """
OPTIONAL SETTING RULES
If the Optional Setting field is blank: choose varied settings automatically.
If supplied: keep all prompts centered on that setting.
"""

PROMPT_DIVERSITY_RULES = """
PROMPT DIVERSITY RULES
Vary poses, camera angles, framing, and micro-locations.
Include a mix of:
- Wide / full body shots
- Medium shots
- Tight close-ups and extreme close framing on sexual action (especially pussy and dildo)
Maintain the same woman and core explicit action.
"""

# ==================== HELPER FUNCTIONS ====================
TOPLESS_TERMS = ["topless", "bare breasts", "bare breast", "nude", "nudity", "naked", "upper body uncovered", "no upper-body clothing", "no bra", "no top"]
NUDE_LOWER_BODY_TERMS = ["nude", "nudity", "naked", "fully nude", "completely nude", "bare body", "lower body visible", "pubic area"]

NIPPLE_VISIBILITY_PHRASE = "topless with bare breasts and perky visible nipples unobstructed"
NUDITY_GROOMING_PHRASE = "no pubic hair, fully smooth pubic area"

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
    return any(term in text_lower for term in TOPLESS_TERMS)

def references_nude_lower_body_content(text: str) -> bool:
    text_lower = (text or "").lower()
    return any(term in text_lower for term in NUDE_LOWER_BODY_TERMS)

def normalize_topless_visibility(prompt: str) -> str:
    cleaned_prompt = (prompt or "").strip()
    if not cleaned_prompt or not references_topless_content(cleaned_prompt):
        return cleaned_prompt
    if "visible nipple" in cleaned_prompt.lower():
        return cleaned_prompt
    cleaned_prompt = cleaned_prompt.rstrip(" ,.")
    return f"{cleaned_prompt}, {NIPPLE_VISIBILITY_PHRASE}"

def normalize_nudity_grooming(prompt: str) -> str:
    cleaned_prompt = (prompt or "").strip()
    if not cleaned_prompt or not references_nude_lower_body_content(cleaned_prompt):
        return cleaned_prompt
    if "no pubic hair" in cleaned_prompt.lower():
        return cleaned_prompt
    cleaned_prompt = cleaned_prompt.rstrip(" ,.")
    return f"{cleaned_prompt}, {NUDITY_GROOMING_PHRASE}"

def split_user_tags(raw_tags: str) -> list[str]:
    if not raw_tags:
        return []
    return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]

def split_numbered_prompts(raw_text) -> list[str]:
    if not raw_text:
        return []
    if isinstance(raw_text, list):
        return [str(item).strip() for item in raw_text if str(item).strip()]
    parts = re.split(r"\n\s*\d+[\.\)]\s+", "\n" + str(raw_text).strip())
    return [part.strip() for part in parts if part.strip()]

# ==================== INSTRUCTIONS ====================
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
You are an expert at creating MAXIMUM explicit, hardcore pornographic image prompts for Seedream 4.5 / WAN models.
Raw user tags:
{raw_explicit_tags}
{setting_instruction}
{USER_TAG_PRESERVATION_RULES}
{IDENTITY_LOCK_RULES}
{EXPLICIT_ACTION_RULES}
{TOPLESS_VISIBILITY_RULES}
{NUDITY_GROOMING_RULES}
Return ONLY a rich comma-separated tag list. No explanations. No numbering.
Make it as graphically sexual and detailed as possible.
""".strip()


def build_explicit_prompt_instruction(
    enhanced_explicit_tags: str,
    prompt_count: int,
    optional_setting: str | None = None,
    explicit_level: int = 8,   # Default = Hardcore
) -> str:
    setting_text = (optional_setting or "").strip()
    setting_instruction = (
        f"Optional setting supplied by user: {setting_text}. "
        "Treat this as mandatory and keep all prompts centered on it."
        if setting_text
        else "No setting supplied by user. Default to luxurious bedroom."
    )

    intensity = EXPLICITNESS_LEVELS.get(explicit_level, EXPLICITNESS_LEVELS[10])

    return f"""
You are creating {intensity} image prompts for Seedream 4.5 / WAN 2.7.

Enhanced tags:
{enhanced_explicit_tags}

{setting_instruction}

{IDENTITY_LOCK_RULES}
{EXPLICIT_ACTION_RULES}
{TOPLESS_VISIBILITY_RULES}
{NUDITY_GROOMING_RULES}
{PROMPT_DIVERSITY_RULES}

Output requirements:
- Generate exactly {prompt_count} numbered prompts (1., 2., 3. etc.)
- Each prompt must be one detailed, flowing paragraph
- Heavily feature the dildo in action when relevant
- Include close-up and macro shots of the explicit action
- Strong arousal expressions
- Vary poses and camera angles but keep the same woman and core action
- End every single prompt with: , {QUALITY_SUFFIX}

Go full {intensity}. Do not be elegant or soft.
No commentary.
""".strip()


# ==================== PUBLIC FUNCTIONS ====================
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
    response = generate_prompts_with_grok(instruction, get_grok_api_key())
    if isinstance(response, list):
        return ", ".join(
            tag for item in response for tag in split_user_tags(str(item))
        )
    return str(response).strip()


def generate_explicit_prompts(
    enhanced_explicit_tags: str,
    prompt_count: int,
    optional_setting: str | None = None,
    explicit_level: int = 8,      # New parameter for slider
) -> list[str]:
    if not enhanced_explicit_tags or not enhanced_explicit_tags.strip():
        raise ValueError("Enhanced Explicit Tags are required.")

    instruction = build_explicit_prompt_instruction(
        enhanced_explicit_tags=enhanced_explicit_tags,
        prompt_count=prompt_count,
        optional_setting=optional_setting,
        explicit_level=explicit_level,
    )

    raw_response = generate_prompts_with_grok(
        instruction,
        get_grok_api_key(),
    )
    prompts = split_numbered_prompts(raw_response)

    force_topless_visibility = references_topless_content(enhanced_explicit_tags)
    force_nudity_grooming = references_nude_lower_body_content(enhanced_explicit_tags)

    normalized_prompts = []
    for prompt in prompts:
        if not prompt.strip():
            continue
        if force_topless_visibility:
            prompt = f"{prompt.rstrip(' ,.')}, {NIPPLE_VISIBILITY_PHRASE}"
        else:
            prompt = normalize_topless_visibility(prompt)

        if force_nudity_grooming:
            prompt = f"{prompt.rstrip(' ,.')}, {NUDITY_GROOMING_PHRASE}"
        else:
            prompt = normalize_nudity_grooming(prompt)

        normalized_prompts.append(normalize_prompt_suffix(prompt))

    return normalized_prompts[:prompt_count]