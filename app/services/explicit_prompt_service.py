import os
import re
from dotenv import load_dotenv
from main import generate_prompts_with_grok

load_dotenv()

# ==================== QUALITY & REALISM ====================
QUALITY_SUFFIX = (
    "photorealistic, ultra-realistic 8k raw photo, natural skin texture with visible pores, "
    "realistic anatomy and proportions, natural lighting with subtle shadows, "
    "candid intimate atmosphere, film grain, natural body, masterpiece, best quality"
)

# ==================== REALISTIC & INTIMATE EXPLICIT RULES ====================
EXPLICIT_ACTION_RULES = """
EXPLICIT ACTION RULES - REALISTIC & INTIMATE STYLE

When the user mentions dildo, toy, insertion, masturbating, riding, spreading, or similar:
- Use a thick but realistically proportioned purple translucent dildo
- Show believable natural vaginal insertion with realistic stretching and tight fit (avoid extreme gaping)
- Natural wetness and arousal: glistening fluids or creamy juices ONLY if the user specifically asks for "wet", "dripping", "creamy", "soaked", or similar
- Natural anatomy: detailed but realistic pussy, swollen clit, natural labia

VARYING EXPRESSIONS:
- Vary facial expressions naturally: soft moaning with eyes half-closed, intense pleasure with eyes rolled back, biting lip in ecstasy, flushed cheeks with open mouth, genuine orgasm face, seductive eye contact with the viewer, head tilted back in bliss, etc.
- Mix subtle and strong expressions across the batch for more "in the moment" feel

- Keep poses natural, sensual and intimate — like private photos taken just for the viewer
- Focus on realistic, seductive sexuality rather than exaggerated porn style
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
If the Optional Setting field is blank: choose varied natural settings automatically.
If supplied: keep all prompts centered on that setting.
"""

PROMPT_DIVERSITY_RULES = """
PROMPT DIVERSITY RULES
Vary poses, camera angles, framing, and lighting while maintaining realistic proportions.
Include a natural mix of:
- Wide and medium shots
- Tight intimate close-ups
- Candid "in the moment" angles as if taken privately
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
You are an expert at creating realistic and intimate NSFW image prompts for Seedream 4.5.
Raw user tags:
{raw_explicit_tags}
{setting_instruction}
{USER_TAG_PRESERVATION_RULES}
{IDENTITY_LOCK_RULES}
{EXPLICIT_ACTION_RULES}
{TOPLESS_VISIBILITY_RULES}
{NUDITY_GROOMING_RULES}
Return ONLY a rich comma-separated tag list. No explanations. No numbering.
Make it detailed but realistic.
""".strip()


def build_explicit_prompt_instruction(
    enhanced_explicit_tags: str,
    prompt_count: int,
    optional_setting: str | None = None,
) -> str:
    setting_text = (optional_setting or "").strip()
    setting_instruction = (
        f"Optional setting supplied by user: {setting_text}. "
        "Treat this as mandatory and keep all prompts centered on that setting."
        if setting_text
        else "No setting supplied by user. Default to luxurious modern bedroom with natural lighting."
    )

    return f"""
You are an expert at creating highly realistic, intimate NSFW image prompts for Seedream 4.5.

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
- Prioritize extreme photorealism and natural body proportions at all times
- Create the feeling of private, "in the moment" intimate photos taken just for the viewer
- Use natural, believable lighting in every prompt
- Feature realistic dildo insertion and arousal when relevant
- Maintain natural anatomy and sensual expressions
- End every single prompt with: , {QUALITY_SUFFIX}

Keep the tone sensual and realistic. Avoid cartoonish exaggeration or overly vulgar language.
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