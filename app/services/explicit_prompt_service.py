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

Only include a dildo or toy if the user explicitly mentions "dildo", "toy", "insertion", "riding", or similar terms.
When a dildo is mentioned:
- Use a thick but realistically proportioned dildo (natural human size, not oversized)
- Do not force purple color unless the user specifically says "purple". Use any realistic color.
- Show believable natural vaginal insertion with realistic stretching and tight fit (avoid extreme gaping)

For general masturbation, touching, or spreading prompts (without mentioning a toy):
- Focus only on manual stimulation, fingers, rubbing, grinding, etc.
- Do NOT add any dildo or toy

General rules:
- Natural wetness and arousal: glistening fluids or creamy juices ONLY if the user specifically mentions "wet", "dripping", "creamy", "soaked", or similar
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
- same skin tone, with rich dark tan skin
- same body
- same body proportions
- same bust size
- full natural D-cup breast proportions
- full natural D-cup breast volume
- same feminine hourglass body
- same waist-to-hip proportions
- same overall identity from the reference image
Do not change her hair color.
"""

BODY_AND_FRAMING_LOCK_RULES = """
BODY, TAN, AND FRAMING CONTINUITY LOCK
Every generated prompt must explicitly preserve:
- rich dark tan skin
- same full natural D-cup bust
- same feminine hourglass body
- same waist-to-hip proportions
- same visible body size and recognizable body structure from the reference image

Skin tone rules:
- keep the tan natural, even, sun-kissed, and photorealistic
- preserve the same rich dark tan across face, chest, arms, waist, hips, and legs when visible
- do not make her pale, washed out, fair-skinned, or red-haired

Framing rules:
- favor tight medium, close-up, waist-up, upper-thigh, head-to-hips, or head-to-upper-thigh creator framing
- make her upper body and torso visually dominant in the composition
- keep the camera close enough that her full natural D-cup bust, hourglass waist, and dark tan skin are obvious
- keep her body large in frame, with the background supporting the scene rather than dominating it
- avoid wide bed shots, wide room shots, distant mattress compositions, scenery-dominant framing, or any framing where the bed/furniture is more visually important than her body
- avoid distant full-body compositions unless the user explicitly asks for a wide shot
- do not crop out the body cues needed to preserve her D-cup bust, hourglass shape, and tan skin
- do not use side/rear all-fours angles that hide or minimize the bust; if using side/rear body orientation, keep the chest/bust still visible and prominent
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
OPTIONAL SETTING / DIRECTION RULES
If the Optional Setting / Direction field is blank: 
- Treat each prompt as its own standalone scene, not one continuous photoshoot.
- Randomize realistic locations and micro-settings across the batch.
- Vary indoor, outdoor, luxury, casual, hotel, bathroom, shower, pool, balcony, kitchen, living room, studio, car, patio, vacation, nightlife, and private-home concepts when appropriate.
- Vary time of day, lighting style, mood, background textures, props, and camera angle.
- Avoid repeating the same room, bed, bathroom, tub, lighting setup, or visual theme across the batch.
- Do not make the batch look like one session in one location unless the user specifically supplies that setting.

If the Optional Setting / Direction field is supplied:
- Treat it as mandatory creative direction for the batch.
- Stay centered on any supplied setting, but still vary micro-locations, angles, and lighting within it.
- If it includes framing language such as full body, wide shot, environmental shot, mirror selfie, waist-up, close-up, medium shot, or upper-thigh framing, follow that framing direction even when it differs from the default close-framing preference.
- Still preserve her full natural D-cup bust, feminine hourglass body, same waist-to-hip proportions, rich dark tan skin, and recognizable body structure.
"""

PROMPT_DIVERSITY_RULES = """
PROMPT DIVERSITY RULES
For every batch of prompts:
- Create natural variety in environment even when the main action is the same.
- Vary poses, camera angles, framing, and facial expressions.
- Prefer chest-forward, upper-body-forward, tight medium crops over wide bedroom or wide bed compositions.
- Avoid repeatedly using wide beds, large mattresses, broad room descriptions, or distant all-fours shots that make the body continuity less visible.
- Generate the feeling of authentic, private, "in the moment" intimate scenes rather than a uniform photoshoot.
- Maintain the same woman and core body continuity, but randomize the scene concept unless the user supplies a fixed setting.
- Do not repeat the same location type more than twice in a batch of 10.
- Do not let "bed", "hotel room", or "bathroom" dominate the whole batch unless the user explicitly asks for that.
"""

EXPRESSION_PERSONALITY_RULES = """
FACIAL EXPRESSION AND PERSONALITY RULES
Every generated prompt must give her a visible, emotionally alive facial expression.
Do not default to blank, neutral, bored, monotone, mannequin-like, or emotionless expressions.
Across the batch, vary expressions naturally with a strong bias toward alluring, playful, teasing, warm, confident, and genuinely engaged energy.
Expressions must look candid and believable, not forced, fake, exaggerated, plastic, or overacted.
Favor subtle eye warmth, relaxed cheeks, small asymmetry, natural mouth shape, and in-the-moment micro-expressions over big posed smiles.

