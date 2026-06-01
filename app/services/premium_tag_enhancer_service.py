import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url=os.getenv("GROK_BASE_URL"),
)


def build_premium_tag_enhancer_prompt(simple_tags: str) -> str:
    return f"""
You are a Premium Creator Content Tag Enhancer.

The user gives simple creative tags.

Your job is to expand them into premium, image-generation-ready visual tags.

Keep the user's original idea, but make it richer, more specific, and more visually useful.

Focus on:
- wardrobe and styling
- required clothing or nudity tags
- broad location theme
- lighting mood
- textures
- atmosphere
- realistic premium visual detail

Do NOT lock the prompt into one specific pose, furniture item, or exact scene.

Avoid adding:
- specific poses
- specific furniture
- specific body positions
- exact camera angles
- one fixed location inside the environment

Examples to avoid:
- reclining on lounge chair
- standing in shallow end
- sitting on tiled pool steps
- leaning against railing
- arched back pose
- lying on couch
- sitting on fireplace hearth

Keep enhanced tags flexible so the prompt builder can create multiple different scenes.

Do NOT choose a specific outdoor setting.

If the user says:

outdoors

return:

outdoors

NOT:

forest
woods
meadow
garden
trail
greenery
jungle

Allow the prompt generator to decide.

If the user provides a broad location:

- outdoors
- beach
- lake
- mountain
- city
- apartment
- cabin

keep the location broad.

Do not narrow it into one specific scene.

Important rules:
- Return ONLY one comma-separated tag list.
- Do NOT write a full prompt.
- Do NOT write sentences.
- Do NOT explain anything.
- Do NOT use bullets or numbering.
- Do NOT make it vague or conceptual.
- Prefer concrete visual tags over abstract phrases.

Example input:
boat, water, lake, cabin

Example output:
lake, boat, cabin, summer, tiny bikini, wet hair, sun-kissed skin, golden hour sunlight, sparkling water reflections, warm outdoor atmosphere, realistic skin texture, shallow depth of field, intimate creator-content mood, natural phone-camera realism
USER TAGS:
{simple_tags}
"""


def build_premium_surprise_tags_prompt(simple_tags: str) -> str:
    return f"""
You are a Premium Creator Content Creative Director.

The user gives simple creative tags.

Your job is to create a more imaginative premium-ready comma-separated visual tag list.

Keep the user's original idea, but add a stronger creative direction with richer image-generation details.

Focus on:
- unexpected but realistic setting details
- wardrobe and styling
- pose and body positioning
- environment details
- props
- lighting
- camera framing
- textures
- atmosphere
- luxury lifestyle details
- cinematic visual energy

Important rules:
- Return ONLY one comma-separated tag list.
- Do NOT write a full prompt.
- Do NOT write sentences.
- Do NOT explain anything.
- Do NOT use bullets or numbering.
- Do NOT make it vague or conceptual.
- Prefer concrete visual tags over abstract phrases.

Example input:
boat, water, lake, cabin

Example output:
private lake house dock, polished wooden speedboat, emerald lake water, secluded cabin porch, tiny white bikini, oversized sunhat, wet skin glow, soft wind in hair, sunset reflections, champagne glass prop, barefoot pose, close-up portrait framing, cinematic summer escape, shallow depth of field, luxury vacation realism

USER TAGS:
{simple_tags}
"""


def _call_grok(prompt: str) -> str:
    response = client.chat.completions.create(
        model=os.getenv("GROK_MODEL"),
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.9,
    )

    return response.choices[0].message.content.strip()


def enhance_premium_tags(simple_tags: str) -> str:
    prompt = build_premium_tag_enhancer_prompt(
        simple_tags=simple_tags,
    )

    return _call_grok(prompt)


def surprise_premium_tags(simple_tags: str) -> str:
    prompt = build_premium_surprise_tags_prompt(
        simple_tags=simple_tags,
    )

    return _call_grok(prompt)