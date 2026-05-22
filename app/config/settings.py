import os
from datetime import datetime


WAVESPEED_RESULT_URL = "https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"


MODELS = {
    "1": {
        "name": "Google Nano Banana 2 Edit",
        "endpoint": "https://api.wavespeed.ai/api/v3/google/nano-banana-2/edit",
    },
    "2": {
        "name": "Google Nano Banana Pro Edit",
        "endpoint": "https://api.wavespeed.ai/api/v3/google/nano-banana-pro/edit",
    },
    "3": {
        "name": "ByteDance Seedream 4.5 Edit",
        "endpoint": "https://api.wavespeed.ai/api/v3/bytedance/seedream-v4.5/edit",
    },
    "4": {
        "name": "ByteDance Seedream 5.0 Lite Edit",
        "endpoint": "https://api.wavespeed.ai/api/v3/bytedance/seedream-v5.0-lite/edit",
    },
}


PERSONA_OUTPUT_DIRS = {
    "1": {
        "name": "Ava Blackthorne",
        "output_dir": r"D:\Ava Blackthorne\Ready\Wavespeed",
    },
    "2": {
        "name": "Amanda Cayne",
        "output_dir": r"D:\Amanda Cayne\Ready\Wavespeed",
    },
}


def get_script_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def get_prompts_file_path():
    return os.path.join(get_script_dir(), "prompts.txt")


def get_outputs_dir(persona_choice):
    return PERSONA_OUTPUT_DIRS[persona_choice]["output_dir"]


def create_run_stamp():
    return datetime.now().strftime("run_%Y%m%d_%H%M%S")


def get_failed_prompts_file_path(run_stamp):
    return os.path.join(get_script_dir(), f"failed_prompts_{run_stamp}.txt")