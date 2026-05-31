import requests


def submit_multi_edit_task(
    api_key,
    model_url,
    prompt,
    image_urls,
):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "prompt": prompt,
        "images": image_urls,
    }

    response = requests.post(
        model_url,
        headers=headers,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return (
        data.get("id")
        or data.get("request_id")
        or data.get("data", {}).get("id")
    )

def poll_multi_edit_result(
    api_key,
    request_id,
):
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    result_url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"

    while True:
        response = requests.get(
            result_url,
            headers=headers,
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()
        status = data.get("status") or data.get("data", {}).get("status")

        if status in ["completed", "succeeded"]:
            outputs = (
                data.get("outputs")
                or data.get("output")
                or data.get("data", {}).get("outputs")
                or data.get("data", {}).get("output")
            )

            if isinstance(outputs, list):
                return outputs[0]

            return outputs

        if status in ["failed", "error"]:
            raise RuntimeError(f"Multi edit failed: {data}")

        import time
        time.sleep(2)