from app.prompts.shot_types import SHOT_TYPES


def build_shot_type_context():
    formatted_shot_types = "\n".join(
        f"- {shot_type}"
        for shot_type in SHOT_TYPES
    )

    return f"""
SHOT INTELLIGENCE:
Use a natural mix of universal photography shot types to create visual variety.

Suggested shot types:
{formatted_shot_types}

IMPORTANT:
- These are not hard rules.
- Do not repeat the same shot type too often.
- Adapt shot types dynamically to the user's tags.
- Use them to improve pose variety, framing, camera distance, and composition.
"""


def build_chatgpt_prompt(
    prompt_count,
    user_request,
    generation_mode,
    platform_mode,
    spice_level,
):

    shot_type_context = build_shot_type_context()

    universal_style = f"""
Photorealistic AI influencer photography.

The images should feel:
- premium
- realistic
- visually compelling
- creator-content ready
- social-media polished
- intentional
- natural
- high quality

User tags/request:
{user_request}

Creative mode:
{spice_level}
"""

    creative_director_rules = f"""
CREATIVE DIRECTOR MODE:

The user is NOT writing prompts.
The user is only providing creative signals.

Your job is to become an AI Creative Director.

IMPORTANT:
Minimal input should produce MAXIMUM intelligent creativity.

Creative Director behavior:
- Preserve roughly 70-80% of the user's idea and aesthetic
- Add roughly 20-30% intelligent expansion
- Invent realistic scene details
- Invent realistic environments
- Invent camera framing
- Invent lighting
- Invent mood
- Invent pose ideas
- Invent composition
- Invent visual storytelling
- Invent creator-style scenarios

Treat user tags as CREATIVE SIGNALS
rather than rigid repeated objects.

Examples:

cowgirl hat, desert

does NOT require:
- identical hat usage
- identical outfits
- identical styling
- identical scene setup

Instead intelligently preserve:
- overall aesthetic
- creator vibe
- visual theme
- emotional feel
- core user intent

while varying:
- styling
- accessories
- activities
- environment details
- pose concepts
- camera framing
- visual hooks
- content scenarios

Think like:
- photographer
- influencer content producer
- creative director
- visual marketing director
- creator strategist

Do NOT simply repeat keywords.
Do NOT create duplicate ideas.

The batch should feel like:
10 different posts from the same creator brand.

User creative tags:
{user_request}
"""

    if generation_mode["key"] == "variety_batch":

        mode_rules = """
CREATIVE FLOW:
VARIETY MODE

PURPOSE:
Generate multiple different content ideas from the user's tags.

This is discovery mode.

The images should NOT feel like one continuous photoshoot.
The images should NOT require continuity.
The images should feel like different strong options based on the same user idea.

RULES:
- Create completely different image ideas
- Keep the user's core tags/intention present
- Treat tags as creative signals, not rigid repeated objects
- Vary setting, pose, outfit styling, lighting, camera angle, framing, activity, and mood
- Use creative expansion freely when it fits the user's idea
- Avoid duplicate-looking prompts
- Each image should work as its own standalone content option
- Prioritize variety over continuity

Example:
If the user enters "bikini, beach", do NOT make 10 versions of the same beach pose.
Create varied bikini/beach-inspired ideas such as selfie, shoreline, poolside, beach chair, sunset, water edge, close portrait, candid walking, hero shot, lifestyle shot.
"""

    elif generation_mode["key"] == "photoshoot_set":

        mode_rules = """
CREATIVE FLOW:
PHOTOSHOOT MODE

PURPOSE:
Continue one selected image as the same photoshoot.

This is expansion mode.

LOCK:
- same outfit
- same setting
- same environment
- same lighting
- same vibe
- same camera style
- same creative concept

VARY ONLY:
- pose
- camera angle
- framing
- crop
- expression
- perspective

Do NOT change the outfit.
Do NOT change the setting.
Do NOT create unrelated scenes.
"""

    elif generation_mode["key"] == "story_sequence":

        mode_rules = """
CREATIVE FLOW:
STORY MODE

PURPOSE:
Turn one selected image into a visual timeline.

This is progression mode.

RULES:
- Keep continuity
- Keep same subject
- Keep same outfit direction
- Keep same environment
- Keep same overall vibe
- Create a sequence of connected moments
- Each image should feel like the next beat in the same story

Example:
For a beach image, create a progression such as arriving, walking toward water, standing at shoreline, sitting on towel, entering water, candid close-up, sunset ending.
"""

    else:

        mode_rules = """
CREATIVE FLOW:
DEFAULT VARIETY MODE

Create varied, photorealistic content ideas from the user's tags.
"""

    if spice_level == "Social Safe":

        spice_rules = """
CREATIVE MODE:
SOCIAL SAFE

PRIMARY GOAL:
Lifestyle appeal.

The images should still feel attractive and visually engaging,
but the tone should be more lifestyle, fashion, travel, beauty, and social-media safe.

CONSTANT PRIORITIES:
- lifestyle content
- beauty
- confidence
- realism
- natural attractiveness
- fashionable styling
- friendly energy
- polished social-media appeal
- tasteful sex appeal
- safe creator-content aesthetics

VARIABLE ELEMENTS:
- outfit styling
- activity
- environment
- mood
- pose
- camera angle
- framing
- lighting
- expression

IMPORTANT:
- Keep everything social-media safe
- No nudity
- No explicit sexual content
- Avoid overly sexual wording
- Avoid adult-platform language
- Avoid excessive body emphasis
- Use attractiveness through lifestyle, confidence, fashion, lighting, and composition
- The image should feel like it could fit Instagram, X, or mainstream social content
"""

    elif spice_level == "Spicy":

        spice_rules = """
CREATIVE MODE:
SPICY

PRIMARY GOAL:
Male audience visual appeal.

Maintain strong visual engagement across ALL generated images.

The images should feel attention-grabbing,
confident,
playful,
creator-oriented,
and optimized for social engagement.

DO NOT directly use words like:
- sexy
- seductive
- erotic
- huge breasts
- provocative

Instead create attraction indirectly through visual design.

CONSTANT PRIORITIES:
- premium creator aesthetics
- confidence
- visual hooks
- playful energy
- stronger composition
- stronger engagement potential
- polished influencer style
- realistic photography
- attractive styling

CAMERA PRIORITIES:
- low-angle framing
- slight over-shoulder framing
- selfie framing
- close framing
- body-leading composition
- candid smartphone perspective
- dynamic movement framing
- portrait variation
- environmental framing

STYLING PRIORITIES:
- fitted clothing
- flattering silhouettes
- shorter cuts when appropriate
- waist emphasis
- leg emphasis
- shape emphasis
- stylish creator wardrobe
- skin exposure when naturally appropriate

ENERGY PRIORITIES:
- playful smile
- confident expression
- direct eye contact
- teasing expression
- casual confident body language
- hair movement
- natural candid energy

LIGHTING PRIORITIES:
- golden rim light
- warm skin glow
- sunset contrast
- soft highlights
- warm cinematic lighting

VARIABLE ELEMENTS:
- environment
- outfit styling
- pose
- framing
- expression
- activity
- camera angle
- mood
- accessories
- creator scenario

VARIETY RULES:
Across the batch vary:
- camera perspective
- framing
- pose
- movement
- expression
- styling
- activity
- environment details
- creator scenarios
- visual hooks

Creator scenario examples:
- candid selfie
- phone-content moment
- adjusting hair
- adjusting outfit
- hat adjustment moment
- looking back while walking
- over-the-shoulder glance
- seated casual pose
- leaning pose
- travel-content moment
- movement shot
- close portrait
- lifestyle interaction
- candid laugh
- mirror-style composition
- fixing sunglasses
- relaxed vacation moment

VISUAL HOOK RULES:
Use attraction through natural creator-content psychology:

- body-leading composition
- low-angle framing
- natural posture curves
- confident eye contact
- movement in clothing
- wind interaction
- hair movement
- subtle skin visibility where naturally appropriate
- warm skin glow
- layered outfit styling
- framing depth
- perspective variation
- smartphone-content feel
- candid creator energy
- natural asymmetry
- movement and action
- environmental depth
- lifestyle realism
- natural storytelling
- creator-content energy

Do NOT repeatedly generate:

- same object placement
- same accessory placement
- same outfit layout
- same pose
- same angle
- same composition
- same camera distance
- same framing
- same body orientation
- same creator scenario
- same activity
- same environmental interaction
- same clothing combinations
- same hairstyle behavior
- same emotional expression
- same visual hook

Keep:

- same creator identity
- same overall vibe
- same user intent
- same broad aesthetic

Treat user tags as CREATIVE SIGNALS rather than rigid wardrobe requirements.

Example:

cowgirl hat, desert

does NOT mean:

- same shirt + same shorts + same hat repeatedly
- same hat position repeatedly
- same desert pose repeatedly
- same standing pose repeatedly
- same camera perspective repeatedly

Instead preserve the theme while allowing intelligent variation in:

- styling
- accessories
- outfit combinations
- pose concepts
- creator scenarios
- environmental details
- composition
- visual hooks
- activities
- camera behavior
- content situations

Outfit combinations may intelligently vary using:

- fitted tanks
- tied shirts
- oversized shirts
- denim jackets
- layered western pieces
- lightweight jackets
- fitted casualwear
- creator lifestyle outfits
- athletic-inspired looks
- travel-inspired looks
- seasonal styling
- beachwear where appropriate
- modern creator fashion
- casual social-media styling

Activity variation may intelligently include:

- walking
- sitting
- leaning
- kneeling
- adjusting clothing
- fixing hair
- adjusting accessories
- looking back
- interacting with environment
- taking selfie
- holding phone
- candid moments
- moving through scene
- natural action moments

The batch should feel like:

10 separate social posts from the same creator brand.

Examples:

cowgirl hat, desert

- walking ridgeline at sunset
- candid selfie near old truck
- leaning on weathered fence
- seated on sandstone ledge
- over-the-shoulder wind shot
- standing near dry riverbed
- adjusting hat in moving wind
- kneeling near cactus scene
- close-up beauty framing
- low-angle hero composition

No nudity.
No explicit sexual acts.
No underage appearance.
Keep realistic photography.
"""

    else:

        spice_rules = """
CREATIVE MODE:
EXPLICIT

Explicit mode is coming later.
For now, behave like Spicy mode.
"""

    return f"""
I need a list of {prompt_count} high-quality image-to-image prompts.

These prompts always use the SAME reference image.

Every prompt MUST preserve:
- same woman
- same face
- same hair
- same body
- same identity from the reference image

{universal_style}

{creative_director_rules}

{shot_type_context}

{mode_rules}

{spice_rules}

PROMPT STRUCTURE:
Each prompt MUST start with:
"The exact same woman from the reference image with identical face, hair, and body,"

QUALITY RULES:
- Photorealistic
- Real camera photography
- Natural realistic skin texture
- Strong lighting
- Strong composition
- Strong pose
- Premium creator aesthetic
- No other people
- No cartoon/anime style
- No distorted hands
- No distorted face
- No extra limbs
- No childish styling
- No school themes
- No underage implication

OUTPUT RULES:
- One prompt per line
- No numbering
- No explanations
- No emojis
- Return ONLY prompts
"""