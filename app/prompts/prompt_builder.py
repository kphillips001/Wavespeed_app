from app.prompts.shot_types import SHOT_TYPES

def build_shot_type_context():
    formatted_shot_types = "\n".join(f"- {shot_type}" for shot_type in SHOT_TYPES)

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
Photorealistic AI influencer glamour photography.

The images should feel:
- premium
- realistic
- confident
- attractive
- visually compelling
- creator-content ready
- social-media polished

The final image style should feel like:
- high-end influencer photography
- luxury social media glamour
- realistic camera photography
- flattering lighting
- confident feminine posing
- premium creator content
- scroll-stopping visual appeal

User tags/request:
{user_request}

Platform target:
{platform_mode}

Spice level:
{spice_level}
"""

    dynamic_tag_rules = """
DYNAMIC TAG INTERPRETATION:
The user may enter ANY tags, locations, outfits, roles, objects, moods, aesthetics, or scene ideas.

Examples of possible user inputs:
- airplane, airport, stewardess outfit
- desert, bikini, sunset
- lake, tight shorts
- luxury apartment, loungewear
- nightclub, mini dress
- boat, crop-top, summer
- country outdoors, denim shorts
- gym, leggings, mirror selfie

IMPORTANT:
- Do NOT rely on preset or hardcoded tags.
- Do NOT limit creativity to examples listed here.
- Always preserve the user's exact concept.
- Treat the user's tags as creative direction for a realistic glamour photoshoot.
- Dynamically infer realistic settings, poses, wardrobe styling, lighting, camera angles, framing, and scene details from the user's tags.
- Make the output feel intentional, natural, and visually believable.
- If the user enters an object or location, creatively turn it into a realistic influencer-style scene.
- If the user enters an outfit or role, style it in a flattering, polished, adult glamour way.
"""

    if generation_mode["key"] == "variety_batch":
        mode_rules = """
GENERATION MODE:
VARIETY BATCH MODE

PURPOSE:
Create a varied batch of images from the user's tags.

RULES:
- Every prompt should feel different.
- Vary setting, pose, lighting, camera angle, framing, expression, and mood.
- Keep the user's requested outfit/tag direction present in every prompt.
- If the user gives multiple outfit/location/vibe tags, combine or rotate them naturally.
- Do NOT make the images feel like the same photoshoot.
- Make each image useful as a separate social, Telegram, or Fanvue teaser asset.
- Use Grok's creativity to infer new but relevant scene details from the user's tags.
- Avoid repeating nearly identical poses or framing.

VARIATION REQUIREMENTS:
Across the full batch, vary:
- environment details
- pose category
- body orientation
- camera distance
- camera height
- lighting mood
- facial expression
- composition style
- candid vs posed feel
"""

    elif generation_mode["key"] == "photoshoot_set":
        mode_rules = """
GENERATION MODE:
PHOTOSHOOT SET MODE

PURPOSE:
Create a cohesive photoshoot set.

RULES:
- All prompts must keep the SAME outfit direction.
- All prompts must keep the SAME primary setting/location.
- All prompts must keep the SAME lighting style and vibe.
- ONLY vary pose, camera angle, framing, expression, and body orientation.
- The set should feel like one real photoshoot session.
- Do NOT switch locations.
- Do NOT switch outfits.
- Do NOT create unrelated scenes.
- Use the user's tags to dynamically infer a believable photoshoot location and styling.
- Avoid duplicate-looking shots.

PHOTOSHOOT VARIATION REQUIREMENTS:
Across the set, vary:
- standing / seated / leaning / walking / close-up style
- full-body / three-quarter / waist-up framing
- direct eye contact / looking away / over-the-shoulder
- candid movement / polished pose
- camera height and angle
"""

    elif generation_mode["key"] == "story_sequence":
        mode_rules = """
GENERATION MODE:
STORY SEQUENCE MODE

PURPOSE:
Create a connected visual sequence that feels like a mini photoshoot story.

RULES:
- All prompts should feel connected.
- Keep the same woman, same general outfit direction, and same overall vibe.
- The images should progress naturally like moments from one scene.
- Each image should feel like a different beat in the same story.
- Do NOT create random unrelated scenes.
- Do NOT jump wildly between locations.
- Keep continuity in setting, lighting, outfit, and mood.
- Each image should still work as a strong standalone image.
- Use the user's tags to dynamically infer the story setting, sequence flow, and visual progression.

STORY STRUCTURE:
Create a natural progression such as:
- opening / arrival moment
- establishing shot
- first confident pose
- closer candid moment
- more polished glamour pose
- playful or teasing moment
- final hero shot

IMPORTANT:
The story structure must adapt to the user's tags.
For example, airplane/airport/stewardess outfit should feel different from beach/bikini/sunset.
Do NOT use a beach-style sequence unless the user asked for beach.
"""

    else:
        mode_rules = """
GENERATION MODE:
DEFAULT GLAMOUR MODE

Create strong, varied, photorealistic glamour prompts using the user's tags dynamically.
"""

    if spice_level in {"Social Safe", "Glamour"}:
        spice_rules = """
SPICE RULES:
- Keep everything social-media safe.
- No nudity.
- No explicit sexual content.
- Use fashionable, flattering, suggestive-but-safe styling.
- Focus on glamour, beauty, confidence, realism, and tasteful attraction.
"""

    elif spice_level in {"Spicy Glamour", "Fanvue Tease"}:
        spice_rules = """
SPICE RULES:
- More seductive and teasing than normal social content.
- Still avoid explicit sex acts.
- Use confident, premium creator-content energy.
- Emphasize glamour, pose, lighting, and outfit styling.
- Keep the wording classy and model-friendly.
- Lean into stronger tease, but preserve realism and taste.
"""

    else:
        spice_rules = """
SPICE RULES:
- Adult platform mode.
- Keep the subject clearly adult.
- Avoid minors, teen language, school themes, or anything youthful.
- Avoid explicit sex acts in the prompt text.
- Focus on adult glamour, intimacy, premium creator content, and platform-appropriate seduction.
"""

    return f"""
I need a list of {prompt_count} high-quality image-to-image editing prompts.

These prompts will always be used with the SAME reference image,
so every prompt MUST preserve the exact same woman.

{universal_style}

{dynamic_tag_rules}

{shot_type_context}

{mode_rules}

{spice_rules}

STRICT IDENTITY RULES:
- SAME woman always
- SAME face
- SAME hair
- SAME body
- Preserve identity from the reference image

PROMPT STRUCTURE:
Each prompt MUST start with:
"The exact same woman from the reference image with identical face, hair, and body,"

QUALITY RULES:
- Photorealistic
- Natural realistic skin texture
- Real camera photography
- Strong lighting
- Strong setting
- Strong pose
- Premium glamour aesthetic
- No other people
- No cartoon/anime style
- No distorted hands
- No distorted face
- No extra limbs
- No childish styling
- No school themes
- No underage implication

OUTPUT RULES:
- One line per prompt
- No numbering
- No explanations
- No emojis
- Return ONLY the list of prompts

PROMPT STYLE:
- Keep prompts visually cinematic and concise
- Avoid overly long run-on sentences
- Focus on visual composition and photography direction
- Prioritize strong subject, outfit, pose, setting, and lighting
- Avoid repetitive filler wording
- Keep prompts clean and efficient for image-generation models
- Use natural glamour photography language
- Every prompt should feel like a premium influencer photoshoot concept
"""