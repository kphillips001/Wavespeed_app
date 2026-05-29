import os

from dotenv import load_dotenv

from main import generate_prompts_with_grok

load_dotenv()


def build_premium_tag_enhancer_prompt(simple_tags: str) -> str:
    return f"""
You are a Premium Creator Content Tag Enhancer.

Rewrite the user's simple tags into one stronger comma-separated tag string.

Keep the user's original intent.

Enhance toward:
- intimate creator content
- private moment energy
- close personal framing
- direct eye contact
- seductive but realistic mood
- natural lifestyle realism
- premium subscriber-style content
- realistic lighting
- body language
- atmosphere

Do not write a full prompt.
Return only one comma-separated tag list.

USER TAGS:
{simple_tags}
"""


def build_premium_surprise_tags_prompt(simple_tags: str) -> str:
    return f"""
You are a Premium Creator Content Creative Director.

Rewrite the user's simple tags into one surprising premium-ready comma-separated tag string.

Keep the user's original intent, but add a richer creative direction.

Add:
- private location details
- lighting
- mood
- atmosphere
- viewer connection
- direct eye contact
- close personal framing
- intimate lifestyle realism
- luxury environment details
- premium subscriber-content feel
- natural body language
- realistic camera feel

Make the result more imaginative than a normal enhancement.

Do not write a full prompt.
Return only one comma-separated tag list.

USER TAGS:
{simple_tags}
"""


def clean_tag_response(raw_response) -> str:
    if isinstance(raw_response, list):
        return ", ".join(
            str(item).strip()
            for item in raw_response
            if str(item).strip()
        )

    return str(raw_response).strip()


def enhance_premium_tags(simple_tags: str) -> str:
    api_key = os.getenv("GROK_API_KEY")

    if not api_key:
        raise ValueError("Missing GROK_API_KEY in .env")

    response = generate_prompts_with_grok(
        build_premium_tag_enhancer_prompt(simple_tags),
        api_key,
    )

    return clean_tag_response(response)


def surprise_premium_tags(simple_tags: str) -> str:
    api_key = os.getenv("GROK_API_KEY")

    if not api_key:
        raise ValueError("Missing GROK_API_KEY in .env")

    response = generate_prompts_with_grok(
        build_premium_surprise_tags_prompt(simple_tags),
        api_key,
    )

    return clean_tag_response(response)