Use a varied expression palette such as:
- soft genuine seductive smile
- subtle playful smile with warmth in her eyes
- private teasing eye contact
- relaxed mischievous smirk
- flirty slight parted-lip smile
- confident warm gaze
- coy over-the-shoulder half-smile
- breathless pleasure expression with natural relaxed mouth
- soft moaning expression with visible emotion
- half-lidded seductive look with a hint of a smile
- quietly delighted, turned-on, in-the-moment expression

Use stronger expressions only occasionally, such as:
- candid laugh caught mid-moment
- excited smile that reaches her eyes
- playful grin that still looks natural

Avoid:
- forced smile
- fake grin
- overly toothy smile
- frozen pageant smile
- uncanny perfect smile
- exaggerated open-mouth acting
- dead eyes with a pasted-on smile

Most prompts should feel alive, warm, playful, alluring, or quietly excited rather than calm and expressionless.
Explicit prompts should lean more alluring, sexy, teasing, seductive, and visibly engaged while staying realistic.
Vary the expression in every prompt and do not repeat the same facial gesture across the batch.
"""
# ==================== HELPER FUNCTIONS ====================
TOPLESS_TERMS = ["topless", "bare breasts", "bare breast", "nude", "nudity", "naked", "upper body uncovered", "no upper-body clothing", "no bra", "no top"]
NUDE_LOWER_BODY_TERMS = ["nude", "nudity", "naked", "fully nude", "completely nude", "bare body", "lower body visible", "pubic area"]

NIPPLE_VISIBILITY_PHRASE = "topless with bare breasts and perky visible nipples unobstructed"
NUDITY_GROOMING_PHRASE = "no pubic hair, fully smooth pubic area"
BODY_CONTINUITY_PHRASE = (
    "rich dark tan skin, full natural D-cup bust, feminine hourglass body, "
    "same waist-to-hip proportions, tight medium head-to-upper-thigh creator framing, "
    "upper body and torso dominant, chest and bust clearly visible, body large in frame, "
    "no wide room or wide bed composition"
)

def normalize_prompt_suffix(prompt: str, suffix: str = QUALITY_SUFFIX) -> str:
    cleaned_prompt = (prompt or "").strip()
    if not cleaned_prompt:
        return ""
    cleaned_prompt = cleaned_prompt.rstrip(" ,.")
    normalized_suffix = suffix.strip().rstrip(" ,.")
    cleaned_prompt = re.sub(
        re.escape(normalized_suffix),
        "",
        cleaned_prompt,
        flags=re.IGNORECASE,
    ).rstrip(" ,.")
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

def normalize_body_continuity(prompt: str) -> str:
    cleaned_prompt = (prompt or "").strip()
    if not cleaned_prompt:
        return ""

    prompt_lower = cleaned_prompt.lower()
    required_fragments = [
        ("rich dark tan", "rich dark tan skin"),
        ("d-cup", "full natural D-cup bust"),
        ("hourglass", "feminine hourglass body"),
        ("waist-to-hip", "same waist-to-hip proportions"),
        ("tight medium", "tight medium head-to-upper-thigh creator framing"),
        ("upper body", "upper body and torso dominant"),
        ("body large in frame", "body large in frame"),
        ("wide room", "no wide room or wide bed composition"),
    ]

    missing_fragments = [
        fragment
        for term, fragment in required_fragments
        if term not in prompt_lower
    ]

    if not missing_fragments:
        return cleaned_prompt

    cleaned_prompt = cleaned_prompt.rstrip(" ,.")
    return f"{cleaned_prompt}, {', '.join(missing_fragments)}"

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
        f"The user supplied this optional setting/framing direction: {setting_text}. "
        "Preserve it as a mandatory creative direction."
        if setting_text
        else (
            "No setting was supplied. Do not choose one fixed setting. "
            "Create a varied setting pool with multiple distinct standalone scene ideas."
        )
    )
    return f"""
