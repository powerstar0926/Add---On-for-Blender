import requests

api_token = "msy_9a7pGswKXXAfouDj1PFIs6WgvAymPGzQp2Yk"

payload = {
    "model_url": "https://cdn.meshy.ai/model/example_model_2.glb",
    "object_prompt": "a rabbit",
    "style_prompt": "white and cute rabbit",
    "enable_original_uv": True,
    "enable_pbr": True,
    "resolution": "1024",
    "negative_prompt": "low quality, low resolution, low poly, ugly"
}

headers = {
    "Authorization": f"Bearer {api_token}"
}

try:
    response = requests.post(
        "https://api.meshy.ai/v1/text-to-texture",
        headers=headers,
        json=payload,
    )
    response.raise_for_status()
    print(response.json())
except requests.exceptions.HTTPError as err:
    print(f"HTTP error occurred: {err}")
