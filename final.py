import requests
import time

api_token = "msy_9a7pGswKXXAfouDj1PFIs6WgvAymPGzQp2Yk"

# Step 1: Generate the task ID
payload = {
    "mode": "preview",
    "prompt": "the tiger",
    "art_style": "realistic",
    "negative_prompt": "low quality, low resolution, low poly, attractive"
}

headers = {
    "Authorization": f"Bearer {api_token}"
}

try:
    response = requests.post(
        "https://api.meshy.ai/v2/text-to-3d",
        headers=headers,
        json=payload,
    )
    response.raise_for_status()
    task_id = response.json().get('result')
    if not task_id:
        raise ValueError("No task ID returned in response")
    print(f"Task ID: {task_id}")

    # Optional: Wait for a few seconds to ensure the task has had time to process
    time.sleep(5)
    
    while True:
        response = requests.get(
            f"https://api.meshy.ai/v1/text-to-texture/{task_id}",
            headers=headers,
        )

        response.raise_for_status()
        result = response.json()
                
        if result['status'] == 'SUCCEEDED':
            print("Task succeeded!")
            print(result)
            break
        elif result['status'] == 'FAILED':
            print("Task failed!")
            break
        else:
            print(f"Task status: {result['status']}. Checking again in 10 seconds...")
            time.sleep(10)

except requests.exceptions.HTTPError as err:
    print(f"HTTP error occurred: {err}")
except Exception as err:
    print(f"An error occurred: {err}")