You are an expert at creating realistic and intimate NSFW image prompts for Seedream 4.5.
Raw user tags:
{raw_explicit_tags}
{setting_instruction}
{USER_TAG_PRESERVATION_RULES}
{IDENTITY_LOCK_RULES}
{BODY_AND_FRAMING_LOCK_RULES}
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
        f"Optional setting/framing direction supplied by user: {setting_text}. "
        "Treat this as mandatory. If it includes camera distance or framing instructions, follow them."
        if setting_text
        else (
            "No setting supplied by user. Treat this as a random mixed batch: "
            "each prompt should use a distinct standalone setting, lighting setup, "
            "and scene concept while keeping the camera close and the background secondary."
        )
    )

    return f"""
You are an expert at creating highly realistic, intimate NSFW image prompts for Seedream 4.5.

Enhanced tags:
{enhanced_explicit_tags}

{setting_instruction}

{IDENTITY_LOCK_RULES}
{BODY_AND_FRAMING_LOCK_RULES}
{EXPLICIT_ACTION_RULES}
{TOPLESS_VISIBILITY_RULES}
{NUDITY_GROOMING_RULES}
{SETTING_RULES}
{PROMPT_DIVERSITY_RULES}
{EXPRESSION_PERSONALITY_RULES}

Output requirements:
- Generate exactly {prompt_count} numbered prompts (1., 2., 3. etc.)
- Each prompt must be one detailed, flowing paragraph
- Prioritize extreme photorealism and natural body proportions at all times
- Every prompt must explicitly include rich dark tan skin
- Every prompt must explicitly include full natural D-cup bust
- Every prompt must explicitly include feminine hourglass body
- Every prompt must explicitly include same waist-to-hip proportions
- Every prompt must use tight medium, close-up, waist-up, head-to-hips, or head-to-upper-thigh creator framing by default, unless the user specifically asks for a different framing style in the Optional Setting / Direction field or explicit tags
- Every prompt must make her upper body and torso visually dominant
- Every prompt must keep her full natural D-cup bust visibly prominent and unobstructed when the upper body is visible
- Every prompt must keep her body large in frame
- Every prompt must avoid wide room shots, wide bed shots, distant mattress compositions, and background-dominant framing
- Create the feeling of private, "in the moment" intimate photos taken just for the viewer
- Use natural, believable lighting in every prompt
- Feature realistic dildo insertion and arousal when relevant
- Maintain natural anatomy and sensual expressions
- Every prompt must include a clearly described natural facial expression with alluring, teasing, warm, playful, seductive, quietly excited, or genuinely engaged energy
- Do not use blank, neutral, bored, monotone, mannequin-like, emotionless, forced-smile, fake-grin, or overacted facial expressions
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
            prompt = (
                normalize_topless_visibility(prompt)
                if references_topless_content(prompt)
                else f"{prompt.rstrip(' ,.')}, {NIPPLE_VISIBILITY_PHRASE}"
            )
        else:
            prompt = normalize_topless_visibility(prompt)

        if force_nudity_grooming:
            prompt = (
                normalize_nudity_grooming(prompt)
                if references_nude_lower_body_content(prompt)
                else f"{prompt.rstrip(' ,.')}, {NUDITY_GROOMING_PHRASE}"
            )
        else:
            prompt = normalize_nudity_grooming(prompt)

        prompt = normalize_body_continuity(prompt)

        normalized_prompts.append(normalize_prompt_suffix(prompt))

    return normalized_prompts[:prompt_count]
